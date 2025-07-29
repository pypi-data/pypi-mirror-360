"""JSON data source (placeholder)"""

from typing import Any, Dict, Optional
from ..core.base import DataSource
from ..core.data_packet import DataPacket


class JSONSource(DataSource):
    """JSON file data source (placeholder)"""
    
    def extract(self, variables: Optional[Dict[str, Any]] = None) -> DataPacket:
        raise NotImplementedError("JSON source not implemented yet")
    
    def test_connection(self) -> bool:
        return False