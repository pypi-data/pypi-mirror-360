from shipping6DOF.baseclasses import MultipleMeta
from shipping6DOF.rotationclasses import vector, rotation
import numpy as np



class originAndAxis(metaclass=MultipleMeta):
    """ This is the class over which planes are going to 
        be described. 

        Why is it not called 'Plane'?
        Because we will define planes in many ways, so
        I prefer to keep this class a bit more "abstract"
    """
    def __init__(self, point: vector, axis: vector ):
        self._origin = point
        self._axis   = axis

    def __init__(self):
        self._origin = vector()
        self._axis   = vector()

    def origin(self):
        return self._origin
    def axis(self):
        return self._axis

