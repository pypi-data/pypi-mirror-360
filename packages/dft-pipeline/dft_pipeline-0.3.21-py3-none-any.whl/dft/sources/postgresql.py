"""PostgreSQL data source"""

import pyarrow as pa
from typing import Any, Dict, Optional
import logging

from ..core.base import DataSource
from ..core.data_packet import DataPacket


class PostgreSQLSource(DataSource):
    """PostgreSQL database data source"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.logger = logging.getLogger(f"dft.sources.postgresql.{self.name}")
    
    def extract(self, variables: Optional[Dict[str, Any]] = None) -> DataPacket:
        """Extract data from PostgreSQL"""
        
        query = self.get_config("query")
        if not query:
            raise ValueError("query is required for PostgreSQL source")
        
        try:
            import psycopg2
            import psycopg2.extras
        except ImportError:
            raise ImportError("psycopg2 is required for PostgreSQL source. Install with: pip install psycopg2-binary")
        
        # Connection parameters
        conn_params = {
            "host": self.get_config("host", "localhost"),
            "port": self.get_config("port", 5432),
            "database": self.get_config("database"),
            "user": self.get_config("user"),
            "password": self.get_config("password"),
        }
        
        # Remove None values
        conn_params = {k: v for k, v in conn_params.items() if v is not None}
        
        try:
            # Connect and execute query
            conn = psycopg2.connect(**conn_params)
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cur.execute(query)
            
            # Fetch all results as list of dicts
            rows = cur.fetchall()
            data_list = [dict(row) for row in rows]
            
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
                source=f"postgresql:{conn_params.get('host', 'localhost')}:{conn_params.get('database', 'unknown')}",
                metadata={
                    "query": query,
                    "host": conn_params.get("host"),
                    "database": conn_params.get("database"),
                    "variables": variables or {},
                }
            )
            
            self.logger.info(f"Extracted {packet.row_count} rows from PostgreSQL")
            return packet
            
        except Exception as e:
            self.logger.error(f"Failed to extract from PostgreSQL: {e}")
            raise RuntimeError(f"PostgreSQL extraction failed: {e}")
    
    def test_connection(self) -> bool:
        """Test PostgreSQL connection"""
        try:
            import psycopg2
            
            conn_params = {
                "host": self.get_config("host", "localhost"),
                "port": self.get_config("port", 5432),
                "database": self.get_config("database"),
                "user": self.get_config("user"),
                "password": self.get_config("password"),
            }
            
            conn_params = {k: v for k, v in conn_params.items() if v is not None}
            
            conn = psycopg2.connect(**conn_params)
            conn.close()
            return True
            
        except Exception as e:
            self.logger.error(f"PostgreSQL connection test failed: {e}")
            return False