"""CSV data endpoint"""

from pathlib import Path
from typing import Any, Dict, Optional
import pyarrow.csv as pa_csv

from ..core.base import DataEndpoint
from ..core.data_packet import DataPacket


class CSVEndpoint(DataEndpoint):
    """CSV file data endpoint"""
    
    def load(self, packet: DataPacket, variables: Optional[Dict[str, Any]] = None) -> bool:
        """Load data to CSV file"""
        
        file_path = self.get_config("file_path")
        if not file_path:
            raise ValueError("file_path is required for CSV endpoint")
        
        # Get write mode (append, replace)
        mode = self.get_config("mode", "replace")  # replace (overwrite) is default
        
        try:
            # Create directory if it doesn't exist
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            
            if mode == "append":
                # Check if file exists to decide if we need headers
                file_exists = Path(file_path).exists() and Path(file_path).stat().st_size > 0
                
                if file_exists:
                    # Append without headers - use pandas for append mode
                    import pandas as pd
                    df = packet.data.to_pandas()
                    df.to_csv(file_path, mode='a', header=False, index=False)
                else:
                    # First write, include headers
                    pa_csv.write_csv(packet.data, file_path)
            else:  # mode == "replace" or any other value
                # Overwrite file completely
                pa_csv.write_csv(packet.data, file_path)
            
            return True
            
        except Exception as e:
            raise RuntimeError(f"Failed to save CSV file {file_path} with mode '{mode}': {e}")