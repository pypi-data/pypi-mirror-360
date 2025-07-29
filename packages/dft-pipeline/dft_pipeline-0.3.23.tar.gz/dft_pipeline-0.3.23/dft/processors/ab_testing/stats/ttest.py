from typing import List
import numpy as np
import scipy.stats as sps
from itertools import combinations

from .base_test import BaseTest
from ..models.sample import Sample
from ..models.test_result import TestResult


class TTest(BaseTest):
    def __init__(self, alpha: float = 0.05, test_direction: str = "relative", 
                 calculate_mde: bool = True, power: float = 0.8):
        self.alpha = alpha
        self.test_direction = test_direction
        self.calculate_mde = calculate_mde
        self.power = power
        self.test_name = "t-test"
        
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
        mean_1 = sample1.mean
        mean_2 = sample2.mean
        std_1 = sample1.std
        std_2 = sample2.std
        n_1 = sample1.sample_size
        n_2 = sample2.sample_size

        # Welch's t-test (unequal variances)
        se_1 = std_1 / np.sqrt(n_1)
        se_2 = std_2 / np.sqrt(n_2)
        se_diff = np.sqrt(se_1**2 + se_2**2)
        
        t_stat = (mean_2 - mean_1) / se_diff
        
        # Degrees of freedom for Welch's t-test
        df = (se_1**2 + se_2**2)**2 / (se_1**4 / (n_1 - 1) + se_2**4 / (n_2 - 1))
        
        pvalue = 2 * (1 - sps.t.cdf(abs(t_stat), df))
        
        # Effect size calculation
        effect = mean_2 - mean_1
        
        # Confidence interval
        t_critical = sps.t.ppf(1 - self.alpha / 2, df)
        margin_error = t_critical * se_diff
        left_bound = effect - margin_error
        right_bound = effect + margin_error
        
        if self.test_direction == "relative":
            if mean_1 != 0:
                effect = effect / mean_1
                left_bound = left_bound / mean_1
                right_bound = right_bound / mean_1
            else:
                raise ValueError("Cannot calculate relative effect when control mean is zero")
        
        ci_length = right_bound - left_bound
        reject = pvalue < self.alpha

        # MDE calculation (simplified)
        mde_1 = mde_2 = 0
        if self.calculate_mde:
            mde_1 = self._calculate_mde(std_1, n_1, n_2)
            mde_2 = self._calculate_mde(std_2, n_2, n_1)

        return TestResult(
            name_1=sample1.name,
            name_2=sample2.name, 
            value_1=mean_1,
            value_2=mean_2,
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

    def _calculate_mde(self, std: float, n1: int, n2: int) -> float:
        """Calculate Minimum Detectable Effect"""
        t_alpha = sps.t.ppf(1 - self.alpha / 2, n1 + n2 - 2)
        t_beta = sps.t.ppf(self.power, n1 + n2 - 2)
        
        se = std * np.sqrt(1/n1 + 1/n2)
        mde = (t_alpha + t_beta) * se
        
        return mde

    def validate_data(self, samples: List[Sample]) -> None:
        if len(samples) < 2:
            raise ValueError("At least two samples are required for t-test")
        
        for sample in samples:
            if sample.sample_size < 2:
                raise ValueError(f"Sample '{sample.name}' has insufficient data (n < 2)")
            if sample.std == 0:
                raise ValueError(f"Sample '{sample.name}' has zero variance")
                
        # Check for duplicate names
        names = [s.name for s in samples if s.name]
        if len(names) != len(set(names)):
            raise ValueError("Sample names must be unique")