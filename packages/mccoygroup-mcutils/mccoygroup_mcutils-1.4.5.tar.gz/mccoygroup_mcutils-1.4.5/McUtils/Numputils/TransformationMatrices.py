import itertools

import scipy.linalg

from .VectorOps import vec_normalize, vec_angles
from . import VectorOps as vec_ops
from . import Misc as misc
import math, numpy as np, scipy as sp

__all__ = [
    "rotation_matrix",
    "skew_symmetric_matrix",
    "rotation_matrix_skew",
    "youla_skew_decomp",
    "youla_skew_matrix",
    "youla_angles",
    "youla_matrix",
    "skew_from_rotation_matrix",
    "translation_matrix",
    "affine_matrix",
    "extract_rotation_angle_axis"
]

#######################################################################################################################
#
#                                                 rotation_matrix
#

def rotation_matrix_2d(theta):
    return np.moveaxis(
        np.array([
            [np.cos(theta), -np.sin(theta)],
            [np.sin(theta), np.cos(theta)]
        ]),
        0, -2
    )

def rotation_matrix_basic(xyz, theta):
    """rotation matrix about x, y, or z axis

    :param xyz: x, y, or z axis
    :type xyz: str
    :param theta: counter clockwise angle in radians
    :type theta: float
    """

    axis = xyz.lower()
    theta = np.asanyarray(theta)
    one = np.ones_like(theta)
    zero = np.zeros_like(theta)
    if axis == "z": # most common case so it comes first
        mat = [
            [ np.cos(theta), -np.sin(theta), zero],
            [ np.sin(theta),  np.cos(theta), zero],
            [ zero,                    zero,  one]
        ]
    elif axis == "y":
        mat = [
            [ np.cos(theta), zero, -np.sin(theta)],
            [ zero,           one,           zero],
            [ np.sin(theta), zero,  np.cos(theta)]
        ]
    elif axis == "x":
        mat = [
            [  one,           zero,           zero],
            [ zero,  np.cos(theta), -np.sin(theta)],
            [ zero,  np.sin(theta),  np.cos(theta)]
        ]
    else:
        raise Exception("{}: axis '{}' invalid".format('rotation_matrix_basic', xyz))
    return np.moveaxis(np.array(mat), 0, -1)

#thank you SE for the nice Euler-Rodrigues imp: https://stackoverflow.com/questions/6802577/rotation-of-3d-vector
def rotation_matrix_ER(axis, theta):
    """
    Return the rotation matrix associated with counterclockwise rotation about
    the given axis by theta radians.
    """
    axis = np.asarray(axis)
    axis = axis / math.sqrt(np.dot(axis, axis))
    a = math.cos(theta / 2.0)
    b, c, d = -axis * math.sin(theta / 2.0)
    aa, bb, cc, dd = a * a, b * b, c * c, d * d
    bc, ad, ac, ab, bd, cd = b * c, a * d, a * c, a * b, b * d, c * d
    return np.array([
        [aa + bb - cc - dd, 2 * (bc + ad),     2 * (bd - ac)    ],
        [2 * (bc - ad),     aa + cc - bb - dd, 2 * (cd + ab)    ],
        [2 * (bd + ac),     2 * (cd - ab),     aa + dd - bb - cc]
    ])

