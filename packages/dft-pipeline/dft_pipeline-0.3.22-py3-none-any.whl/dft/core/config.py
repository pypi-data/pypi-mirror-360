"""Configuration loading and parsing"""

import yaml
from pathlib import Path
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv
from .pipeline import Pipeline, PipelineStep


class ProjectConfig:
    """DFT project configuration"""
    
    def __init__(self, config_path: str = "dft_project.yml"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        
        # Load environment variables
        env_file = self.config_path.parent / ".env"
        if env_file.exists():
            load_dotenv(env_file)
    
    def _load_config(self) -> Dict[str, Any]:
        """Load project configuration from YAML"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Project config not found: {self.config_path}")
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    @property
    def project_name(self) -> str:
        return self.config.get("project_name", "unknown")
    
    @property
    def pipelines_dir(self) -> str:
        return self.config.get("pipelines_dir", "pipelines")
    
    @property
    def variables(self) -> Dict[str, Any]:
        return self.config.get("vars", {})
    
    @property
    def sources(self) -> Dict[str, Any]:
        # Support both old 'sources' format and new 'connections' format
        # Connections can be used as both sources and endpoints
        connections = self.config.get("connections", {})
        sources = self.config.get("sources", {})
        
        # Merge connections and sources (sources take precedence for backward compatibility)
        return {**connections, **sources}
    
    @property
    def connections(self) -> Dict[str, Any]:
        """Get all connections (can be used as sources or endpoints)"""
        return self.config.get("connections", {})
    
    @property
    def state_config(self) -> Dict[str, Any]:
        """Get state management configuration"""
        return self.config.get("state", {"ignore_in_git": True})
    
    @property
    def should_ignore_state_in_git(self) -> bool:
        """Whether state files should be ignored in git"""
        return self.state_config.get("ignore_in_git", True)
    
    @property
    def logging_config(self) -> Dict[str, Any]:
        return self.config.get("logging", {})


class PipelineLoader:
    """Load and parse pipeline configurations"""
    
    def __init__(self, project_config: ProjectConfig):
        self.project_config = project_config
        self.pipelines_dir = Path(project_config.pipelines_dir)
    
    def load_all_pipelines(self) -> List[Pipeline]:
        """Load all pipeline configurations from directory"""
        pipelines = []
        
        if not self.pipelines_dir.exists():
            return pipelines
        
        for yaml_file in self.pipelines_dir.glob("*.yml"):
            try:
                pipeline = self.load_pipeline(yaml_file)
                if pipeline:
                    pipelines.append(pipeline)
            except Exception as e:
                print(f"Error loading pipeline {yaml_file}: {e}")
        
        # Validate pipeline dependencies
        self._validate_pipeline_dependencies(pipelines)
        
        return pipelines
    
    def load_pipeline(self, file_path: Path) -> Optional[Pipeline]:
        """Load single pipeline from YAML file"""
        
        with open(file_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        if not config:
            return None
        
        # Parse pipeline
        pipeline_name = config.get("pipeline_name")
        if not pipeline_name:
            # Use filename as pipeline name if not specified
            pipeline_name = file_path.stem
        
        # Parse steps
        steps = []
        for step_config in config.get("steps", []):
            step = PipelineStep(
                id=step_config["id"],
                type=step_config["type"],
                config=step_config.get("config", {}),
                depends_on=step_config.get("depends_on", []),
                source_type=step_config.get("source_type"),
                processor_type=step_config.get("processor_type"),
                endpoint_type=step_config.get("endpoint_type"),
                name=step_config.get("name"),
                connection=step_config.get("connection")
            )
            steps.append(step)
        
        # Create pipeline
        pipeline = Pipeline(
            name=pipeline_name,
            steps=steps,
            tags=config.get("tags", []),
            depends_on=config.get("depends_on", []),
            variables=config.get("variables", {})
        )
        
        return pipeline
    
    def find_pipelines(self, select: Optional[str] = None, exclude: Optional[str] = None) -> List[Pipeline]:
        """Find pipelines matching selection criteria"""
        all_pipelines = self.load_all_pipelines()
        
        if not select and not exclude:
            return all_pipelines
        
        selected = []
        
        for pipeline in all_pipelines:
            include = True
            
            # Apply selection criteria
            if select:
                include = self._matches_selection(pipeline, select, all_pipelines)
            
            # Apply exclusion criteria
            if exclude and include:
                include = not self._matches_selection(pipeline, exclude, all_pipelines)
            
            if include:
                selected.append(pipeline)
        
        return selected
    
    def _matches_selection(self, pipeline: Pipeline, criteria: str, all_pipelines: List[Pipeline]) -> bool:
        """Check if pipeline matches selection criteria"""
        
        # Direct name match
        if criteria == pipeline.name:
            return True
        
        # Tag match (tag:tagname)
        if criteria.startswith("tag:"):
            tag = criteria[4:]
            return pipeline.has_tag(tag)
        
        # Dependencies match (+pipeline_name, pipeline_name+, +pipeline_name+)
        if criteria.startswith("+") or criteria.endswith("+"):
            return self._matches_dependency_selection(pipeline, criteria, all_pipelines)
        
        # Wildcard match
        if "*" in criteria:
            import fnmatch
            return fnmatch.fnmatch(pipeline.name, criteria)
        
        return False
    
    def _has_dependency(self, pipeline: Pipeline, target_name: str) -> bool:
        """Check if pipeline depends on target pipeline"""
        return target_name in pipeline.depends_on
    
    def _validate_pipeline_dependencies(self, pipelines: List[Pipeline]) -> None:
        """Validate that all pipeline dependencies exist and are not circular"""
        
        # Create mapping of pipeline names
        pipeline_names = {p.name for p in pipelines}
        
        # Check that all dependencies exist
        for pipeline in pipelines:
            for dep in pipeline.depends_on:
                if dep not in pipeline_names:
                    raise ValueError(f"Pipeline '{pipeline.name}' depends on '{dep}' which does not exist")
        
        # Check for circular dependencies using DFS
        visited = set()
        temp_visited = set()
        
        def has_cycle(pipeline_name: str, pipeline_map: Dict[str, Pipeline]) -> bool:
            if pipeline_name in temp_visited:
                return True  # Cycle detected
            
            if pipeline_name in visited:
                return False
            
            temp_visited.add(pipeline_name)
            
            # Check dependencies
            pipeline = pipeline_map.get(pipeline_name)
            if pipeline:
                for dep in pipeline.depends_on:
                    if has_cycle(dep, pipeline_map):
                        return True
            
            temp_visited.remove(pipeline_name)
            visited.add(pipeline_name)
            return False
        
        # Create pipeline mapping
        pipeline_map = {p.name: p for p in pipelines}
        
        # Check each pipeline for cycles
        for pipeline in pipelines:
            visited.clear()
            temp_visited.clear()
            if has_cycle(pipeline.name, pipeline_map):
                raise ValueError(f"Circular dependency detected in pipeline dependency graph involving '{pipeline.name}'")
    
    def _matches_dependency_selection(self, pipeline: Pipeline, criteria: str, all_pipelines: List[Pipeline]) -> bool:
        """Check if pipeline matches dependency-based selection criteria"""
        
        # Parse the criteria to understand the dependency pattern
        upstream_only = criteria.startswith("+") and not criteria.endswith("+")  # +pipeline
        downstream_only = criteria.endswith("+") and not criteria.startswith("+")  # pipeline+
        both_directions = criteria.startswith("+") and criteria.endswith("+")  # +pipeline+
        
        # Extract target pipeline name
        if upstream_only:
            target_name = criteria[1:]  # Remove leading +
        elif downstream_only:
            target_name = criteria[:-1]  # Remove trailing +
        elif both_directions:
            target_name = criteria[1:-1]  # Remove both + symbols
        else:
            return False
        
        # Create pipeline mapping for dependency resolution
        pipeline_map = {p.name: p for p in all_pipelines}
        
        if target_name not in pipeline_map:
            return False
        
        target_pipeline = pipeline_map[target_name]
        
        # Check different dependency relationships
        if upstream_only:
            # +pipeline: Include pipelines that the target depends on (upstream)
            return self._is_upstream_of(pipeline, target_pipeline, pipeline_map)
        elif downstream_only:
            # pipeline+: Include pipelines that depend on the target (downstream)
            return self._is_downstream_of(pipeline, target_pipeline, pipeline_map)
        elif both_directions:
            # +pipeline+: Include both upstream and downstream of target, plus target itself
            return (pipeline.name == target_name or 
                    self._is_upstream_of(pipeline, target_pipeline, pipeline_map) or
                    self._is_downstream_of(pipeline, target_pipeline, pipeline_map))
        
        return False
    
    def _is_upstream_of(self, pipeline: Pipeline, target: Pipeline, pipeline_map: Dict[str, Pipeline]) -> bool:
        """Check if pipeline is upstream of target (target depends on pipeline, directly or indirectly)"""
        visited = set()
        
        def has_upstream_dependency(current_pipeline: Pipeline) -> bool:
            if current_pipeline.name in visited:
                return False
            visited.add(current_pipeline.name)
            
            # Direct dependency
            if pipeline.name in current_pipeline.depends_on:
                return True
            
            # Indirect dependency through chain
            for dep_name in current_pipeline.depends_on:
                dep_pipeline = pipeline_map.get(dep_name)
                if dep_pipeline and has_upstream_dependency(dep_pipeline):
                    return True
            
            return False
        
        return has_upstream_dependency(target)
    
    def _is_downstream_of(self, pipeline: Pipeline, target: Pipeline, pipeline_map: Dict[str, Pipeline]) -> bool:
        """Check if pipeline is downstream of target (pipeline depends on target, directly or indirectly)"""
        visited = set()
        
        def has_downstream_dependency(current_pipeline: Pipeline) -> bool:
            if current_pipeline.name in visited:
                return False
            visited.add(current_pipeline.name)
            
            # Direct dependency
            if target.name in current_pipeline.depends_on:
                return True
            
            # Indirect dependency through chain
            for dep_name in current_pipeline.depends_on:
                dep_pipeline = pipeline_map.get(dep_name)
                if dep_pipeline and has_downstream_dependency(dep_pipeline):
                    return True
            
            return False
        
        return has_downstream_dependency(pipeline)