from abc import ABC, abstractmethod
from typing import List, Union
from ..models.sample import Sample
from ..models.fraction import Fraction
from ..models.test_result import TestResult


class BaseTest(ABC):
    """Base class for all statistical tests"""
    
    @abstractmethod
    def run_test(self, data: Union[List[Sample], List[Fraction]], **kwargs) -> List[TestResult]:
        """Run statistical test on the provided data"""
        pass
    
    @abstractmethod 
    def validate_data(self, data: Union[List[Sample], List[Fraction]]) -> None:
        """Validate input data for the test"""
        pass