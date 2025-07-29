from typing import List
import numpy as np
import scipy.stats as sps
from itertools import combinations

from .base_test import BaseTest
from ..models.sample import Sample
from ..models.test_result import TestResult


class ZTest(BaseTest):
    def __init__(self, alpha: float = 0.05, test_direction: str = "relative", 
                 calculate_mde: bool = True, power: float = 0.8):
        self.alpha = alpha
        self.test_direction = test_direction
        self.calculate_mde = calculate_mde
        self.power = power
        self.test_name = "z-test"
        
        if test_direction not in ["relative", "absolute"]:
            raise ValueError('test_direction must be "relative" or "absolute"')

    def run_test(self, samples: List[Sample], **kwargs) -> List[TestResult]:
        self.validate_data(samples)
        
        results = []
        for sample1, sample2 in combinations(samples, 2):
            result = self._compare_samples(sample1, sample2)
            results.append(result)
        
        return results

    def _compare_samples(self, sample1: Sample, sample2: Sample) -> TestResult:
        # Convert binary arrays to proportions
        data1 = sample1.array
        data2 = sample2.array
        
        # Calculate proportions and counts
        prop_1 = np.mean(data1)
        prop_2 = np.mean(data2)
        count_1 = np.sum(data1)
        count_2 = np.sum(data2)
        n_1 = len(data1)
        n_2 = len(data2)
        
        # Pooled proportion for hypothesis testing
        prop_combined = (count_1 + count_2) / (n_1 + n_2)

        # Standard errors
        std_1 = np.sqrt(prop_1 * (1 - prop_1) / n_1)
        std_2 = np.sqrt(prop_2 * (1 - prop_2) / n_2)

        # Z-statistic using pooled variance
        se_pooled = np.sqrt(prop_combined * (1 - prop_combined) * (1/n_1 + 1/n_2))
        z_stat = (prop_2 - prop_1) / se_pooled
        
        # Two-tailed p-value
        pvalue = 2 * (1 - sps.norm.cdf(abs(z_stat)))

        # Effect size and confidence interval using separate variances
        effect = prop_2 - prop_1
        se_diff = np.sqrt(std_1**2 + std_2**2)
        
        z_critical = sps.norm.ppf(1 - self.alpha / 2)
        margin_error = z_critical * se_diff
        left_bound = effect - margin_error
        right_bound = effect + margin_error

        if self.test_direction == "relative":
            if prop_1 != 0:
                effect = effect / prop_1
                left_bound = left_bound / prop_1
                right_bound = right_bound / prop_1
            else:
                raise ValueError("Cannot calculate relative effect when control proportion is zero")

        ci_length = right_bound - left_bound
        reject = pvalue < self.alpha

        # MDE calculation
        mde_1 = mde_2 = 0
        if self.calculate_mde:
            mde_1 = self._calculate_mde(prop_1, n_1, n_2)
            mde_2 = self._calculate_mde(prop_2, n_2, n_1)

        return TestResult(
            name_1=sample1.name,
            name_2=sample2.name,
            value_1=prop_1,
            value_2=prop_2,
            std_1=std_1,
            std_2=std_2,
            size_1=n_1,
            size_2=n_2,
            method_name=self.test_name,
            method_params={
                "alpha": self.alpha,
                "test_direction": self.test_direction,
                "calculate_mde": self.calculate_mde,
                "power": self.power
            },
            alpha=self.alpha,
            pvalue=pvalue,
            effect=effect,
            ci_length=ci_length,
            left_bound=left_bound,
            right_bound=right_bound,
            reject=reject,
            mde_1=mde_1,
            mde_2=mde_2,
            effect_distribution=sps.norm(loc=effect, scale=se_diff)
        )

    def _calculate_mde(self, prop: float, n1: int, n2: int) -> float:
        """Calculate Minimum Detectable Effect for proportions"""
        z_alpha = sps.norm.ppf(1 - self.alpha / 2)
        z_beta = sps.norm.ppf(self.power)
        
        # Conservative MDE calculation using baseline proportion
        se = np.sqrt(prop * (1 - prop) * (1/n1 + 1/n2))
        mde = (z_alpha + z_beta) * se
        
        return mde

    def validate_data(self, samples: List[Sample]) -> None:
        if len(samples) < 2:
            raise ValueError("At least two samples are required for z-test")

        for sample in samples:
            if sample.sample_size == 0:
                raise ValueError(f"Sample '{sample.name}' has no observations")
                
            # Check if values are binary (0/1)
            unique_values = np.unique(sample.array)
            if not np.all(np.isin(unique_values, [0, 1])):
                raise ValueError(f"Z-test requires binary values (0/1) for sample '{sample.name}'. "
                               f"Found values: {unique_values}")
            
            # Check minimum sample size for normal approximation
            prop = np.mean(sample.array)
            expected_successes = prop * sample.sample_size
            expected_failures = (1 - prop) * sample.sample_size
            
            if expected_successes < 5 or expected_failures < 5:
                raise ValueError(
                    f"Sample '{sample.name}' does not meet normal approximation requirements "
                    f"(need at least 5 expected successes and failures, got {expected_successes:.1f} and {expected_failures:.1f})"
                )

        # Check for duplicate names
        names = [s.name for s in samples if s.name]
        if len(names) != len(set(names)):
            raise ValueError("Sample names must be unique")