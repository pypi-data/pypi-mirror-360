import numpy as np
from typing import Union, Optional, Dict


class Sample:
    def __init__(self, array: Union[list, np.ndarray], categories_array: Union[list, np.ndarray] = None, 
                 cov_array=None, name: str = None):
        if not isinstance(array, (list, np.ndarray)):
            raise ValueError('array must be a list or numpy array')
        
        self.array = np.array(array)
        self.std = np.std(self.array)
        self.mean = np.mean(self.array)
        self.sample_size = len(self.array)
        self.var = np.square(self.std)
        self.name = name

        self.categories_array = None
        self.cov_array = None
        self.cov_mean = None
        self.cov_std = None
        self.cov_var = None
        self.corr_coef = None

        if categories_array is not None:
            self.__set_categories(categories_array)
        
        if cov_array is not None:
            self.__set_covariate(cov_array)

    def __set_categories(self, categories_array):
        if len(categories_array) != self.sample_size:
            raise ValueError('Array and categories_array lengths do not match')
        self.categories_array = np.array(categories_array)

    def __set_covariate(self, cov_array):
        if len(cov_array) != self.sample_size:
            raise ValueError('Array and cov_array lengths do not match')
        self.cov_array = np.array(cov_array)
        self.cov_mean = np.mean(self.cov_array)
        self.cov_std = np.std(self.cov_array)
        self.cov_var = np.square(self.cov_std)
        self.corr_coef = np.corrcoef(self.array, self.cov_array)[0][1]

    def get_category_weights(self, sample_size: Optional[int] = None, stratify: bool = True) -> Dict[Union[str, int], int]:
        sample_size = sample_size or self.sample_size

        if not stratify or self.categories_array is None:
            return {'all_values': sample_size}
        
        categories, counts = np.unique(self.categories_array, return_counts=True)
        weights = dict(zip(categories, counts))
        return {k: max(1, int(v * sample_size / self.sample_size)) for k, v in weights.items()}