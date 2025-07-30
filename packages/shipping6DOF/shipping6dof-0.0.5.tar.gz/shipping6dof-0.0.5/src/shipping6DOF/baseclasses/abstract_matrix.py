from abc import ABC, abstractmethod
import numpy as np

class matrix(ABC):

    _matrix = np.ndarray

    def coeffs(self):
        return self._matrix
    def norm(self):
        return np.linalg.norm(self.coeffs())

    
    @abstractmethod
    def __init__(self,value=None):
        pass

    @abstractmethod
    def __add__(self, lhs):
        pass
    @abstractmethod
    def __sub__(self, lhs):
        pass
    @abstractmethod
    def __mul__(self, vec):
        pass

