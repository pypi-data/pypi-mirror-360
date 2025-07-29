import numpy as np
import pyarrow as pa
from typing import List, Optional, Union, Tuple
from itertools import combinations

from ..models.sample import Sample
from ..models.ab_test_config import ABTestConfig


class DataPreparer:
    """Utility class for preparing data for A/B testing"""
    
    @staticmethod
    def prepare_samples(data: pa.Table, config: ABTestConfig) -> List[Sample]:
        """Prepare all Sample objects from PyArrow Table for all test types"""
        if config.test_type in ["ttest", "cuped_ttest", "bootstrap"]:
            return DataPreparer._prepare_samples_for_continuous_tests(data, config)
        elif config.test_type == "ztest":
            return DataPreparer._prepare_samples_for_ztest(data, config)
        else:
            raise ValueError(f"Unsupported test type: {config.test_type}")
    
    
    @staticmethod
    def _prepare_samples_for_continuous_tests(data: pa.Table, config: ABTestConfig) -> List[Sample]:
        """Prepare samples for t-test, CUPED t-test, and bootstrap test"""
        required_columns = [config.group_column, config.metric_column]
        
        # Check required columns
        for col in required_columns:
            if col not in data.column_names:
                raise ValueError(f"Required column '{col}' not found in data")
        
        # Check for CUPED covariate column
        if config.test_type == "cuped_ttest":
            if not config.covariate_column:
                raise ValueError("covariate_column is required for CUPED tests")
            if config.covariate_column not in data.column_names:
                raise ValueError(f"Covariate column '{config.covariate_column}' not found in data")
        
        # Get all unique groups, filtering out None/NaN/empty values first
        group_array = data[config.group_column].to_numpy()
        # Filter out None/NaN/empty values before np.unique to avoid sorting errors
        valid_groups = [g for g in group_array if g is not None and str(g).lower() != 'nan' and str(g).strip() != '']
        
        if len(valid_groups) == 0:
            raise ValueError(f"No valid groups found in column '{config.group_column}'. All values are None or NaN.")
        
        unique_groups = np.unique(valid_groups)
        
        if len(unique_groups) < 2:
            raise ValueError(f"Need at least 2 groups for comparison, found: {len(unique_groups)}")
        
        # Prepare individual samples for each group
        group_samples = {}
        metric_array = data[config.metric_column].to_numpy()
        
        # Get covariate array if needed
        cov_array_full = None
        if config.test_type == "cuped_ttest":
            cov_array_full = data[config.covariate_column].to_numpy()
        
        for group in unique_groups:
            # Filter by group
            group_mask = group_array == group
            
            if not np.any(group_mask):
                continue
            
            metric_values = metric_array[group_mask]
            
            # Remove NaN values
            valid_mask = ~np.isnan(metric_values)
            metric_values = metric_values[valid_mask]
            
            if len(metric_values) == 0:
                continue
            
            # Prepare covariate data for CUPED
            cov_array = None
            if config.test_type == "cuped_ttest":
                cov_values = cov_array_full[group_mask][valid_mask]
                if len(cov_values) != len(metric_values):
                    raise ValueError(f"Metric and covariate arrays have different lengths for group '{group}'")
                cov_array = cov_values
            
            sample = Sample(
                array=metric_values,
                cov_array=cov_array,
                name=str(group)
            )
            group_samples[str(group)] = sample
        
        # Return all samples (tests will handle creating pairs internally)
        return list(group_samples.values())
    
    @staticmethod 
    def _prepare_samples_for_ztest(data: pa.Table, config: ABTestConfig) -> List[Sample]:
        """Prepare samples for z-test (binary metrics)"""
        required_columns = [config.group_column, config.metric_column]
        
        # Check required columns
        for col in required_columns:
            if col not in data.column_names:
                raise ValueError(f"Required column '{col}' not found in data")
        
        # Get all unique groups, filtering out None/NaN values first  
        group_array = data[config.group_column].to_numpy()
        # Filter out None/NaN values before np.unique to avoid sorting errors
        valid_groups = [g for g in group_array if g is not None and str(g).lower() != 'nan']
        
        if len(valid_groups) == 0:
            raise ValueError(f"No valid groups found in column '{config.group_column}'. All values are None or NaN.")
        
        unique_groups = np.unique(valid_groups)
        
        if len(unique_groups) < 2:
            raise ValueError(f"Need at least 2 groups for comparison, found: {len(unique_groups)}")
        
        # Prepare individual samples for each group
        group_samples = {}
        metric_array = data[config.metric_column].to_numpy()
        
        for group in unique_groups:
            # Filter by group
            group_mask = group_array == group
            
            if not np.any(group_mask):
                continue
            
            metric_values = metric_array[group_mask]
            
            # Remove NaN values
            valid_mask = ~np.isnan(metric_values.astype(float))
            metric_values = metric_values[valid_mask]
            
            if len(metric_values) == 0:
                continue
            
            # Check if values are binary (0/1)
            unique_values = np.unique(metric_values)
            if not np.all(np.isin(unique_values, [0, 1])):
                raise ValueError(f"Z-test requires binary metric values (0/1) for group '{group}'. "
                               f"Found values: {unique_values}")
            
            # Convert to binary array for Sample object
            binary_array = metric_values.astype(int)
            
            sample = Sample(
                array=binary_array,
                cov_array=None,
                name=str(group)
            )
            group_samples[str(group)] = sample
        
        # Return all samples (tests will handle creating pairs internally)
        return list(group_samples.values())


def prepare_samples(data: pa.Table, config: ABTestConfig) -> List[Sample]:
    """Convenience function for preparing samples"""
    return DataPreparer.prepare_samples(data, config)