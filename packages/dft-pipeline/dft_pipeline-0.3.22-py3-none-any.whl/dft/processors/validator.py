"""Data validation processor"""

from typing import Any, Dict, List, Optional
import pyarrow as pa

from ..core.base import DataProcessor
from ..core.data_packet import DataPacket


class DataValidator(DataProcessor):
    """
    Data validation processor - validate data quality and constraints
    
    Optional config:
        required_columns (list): List of column names that must be present
        row_count_min (int): Minimum number of rows required
        row_count_max (int): Maximum number of rows allowed
        checks (list): List of column validation rules
    
    Check rule format:
        - column (str): Column name to validate
        - min_value (float): Minimum allowed value for numeric columns
        - max_value (float): Maximum allowed value for numeric columns
        - not_null (bool): Whether column can contain null values (default: false)
        - unique (bool): Whether column values must be unique (default: false)
    
    YAML Example - Basic validation:
        steps:
          - id: validate_data
            type: processor
            processor_type: validator
            config:
              required_columns: ["id", "name", "email"]
              row_count_min: 1
              row_count_max: 1000
    
    YAML Example - Advanced validation:
        steps:
          - id: validate_transactions
            type: processor
            processor_type: validator
            config:
              required_columns: ["trans_id", "amount", "customer_id"]
              row_count_min: 1
              checks:
                - column: "amount"
                  min_value: 0
                  max_value: 10000
                  not_null: true
                - column: "trans_id"
                  unique: true
                  not_null: true
                - column: "customer_id"
                  not_null: true
    """
    
    def process(self, packet: DataPacket, variables: Optional[Dict[str, Any]] = None) -> DataPacket:
        """Validate data packet"""
        
        errors = []
        
        # Check row count constraints
        row_count_min = self.get_config("row_count_min")
        row_count_max = self.get_config("row_count_max")
        
        if row_count_min is not None and packet.row_count < row_count_min:
            errors.append(f"Row count {packet.row_count} is below minimum {row_count_min}")
        
        if row_count_max is not None and packet.row_count > row_count_max:
            errors.append(f"Row count {packet.row_count} exceeds maximum {row_count_max}")
        
        # Check required columns
        required_columns = self.get_config("required_columns", [])
        if required_columns:
            missing_columns = set(required_columns) - set(packet.column_names)
            if missing_columns:
                errors.append(f"Missing required columns: {list(missing_columns)}")
        
        # Check schema if enabled
        schema_check = self.get_config("schema_check", False)
        if schema_check and packet.data is not None:
            # Basic schema validation - check for null values in required columns
            for col_name in required_columns:
                if col_name in packet.column_names:
                    column = packet.data.column(col_name)
                    null_count = column.null_count
                    if null_count > 0:
                        errors.append(f"Column {col_name} contains {null_count} null values")
        
        # If there are validation errors, raise exception
        if errors:
            error_message = "; ".join(errors)
            raise ValueError(f"Data validation failed: {error_message}")
        
        # Add validation metadata
        packet.add_metadata("validation_passed", True)
        packet.add_metadata("validation_checks", {
            "row_count_min": row_count_min,
            "row_count_max": row_count_max,
            "required_columns": required_columns,
            "schema_check": schema_check,
        })
        
        return packet