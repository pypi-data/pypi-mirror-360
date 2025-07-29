"""Template rendering utilities using Jinja2"""

import os
from typing import Any, Dict, Optional
from jinja2 import Environment, BaseLoader
from datetime import datetime, date


class TemplateRenderer:
    """Jinja2 template renderer with DFT-specific functions"""
    
    def __init__(self):
        self.env = Environment(loader=BaseLoader())
        self._add_custom_functions()
    
    def _add_custom_functions(self) -> None:
        """Add custom functions to Jinja environment"""
        
        def var(key: str, default: Any = None) -> Any:
            """Get variable value with optional default"""
            return self.current_variables.get(key, default)
        
        def env_var(key: str, default: str = "") -> str:
            """Get environment variable"""
            return os.getenv(key, default)
        
        def today() -> str:
            """Get today's date in YYYY-MM-DD format"""
            return date.today().isoformat()
        
        def now() -> str:
            """Get current timestamp"""
            return datetime.now().isoformat()
        
        def days_ago(days: int) -> str:
            """Get date N days ago"""
            from datetime import timedelta
            return (date.today() - timedelta(days=days)).isoformat()
        
        # Add functions to Jinja environment
        self.env.globals.update({
            'var': var,
            'env_var': env_var,
            'today': today,
            'now': now,
            'days_ago': days_ago,
        })
    
    def render(
        self, 
        template: str, 
        variables: Optional[Dict[str, Any]] = None,
        step_results: Optional[Dict[str, Any]] = None
    ) -> str:
        """Render template with variables and step results"""
        
        # Store current variables for var() function
        self.current_variables = variables or {}
        
        # Create context with variables and step results
        context = {
            **(variables or {}),
            'steps': step_results or {},
        }
        
        # Render template
        template_obj = self.env.from_string(template)
        return template_obj.render(context)
    
    def render_config(
        self, 
        config: Dict[str, Any], 
        variables: Optional[Dict[str, Any]] = None,
        step_results: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Recursively render all string values in config dict"""
        
        def render_value(value: Any) -> Any:
            if isinstance(value, str):
                return self.render(value, variables, step_results)
            elif isinstance(value, dict):
                return {k: render_value(v) for k, v in value.items()}
            elif isinstance(value, list):
                return [render_value(item) for item in value]
            else:
                return value
        
        return render_value(config)