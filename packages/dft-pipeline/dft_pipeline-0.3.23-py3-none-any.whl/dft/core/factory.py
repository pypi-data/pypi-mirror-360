"""Component factory for creating sources, processors, and endpoints"""

import os
import sys
import importlib.util
from pathlib import Path
from typing import Any, Dict
from .base import DataSource, DataProcessor, DataEndpoint
from .config import ProjectConfig
from ..utils.template import TemplateRenderer


class ComponentFactory:
    """Factory for creating DFT components"""
    
    def __init__(self, project_config: ProjectConfig, template_renderer: TemplateRenderer = None):
        self.project_config = project_config
        self.template_renderer = template_renderer or TemplateRenderer()
        self._register_built_in_components()
        self._load_custom_components()
    
    def _register_built_in_components(self) -> None:
        """Register built-in component types"""
        # Sources
        self._source_registry = {
            "csv": "dft.sources.csv.CSVSource",
            "json": "dft.sources.json.JSONSource", 
            "postgresql": "dft.sources.postgresql.PostgreSQLSource",
            "clickhouse": "dft.sources.clickhouse.ClickHouseSource",
            "mysql": "dft.sources.mysql.MySQLSource",
            "google_play": "dft.sources.google_play.GooglePlaySource",
            "api": "dft.sources.api.APISource",
        }
        
        # Processors
        self._processor_registry = {
            "validator": "dft.processors.validator.DataValidator",
            "mad_anomaly_detector": "dft.processors.mad_anomaly_detector.MADAnomalyDetector",
            "aggregator": "dft.processors.aggregator.Aggregator",
            "filter": "dft.processors.filter.Filter",
            "transformer": "dft.processors.transformer.Transformer",
            "ab_testing": "dft.processors.ab_testing.ABTestProcessor",
        }
        
        # Endpoints
        self._endpoint_registry = {
            "csv": "dft.endpoints.csv.CSVEndpoint",
            "json": "dft.endpoints.json.JSONEndpoint",
            "postgresql": "dft.endpoints.postgresql.PostgreSQLEndpoint", 
            "clickhouse": "dft.endpoints.clickhouse.ClickHouseEndpoint",
            "mysql": "dft.endpoints.mysql.MySQLEndpoint",
            "slack": "dft.endpoints.slack.SlackEndpoint",
            "mattermost": "dft.endpoints.mattermost.MattermostEndpoint",
        }
    
    def create_source(self, source_type: str, config: Dict[str, Any]) -> DataSource:
        """Create data source instance"""
        if source_type not in self._source_registry:
            raise ValueError(f"Unknown source type: {source_type}")
        
        class_path = self._source_registry[source_type]
        source_class = self._import_class(class_path)
        
        # Merge with project source config if available
        # Support both 'name' (legacy) and 'connection' (new) parameters
        connection_name = config.get("connection") or config.get("name", "")
        source_config = self._get_source_config(connection_name, config)
        
        return source_class(source_config)
    
    def create_processor(self, processor_type: str, config: Dict[str, Any]) -> DataProcessor:
        """Create data processor instance"""
        if processor_type not in self._processor_registry:
            raise ValueError(f"Unknown processor type: {processor_type}")
        
        class_path = self._processor_registry[processor_type]
        processor_class = self._import_class(class_path)
        
        return processor_class(config)
    
    def create_endpoint(self, endpoint_type: str, config: Dict[str, Any]) -> DataEndpoint:
        """Create data endpoint instance"""
        if endpoint_type not in self._endpoint_registry:
            raise ValueError(f"Unknown endpoint type: {endpoint_type}")
        
        class_path = self._endpoint_registry[endpoint_type]
        endpoint_class = self._import_class(class_path)
        
        # Merge with project source config if available (for database endpoints)
        # Support both 'name' (legacy) and 'connection' (new) parameters
        connection_name = config.get("connection") or config.get("name", "")
        endpoint_config = self._get_source_config(connection_name, config)
        
        return endpoint_class(endpoint_config)
    
    def _get_source_config(self, source_name: str, step_config: Dict[str, Any]) -> Dict[str, Any]:
        """Get merged source configuration from project config and step config"""
        
        # Start with step config
        merged_config = step_config.copy()
        
        # If source name is specified, merge with project source config
        if source_name and source_name in self.project_config.sources:
            project_source_config = self.project_config.sources[source_name]
            # Project config takes precedence for connection details
            merged_config = {**merged_config, **project_source_config}
        
        # Render templates in the merged configuration
        if self.template_renderer:
            merged_config = self.template_renderer.render_config(merged_config)
        
        return merged_config
    
    def _import_class(self, class_path: str):
        """Dynamically import class from string path"""
        module_path, class_name = class_path.rsplit(".", 1)
        
        try:
            module = __import__(module_path, fromlist=[class_name])
            return getattr(module, class_name)
        except (ImportError, AttributeError) as e:
            raise ImportError(f"Could not import {class_path}: {e}")
    
    def register_source(self, source_type: str, class_path: str) -> None:
        """Register custom source type"""
        self._source_registry[source_type] = class_path
    
    def register_processor(self, processor_type: str, class_path: str) -> None:
        """Register custom processor type"""
        self._processor_registry[processor_type] = class_path
    
    def register_endpoint(self, endpoint_type: str, class_path: str) -> None:
        """Register custom endpoint type"""
        self._endpoint_registry[endpoint_type] = class_path
    
    def _load_custom_components(self) -> None:
        """Load custom components from project dft/ directory"""
        project_root = Path.cwd()
        custom_dft_dir = project_root / "dft"
        
        if not custom_dft_dir.exists():
            return
        
        # Add project root to Python path if not already there
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))
        
        # Load custom sources
        self._load_custom_components_from_dir(
            custom_dft_dir / "sources", 
            "source", 
            self._source_registry
        )
        
        # Load custom processors
        self._load_custom_components_from_dir(
            custom_dft_dir / "processors", 
            "processor", 
            self._processor_registry
        )
        
        # Load custom endpoints
        self._load_custom_components_from_dir(
            custom_dft_dir / "endpoints", 
            "endpoint", 
            self._endpoint_registry
        )
    
    def _load_custom_components_from_dir(self, components_dir: Path, component_type: str, registry: Dict[str, str]) -> None:
        """Load custom components from a specific directory"""
        if not components_dir.exists():
            return
        
        for py_file in components_dir.glob("*.py"):
            if py_file.name == "__init__.py":
                continue
            
            module_name = py_file.stem
            try:
                # Load the module
                spec = importlib.util.spec_from_file_location(
                    f"dft.{component_type}s.{module_name}", 
                    py_file
                )
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    # Look for classes that inherit from the appropriate base class
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if (isinstance(attr, type) and 
                            attr.__name__ != f"Data{component_type.capitalize()}" and
                            self._is_component_class(attr, component_type)):
                            
                            # Register the component with a snake_case name
                            component_name = self._class_name_to_component_name(attr.__name__)
                            class_path = f"dft.{component_type}s.{module_name}.{attr.__name__}"
                            registry[component_name] = class_path
                            
            except Exception as e:
                # Log warning but don't fail the entire loading process
                print(f"Warning: Could not load custom {component_type} from {py_file}: {e}")
    
    def _is_component_class(self, cls, component_type: str) -> bool:
        """Check if a class is a valid component class"""
        from .base import DataSource, DataProcessor, DataEndpoint
        
        base_classes = {
            "source": DataSource,
            "processor": DataProcessor, 
            "endpoint": DataEndpoint
        }
        
        base_class = base_classes.get(component_type)
        if not base_class:
            return False
        
        try:
            return issubclass(cls, base_class) and cls != base_class
        except TypeError:
            return False
    
    def _class_name_to_component_name(self, class_name: str) -> str:
        """Convert CamelCase class name to snake_case component name"""
        # Remove common suffixes
        suffixes = ["Source", "Processor", "Endpoint"]
        for suffix in suffixes:
            if class_name.endswith(suffix):
                class_name = class_name[:-len(suffix)]
                break
        
        # Convert to snake_case
        result = ""
        for i, char in enumerate(class_name):
            if i > 0 and char.isupper():
                result += "_"
            result += char.lower()
        
        return result