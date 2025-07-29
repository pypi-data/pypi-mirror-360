"""Dependencies command for DFT"""

import click
from pathlib import Path


def show_dependencies() -> None:
    """Show pipeline dependencies"""
    
    if not Path("dft_project.yml").exists():
        click.echo("Error: Not in a DFT project directory. Run 'dft init' first.")
        return
    
    try:
        from ...core.config import ProjectConfig, PipelineLoader
        
        project_config = ProjectConfig()
        pipeline_loader = PipelineLoader(project_config)
        
        pipelines = pipeline_loader.load_all_pipelines()
        
        if not pipelines:
            click.echo("No pipelines found")
            return
        
        click.echo("Pipeline Dependencies:")
        click.echo("=" * 50)
        
        for pipeline in pipelines:
            click.echo(f"\n📋 {pipeline.name}")
            
            if pipeline.tags:
                click.echo(f"   Tags: {', '.join(pipeline.tags)}")
            
            if pipeline.depends_on:
                click.echo(f"   Depends on: {', '.join(pipeline.depends_on)}")
            
            click.echo(f"   Steps: {len(pipeline.steps)}")
            
            # Show step dependencies
            for step in pipeline.steps:
                if step.depends_on:
                    click.echo(f"     - {step.id} → depends on: {', '.join(step.depends_on)}")
                else:
                    click.echo(f"     - {step.id}")
            
            try:
                execution_order = pipeline.get_execution_order()
                click.echo(f"   Execution order: {' → '.join(execution_order)}")
            except Exception as e:
                click.echo(f"   ⚠️  Dependency error: {e}")
        
    except Exception as e:
        click.echo(f"Error showing dependencies: {e}")