#!/usr/bin/env python
# -*- coding: utf-8 -*-

from geoclide.basic import Vector, Point, Normal
import math
import numpy as np


def dot(a, b):
    """
    The dot/scalar product

    Definition of the dot product:

    - :math:`(a . b) = a.x*b.x + a.y*b.y + a.z*b.z`
    - :math:`(a . b) = ||a|| * ||b|| * cos(θ)`

    Parameters
    ----------
    a : Vector | Normal
        The first vector(s) or normal(s) used for the dot product
    b : Vector | Normal
        The second vector(s) or normal(s) used for the dot product
    
    Returns
    -------
    out : float | 1-D ndarray
        The result(s) of the dot product i.e. sum of products

    Examples
    --------
    >>> import geoclide as gc
    >>> a = gc.Vector(0., 0., 1.)
    >>> b = gc.Vector(math.sqrt(2.)/2., 0., math.sqrt(2.)/2.)
    >>> gc.dot(a,b)
    0.7071067811865476
    """
    if (isinstance(a, Vector) or isinstance(a, Normal)) and \
       (isinstance(b, Vector) or isinstance(b, Normal)):
        return (a.x*b.x + a.y*b.y + a.z*b.z)
    else:
        raise ValueError('Only Vector or Normal parameters are accepted')


def cross(a, b):
    """
    The cross product

    - .. warning:: The cross product of 2 normals is not allowed

    Definition of the cross product:

    - :math:`(a × b) = ((a.y*b.z)-(a.z*b.y))x̂ + ((a.z*b.x)-(a.x*b.z))ŷ + ((a.x*b.y)-(a.y*b.x))`
    - :math:`(a × b) = ||a||*||b||*sin(θ)`

        where x̂, ŷ and ẑ are the unitary vectors respectively in axes x, y and z

    Parameters
    ----------
    a : Vector | Normal
        The first vector(s) or normal(s) used for the cross product
    b : Vector | Normal
        The second vector(s) or normal(s) used for the cross product
    
    Returns
    -------
    out : Vector
        The result(s) of the cross product

    Examples
    --------
    >>> import geoclide as gc
    >>> a = gc.Vector(0.,0.,1.)
    >>> b = gc.Vector(1.,0.,0.)
    >>> gc.cross(a,b)
    Vector(0.0, 1.0, 0.0)
    """
    if ( (isinstance(a, Vector) and isinstance(b, Vector)) or 
         (isinstance(a, Vector) and isinstance(b, Normal)) or 
         (isinstance(a, Normal) and isinstance(b, Vector)) ):
        return Vector((a.y*b.z)-(a.z*b.y), (a.z*b.x)-(a.x*b.z), (a.x*b.y)-(a.y*b.x))
    elif isinstance(a, Normal) and isinstance(b, Normal):
        raise ValueError('Only 1 Normal is tolerated not 2')
    else:
        raise ValueError('Only Vector or Normal parameters are accepted')
    

def normalize(v):
    """
    Normalize a vector/normal or a set of vectors/normals

    Parameters
    ----------
    v : Vector | Normal
        The vector(s) or normal(s) to be normalized
    
    Returns
    -------
    out : Vector | Normal
        The normalized vector(s)/normal(s)

    Examples
    --------
    >>> import geoclide as gc
    >>> v = gc.Vector(1.,0.,1.)
    >>> gc.normalize(v)
    Vector(0.7071067811865475, 0.0, 0.7071067811865475)
    """
    if isinstance(v, Vector) or isinstance(v, Normal):
        return v / v.length()
    else:
        raise ValueError('The parameter v must be a Vector or Normal')


