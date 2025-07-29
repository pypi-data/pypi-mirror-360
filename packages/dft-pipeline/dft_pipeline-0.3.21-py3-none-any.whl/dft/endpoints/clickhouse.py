"""ClickHouse data endpoint"""

from typing import Any, Dict, Optional
import logging
import pyarrow as pa

from ..core.base import DataEndpoint
from ..core.data_packet import DataPacket


class ClickHouseEndpoint(DataEndpoint):
    """ClickHouse database data endpoint"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.logger = logging.getLogger(f"dft.endpoints.clickhouse.{self.name}")

    def load(self, packet: DataPacket, variables: Optional[Dict[str, Any]] = None) -> bool:
        """Load data to ClickHouse table"""

        table_name = self.get_config("table")
        if not table_name:
            raise ValueError("table is required for ClickHouse endpoint")

        try:
            from clickhouse_driver import Client
        except ImportError:
            raise ImportError("clickhouse-driver is required for ClickHouse endpoint")

        # Connection parameters
        host = self.get_config("host", "localhost")
        port = self.get_config("port", 9000)
        database = self.get_config("database", "default")
        user = self.get_config("user", "default")
        password = self.get_config("password", "")

        # Load mode
        mode = self.get_config("mode", "append")  # append, replace, upsert
        auto_create = self.get_config("auto_create", True)

        try:
            client = Client(
                host=host,
                port=port,
                database=database,
                user=user,
                password=password,
            )

            # Check if table exists
            table_exists = self._table_exists(client, table_name)

            if not table_exists and auto_create:
                self._create_table(client, table_name, packet.data)
                self.logger.info(f"Created table {table_name}")

            # Handle different load modes
            if mode == "replace":
                # Truncate table first
                client.execute(f"TRUNCATE TABLE {table_name}")
                self.logger.info(f"Truncated table {table_name}")

            # Convert Arrow to format suitable for ClickHouse
            data_list = packet.to_dict_list()

            if data_list:
                # Get column names and prepare data
                columns = list(data_list[0].keys())
                # Handle None values - replace with empty string for string columns
                # and appropriate defaults for other types
                def handle_none_value(value):
                    if value is None:
                        return ""  # ClickHouse String columns need empty string instead of None
                    return value
                
                values = [tuple(handle_none_value(row[col]) for col in columns) for row in data_list]

                if mode == "upsert":
                    # Get upsert key columns (required for upsert mode)
                    upsert_keys = self.get_config("upsert_keys")
                    if not upsert_keys:
                        raise ValueError("upsert_keys is required for upsert mode. Specify unique columns for conflict resolution.")
                    
                    # Validate that all upsert keys exist in data
                    if not all(key in columns for key in upsert_keys):
                        missing_keys = [key for key in upsert_keys if key not in columns]
                        raise ValueError(f"Upsert keys {missing_keys} not found in data columns: {columns}")
                    
                    # For ClickHouse, use DELETE + INSERT strategy for each unique key combination
                    # This is more reliable than ReplacingMergeTree which works asynchronously
                    
                    # Group values by unique key combination to optimize DELETE operations
                    unique_key_values = set()
                    for row_tuple in values:
                        row_dict = dict(zip(columns, row_tuple))
                        key_tuple = tuple(row_dict[key] for key in upsert_keys)
                        unique_key_values.add(key_tuple)
                    
                    if unique_key_values:
                        # Build WHERE condition for ALTER TABLE DELETE (compatible with older ClickHouse versions)
                        if len(upsert_keys) == 1:
                            # Single key optimization
                            key_name = upsert_keys[0]
                            key_values = [str(key_tuple[0]) for key_tuple in unique_key_values]
                            
                            # Use appropriate type formatting for ClickHouse
                            if isinstance(list(unique_key_values)[0][0], str):
                                formatted_values = "'" + "', '".join(key_values) + "'"
                            else:
                                formatted_values = ", ".join(key_values)
                            
                            delete_query = f"ALTER TABLE {table_name} DELETE WHERE {key_name} IN ({formatted_values})"
                        else:
                            # Multiple keys - use OR conditions for each combination
                            conditions = []
                            for key_tuple in unique_key_values:
                                key_conditions = []
                                for i, key_name in enumerate(upsert_keys):
                                    value = key_tuple[i]
                                    if isinstance(value, str):
                                        key_conditions.append(f"{key_name} = '{value}'")
                                    else:
                                        key_conditions.append(f"{key_name} = {value}")
                                conditions.append(f"({' AND '.join(key_conditions)})")
                            
                            delete_query = f"ALTER TABLE {table_name} DELETE WHERE {' OR '.join(conditions)}"
                        
                        # Execute DELETE
                        client.execute(delete_query)
                        self.logger.info(f"Deleted existing rows for {len(unique_key_values)} unique key combinations")
                    
                    self.logger.info(f"Using upsert mode with keys: {upsert_keys}")

                # Insert new data (works for both regular insert and upsert after DELETE)
                insert_query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES"
                client.execute(insert_query, values)

                action = "upserted" if mode == "upsert" else "loaded"
                self.logger.info(f"{action.capitalize()} {len(values)} rows to ClickHouse table {table_name}")
            else:
                self.logger.warning("No data to load to ClickHouse")

            return True

        except Exception as e:
            self.logger.error(f"Failed to load to ClickHouse: {e}")
            raise RuntimeError(f"ClickHouse load failed: {e}")

    def _table_exists(self, client, table_name: str) -> bool:
        """Check if table exists"""
        try:
            database = self.get_config("database", "default")
            result = client.execute(
                "SELECT count() FROM system.tables WHERE database = %s AND name = %s", [database, table_name]
            )
            return result[0][0] > 0
        except Exception:
            return False

    def _create_table(self, client, table_name: str, _: pa.Table) -> None:
        """Create table from explicit schema definition"""

        # Require explicit schema definition
        user_schema = self.get_config("schema")
        if not user_schema:
            raise ValueError(f"Schema is required for ClickHouse endpoint. Please define schema for table {table_name}")

        # Build column definitions from user-defined schema only
        columns = []
        for column_name, column_type in user_schema.items():
            columns.append(f"{column_name} {column_type}")

        # Create table SQL
        engine = self.get_config("engine", "MergeTree()")
        order_by = self.get_config("order_by", "tuple()")

        create_sql = f"""
        CREATE TABLE {table_name} (
            {', '.join(columns)}
        ) ENGINE = {engine}
        ORDER BY {order_by}
        """

        client.execute(create_sql)
        self.logger.info(f"Created ClickHouse table {table_name} with schema: {columns}")

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

            client.execute("SELECT 1")
            return True

        except Exception as e:
            self.logger.error(f"ClickHouse connection test failed: {e}")
            return False
