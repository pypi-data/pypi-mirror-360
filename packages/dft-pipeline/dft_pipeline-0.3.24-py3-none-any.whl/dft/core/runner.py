"""Pipeline execution runner"""

from typing import Any, Dict, List, Optional
from datetime import datetime
import logging
from pathlib import Path

from .config import ProjectConfig, PipelineLoader
from .pipeline import Pipeline, PipelineStep
from .factory import ComponentFactory
from .state import PipelineState, IncrementalProcessor
from .microbatch import MicrobatchStrategy, MicrobatchConfig, BatchPeriod
from ..utils.template import TemplateRenderer
from ..utils.logging import PipelineLogger


class PipelineRunner:
    """Main pipeline execution engine"""
    
    def __init__(self):
        self.project_config = ProjectConfig()
        self.pipeline_loader = PipelineLoader(self.project_config)
        self.template_renderer = TemplateRenderer()
        self.factory = ComponentFactory(self.project_config, self.template_renderer)
        self.logger = logging.getLogger("dft.runner")
    
    def run(
        self,
        select: Optional[str] = None,
        exclude: Optional[str] = None,
        variables: Optional[Dict[str, Any]] = None,
        full_refresh: bool = False
    ) -> bool:
        """Run selected pipelines"""
        
        # Find pipelines to run
        pipelines = self.pipeline_loader.find_pipelines(select, exclude)
        
        if not pipelines:
            self.logger.info("No pipelines found matching criteria")
            return True
        
        # Sort pipelines by dependencies
        try:
            ordered_pipelines = self._resolve_pipeline_dependencies(pipelines)
        except ValueError as e:
            self.logger.error(f"Pipeline dependency error: {e}")
            return False
        
        # Merge variables from config and command line
        all_variables = {
            **self.project_config.variables,
            **(variables or {})
        }
        
        self.logger.info(f"Running {len(ordered_pipelines)} pipeline(s) in dependency order")
        
        overall_success = True
        failed_pipelines = set()
        
        # Execute pipelines in dependency order
        for pipeline in ordered_pipelines:
            try:
                # Check if any dependencies failed
                if self._has_failed_dependencies(pipeline, failed_pipelines):
                    self.logger.warning(f"Skipping pipeline {pipeline.name} due to failed dependencies")
                    failed_pipelines.add(pipeline.name)
                    overall_success = False
                    continue
                
                success = self.run_pipeline(pipeline, all_variables, full_refresh)
                if not success:
                    failed_pipelines.add(pipeline.name)
                    overall_success = False
            except Exception as e:
                self.logger.error(f"Failed to run pipeline {pipeline.name}: {e}")
                failed_pipelines.add(pipeline.name)
                overall_success = False
        
        return overall_success
    
    def run_pipeline(
        self, 
        pipeline: Pipeline, 
        variables: Dict[str, Any], 
        full_refresh: bool = False
    ) -> bool:
        """Run single pipeline"""
        
        # Check if pipeline has microbatch configuration
        microbatch_config = pipeline.variables.get("microbatch")
        if microbatch_config:
            return self._run_microbatch_pipeline(pipeline, variables, full_refresh)
        else:
            return self._run_regular_pipeline(pipeline, variables, full_refresh)
    
    def _run_microbatch_pipeline(
        self, 
        pipeline: Pipeline, 
        variables: Dict[str, Any], 
        full_refresh: bool = False
    ) -> bool:
        """Run pipeline with microbatch strategy"""
        
        self.logger.info(f"Running pipeline {pipeline.name} with microbatch strategy")
        
        # Parse microbatch configuration
        mb_config = pipeline.variables["microbatch"]
        
        # Parse datetime strings
        begin_dt = None
        if mb_config.get("begin"):
            begin_dt = datetime.fromisoformat(mb_config["begin"])
        
        end_dt = None
        if mb_config.get("end"):
            end_dt = datetime.fromisoformat(mb_config["end"])
        
        config = MicrobatchConfig(
            event_time_column=mb_config["event_time_column"],
            batch_size=BatchPeriod(mb_config["batch_size"]),
            lookback=mb_config.get("lookback", 1),
            begin=begin_dt,
            end=end_dt
        )
        
        # Create microbatch strategy
        strategy = MicrobatchStrategy(config, pipeline.name)
        
        # Get batch windows to process
        windows = strategy.get_batch_windows()
        
        if not windows:
            self.logger.info(f"No batch windows to process for pipeline {pipeline.name}")
            return True
        
        self.logger.info(f"Processing {len(windows)} batch windows for pipeline {pipeline.name}")
        
        # Process each batch window
        for i, window in enumerate(windows, 1):
            self.logger.info(f"Processing batch {i}/{len(windows)}: {window}")
            
            # Get batch-specific variables
            batch_variables = {
                **variables,
                **strategy.get_batch_variables(window)
            }
            
            # Run regular pipeline with batch variables
            success = self._run_regular_pipeline(pipeline, batch_variables, full_refresh)
            
            if success:
                # Mark window as processed
                strategy.mark_window_processed(window)
                self.logger.info(f"Successfully processed batch {i}/{len(windows)}: {window}")
            else:
                self.logger.error(f"Failed to process batch {i}/{len(windows)}: {window}")
                self.logger.error(f"Stopping microbatch processing due to failure")
                return False
        
        self.logger.info(f"Successfully completed microbatch pipeline {pipeline.name}: {len(windows)} batches processed")
        return True
    
    def _run_regular_pipeline(
        self, 
        pipeline: Pipeline, 
        variables: Dict[str, Any], 
        full_refresh: bool = False
    ) -> bool:
        """Run regular pipeline"""
        
        pipeline_logger = PipelineLogger(pipeline.name)
        pipeline_logger.set_total_steps(len(pipeline.steps))
        
        # Check if this is microbatch run and add batch info
        batch_info = None
        if variables.get('batch_start') and variables.get('batch_end'):
            batch_info = f"batch {variables['batch_period']} [{variables['batch_start']} - {variables['batch_end']}]"
        
        execution_id = pipeline_logger.log_pipeline_start(batch_info)
        
        # Initialize pipeline state for incremental processing
        pipeline_state = PipelineState(pipeline.name)
        incremental_processor = IncrementalProcessor(pipeline_state)
        
        # Add state and incremental processor to variables for template access
        variables = {
            **variables,
            **pipeline.variables,  # Add pipeline variables
            'state': pipeline_state,
            'incremental': incremental_processor,
        }
        
        try:
            pipeline.status = "running"
            pipeline.start_time = datetime.now()
            
            # Record pipeline run start
            pipeline_state.add_run_record("running", pipeline.start_time)
            
            # Get execution order
            execution_order = pipeline.get_execution_order()
            
            # Store step results for template rendering
            step_results = {}
            
            # Execute steps in order
            for step_id in execution_order:
                step = pipeline.get_step(step_id)
                if not step:
                    continue
                
                success = self.run_step(
                    step, 
                    pipeline, 
                    variables, 
                    step_results, 
                    pipeline_logger,
                    full_refresh
                )
                
                if not success:
                    pipeline.status = "failed"
                    pipeline_logger.log_pipeline_complete(execution_id, False)
                    return False
            
            pipeline.status = "success"
            pipeline.end_time = datetime.now()
            
            # Record successful pipeline run
            pipeline_state.add_run_record("success", pipeline.start_time, pipeline.end_time)
            
            pipeline_logger.log_pipeline_complete(execution_id, True)
            return True
            
        except Exception as e:
            pipeline.status = "failed"
            pipeline.end_time = datetime.now()
            
            # Record failed pipeline run
            pipeline_state.add_run_record("failed", pipeline.start_time, pipeline.end_time, str(e))
            
            # Log full error with traceback
            import traceback
            full_traceback = traceback.format_exc()
            self.logger.error(f"Pipeline {pipeline.name} failed: {e}")
            self.logger.error(f"Full traceback:\n{full_traceback}")
            
            # Also print to console for immediate visibility
            print(f"\nPIPELINE ERROR: {e}")
            print(f"Full traceback:\n{full_traceback}")
            
            pipeline_logger.log_pipeline_complete(execution_id, False)
            return False
    
    def run_step(
        self,
        step: PipelineStep,
        pipeline: Pipeline,
        variables: Dict[str, Any],
        step_results: Dict[str, Any],
        pipeline_logger: PipelineLogger,
        full_refresh: bool = False
    ) -> bool:
        """Run single step"""
        
        try:
            step.status = "running"
            step.start_time = datetime.now()
            
            pipeline_logger.log_step_start(step.id)
            
            # Render step configuration with variables and previous results
            rendered_config = self.template_renderer.render_config(
                step.config, variables, step_results
            )
            
            # Add connection information to rendered config
            # Support both 'connection' (new) and 'name' (legacy) fields
            if step.connection:
                rendered_config["connection"] = step.connection
            elif step.name:
                rendered_config["name"] = step.name
            
            # Execute step based on type
            if step.type == "source":
                component = self.factory.create_source(step.source_type or "", rendered_config)
                result = component.extract(variables)
                
            elif step.type == "processor":
                component = self.factory.create_processor(step.processor_type or "", rendered_config)
                
                # Get input data from dependencies
                if step.depends_on:
                    # For now, use result from first dependency
                    dep_step_id = step.depends_on[0]
                    if dep_step_id in step_results:
                        input_data = step_results[dep_step_id]
                    else:
                        raise ValueError(f"Dependency {dep_step_id} not found")
                else:
                    raise ValueError("Processor step requires dependencies")
                
                result = component.process(input_data, variables)
                
            elif step.type == "endpoint":
                component = self.factory.create_endpoint(step.endpoint_type or "", rendered_config)
                
                # Get input data from dependencies  
                if step.depends_on:
                    dep_step_id = step.depends_on[0]
                    if dep_step_id in step_results:
                        input_data = step_results[dep_step_id]
                    else:
                        raise ValueError(f"Dependency {dep_step_id} not found")
                else:
                    raise ValueError("Endpoint step requires dependencies")
                
                # Check if this is microbatch processing
                if variables.get('batch_start') and variables.get('batch_end'):
                    # Use microbatch-aware loading
                    success = component.load_with_microbatch(
                        input_data, 
                        variables,
                        variables.get('batch_start'),
                        variables.get('batch_end')
                    )
                else:
                    # Regular loading
                    success = component.load(input_data, variables)
                
                result = input_data  # Pass through data
                
                if not success:
                    raise RuntimeError("Failed to load data to endpoint")
                    
            else:
                raise ValueError(f"Unknown step type: {step.type}")
            
            # Store result for use by dependent steps
            step_results[step.id] = result
            step.result = result
            
            step.status = "success"
            step.end_time = datetime.now()
            
            # Log metrics
            if result:
                pipeline_logger.log_step_complete(
                    step.id, True, result.row_count, result.size_mb
                )
            else:
                pipeline_logger.log_step_complete(step.id, True)
            
            return True
            
        except Exception as e:
            step.status = "failed"
            step.end_time = datetime.now()
            step.error_message = str(e)
            
            # Log error with full traceback
            import traceback
            full_traceback = traceback.format_exc()
            self.logger.error(f"Step {step.id} failed: {e}")
            self.logger.error(f"Full traceback:\n{full_traceback}")
            
            # Also print to console for immediate visibility
            print(f"\nSTEP ERROR in {step.id}: {e}")
            print(f"Full traceback:\n{full_traceback}")
            
            pipeline_logger.log_step_error(step.id, str(e))
            return False
    
    def _resolve_pipeline_dependencies(self, pipelines: List[Pipeline]) -> List[Pipeline]:
        """Resolve pipeline dependencies using topological sort"""
        
        # Create pipeline name to pipeline mapping
        pipeline_map = {p.name: p for p in pipelines}
        
        # Validate that all dependencies exist
        for pipeline in pipelines:
            for dep in pipeline.depends_on:
                if dep not in pipeline_map:
                    raise ValueError(f"Pipeline {pipeline.name} depends on {dep} which is not found in selected pipelines")
        
        # Topological sort
        visited = set()
        temp_visited = set()
        result = []
        
        def dfs(pipeline_name: str) -> None:
            if pipeline_name in temp_visited:
                raise ValueError(f"Circular dependency detected involving pipeline: {pipeline_name}")
            
            if pipeline_name in visited:
                return
            
            temp_visited.add(pipeline_name)
            
            # Visit dependencies first
            pipeline = pipeline_map[pipeline_name]
            for dep in pipeline.depends_on:
                if dep in pipeline_map:  # Only process dependencies that are in our selection
                    dfs(dep)
            
            temp_visited.remove(pipeline_name)
            visited.add(pipeline_name)
            result.append(pipeline)
        
        # Process all pipelines
        for pipeline in pipelines:
            if pipeline.name not in visited:
                dfs(pipeline.name)
        
        return result
    
    def _has_failed_dependencies(self, pipeline: Pipeline, failed_pipelines: set) -> bool:
        """Check if any of the pipeline's dependencies have failed"""
        return any(dep in failed_pipelines for dep in pipeline.depends_on)