def coordinate_system(v1, method="m2"):
    """
    Create orthogonal coordinate system(s) from a vector/set of vectors

    Parameters
    ----------
    v1 : Vector
        The base vector(s) used to create the orthogonal coordinate system(s)
    method: str, optional
        Default is 'm2' (method from pbrt v4), other choice is 'm1' (pbrt v2 and v3)
    
    Returns
    -------
    v2 : Vector
        The second vector(s) of the orthogonal coordinate system(s)
    v3 : Vector
        The third vector(s) of the orthogonal coordinate system(s)
    
    Examples
    --------
    >>> import geoclide as gc
    >>> v1 = gc.Vector(0., 0., 1.)
    >>> v2, v3 = gc.coordinate_system(v1)
    (Vector(1.0, -0.0, -0.0), Vector(-0.0, 1.0, -0.0))
    """
    if not isinstance(v1, Vector):
        raise ValueError("The parameter v1 must be a Vector")

    # used in pbrt v4    
    if (method == "m2"):
        if (isinstance(v1.x, np.ndarray)):
            sign = np.ones_like(v1.x)
            sign[v1.z<=0] = -1
        else:
            if v1.z > 0:sign = 1.
            else: sign =-1.
        term_1 = -1. / (sign + v1.z)
        term_2 = v1.x * v1.y * term_1
        v2 = Vector(1 + sign * (v1.x*v1.x) * term_1, sign * term_2, -sign * v1.x)
        v3 = Vector(term_2, sign + (v1.y*v1.y) * term_1, -v1.y)
    # used in pbrt v2 and v3
    elif (method == "m1"):
        if (isinstance(v1.x, np.ndarray)):
            v2 = np.zeros((len(v1.x), 3), np.float64)
            cond = np.abs(v1.x) > np.abs(v1.y)
            not_cond = np.logical_not(cond)
            any_cond = np.any(cond)
            any_not_cond = np.any(not_cond)
            if any_cond:
                v2[cond,0] =  (1./np.sqrt(v1.x*v1.x + v1.z*v1.z)) * -v1.z
                v2[cond,2] =  (1./np.sqrt(v1.x*v1.x + v1.z*v1.z)) * v1.x
            if any_not_cond:
                v2[not_cond,1] = (1./np.sqrt(v1.x*v1.x + v1.z*v1.z)) * v1.z
                v2[not_cond,2] = (1./np.sqrt(v1.x*v1.x + v1.z*v1.z)) * -v1.y
            v2 = Vector(v2)
        else:
            if (abs(v1.x) > abs(v1.y)):
                invLen = 1/ math.sqrt(v1.x*v1.x + v1.z*v1.z)
                v2 = Vector(-v1.z*invLen, 0, v1.x*invLen)
            else:
                invLen = 1/ math.sqrt(v1.y*v1.y + v1.z*v1.z)
                v2 = Vector(0, v1.z*invLen, -v1.y*invLen)
        v3 = cross(v1, v2)
    else:
        raise ValueError("Only 2 choices for parameter method: 'm1' or 'm2'")
    
    return v2, v3


def distance(p1, p2):
    """
    Compute the distance(s) between 2 points/set of points

    Parameters
    ----------
    p1 : Point
        The first point(s)
    p2 : Point
        The second point(s)

    Returns
    -------
    out : float | 1-D ndarray
        The distance(s) between the 2 points/set of points
    
    Examples
    --------
    >>> p1 = gc.Point(0., 0., 0.)
    >>> p2 = gc.Point(0., 0., 10.)
    >>> gc.distance(p1,p2)
    10.0
    >>> p1 = gc.Point(1., 2., 1.9)
    >>> p2 = gc.Point(5., 15., 3.)
    >>> gc.distance(p1,p2)
    13.64587849865299
    """
    if isinstance(p1, Point) and isinstance(p2, Point):
        return (p1 - p2).length()
    else:
        raise ValueError('Only Point parameters are accepted')


def face_forward(a, b):
    """
    Flip the vector(s)/normal(s) a if the vector(s)/normal(s) b is/are in the opposite 
    direction(s)

    It can be useful to flip a surface normal so that it lies in the same
    hemisphere as a given vector.

    Parameters
    ----------
    a : Vector | Normal
        The vector(s) or normal(s) to potentially flip
    b : Vector | Normal
        The base vector(s) or normal(s) used for the flip

    Returns
    -------
    out : Vector | Normal
        The potentially flipped vector(s) or normal(s)

    Examples
    --------
    >>> import geoclide as gc
    >>> n1 = gc.Normal(1., 0., 0.)
    >>> v1 = gc.Vector(-1., 0., 0.)
    >>> gc.face_forward(v1, n1)
    Vector(1.0, -0.0, -0.0)
    """
    if (isinstance(a, Vector) or isinstance(a, Normal)) and \
    (isinstance(b, Vector) or isinstance(b, Normal)):
        if isinstance(a.x, np.ndarray):
            a_bis = a.to_numpy()
            cond = dot(a, b) < 0
            if np.any(cond): a_bis[cond,:] *= -1
            if(isinstance(a, Vector)): return Vector(a_bis)
            else: return Normal(a_bis)
        elif isinstance(b.x, np.ndarray):
            a_bis = np.zeros_like(b.to_numpy())
            a_bis[:,0] = a.x
            a_bis[:,1] = a.y
            a_bis[:,2] = a.z
            cond = dot(a, b) < 0
            if np.any(cond): a_bis[cond,:] *= -1
            if(isinstance(a, Vector)): return Vector(a_bis)
            else: return Normal(a_bis)
        else:
            return (a*-1) if (dot(a, b) < 0) else a
    else:
        raise ValueError('Only Vector or Normal parameters are accepted')


