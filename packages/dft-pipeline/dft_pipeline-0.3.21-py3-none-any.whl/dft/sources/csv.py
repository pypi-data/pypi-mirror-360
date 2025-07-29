"""CSV data source"""

import pyarrow as pa
import pyarrow.csv as pa_csv
from pathlib import Path
from typing import Any, Dict, Optional

from ..core.base import DataSource
from ..core.data_packet import DataPacket


class CSVSource(DataSource):
    """
    CSV file data source - read data from CSV files
    
    Required config:
        file_path (str): Path to the CSV file
    
    Optional config:
        delimiter (str): Column delimiter (default: ',')
        encoding (str): File encoding (default: 'utf-8')
        has_header (bool): Whether first row contains column names (default: True)
        skip_rows (int): Number of rows to skip from beginning (default: 0)
    
    YAML Example:
        steps:
          - id: read_data
            type: source
            source_type: csv
            config:
              file_path: "data/input.csv"
              delimiter: ","
              encoding: "utf-8"
              has_header: true
              skip_rows: 0
    
    Variables Example:
        steps:
          - id: read_data
            type: source
            source_type: csv
            config:
              file_path: "{{ var('input_file') }}"
    """
    
    def extract(self, variables: Optional[Dict[str, Any]] = None) -> DataPacket:
        """Extract data from CSV file"""
        
        file_path = self.get_config("file_path")
        if not file_path:
            raise ValueError("file_path is required for CSV source")
        
        # Read CSV file directly with Arrow (faster than pandas)
        table = pa_csv.read_csv(file_path)
        
        # Create data packet
        packet = DataPacket(
            data=table,
            source=f"csv:{file_path}",
            metadata={
                "file_path": file_path,
                "file_size": Path(file_path).stat().st_size if Path(file_path).exists() else 0,
            }
        )
        
        return packet
    
    def test_connection(self) -> bool:
        """Test if CSV file exists and is readable"""
        file_path = self.get_config("file_path")
        if not file_path:
            return False
        
        try:
            path = Path(file_path)
            return path.exists() and path.is_file() and path.suffix.lower() == '.csv'
        except Exception:
            return False