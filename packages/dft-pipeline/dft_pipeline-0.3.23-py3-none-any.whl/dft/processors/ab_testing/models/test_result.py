from dataclasses import dataclass
from typing import Optional
import scipy.stats as sps


@dataclass
class TestResult:
    name_1: str
    value_1: float
    std_1: float
    size_1: int

    name_2: str
    value_2: float
    std_2: float
    size_2: int
    
    method_name: str
    method_params: dict

    alpha: float
    pvalue: float
    effect: float
    ci_length: float
    left_bound: float
    right_bound: float
    reject: bool

    mde_1: Optional[float] = 0
    mde_2: Optional[float] = 0
    cov_value_1: Optional[float] = 0
    cov_value_2: Optional[float] = 0
    effect_distribution: Optional[sps.norm] = None

    def to_dict(self):
        """Convert TestResult to dictionary for easy serialization"""
        result = {
            "group_1": self.name_1,
            "group_2": self.name_2,
            "mean_1": self.value_1,
            "mean_2": self.value_2,
            "std_1": self.std_1,
            "std_2": self.std_2,
            "size_1": self.size_1,
            "size_2": self.size_2,
            "method": self.method_name,
            "method_params": self.method_params,
            "alpha": self.alpha,
            "pvalue": self.pvalue,
            "effect": self.effect,
            "ci_length": self.ci_length,
            "ci_lower": self.left_bound,
            "ci_upper": self.right_bound,
            "significant": self.reject,
            "mde_1": self.mde_1,
            "mde_2": self.mde_2,
            "covariate_1": self.cov_value_1 if self.cov_value_1 is not None else 0.0,
            "covariate_2": self.cov_value_2 if self.cov_value_2 is not None else 0.0
        }
            
        return result