def rotation_matrix_ER_vec(axes, thetas):
    """
    Vectorized version of basic ER
    """

    axes = vec_normalize(np.asanyarray(axes))
    thetas = np.asanyarray(thetas)
    # if len(axes.shape) == 1:
    #     axes = axes/np.linalg.norm(axes)
    #     axes = np.broadcast_to(axes, (len(thetas), 3))
    # else:
    #     axes = vec_normalize(axes)

    ax_shape = axes.shape[:-1]
    t_shape = thetas.shape
    axes = np.reshape(axes, (-1, 3))
    thetas = thetas.reshape(-1)
    if thetas.ndim == 0:
        base_shape = ax_shape
    elif axes.ndim == 1:
        base_shape = t_shape
    elif thetas.ndim != axes.ndim - 1:
        raise ValueError(f"can't broadcast axes and angles with shapes {ax_shape} and {t_shape}")
    else:
        base_shape = tuple(a if t == 1 else t for a,t in zip(ax_shape, t_shape))

    a = np.cos(thetas/2.0)
    b, c, d = np.moveaxis(-axes * np.reshape(np.sin(thetas / 2.0), (len(thetas), 1)), -1, 0)
    v = np.array([a, b, c, d])
    # triu_indices
    rows, cols = (
        np.array([0, 0, 0, 0, 1, 1, 1, 2, 2, 3]),
        np.array([0, 1, 2, 3, 1, 2, 3, 2, 3, 3])
    )
    aa, ab, ac, ad, bb, bc, bd, cc, cd, dd = v[rows] * v[cols]
    ## Uses half-angle formula to get compact form for Euler-Rodrigues
    # a^2 * I + [[ 0,    2ad, -2ac]   + [[b^2 - c^2 - d^2,               2bc,              2bd]
    #            [-2ad,    0,  2ab],     [             2bc, -b^2 + c^2 - d^2,              2cd]
    #            [ 2ac, -2ab,    0]]     [             2bd,              2cd, -b^2 - c^2 + d^2]]
    R = np.array([
        [aa + bb - cc - dd,      2 * (bc + ad),         2 * (bd - ac)],
        [    2 * (bc - ad),  aa - bb + cc - dd,         2 * (cd + ab)],
        [    2 * (bd + ac),      2 * (cd - ab),     aa - bb - cc + dd]
    ])
    R = np.moveaxis(R, -1, 0)

    return R.reshape(base_shape + (3, 3))

def rotation_matrix_align_vectors(vec1, vec2):
    vec1 = vec_ops.vec_normalize(vec1)
    vec2 = vec_ops.vec_normalize(vec2)
    s = vec1 + vec2
    i = vec_ops.identity_tensors(vec1.shape[:-1], vec1.shape[-1])
    inner = 1 + vec1[..., np.newaxis, :] @ vec2[..., :, np.newaxis]

    return i - s[..., :, np.newaxis] * (s[..., np.newaxis, :]/inner) + 2 * vec1[..., :, np.newaxis] * vec2[..., np.newaxis, :]

def rotation_matrix(axis, theta=None):
    """
    :param axis:
    :type axis:
    :param theta: angle to rotate by (or Euler angles)
    :type theta:
    :return:
    :rtype:
    """
    if theta is None:
        skew_vector = np.asanyarray(axis, dtype=float)
        if skew_vector.ndim == 0:
            skew_vector = skew_vector[np.newaxis]
        base_shape = skew_vector.shape[:-1]
        skew_vector = skew_vector.reshape(-1, skew_vector.shape[-1])
        rots = np.array([
            rotation_matrix_skew(v)
            for v in skew_vector
        ])
        return rots.reshape(base_shape + rots.shape[-2:])
    elif isinstance(axis, str):
        if axis.lower() == '2d':
            return rotation_matrix_2d(theta)

        theta = np.asanyarray(theta)
        if len(axis) == 1 and theta.ndim == 1 or theta.shape[-2] != 1:
            theta = np.expand_dims(theta, -2)
        rot_mat = None
        for x,t in zip(axis.lower(), np.moveaxis(theta, -2, 0)):
            rr = rotation_matrix_basic(x, t)
            if rot_mat is None:
                rot_mat = rr
            else:
                rot_mat = rr @ rot_mat
        return rot_mat
    else:
        axis = np.asanyarray(axis)
        theta = np.asanyarray(theta)

        if axis.shape == theta.shape:
            return rotation_matrix_align_vectors(axis, theta)
        elif axis.ndim == theta.ndim + 1 and axis.shape[-1] == 3:
            return rotation_matrix_ER_vec(axis, theta)
        else:
            # we have the vectors that get mixed and their mixing angles, we assume any fixed axis is the 0 element
            # I haven't vectorized this at all...
            base_shape = axis.shape[:-2]
            theta = theta.reshape(-1, theta.shape[-1])
            axis = axis.reshape(-1, axis.shape[-2:])

            rots = np.array([
                rotation_matrix_from_angles_vectors(l, T)
                for T, l in zip(axis, theta)
            ])

            return rots.reshape(base_shape + rots.shape[-2:])

