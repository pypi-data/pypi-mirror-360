"""Main CLI entry point for DFT"""

import click
from pathlib import Path
from typing import Optional
from ..utils.logging import setup_logging


@click.group()
@click.option("--log-level", default="INFO", help="Logging level")
@click.option("--log-dir", help="Directory for log files")
@click.pass_context
def cli(ctx: click.Context, log_level: str, log_dir: Optional[str]) -> None:
    """DFT - Data Flow Tools
    
    Flexible ETL pipeline framework for data analysts and engineers.
    """
    ctx.ensure_object(dict)
    ctx.obj["log_level"] = log_level
    ctx.obj["log_dir"] = log_dir
    
    # Setup logging
    setup_logging(level=log_level, log_dir=log_dir)


@cli.command()
@click.argument("project_name")
@click.option("--pipelines-dir", default="pipelines", help="Directory for pipeline configs")
def init(project_name: str, pipelines_dir: str) -> None:
    """Initialize a new DFT project"""
    from .commands.init import init_project
    init_project(project_name, pipelines_dir)


@cli.command()
@click.option("--select", help="Select pipelines to run. Supports: pipeline_name, tag:tagname, +pipeline_name, pipeline_name+, +pipeline_name+")
@click.option("--exclude", help="Exclude specific pipelines from selection")
@click.option("--vars", help="Pipeline variables as key=value pairs")
@click.option("--full-refresh", is_flag=True, help="Run full refresh (ignore incremental state)")
def run(select: Optional[str], exclude: Optional[str], vars: Optional[str], full_refresh: bool) -> None:
    """Run DFT pipelines with automatic dependency resolution.
    
    Pipelines are automatically executed in dependency order.
    Dependencies are validated before execution.
    
    Examples:
      dft run                         # Run all pipelines
      dft run --select my_pipeline    # Run specific pipeline
      dft run --select tag:daily      # Run pipelines with tag
      dft run --select +my_pipeline   # Run upstream dependencies
      dft run --select my_pipeline+   # Run downstream dependencies
      dft run --select +my_pipeline+  # Run all related pipelines
    """
    from .commands.run import run_pipelines
    run_pipelines(select, exclude, vars, full_refresh)


@cli.command()
@click.option("--select", help="Select specific pipelines to validate")
def validate(select: Optional[str]) -> None:
    """Validate pipeline configurations and dependencies"""
    from .commands.validate import run_validation
    run_validation(select)


@cli.command()
def deps() -> None:
    """Show pipeline dependencies"""
    from .commands.deps import show_dependencies
    show_dependencies()


@cli.command()
@click.option("--serve", is_flag=True, help="Serve documentation locally")
def docs(serve: bool) -> None:
    """Generate and optionally serve documentation"""
    from .commands.docs import generate_docs
    generate_docs(serve)


@cli.command("update-gitignore")
@click.option('--config', default='dft_project.yml', help='Path to project config file')
def update_gitignore_cmd(config: str) -> None:
    """Update .gitignore based on project configuration"""
    from .commands.gitignore import update_gitignore
    update_gitignore.callback(config)


# Add components subcommand
from .commands.components import components
cli.add_command(components)


if __name__ == "__main__":
    cli()