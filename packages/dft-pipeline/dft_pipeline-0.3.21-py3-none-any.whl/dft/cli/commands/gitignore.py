"""Gitignore management command"""

import click
from pathlib import Path
from dft.core.config import ProjectConfig


def update_gitignore_for_state(project_config: ProjectConfig) -> None:
    """Update .gitignore based on state configuration"""
    
    gitignore_path = Path(".gitignore")
    state_entry = ".dft/state/"
    
    if not gitignore_path.exists():
        click.echo("Warning: .gitignore file not found")
        return
    
    # Read current gitignore
    with open(gitignore_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Remove existing state entry
    lines = [line for line in lines if line.strip() != state_entry.rstrip('/')]
    
    # Add state entry if it should be ignored
    if project_config.should_ignore_state_in_git:
        if not any(state_entry.rstrip('/') in line for line in lines):
            lines.append(f"{state_entry}\n")
            click.echo(f"✅ Added {state_entry} to .gitignore")
    else:
        click.echo(f"✅ Removed {state_entry} from .gitignore (state will be versioned)")
    
    # Write updated gitignore
    with open(gitignore_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)


@click.command()
@click.option('--config', default='dft_project.yml', help='Path to project config file')
def update_gitignore(config: str) -> None:
    """Update .gitignore based on project configuration"""
    
    try:
        project_config = ProjectConfig(config)
        update_gitignore_for_state(project_config)
        
        state_strategy = "ignored" if project_config.should_ignore_state_in_git else "versioned"
        click.echo(f"State strategy: {state_strategy}")
        
    except FileNotFoundError as e:
        click.echo(f"Error: {e}")
    except Exception as e:
        click.echo(f"Error updating .gitignore: {e}")