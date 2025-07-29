"""JSON data endpoint (placeholder)"""

from typing import Any, Dict, Optional
from ..core.base import DataEndpoint
from ..core.data_packet import DataPacket


class JSONEndpoint(DataEndpoint):
    """JSON file data endpoint (placeholder)"""
    
    def load(self, packet: DataPacket, variables: Optional[Dict[str, Any]] = None) -> bool:
        raise NotImplementedError("JSON endpoint not implemented yet")