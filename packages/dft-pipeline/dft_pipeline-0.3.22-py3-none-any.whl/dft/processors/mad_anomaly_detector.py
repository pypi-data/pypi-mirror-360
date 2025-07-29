"""MAD Anomaly Detector adapted for DFT"""

from typing import Any, Dict, Optional, Tuple, List
import numpy as np
import pyarrow as pa
from scipy import stats
import logging
from datetime import datetime

from ..core.base import DataProcessor
from ..core.data_packet import DataPacket


class MADAnomalyDetector(DataProcessor):
    """
    Robust anomaly detector based on MAD (Median Absolute Deviation)
    with support for seasonal components
    
    Adapted from existing MAD detector to work with DFT DataPacket format
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        
        # Configuration parameters
        self.window_size = self.get_config("window_size", 24 * 60)  # 24 hours with minute data
        self.n_sigma = self.get_config("n_sigma", 3.0)
        self.min_window_size = self.get_config("min_window_size", 10)
        self.use_weighted = self.get_config("use_weighted", True)
        self.weights_type = self.get_config("weights_type", "exponential")
        self.exp_decay_factor = self.get_config("exp_decay_factor", 0.1)
        self.use_combined_seasonality = self.get_config("use_combined_seasonality", False)
        
        # Data columns configuration
        self.value_column = self.get_config("value_column", "value")
        self.timestamp_column = self.get_config("timestamp_column", "timestamp")
        self.group_column = self.get_config("group_column", "group")
        self.feature_columns = self.get_config("feature_columns", [])  # seasonal features
        
        self.logger = logging.getLogger(f"dft.processors.mad_anomaly_detector.{self.name}")
        
        self.logger.info(f"Initialized MAD detector with window_size={self.window_size}, n_sigma={self.n_sigma}")

    def process(self, packet: DataPacket, variables: Optional[Dict[str, Any]] = None) -> DataPacket:
        """
        Process data packet and detect anomalies
        
        Input packet should contain time series data with columns:
        - value_column: metric values
        - timestamp_column: timestamps
        - group_column: group identifier (optional)
        - feature_columns: seasonal features (optional)
        """
        
        # Convert to numpy arrays for processing
        data_dict = packet.to_numpy_dict()
        
        if len(data_dict) == 0:
            self.logger.warning("Empty data packet received")
            return self._create_empty_result_packet()
        
        # Validate required columns
        if self.value_column not in data_dict:
            raise ValueError(f"Required column '{self.value_column}' not found in data")
        if self.timestamp_column not in data_dict:
            raise ValueError(f"Required column '{self.timestamp_column}' not found in data")
        
        # Get data arrays
        values = data_dict[self.value_column]
        timestamps = data_dict[self.timestamp_column]
        n = len(values)
        
        # Get groups if present
        if self.group_column in data_dict:
            groups = data_dict[self.group_column]
            unique_groups = np.unique(groups)
            
            grouped_results = []
            for group_name in unique_groups:
                group_mask = groups == group_name
                group_values = values[group_mask]
                group_timestamps = timestamps[group_mask]
                
                # Create group data dict
                group_data = {col: arr[group_mask] for col, arr in data_dict.items()}
                
                self.logger.debug(f"Processing group: {group_name}")
                group_result = self._process_group_arrays(group_data, str(group_name))
                grouped_results.append(group_result)
            
            # Combine all group results
            result_dict = self._combine_group_results(grouped_results)
        else:
            # Process as single group
            result_dict = self._process_group_arrays(data_dict, "default")
        
        # Convert back to Arrow
        result_table = pa.table(result_dict)
        
        # Calculate metrics
        is_anomaly_array = result_dict["is_anomaly"]
        total_anomalies = int(np.sum(is_anomaly_array))
        anomaly_rate = float(np.mean(is_anomaly_array))
        
        # Create result packet
        result_packet = DataPacket(
            data=result_table,
            source=f"mad_anomaly_detector:{packet.source}",
            metadata={
                **packet.metadata,
                "detector_config": {
                    "window_size": self.window_size,
                    "n_sigma": self.n_sigma,
                    "use_weighted": self.use_weighted,
                    "use_combined_seasonality": self.use_combined_seasonality,
                },
                "total_anomalies": total_anomalies,
                "anomaly_rate": anomaly_rate,
            }
        )
        
        self.logger.info(f"Detected {total_anomalies} anomalies in {len(is_anomaly_array)} records")
        
        return result_packet

    def _process_group_arrays(self, data_dict: Dict[str, np.ndarray], group_name: str) -> Dict[str, np.ndarray]:
        """Process single group of time series data using numpy arrays"""
        
        n = len(data_dict[self.value_column])
        values = data_dict[self.value_column]
        timestamps = data_dict[self.timestamp_column]
        
        # Prepare feature data if available
        features = None
        if self.feature_columns and all(col in data_dict for col in self.feature_columns):
            features = np.column_stack([data_dict[col] for col in self.feature_columns])
        
        # Initialize result arrays
        means = np.zeros(n)
        stds = np.zeros(n)
        is_anomaly = np.zeros(n, dtype=bool)
        scores = np.zeros(n)
        directions = np.array([""] * n, dtype=object)
        percent_deviations = np.zeros(n)
        lower_bounds = np.zeros(n)
        upper_bounds = np.zeros(n)
        pvalues = np.zeros(n)

        for i in range(n):
            if i < self.min_window_size:
                continue

            # Define window
            start_idx = max(0, i - self.window_size)
            window = values[start_idx:i]
            
            # Create mask for excluding anomalies (if available)
            window_mask = np.ones(len(window), dtype=bool)
            if "is_anomaly_verified" in data_dict:
                window_verified = data_dict["is_anomaly_verified"][start_idx:i]
                window_mask = ~window_verified

            window_size = len(window[window_mask])
            if window_size < self.min_window_size:
                continue

            # Calculate weights
            weights = self._compute_weights(len(window))
            masked_weights = weights * window_mask
            if masked_weights.sum() > 0:
                masked_weights = masked_weights / masked_weights.sum()

            # Calculate base statistics
            base_median, base_mad = self._weighted_mad(window, masked_weights)

            # Adjust for seasonality if features available
            if features is not None:
                current_features = features[i:i+1]
                window_features = features[start_idx:i]
                means[i], stds[i] = self._adjust_stats_for_seasonality(
                    base_median, base_mad, current_features, window_features, 
                    window, masked_weights, window_mask
                )
            else:
                means[i] = base_median
                stds[i] = base_mad

            # Anomaly detection
            current_value = values[i]
            
            if stds[i] > 0:
                scores[i] = abs(current_value - means[i]) / stds[i]
                is_anomaly[i] = scores[i] > self.n_sigma

                if is_anomaly[i]:
                    directions[i] = "up" if current_value > means[i] else "down"

            # Calculate bounds and p-values
            lower_bounds[i] = means[i] - self.n_sigma * stds[i]
            upper_bounds[i] = means[i] + self.n_sigma * stds[i]
            
            if means[i] != 0:
                percent_deviations[i] = (current_value - means[i]) / abs(means[i])
            
            if stds[i] > 0:
                z_score = abs(values[i] - means[i]) / stds[i]
                pvalues[i] = 2 * min(stats.laplace.cdf(z_score), 1 - stats.laplace.cdf(z_score))
            else:
                pvalues[i] = 1.0

        # Create result dict with all original columns plus new ones
        result_dict = data_dict.copy()
        result_dict["group"] = np.array([group_name] * n)
        result_dict["mean"] = means
        result_dict["std"] = stds
        result_dict["is_anomaly"] = is_anomaly
        result_dict["anomaly_score"] = scores
        result_dict["anomaly_direction"] = directions
        result_dict["percent_deviation"] = percent_deviations
        result_dict["lower_bound"] = lower_bounds
        result_dict["upper_bound"] = upper_bounds
        result_dict["p_value"] = pvalues
        result_dict["ci_length"] = upper_bounds - lower_bounds

        return result_dict
    
    def _combine_group_results(self, group_results: List[Dict[str, np.ndarray]]) -> Dict[str, np.ndarray]:
        """Combine results from multiple groups"""
        if not group_results:
            return {}
        
        combined_dict = {}
        for key in group_results[0].keys():
            combined_dict[key] = np.concatenate([result[key] for result in group_results])
        
        return combined_dict

    def _compute_weights(self, size: int) -> np.ndarray:
        """Calculate weights for window"""
        if not self.use_weighted:
            return np.ones(size)

        if self.weights_type == "exponential":
            weights = np.exp(-self.exp_decay_factor * np.arange(size)[::-1])
        elif self.weights_type == "linear":
            weights = np.linspace(0.1, 1.0, size)
        else:
            self.logger.warning(f"Unknown weights type: {self.weights_type}. Using exponential.")
            weights = np.exp(-self.exp_decay_factor * np.arange(size)[::-1])

        return weights / weights.sum()

    def _weighted_median(self, data: np.ndarray, weights: np.ndarray) -> float:
        """Calculate weighted median"""
        sorted_idx = np.argsort(data)
        sorted_data = data[sorted_idx]
        sorted_weights = weights[sorted_idx]
        cumsum = np.cumsum(sorted_weights)
        median_idx = np.searchsorted(cumsum, 0.5)
        return sorted_data[median_idx]

    def _weighted_mad(self, data: np.ndarray, weights: np.ndarray) -> Tuple[float, float]:
        """Calculate weighted median and MAD"""
        median = self._weighted_median(data, weights)
        abs_dev = np.abs(data - median)
        mad = self._weighted_median(abs_dev, weights)
        mad_sigma = 1.4826 * mad
        return median, mad_sigma

    def _adjust_stats_for_seasonality(
        self,
        base_median: float,
        base_mad: float,
        current_features: np.ndarray,
        window_features: np.ndarray,
        window_values: np.ndarray,
        weights: np.ndarray,
        window_mask: np.ndarray = None,
    ) -> Tuple[float, float]:
        """Adjust statistics for seasonality"""
        
        # Simplified seasonality adjustment
        # In practice, this would be more sophisticated
        
        if window_mask is not None:
            masked_weights = weights * window_mask
            if masked_weights.sum() > 0:
                masked_weights = masked_weights / masked_weights.sum()
            global_median, global_mad = self._weighted_mad(window_values, masked_weights)
        else:
            global_median, global_mad = self._weighted_mad(window_values, weights)

        # For now, return base statistics
        # TODO: Implement full seasonality adjustment logic
        return base_median, base_mad

    def _create_empty_result_packet(self) -> DataPacket:
        """Create empty result packet"""
        empty_dict = {
            self.timestamp_column: np.array([]),
            self.value_column: np.array([]),
            "group": np.array([]),
            "mean": np.array([]),
            "std": np.array([]),
            "is_anomaly": np.array([], dtype=bool),
            "anomaly_score": np.array([]),
            "anomaly_direction": np.array([]),
            "percent_deviation": np.array([]),
            "lower_bound": np.array([]),
            "upper_bound": np.array([]),
            "p_value": np.array([]),
            "ci_length": np.array([])
        }
        
        table = pa.table(empty_dict)
        
        return DataPacket(
            data=table,
            source="mad_anomaly_detector",
            metadata={
                "total_anomalies": 0,
                "anomaly_rate": 0.0,
            }
        )