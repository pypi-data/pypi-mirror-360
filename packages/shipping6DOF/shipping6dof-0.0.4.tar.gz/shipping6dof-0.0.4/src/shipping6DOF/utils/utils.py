from shipping6DOF.rotationclasses import *
import numpy as np


def change_basis_application(e0: vector, e1: vector, e2: vector, rot : rotation) -> (rotation, rotation):
    """
        A change of basis for a transformation T: Rn -> Rn is performed as follows:
            B = (U^-1) T U
        where U = [u1, u2,...,un] and where the transformation B: Rn -> Rn i similar 
        to that of T, but with a basis {u1,u2,...,un} of Rn.

        Note: a basis ALWAYS has an inverse :)
    """
    basis = rotation(np.c_[e0.coeffs(),e1.coeffs(),e2.coeffs()])
    inv_basis = rotation(np.linalg.inv(basis.coeffs()))

    newRot = basis*(rot*inv_basis)

    return basis, newRot

def create_rot_matrix_from_theta_axis(theta: float, axis: vector) ->  rotation:
    crossp = axis.cpmf()
    out = (axis & axis)
    cos = np.cos(theta)
    sin = np.sin(theta)
    I = np.identity(3)
    return rotation((cos*I)) + (sin * crossp) + ((1.0-cos)*out)

def create_plane_from_npoints(pointlist: np.ndarray):
    
    assert pointlist.shape[0] == 3 
    assert pointlist.shape[1] > 3

    origin = np.mean(pointlist, axis=1,keepdims=True)

    svd = np.linalg.svd(pointlist - origin)
    left = svd[0]
    axis = left[:,-1]

    return originAndAxis(origin,axis)

def create_plane_from_3points(p0: vector, p1: vector, p2: vector):
    
    u = p1 - p0
    v = p2 - p0
    axis = (u ^ v) ##  u x v
    axis = (1./axis.norm())*axis
    origin = (1./3.)*(p0 + p1 + p2)

    return originAndAxis(origin,axis)

def create_plane_from_2points(p0: vector, p1: vector):

    axis = p1 - p0
    axis = (1./axis.norm())*axis

    return originAndAxis(p0,axis)

def rotation_displacement_2planes(plane1: originAndAxis, plane2: originAndAxis):

    disp  = plane2.origin() - plane1.origin()
    angle = np.acos(plane1.axis() * plane2.axis())
    axis  = plane1.axis() ^ plane2.axis()

    rot = create_rot_matrix_from_theta_axis(float(angle),axis)

    return rot, disp