def skew_symmetric_matrix(upper_tri):
    upper_tri = np.asanyarray(upper_tri)
    l = upper_tri.shape[-1]
    n = (1 + np.sqrt(1 + 8*l)) / 2
    if int(n) != n:
        raise ValueError(f"vector of shape {l} doesn't correspond to the upper triangle of a matrix")
    n = int(n)
    base_shape = upper_tri.shape[:-1]
    m = np.zeros(base_shape + (n, n))
    rows, cols = np.triu_indices_from(m, 1)
    m[..., rows, cols] = upper_tri
    m[..., cols, rows] = -upper_tri
    return m

def extract_rotation_angle_axis(rot_mat, normalize=True):
    rot_mat = np.asanyarray(rot_mat)
    if rot_mat.shape[-1] == 2:
        return np.arccos(rot_mat[..., 0, 0]), None
    elif rot_mat.shape[-1] == 3:
        ang = np.arccos((np.trace(rot_mat, axis1=-2, axis2=-1) - 1) / 2)
        skew = (rot_mat - np.moveaxis(rot_mat, -1, -2)) / 2

        rows, cols = (np.array([2, 0, 1]), np.array([1, 2, 0]))
        ax = skew[..., rows, cols]
        if normalize:
            ax = vec_normalize(ax)
        else:
            ax = ax
        return ang, ax
    else:
        base_shape = rot_mat.shape[:-2]
        rot_mat = np.reshape(rot_mat, (-1,) + rot_mat.shape[-2:])
        angles = []
        axes = []
        for r in rot_mat:
            U, Q = scipy.linalg.schur(r)
            angles.append(youla_angles(U))
            axes.append(Q)

        angles = np.array(angles)
        axes = np.array(axes)

        return angles.reshape(base_shape + angles.shape[-1:]), axes.reshape(base_shape + axes.shape[-2:])

def youla_skew_decomp(A):
    n = len(A)
    s, T = sp.linalg.schur(A)

    l = np.diag(s, 1)
    if n % 2 == 0:
        start = 0
        end = n
    else:  # manage padding for odd dimension
        if abs(l[0]) < 1e-7:
            start = 1
            end = n
        else:
            start = 0
            end = n - 1
    l = l[start:end-1:2]

    return youla_matrix(l, n, axis_pos=0 if start == 0 else n), T

def youla_skew_matrix(l, n, axis_pos=0):

    U = np.zeros((n, n))
    o = np.concatenate([  # even inds
        np.arange(0, axis_pos, 2),
        np.arange(axis_pos + 1, n, 2),
    ])
    e = np.concatenate([  # odd inds
        np.arange(1, axis_pos, 2),
        np.arange(axis_pos + 2, n, 2),
    ])

    U[o, e] = l
    U[e, o] = -l

    return U

def youla_matrix(angles, n, axis_pos=0):

    cos = np.cos(angles)
    sin = np.sin(angles)

    # build 2x2 block mat
    U = np.eye(n)
    if n % 2 == 1:
        o = np.concatenate([  # even inds
            np.arange(0, axis_pos, 2),
            np.arange(axis_pos+1, n, 2),
            ])
        e = np.concatenate([  # even inds
            np.arange(1, axis_pos, 2),
            np.arange(axis_pos+2, n, 2),
            ])
    else:
        o = np.arange(0, n, 2)
        e = np.arange(1, n, 2)

    U[o, o] = cos
    U[e, e] = cos
    U[o, e] = sin
    U[e, o] = -sin

    return U

