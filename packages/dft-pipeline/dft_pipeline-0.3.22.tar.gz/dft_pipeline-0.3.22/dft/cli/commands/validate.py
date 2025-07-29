"""Validate command for DFT"""

import click
from pathlib import Path
from typing import Optional


def run_validation(select: Optional[str]) -> None:
    """Validate pipeline configurations and dependencies"""
    
    # Check if we're in a DFT project
    if not Path("dft_project.yml").exists():
        click.echo("Error: Not in a DFT project directory. Run 'dft init' first.")
        return
    
    try:
        # For now, just validate pipeline configurations
        from ...core.config import ProjectConfig, PipelineLoader
        
        project_config = ProjectConfig()
        pipeline_loader = PipelineLoader(project_config)
        
        # Load all pipelines and check for errors
        pipelines = pipeline_loader.load_all_pipelines()
        
        if not pipelines:
            click.echo("No pipelines found to validate")
            return
        
        errors = []
        
        for pipeline in pipelines:
            try:
                # Validate execution order (check for circular dependencies)
                pipeline.get_execution_order()
                click.echo(f"✅ Pipeline '{pipeline.name}' - configuration valid")
            except Exception as e:
                errors.append(f"❌ Pipeline '{pipeline.name}' - {e}")
        
        if errors:
            click.echo("\nErrors found:")
            for error in errors:
                click.echo(error)
            exit(1)
        else:
            click.echo(f"\n✅ All {len(pipelines)} pipeline(s) passed validation")
            
    except Exception as e:
        click.echo(f"Error running validation: {e}")
        exit(1)