def vmax(a):
    """
    Get the largest components value(s) of the vector(s)/point(s)/normal(s)

    Parameters
    ----------
    a : Vector | Point | Normal
        The vector(s)/point(s)/normal(s) used
    
    Returns
    -------
    out: float | 1-D ndarray
        The largest vector(s)/point(s)/normal(s) value(s)
    
    Examples
    --------
    >>> import geoclide as gc
    >>> v1 = gc.Vector(2.,3.,1.)
    >>> gc.max(v1)
    3
    """
    if isinstance(a, Vector) or isinstance(a, Point) or isinstance(a, Normal):
        if (isinstance(a.x, np.ndarray)):
            return np.maximum(a.x, np.maximum(a.y, a.z))
        else:
            return max(a.x, max(a.y, a.z))

    else:
        raise ValueError('Only a Vector, a Point or a Normal parameter is accepted')


def vmin(a):
    """
    Get the smallest components value(s) of the vector(s)/point(s)/normal(s)

    Parameters
    ----------
    a : Vector | Point | Normal
        The vector(s)/point(s)/normal(s) used
    
    Returns
    -------
    out: float | 1-D ndarray
        The smallest vector(s)/point(s)/normal(s) value(s)
    
    Examples
    --------
    >>> import geoclide as gc
    >>> v1 = gc.Vector(2.,3.,1.)
    >>> gc.min(v1)
    1
    """
    if isinstance(a, Vector) or isinstance(a, Point) or isinstance(a, Normal):
        if (isinstance(a.x, np.ndarray)):
            return np.minimum(a.x, np.minimum(a.y, a.z))
        else:
            return min(a.x, min(a.y, a.z))
    else:
        raise ValueError('Only a Vector, a Point or a Normal parameter is accepted')
    

def vargmax(a):
    """
    Get the index/indices of the vector(s)/point(s)/normal(s) components with 
    the largest value(s)

    Parameters
    ----------
    a : Vector | Point | Normal
        The vector(s)/point(s)/normal(s) used
    
    Returns
    -------
    out: int | 1-D ndarray
        The index/indices of the largest vector(s)/point(s)/normal(s) value(s)
    
    Examples
    --------
    >>> import geoclide as gc
    >>> v1 = gc.Vector(2.,3.,1.)
    >>> gc.argmax(v1)
    1
    """
    if isinstance(a, Vector) or isinstance(a, Point) or isinstance(a, Normal):
        if (isinstance(a.x, np.ndarray)):
            a_bis = np.zeros_like(a.x, dtype=np.int32)
            c1 = a.x>a.y
            not_c1 = np.logical_not(c1)
            c2 = a.x<=a.z
            c3 = a.y>a.z
            not_c3 = np.logical_not(c3)
            a_bis[np.logical_and(c1, c2)] = 2
            a_bis[np.logical_and(not_c1, c3)] = 1
            a_bis[np.logical_and(not_c1, not_c3)] = 2
            return a_bis
        else:
            return (0 if a.x>a.z else 2) if (a.x>a.y) else (1 if a.y>a.z else 2)
    else:
        raise ValueError('Only a Vector, a Point or a Normal parameter is accepted')


def vargmin(a):
    """
    Get the index/indices of the vector(s)/point(s)/normal(s) components with 
    the smallest value(s)

    Parameters
    ----------
    a : Vector | Point | Normal
        The vector(s)/point(s)/normal(s) used
    
    Returns
    -------
    out: int | 1-D ndarray
        The index/indices of the smallest vector(s)/point(s)/normal(s) value(s)
    
    Examples
    --------
    >>> import geoclide as gc
    >>> v1 = gc.Vector(2.,3.,1.)
    >>> gc.argmin(v1)
    2
    """
    if isinstance(a, Vector) or isinstance(a, Point) or isinstance(a, Normal):
        if (isinstance(a.x, np.ndarray)):
            a_bis = np.zeros_like(a.x, dtype=np.int32)
            c1 = a.x<a.y
            not_c1 = np.logical_not(c1)
            c2 = a.x>=a.z
            c3 = a.y<a.z
            not_c3 = np.logical_not(c3)
            a_bis[np.logical_and(c1, c2)] = 2
            a_bis[np.logical_and(not_c1, c3)] = 1
            a_bis[np.logical_and(not_c1, not_c3)] = 2
            return a_bis
        else:
            return (0 if a.x<a.z else 2) if (a.x<a.y) else (1 if a.y<a.z else 2)
    else:
        raise ValueError('Only a Vector, a Point or a Normal parameter is accepted')
    

