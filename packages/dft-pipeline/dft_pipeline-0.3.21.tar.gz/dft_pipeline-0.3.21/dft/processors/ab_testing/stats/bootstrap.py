from typing import List, Callable, Optional
import numpy as np
import scipy.stats as sps
from itertools import combinations

from .base_test import BaseTest
from ..models.sample import Sample
from ..models.test_result import TestResult
from ..utils.bootstrap_utils import generate_bootstrap_samples, apply_stat_func


class BootstrapTest(BaseTest):
    def __init__(self, alpha: float = 0.05, test_direction: str = "relative",
                 stat_func: Callable[[np.ndarray], float] = np.mean,
                 n_samples: int = 1000, stratify: bool = False,
                 weight_method: str = "min", random_seed: Optional[int] = None):
        self.alpha = alpha
        self.test_direction = test_direction
        self.stat_func = stat_func
        self.n_samples = n_samples
        self.stratify = stratify
        self.weight_method = weight_method
        self.random_seed = random_seed
        self.test_name = "bootstrap-test"
        
        if test_direction not in ["relative", "absolute"]:
            raise ValueError('test_direction must be "relative" or "absolute"')
        if weight_method not in ["min", "mean"]:
            raise ValueError('weight_method must be "min" or "mean"')

    def run_test(self, samples: List[Sample], **kwargs) -> List[TestResult]:
        self.validate_data(samples)
        
        results = []
        for sample1, sample2 in combinations(samples, 2):
            result = self._compare_samples(sample1, sample2)
            results.append(result)
        
        return results

    def _compare_samples(self, sample1: Sample, sample2: Sample) -> TestResult:
        # Get category weights for stratified sampling
        categories_weights1, categories_weights2 = self._get_category_weights(sample1, sample2)
        
        # Generate bootstrap samples
        boot_samples1 = generate_bootstrap_samples(
            sample1.array, self.n_samples,
            categories_array=sample1.categories_array,
            categories_weights=categories_weights1,
            stratify=self.stratify,
            random_seed=self.random_seed
        )
        
        boot_samples2 = generate_bootstrap_samples(
            sample2.array, self.n_samples,
            categories_array=sample2.categories_array,
            categories_weights=categories_weights2,
            stratify=self.stratify,
            random_seed=self.random_seed
        )
        
        # Apply statistical function to bootstrap samples
        boot_stats1, _ = apply_stat_func(boot_samples1, stat_func=self.stat_func)
        boot_stats2, _ = apply_stat_func(boot_samples2, stat_func=self.stat_func)
        
        # Calculate effect distribution
        if self.test_direction == "relative":
            # Avoid division by zero
            valid_mask = boot_stats1 != 0
            if not np.any(valid_mask):
                raise ValueError("Cannot calculate relative effect when control bootstrap samples contain zeros")
            
            effect_dist = (boot_stats2[valid_mask] - boot_stats1[valid_mask]) / boot_stats1[valid_mask]
        else:
            effect_dist = boot_stats2 - boot_stats1
        
        # Calculate statistics
        effect = np.mean(effect_dist)
        effect_std = np.std(effect_dist)
        
        # P-value calculation (two-tailed test against null hypothesis of no effect)
        if self.test_direction == "relative":
            # Test against relative effect = 0
            p_positive = np.mean(effect_dist > 0)
            p_negative = np.mean(effect_dist < 0)
            pvalue = 2 * min(p_positive, p_negative)
        else:
            # Test against absolute effect = 0
            p_positive = np.mean(effect_dist > 0)
            p_negative = np.mean(effect_dist < 0)
            pvalue = 2 * min(p_positive, p_negative)
        
        # Confidence interval
        ci_lower = np.percentile(effect_dist, 100 * self.alpha / 2)
        ci_upper = np.percentile(effect_dist, 100 * (1 - self.alpha / 2))
        ci_length = ci_upper - ci_lower
        
        reject = pvalue < self.alpha
        
        # Original sample statistics
        mean_1 = sample1.mean
        mean_2 = sample2.mean
        std_1 = sample1.std
        std_2 = sample2.std
        
        return TestResult(
            name_1=sample1.name,
            name_2=sample2.name,
            value_1=mean_1,
            value_2=mean_2,
            std_1=std_1,
            std_2=std_2,
            size_1=sample1.sample_size,
            size_2=sample2.sample_size,
            method_name=self.test_name,
            method_params={
                "alpha": self.alpha,
                "test_direction": self.test_direction,
                "stat_func": self.stat_func.__name__,
                "n_samples": self.n_samples,
                "stratify": self.stratify,
                "weight_method": self.weight_method,
                "random_seed": self.random_seed
            },
            alpha=self.alpha,
            pvalue=pvalue,
            effect=effect,
            ci_length=ci_length,
            left_bound=ci_lower,
            right_bound=ci_upper,
            reject=reject,
            effect_distribution=sps.norm(loc=effect, scale=effect_std)
        )

    def _get_category_weights(self, sample1: Sample, sample2: Sample):
        """Calculate category weights for stratified sampling"""
        if not self.stratify:
            return None, None
        
        weights1 = sample1.get_category_weights(stratify=True)
        weights2 = sample2.get_category_weights(stratify=True)
        
        if self.weight_method == "min":
            # Use minimum sample size for each category
            all_categories = set(weights1.keys()) | set(weights2.keys())
            min_weights1 = {}
            min_weights2 = {}
            
            for cat in all_categories:
                w1 = weights1.get(cat, 0)
                w2 = weights2.get(cat, 0)
                min_weight = min(w1, w2) if w1 > 0 and w2 > 0 else 0
                
                if min_weight > 0:
                    min_weights1[cat] = min_weight
                    min_weights2[cat] = min_weight
            
            return min_weights1, min_weights2
        
        elif self.weight_method == "mean":
            # Use mean sample size for each category
            all_categories = set(weights1.keys()) | set(weights2.keys())
            mean_weights1 = {}
            mean_weights2 = {}
            
            for cat in all_categories:
                w1 = weights1.get(cat, 0)
                w2 = weights2.get(cat, 0)
                
                if w1 > 0 and w2 > 0:
                    mean_weight = int((w1 + w2) / 2)
                    mean_weights1[cat] = mean_weight
                    mean_weights2[cat] = mean_weight
            
            return mean_weights1, mean_weights2
        
        return weights1, weights2

    def validate_data(self, samples: List[Sample]) -> None:
        if len(samples) < 2:
            raise ValueError("At least two samples are required for bootstrap test")
        
        for sample in samples:
            if sample.sample_size < 2:
                raise ValueError(f"Sample '{sample.name}' has insufficient data (n < 2)")
                
        # Check for duplicate names
        names = [s.name for s in samples if s.name]
        if len(names) != len(set(names)):
            raise ValueError("Sample names must be unique")