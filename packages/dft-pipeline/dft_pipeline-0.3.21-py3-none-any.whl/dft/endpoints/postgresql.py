"""PostgreSQL data endpoint"""

from typing import Any, Dict, Optional
import logging
from datetime import datetime
import pyarrow as pa

from ..core.base import DataEndpoint
from ..core.data_packet import DataPacket


class PostgreSQLEndpoint(DataEndpoint):
    """PostgreSQL database data endpoint"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.logger = logging.getLogger(f"dft.endpoints.postgresql.{self.name}")
    
    def load(self, packet: DataPacket, variables: Optional[Dict[str, Any]] = None) -> bool:
        """Load data to PostgreSQL table"""
        
        table_name = self.get_config("table")
        if not table_name:
            raise ValueError("table is required for PostgreSQL endpoint")
        
        try:
            import psycopg2
            import psycopg2.extras
        except ImportError:
            raise ImportError("psycopg2 is required for PostgreSQL endpoint")
        
        # Connection parameters
        conn_params = {
            "host": self.get_config("host", "localhost"),
            "port": self.get_config("port", 5432),
            "database": self.get_config("database"),
            "user": self.get_config("user"),
            "password": self.get_config("password"),
        }
        
        conn_params = {k: v for k, v in conn_params.items() if v is not None}
        
        # Load mode
        mode = self.get_config("mode", "append")  # append, replace, upsert
        auto_create = self.get_config("auto_create", True)
        
        try:
            conn = psycopg2.connect(**conn_params)
            cur = conn.cursor()
            
            # Check if table exists
            table_exists = self._table_exists(cur, table_name)
            
            if not table_exists and auto_create:
                self._create_table(cur, table_name, packet.data)
                conn.commit()
                self.logger.info(f"Created table {table_name}")
            
            # Handle different load modes
            if mode == "replace":
                cur.execute(f"TRUNCATE TABLE {table_name}")
                conn.commit()
                self.logger.info(f"Truncated table {table_name}")
            
            # Convert Arrow to list of dicts for bulk insert
            data_list = packet.to_dict_list()
            
            if data_list:
                # Get column names
                columns = list(data_list[0].keys())
                column_placeholders = ', '.join(['%s'] * len(columns))
                column_names = ', '.join([f'"{col}"' for col in columns])
                
                if mode == "upsert":
                    # Get upsert key columns (required for upsert mode)
                    upsert_keys = self.get_config("upsert_keys")
                    if not upsert_keys:
                        raise ValueError("upsert_keys is required for upsert mode. Specify unique columns for conflict resolution.")
                    
                    # Validate that all upsert keys exist in data
                    if not all(key in columns for key in upsert_keys):
                        missing_keys = [key for key in upsert_keys if key not in columns]
                        raise ValueError(f"Upsert keys {missing_keys} not found in data columns: {columns}")
                    
                    # Build ON CONFLICT DO UPDATE clause
                    update_columns = [col for col in columns if col not in upsert_keys]
                    conflict_columns = ', '.join([f'"{key}"' for key in upsert_keys])
                    
                    if update_columns:
                        update_clause = ', '.join([f'"{col}" = EXCLUDED."{col}"' for col in update_columns])
                        insert_sql = f'INSERT INTO "{table_name}" ({column_names}) VALUES ({column_placeholders}) ON CONFLICT ({conflict_columns}) DO UPDATE SET {update_clause}'
                    else:
                        # If no columns to update, just ignore conflicts
                        insert_sql = f'INSERT INTO "{table_name}" ({column_names}) VALUES ({column_placeholders}) ON CONFLICT ({conflict_columns}) DO NOTHING'
                    
                    self.logger.info(f"Using upsert mode with keys: {upsert_keys}")
                else:
                    # Prepare regular bulk insert SQL
                    insert_sql = f'INSERT INTO "{table_name}" ({column_names}) VALUES ({column_placeholders})'
                
                # Convert data to tuples for bulk insert
                data_tuples = [tuple(row[col] for col in columns) for row in data_list]
                
                # Execute bulk insert
                psycopg2.extras.execute_batch(cur, insert_sql, data_tuples)
                conn.commit()
                
                action = "upserted" if mode == "upsert" else "loaded"
                self.logger.info(f"{action.capitalize()} {len(data_list)} rows to PostgreSQL table {table_name}")
            else:
                self.logger.warning("No data to load to PostgreSQL")
            
            cur.close()
            conn.close()
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load to PostgreSQL: {e}")
            raise RuntimeError(f"PostgreSQL load failed: {e}")
    
    def _table_exists(self, cursor, table_name: str) -> bool:
        """Check if table exists"""
        try:
            cursor.execute(
                "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = %s)",
                (table_name,)
            )
            return cursor.fetchone()[0]
        except Exception:
            return False
    
    def _create_table(self, cursor, table_name: str, arrow_table: pa.Table) -> None:
        """Create table from explicit schema definition"""
        
        # Require explicit schema definition
        user_schema = self.get_config("schema")
        if not user_schema:
            raise ValueError(f"Schema is required for PostgreSQL endpoint. Please define schema for table {table_name}")
        
        # Build column definitions from user-defined schema only
        columns = []
        for column_name, column_type in user_schema.items():
            columns.append(f'"{column_name}" {column_type}')
        
        # Create table SQL
        create_sql = f'''
        CREATE TABLE "{table_name}" (
            {', '.join(columns)}
        )
        '''
        
        cursor.execute(create_sql)
        self.logger.info(f"Created PostgreSQL table {table_name} with schema: {columns}")
    
    def delete_batch_data(self, batch_start: datetime, batch_end: datetime) -> bool:
        """Delete data for microbatch window"""
        
        if not self.event_time_column:
            self.logger.warning("No event_time_column configured, skipping batch delete")
            return True
        
        table_name = self.get_config("table")
        if not table_name:
            raise ValueError("table is required for PostgreSQL endpoint")
        
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
            cur = conn.cursor()
            
            # Delete data in batch window
            delete_sql = f'''
            DELETE FROM "{table_name}" 
            WHERE "{self.event_time_column}" >= %s 
            AND "{self.event_time_column}" < %s
            '''
            
            cur.execute(delete_sql, (batch_start, batch_end))
            deleted_rows = cur.rowcount
            conn.commit()
            
            cur.close()
            conn.close()
            
            self.logger.info(f"Deleted {deleted_rows} rows from {table_name} for batch window [{batch_start} - {batch_end})")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to delete batch data: {e}")
            return False
    
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