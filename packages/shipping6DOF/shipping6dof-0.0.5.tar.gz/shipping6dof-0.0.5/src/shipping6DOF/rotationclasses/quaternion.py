from shipping6DOF.baseclasses import MultipleMeta
from shipping6DOF.rotationclasses import rotation
import numpy as np
from numpy import linalg as la

class quaternion(metaclass=MultipleMeta):
    """
    A quaternion is defined as q = q1*i + q2*j + q3*k + q4, where i,j,k are
    cartesian unit vector.

    It is very easy to recover different groups from Quaternions, instead of general
    rotation matrices. Only algebra involved!

    Obtaining the Euler angles from Quaternions is also quite simple.

    However, transforming vectors with quaternions is no bueno. Prefer rotation
    matrices.
    """
    def _calc_quaternions(self, angle: float, axis: list):
        """
            Quaternion from angle and axis is trivial. 
                q = cos(theta/2) + sin(theta/2)*u
            where u is the axis. See Aris (1972).
        """
        quat = []
        for x in axis:
            quat.append(x*np.sin(angle/2.0))
        quat.append(np.cos(angle/2.0))

        return quat

    def __init__(self, angle: float, axis: list):
        """
            Initialize quaternion from axis and angle of rotation along that axis.
        """
        self._q = self._calc_quaternions(angle, axis)

    def __init__(self, rot: rotation):
        """ THE PLOT THICKENS...
            Let's say you wanna recover a quaternion from a general rotation matrix A.
            Notice that by extracting the eigenvalues(vectors) we get the axis of rotation.
            Why? Simple geometric reasoning:
                A v = lambda v iif v eigenvector, lambda: scalar
                Clearly if the transformation by lambda is only scaling it is because v
                is an axis. The holomorphic axis is the one where lambda = 1.0 (!!!)
            But wait Santi, you still need that pesky angle of rotation around this axis.
            A-ha! That comes by recognizing that the trace of a matrix is invariant between
            changes of bases. That is, if we change the bases of A (general) to one where 
            my newlyfound axis of rotation is a basis, then this new rotation matrix should
            look like this:
                
                | cos(theta) sin(theta) 0 |
                | sin(theta) cos(theta) 0 |     (Recognize this bad boy?)
                |     0          0      1 |

            where trace(A) = 2 cos(theta) + 1, easy!
                                                                ~Santiago Lopez Castano
        """
        A = rot.coeffs()
        angle = np.acos((A.trace() - 1.0)/2.0)

        eigval, eigvec = la.eig(A)
        eigval = eigval.real
        eigvec = eigvec.real
        reigval = (eigval.round(decimals=4))
        
        #index = np.where(reigval == 1.0)[0]
        #if len(index) == 0 or len(index) > 1:

        index = 2

        axis = (eigvec[:,index]).flatten().tolist()

        self._q = self._calc_quaternions(float(angle), axis)

    def returnEulerAngles(self):
        """
        Self-explanatory:
            return roll, pitch, yaw
        """
        pi = np.acos(-1.0)

        qx = self._q[0]
        qy = self._q[1]
        qz = self._q[2]
        qw = self._q[3]

        # sinp = np.sqrt(1.0 + 2.0 * (qw * qy - qx * qz))
        # cosp = np.sqrt(1.0 - 2.0 * (qw * qy - qx * qz))
        # pitch = 2.0 * np.arctan2(sinp, cosp) - pi/2.0

        # CHECK FOR GIMBAL LOCK
        test = qw*qy + qx*qz
        if test > 0.499:
            roll = 0.0
            pitch = pi/2.
            yaw = 2 * np.atan2(qx,qw)
            
            return float(roll), float(pitch), float(yaw)
        if test < -0.499:
            roll = 0.0
            pitch = -pi/2.
            yaw = -2 * np.atan2(qx,qw)
            
            return float(roll), float(pitch), float(yaw)
            

        pitch = np.asin(2*test)

        sinr_cosp = 2.0*(qx*qw-qy*qz)
        cosr_cosp = 1.0 - 2.0 * (qx * qx + qz * qz)
        roll = np.arctan2(sinr_cosp, cosr_cosp)

        siny_cosp = 2.0*(qy*qw-qx*qz)
        cosy_cosp = 1.0 - 2.0 * (qy * qy + qz * qz)
        yaw = np.arctan2(siny_cosp, cosy_cosp)

        return float(roll), float(pitch), float(yaw)

