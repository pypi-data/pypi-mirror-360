"""MySQL data source"""

import pyarrow as pa
from typing import Any, Dict, Optional
import logging

from ..core.base import DataSource
from ..core.data_packet import DataPacket


class MySQLSource(DataSource):
    """MySQL database data source"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.logger = logging.getLogger(f"dft.sources.mysql.{self.name}")
    
    def extract(self, variables: Optional[Dict[str, Any]] = None) -> DataPacket:
        """Extract data from MySQL"""
        
        query = self.get_config("query")
        if not query:
            raise ValueError("query is required for MySQL source")
        
        try:
            import pymysql
            import pymysql.cursors
        except ImportError:
            raise ImportError("PyMySQL is required for MySQL source. Install with: pip install pymysql")
        
        # Connection parameters
        conn_params = {
            "host": self.get_config("host", "localhost"),
            "port": self.get_config("port", 3306),
            "database": self.get_config("database"),
            "user": self.get_config("user"),
            "password": self.get_config("password"),
            "charset": self.get_config("charset", "utf8mb4"),
            "cursorclass": pymysql.cursors.DictCursor,
        }
        
        # Remove None values
        conn_params = {k: v for k, v in conn_params.items() if v is not None}
        
        try:
            # Connect and execute query
            conn = pymysql.connect(**conn_params)
            cur = conn.cursor()
            cur.execute(query)
            
            # Fetch all results as list of dicts
            rows = cur.fetchall()
            data_list = list(rows)
            
            cur.close()
            conn.close()
            
            # Convert to Arrow table
            if data_list:
                table = pa.table(data_list)
            else:
                table = pa.table({})
            
            # Create data packet
            packet = DataPacket(
                data=table,
                source=f"mysql:{conn_params.get('host', 'localhost')}:{conn_params.get('database', 'unknown')}",
                metadata={
                    "query": query,
                    "host": conn_params.get("host"),
                    "database": conn_params.get("database"),
                    "variables": variables or {},
                }
            )
            
            self.logger.info(f"Extracted {packet.row_count} rows from MySQL")
            return packet
            
        except Exception as e:
            self.logger.error(f"Failed to extract from MySQL: {e}")
            raise RuntimeError(f"MySQL extraction failed: {e}")
    
    def test_connection(self) -> bool:
        """Test MySQL connection"""
        try:
            import pymysql
            
            conn_params = {
                "host": self.get_config("host", "localhost"),
                "port": self.get_config("port", 3306),
                "database": self.get_config("database"),
                "user": self.get_config("user"),
                "password": self.get_config("password"),
                "charset": self.get_config("charset", "utf8mb4"),
            }
            
            conn_params = {k: v for k, v in conn_params.items() if v is not None}
            
            conn = pymysql.connect(**conn_params)
            conn.close()
            return True
            
        except Exception as e:
            self.logger.error(f"MySQL connection test failed: {e}")
            return False