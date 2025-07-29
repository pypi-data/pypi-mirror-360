"""Components command for DFT"""

import click
import importlib
import inspect
import pkgutil
from typing import Dict, List, Any
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax

console = Console()


@click.group()
def components():
    """Manage and explore DFT components"""
    pass


@components.command()
@click.option("--type", "component_type", type=click.Choice(['source', 'processor', 'endpoint', 'all']), 
              default='all', help="Filter by component type")
def list(component_type):
    """List available components"""
    components_info = discover_components()
    
    if component_type != 'all':
        components_info = {k: v for k, v in components_info.items() if v['type'] == component_type}
    
    if not components_info:
        console.print(f"[yellow]No {component_type} components found[/yellow]")
        return
    
    # Group by type
    by_type = {}
    for name, info in components_info.items():
        comp_type = info['type']
        if comp_type not in by_type:
            by_type[comp_type] = []
        by_type[comp_type].append((name, info))
    
    for comp_type, items in by_type.items():
        table = Table(title=f"{comp_type.title()} Components")
        table.add_column("Name", style="cyan", no_wrap=True)
        table.add_column("Description", style="white")
        table.add_column("Module", style="dim")
        
        for name, info in sorted(items):
            description = info.get('description', '').split('\n')[0]  # First line only
            module = info.get('module', '')
            table.add_row(name, description, module)
        
        console.print(table)
        console.print()


@components.command()
@click.argument("name")
@click.option("--format", "output_format", type=click.Choice(['text', 'yaml']), 
              default='text', help="Output format")
def describe(name, output_format):
    """Show detailed information about a component"""
    components_info = discover_components()
    
    if name not in components_info:
        console.print(f"[red]Component '{name}' not found[/red]")
        # Show similar names
        similar = [n for n in components_info.keys() if name.lower() in n.lower()]
        if similar:
            console.print(f"[yellow]Did you mean: {', '.join(similar)}?[/yellow]")
        return
    
    info = components_info[name]
    
    if output_format == 'yaml':
        show_yaml_example(name, info)
    else:
        show_component_details(name, info)


def discover_components() -> Dict[str, Dict[str, Any]]:
    """Discover all available components and their metadata"""
    components = {}
    
    # Discover sources
    try:
        import dft.sources as sources_pkg
        for name, cls in discover_in_package(sources_pkg, 'source').items():
            components[name] = cls
    except ImportError:
        pass
    
    # Discover processors
    try:
        import dft.processors as processors_pkg
        for name, cls in discover_in_package(processors_pkg, 'processor').items():
            components[name] = cls
    except ImportError:
        pass
    
    # Discover endpoints
    try:
        import dft.endpoints as endpoints_pkg
        for name, cls in discover_in_package(endpoints_pkg, 'endpoint').items():
            components[name] = cls
    except ImportError:
        pass
    
    return components


def discover_in_package(package, component_type: str) -> Dict[str, Dict[str, Any]]:
    """Discover components in a specific package"""
    components = {}
    
    for importer, modname, ispkg in pkgutil.iter_modules(package.__path__):
        if ispkg:
            continue
        
        try:
            module_name = f"{package.__name__}.{modname}"
            module = importlib.import_module(module_name)
            
            # Find classes that inherit from the appropriate base class
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if is_component_class(obj, component_type):
                    components[modname] = {
                        'type': component_type,
                        'class': obj,
                        'module': module_name,
                        'description': get_component_description(obj),
                        'docstring': inspect.getdoc(obj) or ""
                    }
                    break  # Only one component per module
        except ImportError:
            continue
    
    return components


def is_component_class(cls, component_type: str) -> bool:
    """Check if a class is a component of the specified type"""
    try:
        from dft.core.base import DataSource, DataProcessor, DataEndpoint
        
        if component_type == 'source':
            return (issubclass(cls, DataSource) and 
                   cls != DataSource and
                   not cls.__name__.startswith('_'))
        elif component_type == 'processor':
            return (issubclass(cls, DataProcessor) and 
                   cls != DataProcessor and
                   not cls.__name__.startswith('_'))
        elif component_type == 'endpoint':
            return (issubclass(cls, DataEndpoint) and 
                   cls != DataEndpoint and
                   not cls.__name__.startswith('_'))
    except ImportError:
        pass
    
    return False


