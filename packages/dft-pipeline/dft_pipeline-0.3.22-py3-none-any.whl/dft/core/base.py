"""Base abstract classes for DFT components"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from datetime import datetime
from .data_packet import DataPacket


class DataSource(ABC):
    """Base class for all data sources"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.name = config.get("name", "unknown")
        self.source_type = config.get("source_type", "unknown")
    
    @abstractmethod
    def extract(self, variables: Optional[Dict[str, Any]] = None) -> DataPacket:
        """Extract data from source"""
        pass
    
    @abstractmethod
    def test_connection(self) -> bool:
        """Test connection to source"""
        pass
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self.config.get(key, default)


class DataProcessor(ABC):
    """Base class for all data processors"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.name = config.get("name", "unknown")
        self.processor_type = config.get("processor_type", "unknown")
    
    @abstractmethod
    def process(self, packet: DataPacket, variables: Optional[Dict[str, Any]] = None) -> DataPacket:
        """Process data packet"""
        pass
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self.config.get(key, default)


class DataEndpoint(ABC):
    """Base class for all data endpoints"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.name = config.get("name", "unknown")
        self.endpoint_type = config.get("endpoint_type", "unknown")
        self.event_time_column = config.get("event_time_column")
    
    @abstractmethod
    def load(self, packet: DataPacket, variables: Optional[Dict[str, Any]] = None) -> bool:
        """Load data to endpoint"""
        pass
    
    def delete_batch_data(self, batch_start: datetime, batch_end: datetime) -> bool:
        """Delete data for microbatch window (override in subclasses)"""
        return True
    
    def load_with_microbatch(
        self, 
        packet: DataPacket, 
        variables: Optional[Dict[str, Any]] = None,
        batch_start: Optional[datetime] = None,
        batch_end: Optional[datetime] = None
    ) -> bool:
        """Load data with microbatch support - deletes old data first"""
        
        # If microbatch variables provided and event_time_column configured
        if (batch_start and batch_end and self.event_time_column and 
            variables and variables.get('batch_start') and variables.get('batch_end')):
            
            # Delete existing data for this batch window
            if not self.delete_batch_data(batch_start, batch_end):
                return False
        
        # Load new data
        return self.load(packet, variables)
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self.config.get(key, default)


class DataValidator(ABC):
    """Base class for data validators"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.name = config.get("name", "unknown")
    
    @abstractmethod
    def validate(self, packet: DataPacket) -> tuple[bool, Optional[str]]:
        """Validate data packet
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        pass