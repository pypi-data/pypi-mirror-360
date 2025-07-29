"""DataPacket class for universal data format"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional
import pyarrow as pa


@dataclass
class DataPacket:
    """Universal data packet for DFT pipelines"""
    
    data: pa.Table
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    source: str = "unknown"
    schema: Optional[pa.Schema] = None
    
    def __post_init__(self) -> None:
        """Set schema from data if not provided"""
        if self.schema is None and self.data is not None:
            self.schema = self.data.schema
    
    @property
    def row_count(self) -> int:
        """Get number of rows in the data"""
        return len(self.data) if self.data is not None else 0
    
    @property
    def column_names(self) -> list[str]:
        """Get column names"""
        return self.data.column_names if self.data is not None else []
    
    @property
    def size_mb(self) -> float:
        """Get approximate size in MB"""
        if self.data is None:
            return 0.0
        return self.data.nbytes / (1024 * 1024)
    
    def to_dict_list(self) -> list[dict]:
        """Convert to list of dictionaries"""
        if self.data is None:
            return []
        
        # Convert Arrow table to list of dicts
        columns = self.data.column_names
        result = []
        
        for i in range(len(self.data)):
            row = {}
            for j, col_name in enumerate(columns):
                value = self.data[col_name][i].as_py()
                row[col_name] = value
            result.append(row)
        
        return result
    
    def to_numpy_dict(self) -> dict[str, "np.ndarray"]:
        """Convert to dictionary of numpy arrays"""
        if self.data is None:
            return {}
        
        result = {}
        for column_name in self.data.column_names:
            # Convert Arrow array to numpy
            arrow_array = self.data[column_name]
            numpy_array = arrow_array.to_numpy()
            result[column_name] = numpy_array
        
        return result
    
    @classmethod
    def from_dict_list(cls, data: list[dict], source: str = "dict_list", **kwargs) -> "DataPacket":
        """Create DataPacket from list of dictionaries"""
        if not data:
            # Empty data
            table = pa.table({})
        else:
            # Convert list of dicts to Arrow table
            table = pa.table(data)
        return cls(data=table, source=source, **kwargs)
    
    @classmethod
    def from_numpy_dict(cls, data: dict[str, "np.ndarray"], source: str = "numpy", **kwargs) -> "DataPacket":
        """Create DataPacket from dictionary of numpy arrays"""
        table = pa.table(data)
        return cls(data=table, source=source, **kwargs)
    
    def add_metadata(self, key: str, value: Any) -> None:
        """Add metadata entry"""
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get metadata entry"""
        return self.metadata.get(key, default)