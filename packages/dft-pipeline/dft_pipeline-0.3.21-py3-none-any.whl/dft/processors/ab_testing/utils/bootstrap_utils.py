from typing import Callable, Optional, Tuple
import numpy as np


def apply_stat_func(values_samples: np.ndarray, 
                   cov_values_samples: Optional[np.ndarray] = None, 
                   stat_func: Callable[[np.ndarray], float] = np.mean) -> Tuple[np.ndarray, Optional[np.ndarray]]:
    """Apply statistical function to bootstrap samples"""
    values_results = np.apply_along_axis(stat_func, 1, values_samples)
    
    cov_results = None
    if cov_values_samples is not None:
        cov_results = np.apply_along_axis(stat_func, 1, cov_values_samples)

    return values_results, cov_results


def generate_bootstrap_samples(sample_array: np.ndarray, n_samples: int, 
                              categories_array: Optional[np.ndarray] = None,
                              categories_weights: Optional[dict] = None,
                              stratify: bool = False, 
                              random_seed: Optional[int] = None) -> np.ndarray:
    """Generate bootstrap samples from array"""
    if random_seed is not None:
        np.random.seed(random_seed)
    
    n_obs = len(sample_array)
    
    if not stratify or categories_array is None:
        # Simple bootstrap resampling
        indices = np.random.choice(n_obs, size=(n_samples, n_obs), replace=True)
        return sample_array[indices]
    
    # Stratified bootstrap resampling
    bootstrap_samples = np.zeros((n_samples, n_obs))
    
    unique_categories = np.unique(categories_array)
    current_idx = 0
    
    for category in unique_categories:
        category_mask = categories_array == category
        category_indices = np.where(category_mask)[0]
        category_size = len(category_indices)
        
        if categories_weights and category in categories_weights:
            target_size = categories_weights[category]
        else:
            target_size = category_size
        
        # Generate bootstrap indices for this category
        category_bootstrap_indices = np.random.choice(
            category_indices, 
            size=(n_samples, target_size), 
            replace=True
        )
        
        # Fill bootstrap samples
        end_idx = current_idx + target_size
        for i in range(n_samples):
            bootstrap_samples[i, current_idx:end_idx] = sample_array[category_bootstrap_indices[i]]
        
        current_idx = end_idx
    
    return bootstrap_samples[:, :current_idx]