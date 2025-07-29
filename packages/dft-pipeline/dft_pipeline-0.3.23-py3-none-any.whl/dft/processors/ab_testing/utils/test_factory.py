from typing import Dict, Type
from ..stats.base_test import BaseTest
from ..stats.ttest import TTest
from ..stats.ztest import ZTest
from ..stats.cuped_ttest import CupedTTest
from ..stats.bootstrap import BootstrapTest


class TestFactory:
    """Factory for creating statistical test instances"""
    
    _test_classes: Dict[str, Type[BaseTest]] = {
        "ttest": TTest,
        "ztest": ZTest,
        "cuped_ttest": CupedTTest,
        "bootstrap": BootstrapTest
    }
    
    @classmethod
    def create_test(cls, test_type: str, **kwargs) -> BaseTest:
        """Create a test instance based on test type"""
        if test_type not in cls._test_classes:
            available_tests = ", ".join(cls._test_classes.keys())
            raise ValueError(f"Unknown test type '{test_type}'. Available tests: {available_tests}")
        
        test_class = cls._test_classes[test_type]
        return test_class(**kwargs)
    
    @classmethod
    def get_available_tests(cls) -> list:
        """Get list of available test types"""
        return list(cls._test_classes.keys())
    
    @classmethod
    def register_test(cls, test_type: str, test_class: Type[BaseTest]):
        """Register a new test type"""
        cls._test_classes[test_type] = test_class