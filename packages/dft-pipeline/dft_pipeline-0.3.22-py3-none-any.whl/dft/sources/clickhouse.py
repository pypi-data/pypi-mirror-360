"""ClickHouse data source"""

import pyarrow as pa
from typing import Any, Dict, Optional
import logging

from ..core.base import DataSource
from ..core.data_packet import DataPacket


class ClickHouseSource(DataSource):
    """ClickHouse database data source"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.logger = logging.getLogger(f"dft.sources.clickhouse.{self.name}")
    
    def extract(self, variables: Optional[Dict[str, Any]] = None) -> DataPacket:
        """Extract data from ClickHouse"""
        
        query = self.get_config("query")
        if not query:
            raise ValueError("query is required for ClickHouse source")
        
        try:
            from clickhouse_driver import Client
        except ImportError:
            raise ImportError("clickhouse-driver is required for ClickHouse source. Install with: pip install clickhouse-driver")
        
        # Connection parameters
        host = self.get_config("host", "localhost")
        port = self.get_config("port", 9000)
        database = self.get_config("database", "default")
        user = self.get_config("user", "default")
        password = self.get_config("password", "")
        
        try:
            # Connect to ClickHouse
            client = Client(
                host=host,
                port=port,
                database=database,
                user=user,
                password=password,
            )
            
            # Execute query and get results with column info
            result = client.execute(query, with_column_types=True)
            data, columns = result
            
            # Convert to list of dicts
            if columns:
                column_names = [col[0] for col in columns]
                data_list = []
                
                if data:
                    # Has data - convert rows with type conversion
                    for row in data:
                        row_dict = {}
                        for i, value in enumerate(row):
                            # Convert datetime.date to string for PyArrow compatibility
                            if hasattr(value, 'isoformat'):  # datetime.date or datetime.datetime
                                value = value.isoformat()
                            # Convert empty strings to None for better PyArrow handling
                            elif value == '':
                                value = None
                            row_dict[column_names[i]] = value
                        data_list.append(row_dict)
                    
                    # Convert to Arrow table using column-wise approach
                    # This avoids schema inference issues with mixed/null values
                    columns_data = {}
                    for col_name in column_names:
                        columns_data[col_name] = [row[col_name] for row in data_list]
                    table = pa.table(columns_data)
                else:
                    # Empty result but with known schema
                    empty_data = {col_name: [] for col_name in column_names}
                    table = pa.table(empty_data)
            else:
                # No columns info - completely empty result
                table = pa.table({})
            
            # Create data packet
            packet = DataPacket(
                data=table,
                source=f"clickhouse:{host}:{database}",
                metadata={
                    "query": query,
                    "host": host,
                    "database": database,
                    "variables": variables or {},
                    "column_types": {col[0]: col[1] for col in columns} if columns else {},
                }
            )
            
            # Log at debug level to avoid cluttering output
            self.logger.debug(f"Extracted {packet.row_count} rows from ClickHouse")
            return packet
            
        except Exception as e:
            self.logger.error(f"Failed to extract from ClickHouse: {e}")
            raise RuntimeError(f"ClickHouse extraction failed: {e}")
    
    def test_connection(self) -> bool:
        """Test ClickHouse connection"""
        try:
            from clickhouse_driver import Client
            
            client = Client(
                host=self.get_config("host", "localhost"),
                port=self.get_config("port", 9000),
                database=self.get_config("database", "default"),
                user=self.get_config("user", "default"),
                password=self.get_config("password", ""),
            )
            
            # Simple test query
            client.execute("SELECT 1")
            return True
            
        except Exception as e:
            self.logger.error(f"ClickHouse connection test failed: {e}")
            return False