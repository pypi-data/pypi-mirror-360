import pyarrow as pa
from typing import Any, Dict, List, Optional

from ...core.base import DataProcessor
from ...core.data_packet import DataPacket
from .models.ab_test_config import ABTestConfig
from .models.test_result import TestResult
from .utils.test_factory import TestFactory
from .utils.data_preparers import DataPreparer


class ABTestProcessor(DataProcessor):
    """Main A/B testing processor that orchestrates statistical testing"""

    def process(self, packet: DataPacket, variables: Optional[Dict[str, Any]] = None) -> DataPacket:
        """
        Process A/B test data and return results
        
        Args:
            packet: DataPacket with experiment data
            variables: Optional variables (not used)
            
        Returns:
            DataPacket with test results
        """
        # Get config from processor config
        config = self.config
        
        # Parse and validate configuration
        ab_config = ABTestConfig(**config)
        
        # Get data from packet (already PyArrow Table)
        data = packet.data
        
        # Prepare data - get all samples for the groups
        test_data = DataPreparer.prepare_samples(data, ab_config)
        
        # Create and run the statistical test
        test_kwargs = {
            'alpha': ab_config.alpha,
            'test_direction': ab_config.test_direction
        }
        
        # Add test-specific parameters
        if ab_config.test_type == "bootstrap":
            test_kwargs.update({
                'n_samples': ab_config.n_samples,
                'stratify': ab_config.stratify,
                'random_seed': ab_config.random_seed
            })
        else:
            # Only non-bootstrap tests support calculate_mde and power
            test_kwargs.update({
                'calculate_mde': ab_config.calculate_mde,
                'power': ab_config.power
            })
        
        test_instance = TestFactory.create_test(ab_config.test_type, **test_kwargs)
        
        # Run the test
        results = test_instance.run_test(test_data)
        
        # Convert results to DataFrame
        results_df = self._format_results(results, ab_config)
        
        # Return PyArrow Table as DataPacket
        return DataPacket(results_df, packet.metadata)
    
    def _format_results(self, results: List[TestResult], config: ABTestConfig) -> pa.Table:
        """Format test results into a PyArrow Table"""
        if not results:
            return pa.table({})
        
        # Convert results to dictionaries
        formatted_results = []
        for result in results:
            result_dict = result.to_dict()
            
            # Convert method_params dict to JSON string for PyArrow compatibility
            import json
            result_dict["method_params"] = json.dumps(result_dict["method_params"])
            
            # Add configuration metadata - flatten the config
            result_dict.update({
                "test_type": config.test_type,
                "metric_column": config.metric_column,
                "group_column": config.group_column,
                "covariate_column": config.covariate_column
            })
            
            formatted_results.append(result_dict)
        
        # Convert to PyArrow table manually 
        if not formatted_results:
            return pa.table({})
        
        # Get all possible keys from all results to ensure consistency
        all_keys = set()
        for result_dict in formatted_results:
            all_keys.update(result_dict.keys())
        
        # Create arrays for each column
        columns = {}
        for key in sorted(all_keys):  # Sort for consistent ordering
            column_data = []
            for result_dict in formatted_results:
                value = result_dict.get(key, None)
                column_data.append(value)
            columns[key] = column_data
        
        return pa.table(columns)


# Register the processor
def register_processor():
    """Register the AB test processor with the DFT system"""
    # This will be called when the processor is imported
    pass