def get_component_description(cls) -> str:
    """Extract brief description from docstring"""
    docstring = inspect.getdoc(cls)
    if not docstring:
        return "No description available"
    
    # Get first line of docstring
    first_line = docstring.split('\n')[0].strip()
    return first_line


def show_component_details(name: str, info: Dict[str, Any]):
    """Show detailed component information"""
    cls = info['class']
    docstring = info['docstring']
    
    # Title panel
    console.print(Panel(
        f"[bold cyan]{name}[/bold cyan] ({info['type']})\n"
        f"[dim]{info['module']}[/dim]",
        title="Component Details"
    ))
    
    if docstring:
        # Parse docstring for structured display
        sections = parse_docstring(docstring)
        
        for section_name, content in sections.items():
            if section_name == 'description':
                console.print(Panel(content, title="Description"))
            elif section_name in ['required_config', 'optional_config']:
                title = "Required Configuration" if section_name == 'required_config' else "Optional Configuration"
                console.print(Panel(content, title=title))
            elif 'example' in section_name.lower():
                console.print(Panel(
                    Syntax(content, "yaml", theme="monokai"),
                    title=section_name.replace('_', ' ').title()
                ))
    else:
        console.print("[yellow]No documentation available for this component[/yellow]")


def show_yaml_example(name: str, info: Dict[str, Any]):
    """Show YAML configuration example"""
    docstring = info['docstring']
    
    if not docstring:
        console.print(f"[yellow]No YAML example available for {name}[/yellow]")
        return
    
    # Extract YAML examples from docstring
    examples = extract_yaml_examples(docstring)
    
    if examples:
        for i, example in enumerate(examples):
            title = f"YAML Example {i+1}" if len(examples) > 1 else "YAML Example"
            console.print(Panel(
                Syntax(example, "yaml", theme="monokai"),
                title=title
            ))
    else:
        console.print(f"[yellow]No YAML examples found for {name}[/yellow]")


def parse_docstring(docstring: str) -> Dict[str, str]:
    """Parse structured docstring into sections"""
    sections = {}
    current_section = 'description'
    current_content = []
    
    lines = docstring.split('\n')
    
    for line in lines:
        line = line.strip()
        
        if line.endswith(':') and line.lower().replace(' ', '_') in [
            'required_config', 'optional_config', 'yaml_example', 'variables_example', 
            'named_connection_example', 'check_rule_format'
        ]:
            # Save previous section
            if current_content:
                sections[current_section] = '\n'.join(current_content).strip()
            
            # Start new section
            current_section = line[:-1].lower().replace(' ', '_')
            current_content = []
        else:
            current_content.append(line)
    
    # Save final section
    if current_content:
        sections[current_section] = '\n'.join(current_content).strip()
    
    return sections


def extract_yaml_examples(docstring: str) -> List[str]:
    """Extract YAML code blocks from docstring"""
    examples = []
    lines = docstring.split('\n')
    in_yaml_block = False
    current_example = []
    
    for line in lines:
        if 'yaml example' in line.lower() or 'example:' in line.lower():
            if current_example and in_yaml_block:
                examples.append('\n'.join(current_example))
            current_example = []
            in_yaml_block = True
            continue
        
        if in_yaml_block:
            # Check if we're still in the example block
            if line.strip() and not line.startswith('    ') and not line.startswith('\t'):
                # End of example block
                if current_example:
                    examples.append('\n'.join(current_example))
                current_example = []
                in_yaml_block = False
            else:
                # Remove leading whitespace but preserve relative indentation
                if line.strip():
                    current_example.append(line[4:] if line.startswith('    ') else line)
                elif current_example:  # Only add empty lines if we're in an example
                    current_example.append('')
    
    # Add final example if exists
    if current_example and in_yaml_block:
        examples.append('\n'.join(current_example))
    
    return examples