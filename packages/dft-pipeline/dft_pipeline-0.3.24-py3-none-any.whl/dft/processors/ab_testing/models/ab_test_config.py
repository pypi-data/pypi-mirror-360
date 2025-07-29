from dataclasses import dataclass
from typing import Optional, Literal


@dataclass
class ABTestConfig:
    test_type: Literal["ttest", "ztest", "cuped_ttest", "bootstrap"]
    metric_column: str
    group_column: str
    
    alpha: float = 0.05
    test_direction: Literal["relative", "absolute"] = "relative"
    calculate_mde: bool = True
    power: float = 0.8
    
    # For CUPED tests
    covariate_column: Optional[str] = None
    
    # For bootstrap tests
    n_samples: int = 1000
    stratify: bool = True
    random_seed: Optional[int] = None
    
    def __post_init__(self):
        if self.test_type == "cuped_ttest" and not self.covariate_column:
            raise ValueError("covariate_column is required for CUPED tests")
        
        if self.alpha <= 0 or self.alpha >= 1:
            raise ValueError("alpha must be between 0 and 1")
            
        if self.power <= 0 or self.power >= 1:
            raise ValueError("power must be between 0 and 1")