"""Simplified DataPacket for testing without pyarrow"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional


@dataclass
class SimpleDataPacket:
    """Simplified data packet for testing without external dependencies"""
    
    data: Any = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    source: str = "unknown"
    
    @property
    def row_count(self) -> int:
        """Get number of rows in the data"""
        if self.data is None:
            return 0
        if hasattr(self.data, '__len__'):
            return len(self.data)
        return 1
    
    @property
    def column_names(self) -> list[str]:
        """Get column names"""
        if hasattr(self.data, 'columns'):
            return list(self.data.columns)
        return []
    
    @property
    def size_mb(self) -> float:
        """Get approximate size in MB"""
        return 0.0  # Placeholder
    
    def add_metadata(self, key: str, value: Any) -> None:
        """Add metadata entry"""
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get metadata entry"""
        return self.metadata.get(key, default)