def youla_angles(U, axis_pos=None):
    l = np.arccos(np.round(np.diag(U), 8))
    n = len(U)
    if axis_pos is None:
        if n % 2 == 0:
            axis_pos = -1
        else:  # manage padding for odd dimension
            axis_pos = np.where(abs(l) < 1e-7)[0]
            axis_pos = 0 if axis_pos[0] == 0 else axis_pos[-1]
        if axis_pos < 0:
            axis_pos = n + axis_pos

    return np.concatenate([
        l[0:axis_pos:2],
        l[axis_pos+1::2]
    ])

def rotation_matrix_skew(upper_tri, create_skew=True):
    upper_tri = np.asanyarray(upper_tri)
    if create_skew:
        if (
                upper_tri.ndim < 2
                or upper_tri.shape[-1] != upper_tri.shape[-2]
                or not np.allclose(upper_tri, -np.moveaxis(upper_tri, -2, -1))
        ):
            upper_tri = skew_symmetric_matrix(upper_tri)

    U, T = youla_skew_decomp(upper_tri)
    return T@U@T.T

def skew_from_rotation_matrix(rot_mat):
    U, Q = sp.linalg.schur(rot_mat)

    l = youla_angles(U)
    s = youla_skew_matrix(l, U.shape[0], axis_pos=0 if U[0, 0] == 1 else U.shape[0])
    A = Q @ s @ Q.T
    return A[np.triu_indices_from(A, k=1)]

def rotation_matrix_from_angles_vectors(l, T):
    n = T.shape[0]
    if n % 2 == 1 and len(l) == (n // 2) + 1: # the axis is encoded in l
        axis_pos = np.where(np.abs(l) > 2 * np.pi)[0]
        if len(axis_pos) == 0:
            axis_pos = np.where(np.abs(l) < 1e-7)[0]
            if len(axis_pos) == 0:
                raise ValueError(f"can't find fixed axis position from angle encoding {l}")
        axis_pos = axis_pos[0]
    else:
        axis_pos = 0
    return T @ youla_matrix(l, n, axis_pos=axis_pos) @ T.T

#######################################################################################################################
#
#                                                 translation_matrix
#

def translation_matrix(shift):
    share = np.asarray(shift)
    if len(share.shape) == 1:
        ss = share
        zs = 0.
        os = 1.
        mat = np.array(
            [
                [os, zs, zs, ss[0]],
                [zs, os, zs, ss[1]],
                [zs, zs, os, ss[2]],
                [zs, zs, zs, os   ]
            ]
        )
    else:
        zs = np.zeros((share.shape[0],))
        os = np.ones((share.shape[0],))
        ss = share.T
        mat = np.array(
            [
                [os, zs, zs, ss[0]],
                [zs, os, zs, ss[1]],
                [zs, zs, os, ss[2]],
                [zs, zs, zs, os   ]
            ]
        ).T
    return mat

#######################################################################################################################
#
#                                                 affine_matrix
#

def affine_matrix(tmat, shift):
    """Creates an affine transformation matrix from a 3x3 transformation matrix or set of matrices and a shift or set of vecs

    :param tmat: base transformation matrices
    :type tmat: np.ndarray
    :param shift:
    :type shift:
    :return:
    :rtype:
    """

    base_mat = np.asanyarray(tmat)
    if shift is None:
        return base_mat

    if base_mat.ndim > 2:
        shifts = np.asanyarray(shift)
        if shifts.ndim == 1:
            shifts = np.broadcast_to(shifts, (1,)*(base_mat.ndim-2) + shifts.shape)
        shifts = np.broadcast_to(shifts, base_mat.shape[:-2] + (3,))
        shifts = np.expand_dims(shifts, -1)
        mat = np.concatenate([base_mat, shifts], axis=-1)
        padding = np.array([0., 0., 0., 1.])
        padding = np.broadcast_to(
            np.broadcast_to(padding, (1,)*(base_mat.ndim-2) + padding.shape),
            mat.shape[:-2] + (4,)
        )
        padding = np.expand_dims(padding, -2)
        mat = np.concatenate([mat, padding], axis=-2)
    else:
        mat = np.concatenate([base_mat, shift[:, np.newaxis]], axis=-1)
        mat = np.concatenate([mat, [[0., 0., 0., 1.]]], axis=-2)
    return mat