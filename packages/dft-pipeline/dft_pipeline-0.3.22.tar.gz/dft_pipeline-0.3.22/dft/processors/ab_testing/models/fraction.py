import numpy as np


class Fraction:
    def __init__(self, count: int, nobs: int, name: str = None):
        if count > nobs:
            raise ValueError("Count cannot be greater than number of observations")
        if nobs <= 0:
            raise ValueError("Number of observations must be positive")
        if count < 0:
            raise ValueError("Count cannot be negative")
            
        self.count = count
        self.nobs = nobs
        self.name = name
        self.prop = count / nobs
        self.std = np.sqrt(self.prop * (1 - self.prop) / nobs)