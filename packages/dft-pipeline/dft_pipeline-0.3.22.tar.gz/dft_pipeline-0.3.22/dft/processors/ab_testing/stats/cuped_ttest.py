from typing import List
import numpy as np
import scipy.stats as sps
from itertools import combinations

from .base_test import BaseTest
from ..models.sample import Sample
from ..models.test_result import TestResult


class CupedTTest(BaseTest):
    def __init__(self, alpha: float = 0.05, test_direction: str = "relative", 
                 calculate_mde: bool = True, power: float = 0.8):
        self.alpha = alpha
        self.test_direction = test_direction
        self.calculate_mde = calculate_mde
        self.power = power
        self.test_name = "cuped-t-test"
        
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
        # CUPED adjustment: Y_adjusted = Y - theta * (X - E[X])
        # where theta is the coefficient that minimizes variance
        
        # Original metrics
        y1 = sample1.array
        y2 = sample2.array
        x1 = sample1.cov_array
        x2 = sample2.cov_array
        
        # Calculate pooled covariate mean
        pooled_cov_mean = (np.sum(x1) + np.sum(x2)) / (len(x1) + len(x2))
        
        # Calculate theta (regression coefficient) from pooled data
        all_y = np.concatenate([y1, y2])
        all_x = np.concatenate([x1, x2])
        
        # theta = Cov(X,Y) / Var(X)
        theta = np.cov(all_x, all_y)[0, 1] / np.var(all_x)
        
        # Apply CUPED adjustment
        y1_adj = y1 - theta * (x1 - pooled_cov_mean)
        y2_adj = y2 - theta * (x2 - pooled_cov_mean)
        
        # Calculate adjusted statistics
        mean_1_adj = np.mean(y1_adj)
        mean_2_adj = np.mean(y2_adj)
        std_1_adj = np.std(y1_adj)
        std_2_adj = np.std(y2_adj)
        n_1 = len(y1_adj)
        n_2 = len(y2_adj)

        # Welch's t-test on adjusted data
        se_1 = std_1_adj / np.sqrt(n_1)
        se_2 = std_2_adj / np.sqrt(n_2)
        se_diff = np.sqrt(se_1**2 + se_2**2)
        
        t_stat = (mean_2_adj - mean_1_adj) / se_diff
        
        # Degrees of freedom for Welch's t-test
        df = (se_1**2 + se_2**2)**2 / (se_1**4 / (n_1 - 1) + se_2**4 / (n_2 - 1))
        
        pvalue = 2 * (1 - sps.t.cdf(abs(t_stat), df))
        
        # Effect size on original scale (not adjusted)
        mean_1_orig = sample1.mean
        mean_2_orig = sample2.mean
        effect = mean_2_orig - mean_1_orig
        
        # Confidence interval for adjusted effect
        t_critical = sps.t.ppf(1 - self.alpha / 2, df)
        margin_error = t_critical * se_diff
        left_bound = (mean_2_adj - mean_1_adj) - margin_error
        right_bound = (mean_2_adj - mean_1_adj) + margin_error
        
        if self.test_direction == "relative":
            if mean_1_orig != 0:
                effect = effect / mean_1_orig
                # Approximate relative CI bounds
                left_bound = left_bound / mean_1_orig
                right_bound = right_bound / mean_1_orig
            else:
                raise ValueError("Cannot calculate relative effect when control mean is zero")
        
        ci_length = right_bound - left_bound
        reject = pvalue < self.alpha

        # MDE calculation using adjusted variance
        mde_1 = mde_2 = 0
        if self.calculate_mde:
            mde_1 = self._calculate_mde(std_1_adj, n_1, n_2)
            mde_2 = self._calculate_mde(std_2_adj, n_2, n_1)

        return TestResult(
            name_1=sample1.name,
            name_2=sample2.name,
            value_1=mean_1_orig,  # Report original means
            value_2=mean_2_orig,
            std_1=sample1.std,    # Report original std
            std_2=sample2.std,
            size_1=n_1,
            size_2=n_2,
            method_name=self.test_name,
            method_params={
                "alpha": self.alpha,
                "test_direction": self.test_direction,
                "calculate_mde": self.calculate_mde,
                "power": self.power,
                "theta": theta,
                "variance_reduction": 1 - (std_1_adj**2 + std_2_adj**2) / (sample1.std**2 + sample2.std**2)
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
            cov_value_1=sample1.cov_mean,
            cov_value_2=sample2.cov_mean,
            effect_distribution=sps.norm(loc=effect, scale=se_diff)
        )

    def _calculate_mde(self, std: float, n1: int, n2: int) -> float:
        """Calculate Minimum Detectable Effect using adjusted variance"""
        t_alpha = sps.t.ppf(1 - self.alpha / 2, n1 + n2 - 2)
        t_beta = sps.t.ppf(self.power, n1 + n2 - 2)
        
        se = std * np.sqrt(1/n1 + 1/n2)
        mde = (t_alpha + t_beta) * se
        
        return mde

    def validate_data(self, samples: List[Sample]) -> None:
        if len(samples) < 2:
            raise ValueError("At least two samples are required for CUPED t-test")
        
        for sample in samples:
            if sample.sample_size < 2:
                raise ValueError(f"Sample '{sample.name}' has insufficient data (n < 2)")
            if sample.std == 0:
                raise ValueError(f"Sample '{sample.name}' has zero variance")
            if sample.cov_array is None:
                raise ValueError(f"Sample '{sample.name}' is missing covariate data for CUPED")
            if len(sample.cov_array) != sample.sample_size:
                raise ValueError(f"Sample '{sample.name}' covariate array length mismatch")
            
            # Check correlation strength (optional warning)
            if abs(sample.corr_coef) < 0.1:
                import logging
                logging.getLogger(__name__).warning(
                    f"Low correlation between metric and covariate for sample '{sample.name}' "
                    f"(r={sample.corr_coef:.3f}). CUPED may not be effective."
                )
                
        # Check for duplicate names
        names = [s.name for s in samples if s.name]
        if len(names) != len(set(names)):
            raise ValueError("Sample names must be unique")