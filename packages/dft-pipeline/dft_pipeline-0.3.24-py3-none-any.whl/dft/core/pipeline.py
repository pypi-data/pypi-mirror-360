"""Pipeline execution logic"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime
from .data_packet import DataPacket


@dataclass
class PipelineStep:
    """Single step in a pipeline"""
    id: str
    type: str  # "source", "processor", "endpoint", "validator"
    config: Dict[str, Any] = field(default_factory=dict)
    depends_on: List[str] = field(default_factory=list)
    
    # Component types
    source_type: Optional[str] = None
    processor_type: Optional[str] = None
    endpoint_type: Optional[str] = None
    name: Optional[str] = None  # Named connection from project config (legacy)
    connection: Optional[str] = None  # Named connection from project config (preferred)
    
    # Runtime properties
    status: str = "pending"  # pending, running, success, failed
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    error_message: Optional[str] = None
    result: Optional[DataPacket] = None


@dataclass 
class Pipeline:
    """Pipeline definition and execution"""
    name: str
    steps: List[PipelineStep]
    tags: List[str] = field(default_factory=list)
    depends_on: List[str] = field(default_factory=list)
    variables: Dict[str, Any] = field(default_factory=dict)
    
    # Runtime properties
    status: str = "pending"
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    
    def get_step(self, step_id: str) -> Optional[PipelineStep]:
        """Get step by ID"""
        for step in self.steps:
            if step.id == step_id:
                return step
        return None
    
    def get_dependencies(self, step_id: str) -> List[PipelineStep]:
        """Get dependency steps for given step"""
        step = self.get_step(step_id)
        if not step:
            return []
        
        deps = []
        for dep_id in step.depends_on:
            dep_step = self.get_step(dep_id)
            if dep_step:
                deps.append(dep_step)
        return deps
    
    def get_execution_order(self) -> List[str]:
        """Get topologically sorted execution order"""
        visited = set()
        temp_visited = set()
        result = []
        
        def dfs(step_id: str) -> None:
            if step_id in temp_visited:
                raise ValueError(f"Circular dependency detected involving step: {step_id}")
            if step_id in visited:
                return
                
            temp_visited.add(step_id)
            step = self.get_step(step_id)
            if step:
                for dep_id in step.depends_on:
                    dfs(dep_id)
            temp_visited.remove(step_id)
            visited.add(step_id)
            result.append(step_id)
        
        for step in self.steps:
            if step.id not in visited:
                dfs(step.id)
        
        return result
    
    def has_tag(self, tag: str) -> bool:
        """Check if pipeline has specific tag"""
        return tag in self.tags