def vabs(a):
    """
    Calculate the absolute value(s) of each component of the vector(s)/point(s)/normal(s)

    Parameters
    ----------
    a : Vector | Point | Normal
        The vector(s)/point(s)/normal(s) used
    
    Returns
    -------
    out: Vector | Point | Normal | 1-D ndarray
        The vector(s)/point(s)/normal(s) with absolute values
    """
    if isinstance(a, Vector):
        if (isinstance(a.x, np.ndarray)):
            return Vector(np.abs(a.x), np.abs(a.y), np.abs(a.z))
        else:
            return Vector(abs(a.x), abs(a.y), abs(a.z))
    elif isinstance(a, Point):
        if (isinstance(a.x, np.ndarray)):
            return Point(np.abs(a.x), np.abs(a.y), np.abs(a.z))
        else:
            return Point(abs(a.x), abs(a.y), abs(a.z))
    elif isinstance(a, Normal):
        if (isinstance(a.x, np.ndarray)):
            return Normal(np.abs(a.x), np.abs(a.y), np.abs(a.z))
        else:
            return Normal(abs(a.x), abs(a.y), abs(a.z))
    else:
        raise ValueError('Only a Vector, a Point or a Normal parameter is accepted')


def permute(a, ix=None, iy=None, iz=None):
    """
    Permutes the vector(s)/point(s)/normal(s) x, y, z values according to the given indices

    Parameters
    ----------
    a : Vector | Point | Normal
        The vector(s), point(s) or normal(s) used for permutation
    ix : int | np.ndarray | list, optional
        The index/indices of the value(s) we want to keep as a remplacement for the x component(s)
    iy : int | np.ndarray | list, optional
        The index/indices of the value(s) we want to keep as a remplacement for the y component(s)
    iz : int | np.ndarray | list, optional
        The index/indices of the value(s) we want to keep as a remplacement for the z component(s)
    
    Returns
    -------
    out : Vector | Point | Normal
        The vector(s)/point(s)/normal(s) after the permute operation

    Examples
    --------
    >>> import geoclide as gc
    >>> v1 = gc.Vector(2., 3., 1.)
    >>> gc.permute(v1, 1, 0, 2)
    Vector(3.0, 2.0, 1.0)
    >>> gc.permute(v1, 1, 0, 2])
    Vector(3.0, 2.0, 1.0)
    >>> p_set = np.array([[0.,0.,3.], [1.,0.,0.], [-0.5,0.,0.], [0.,-3.,0.]])
    >>> p_set = gc.Point(p_set)
    >>> gc.permute(p_set, [2,0,0,1], 1, 2).to_numpy()
    array([[ 3. ,  0. ,  3. ],
           [ 1. ,  0. ,  0. ],
           [-0.5,  0. ,  0. ],
           [ 0. , -3. ,  0. ]])
    """
    if not(isinstance(a, Vector) or isinstance(a, Point) or isinstance(a, Normal)):
        raise NameError('The parameter a must be a Vector or Point or Normal')
    if ix is None : ix = int(0)
    if iy is None : iy = int(1)
    if iz is None : iz = int(2)

    if ( isinstance(ix, np.ndarray) or isinstance(ix, list) or
         isinstance(iy, np.ndarray) or isinstance(iy, list) or
         isinstance(iz, np.ndarray) or isinstance(iy, list)):
        a_arr = a.to_numpy()
    if ( isinstance(ix, np.ndarray) or isinstance(ix, list) ): ax = a_arr[np.arange(len(ix)), ix]
    else: ax=a[ix]
    if ( isinstance(iy, np.ndarray) or isinstance(iy, list) ): ay = a_arr[np.arange(len(iy)), iy]
    else: ay=a[iy]
    if ( isinstance(iz, np.ndarray) or isinstance(iz, list) ): az = a_arr[np.arange(len(iz)), iz]
    else: az=a[iz]
    return a.__class__(ax, ay, az)

