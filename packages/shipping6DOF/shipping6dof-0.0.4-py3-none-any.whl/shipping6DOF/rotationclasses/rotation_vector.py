from __future__ import annotations # needed for forward references
from shipping6DOF.baseclasses import matrix
import numpy as np

class vector(matrix):

    def __init__(self,value=None):
        if value is None:
            self._matrix = np.zeros(3)
        else:
            value = np.array(value)
            if len(value) == 3:
                self._matrix = value
            else:
                raise Exception("Ill defined vector.")

    def __add__(self, lhs: vector) -> vector:
        return vector(self.coeffs() + lhs.coeffs())

    def __sub__(self, lhs:vector) -> vector:
        return vector(self.coeffs() - lhs.coeffs())

    def __mul__(self, vec):
        if isinstance(vec,list):
            vec = vector(np.array(vec))
        elif isinstance(vec,(int,float)):
            return vector(vec*self.coeffs())
        elif isinstance(vec,vector):
            return (np.dot(vec.coeffs(),self.coeffs()))
        else:
            raise TypeError("Unrecognized operands type")
    __rmul__ = __mul__

    def __truediv__(self, vec):
        if isinstance(vec,np.float64) or isinstance(vec,float):
            return vector(self.coeffs()/vec)
        else:
            raise TypeError("Unrecognized operands type")

    def __xor__(self, vec: vector) -> vector:
        cross = np.cross(self.coeffs(),vec.coeffs())
        return vector(cross)

    def __and__(self, vec):
        if isinstance(vec,list):
            vec = vector(np.array(vec))
        return rotation(np.outer(self.coeffs(),vec.coeffs()))

    def cpmf(self):
        I = np.identity(3)
        return rotation(np.cross(I, self.coeffs()))


class rotation(matrix):
    
    def __init__(self,value=None):
        if value is None:
            self._matrix = np.identity(3)
        else:
            value = np.array(value)
            if value.shape == (3,3):
                self._matrix = value
            elif value.shape == (9,):
                self._matrix = value.reshape(3,3)
            else:
                raise Exception("Ill defined rotation.")

    def __add__(self, lhs: rotation) -> rotation:
        return rotation(self.coeffs() + lhs.coeffs())

    def __sub__(self, lhs:rotation) -> rotation:
        return vector(self.coeffs() - lhs.coeffs())

    def __mul__(self, vec):
        if isinstance(vec,list):
            vec = vector(np.array(vec))
        elif isinstance(vec,(int,float)):
            return rotation(vec*self.coeffs())
        elif isinstance(vec,rotation):
            return rotation(np.matmul(self.coeffs(), vec.coeffs()))
        elif isinstance(vec,vector):
            return vector(np.matmul(self.coeffs(), vec.coeffs()))
        else:
            raise TypeError("Unrecognized operands type")
    
    __rmul__ = __mul__
