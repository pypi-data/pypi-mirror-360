"""MySQL data endpoint"""

from typing import Any, Dict, Optional
import logging
import pyarrow as pa

from ..core.base import DataEndpoint
from ..core.data_packet import DataPacket


class MySQLEndpoint(DataEndpoint):
    """
    MySQL database endpoint - load data to MySQL tables
    
    Required config:
        table (str): Target table name
        host (str): MySQL server host
        database (str): Database name
        user (str): Username for authentication
        password (str): Password for authentication
    
    Optional config:
        port (int): MySQL server port (default: 3306)
        charset (str): Connection charset (default: 'utf8mb4')
        mode (str): Load mode - 'append', 'replace', or 'upsert' (default: 'append')
        auto_create (bool): Auto-create table if not exists (default: True)
        schema (dict): Table schema for auto-creation (required if auto_create=True)
        upsert_keys (list): Unique columns for upsert mode (required if mode='upsert')
    
    YAML Example - Basic:
        steps:
          - id: save_to_mysql
            type: endpoint
            endpoint_type: mysql
            config:
              host: "localhost"
              database: "analytics"
              user: "analyst"
              password: "secret123"
              table: "user_data"
              mode: "append"
    
    YAML Example - Upsert with schema:
        steps:
          - id: upsert_users
            type: endpoint
            endpoint_type: mysql
            config:
              host: "localhost"
              database: "analytics"
              user: "analyst"
              password: "secret123"
              table: "users"
              mode: "upsert"
              upsert_keys: ["id"]
              auto_create: true
              schema:
                id: "INT PRIMARY KEY"
                name: "VARCHAR(100)"
                email: "VARCHAR(100)"
                updated_at: "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
    
    Named Connection Example:
        # In dft_project.yml:
        connections:
          main_db:
            type: mysql
            host: "localhost"
            database: "analytics"
            user: "analyst"
            password: "secret123"
        
        # In pipeline:
        steps:
          - id: save_data
            type: endpoint
            endpoint_type: mysql
            connection: "main_db"
            config:
              table: "user_data"
              mode: "append"
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.logger = logging.getLogger(f"dft.endpoints.mysql.{self.name}")
    
    def load(self, packet: DataPacket, variables: Optional[Dict[str, Any]] = None) -> bool:
        """Load data to MySQL table"""
        
        table_name = self.get_config("table")
        if not table_name:
            raise ValueError("table is required for MySQL endpoint")
        
        try:
            import pymysql
        except ImportError:
            raise ImportError("PyMySQL is required for MySQL endpoint")
        
        # Connection parameters
        conn_params = {
            "host": self.get_config("host", "localhost"),
            "port": self.get_config("port", 3306),
            "database": self.get_config("database"),
            "user": self.get_config("user"),
            "password": self.get_config("password"),
            "charset": self.get_config("charset", "utf8mb4"),
        }
        
        conn_params = {k: v for k, v in conn_params.items() if v is not None}
        
        # Load mode
        mode = self.get_config("mode", "append")  # append, replace, upsert
        auto_create = self.get_config("auto_create", True)
        
        try:
            conn = pymysql.connect(**conn_params)
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
                column_names = ', '.join([f'`{col}`' for col in columns])
                
                if mode == "upsert":
                    # Get upsert key columns (required for upsert mode)
                    upsert_keys = self.get_config("upsert_keys")
                    if not upsert_keys:
                        raise ValueError("upsert_keys is required for upsert mode. Specify unique columns for conflict resolution.")
                    
                    # Validate that all upsert keys exist in data
                    if not all(key in columns for key in upsert_keys):
                        missing_keys = [key for key in upsert_keys if key not in columns]
                        raise ValueError(f"Upsert keys {missing_keys} not found in data columns: {columns}")
                    
                    # Build ON DUPLICATE KEY UPDATE clause
                    update_columns = [col for col in columns if col not in upsert_keys]
                    if update_columns:
                        update_clause = ', '.join([f'`{col}` = VALUES(`{col}`)' for col in update_columns])
                        insert_sql = f'INSERT INTO `{table_name}` ({column_names}) VALUES ({column_placeholders}) ON DUPLICATE KEY UPDATE {update_clause}'
                    else:
                        # If no columns to update, just ignore duplicates
                        insert_sql = f'INSERT IGNORE INTO `{table_name}` ({column_names}) VALUES ({column_placeholders})'
                    
                    self.logger.info(f"Using upsert mode with keys: {upsert_keys}")
                else:
                    # Prepare regular bulk insert SQL
                    insert_sql = f'INSERT INTO `{table_name}` ({column_names}) VALUES ({column_placeholders})'
                
                # Convert data to tuples for bulk insert
                data_tuples = [tuple(row[col] for col in columns) for row in data_list]
                
                # Execute bulk insert using executemany
                cur.executemany(insert_sql, data_tuples)
                conn.commit()
                
                action = "upserted" if mode == "upsert" else "loaded"
                self.logger.info(f"{action.capitalize()} {len(data_list)} rows to MySQL table {table_name}")
            else:
                self.logger.warning("No data to load to MySQL")
            
            cur.close()
            conn.close()
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load to MySQL: {e}")
            raise RuntimeError(f"MySQL load failed: {e}")
    
    def _table_exists(self, cursor, table_name: str) -> bool:
        """Check if table exists"""
        try:
            cursor.execute("SHOW TABLES LIKE %s", (table_name,))
            return cursor.fetchone() is not None
        except Exception:
            return False
    
    def _create_table(self, cursor, table_name: str, arrow_table: pa.Table) -> None:
        """Create table from explicit schema definition"""
        
        # Require explicit schema definition
        user_schema = self.get_config("schema")
        if not user_schema:
            raise ValueError(f"Schema is required for MySQL endpoint. Please define schema for table {table_name}")
        
        # Build column definitions from user-defined schema only
        columns = []
        for column_name, column_type in user_schema.items():
            columns.append(f"`{column_name}` {column_type}")
        
        # Create table SQL
        create_sql = f"""
        CREATE TABLE `{table_name}` (
            {', '.join(columns)}
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """
        
        cursor.execute(create_sql)
        self.logger.info(f"Created MySQL table {table_name} with schema: {columns}")
    
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