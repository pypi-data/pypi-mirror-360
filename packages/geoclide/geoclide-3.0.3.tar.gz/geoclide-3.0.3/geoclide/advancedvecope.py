#!/usr/bin/env python
# -*- coding: utf-8 -*-

from geoclide.basic import Vector
from geoclide.vecope import normalize
from geoclide.transform import get_rotateY_tf, get_rotateZ_tf
from geoclide.mathope import clamp
import numpy as np
import math
from warnings import warn

# TODO add ds_output option
def ang2vec(theta, phi, vec_view='zenith', diag_calc=False):
    """
    Convert a direction/directions described by 2 angles/set of 2 angles into a 
    direction/directions described by a vector/vectors

    - direct orthogonal coordinate system where z is pointing upwards

    Parameters
    ----------
    theta : float | 1D array
        The polar angle(s) in degrees, starting at z+ in the zx plane and going 
        in the trigonometric direction around the y axis

    phi : float | 1D array
        The azimuthal angle(s) in degrees, starting at x+ in the xy plane and going in 
        the trigonométric direction around the z axis

    vec_view : str, optional
        Two choices (concerning intial direction at theta=phi=0): 'zenith' (i.e. pointing above) or 
        'bellow' (i.e. pointing bellow)
    diag_calc : bool, optional
            Perform diagonal calculations, v(i) is calculated using theta(i) and phi(i)

    Returns
    -------
    v : Vector
        The direction(s) described by a vector

    Notes
    -----
    In case both theta and phi are 1-D ndarrays, the vectors are ordered in phi-major order

    Examples
    --------
    >>> import geoclide as gc
    >>> th = 30.
    >>> ph = 0.
    >>> v1 = gc.ang2vec(theta=th, phi=ph, vec_view='zenith')
    >>> v1
    Vector(0.49999999999999994, 0.0, 0.8660254037844387)
    >>> v2 = gc.ang2vec(theta=th, phi=ph, vec_view='nadir')
    >>> v2
    Vector(-0.49999999999999994, 0.0, -0.8660254037844387)
    """
    if (vec_view == "zenith"): # initial vector is facing zenith (pointing above)
        v = Vector(0., 0., 1.)
    elif (vec_view == "nadir"): # initial vector is facing nadir (pointing bellow)
        v = Vector(0., 0., -1.)
    else:
        raise ValueError("The value of vec_view parameter must be: 'zenith' or 'nadir")
    
    if isinstance(theta, np.ndarray) or isinstance(phi, np.ndarray): flatten = True
    else : flatten = False

    v = get_rotateY_tf(theta)(v, flatten=flatten)
    v = get_rotateZ_tf(phi)(v, flatten=flatten, diag_calc=diag_calc)
    v = normalize(v)
    
    return v


def vec2ang(v, vec_view='zenith', acc=1e-6):
    """
    Convert a direction/directions described by a vector/vectors into 
    a direction/directions described by 2 angles/set of 2 angles

    - direct orthogonal coordinate system where z is pointing upwards

    Parameters
    ----------
    v : Vector
        The direction(s) described by a vector
    vec_view : str, optional
        Two choices (concerning intial direction at theta=phi=0): 'zenith' (i.e. pointing above) or 
        'nadir' (i.e. pointing bellow)
    acc : float, optional
        The tolerance for numerical errors. Default is 1e-6.

    Returns
    -------
    theta : float | 1-D ndarray
        The polar angle(s) in degrees, starting at z+ in the zx plane and going 
        in the trigonometric direction around the y axis
    phi : float | 1-D ndarray
        The azimuthal angle(s) in degrees, starting at x+ in the xy plane and going in 
        the trigonométric direction around the z axis

    Examples
    --------
    >>> import geoclide as gc
    >>> th = 30.
    >>> ph = 0.
    >>> v1 = gc.ang2vec(theta=th, phi=ph, vec_view='zenith')
    >>> v1
    Vector(0.49999999999999994, 0.0, 0.8660254037844387)
    >>> theta, phi = gc.vec2ang(v1, vec_view='zenith')
    >>> theta, phi
    (29.999999999999993, 0.0)
    >>> v2 = gc.ang2vec(theta=th, phi=ph, vec_view='nadir')
    >>> v2
    Vector(-0.49999999999999994, 0.0, -0.8660254037844387)
    >>> theta, phi = gc.vec2ang(v1, vec_view='nadir')
    >>> theta, phi
    (29.999999999999993, 0.0)
    """
    if (not isinstance(v, Vector)):
        raise ValueError('The parameter v must be a vector')
    
    if (vec_view == "zenith"): # initial vector is facing zenith (pointing above)
        pass
    elif (vec_view == "nadir"): # initial vector is facing nadir (pointing bellow)
        v = -v # by doing that, we can keep a v_ini facing upwards
    else:
        raise ValueError("The value of vec_view parameter must be: 'zenith' or 'nadir")
    
    v = normalize(v) # ensure v is normalized

    if isinstance(v.x, np.ndarray):
        nv = len(v.x)
        v_arr = v.to_numpy()
        v_ini_arr = np.zeros_like(v_arr)
        v_ini_arr[:,2] = 1.
        v_ini = Vector(v_ini_arr)
        theta = np.full(nv, np.nan, dtype=np.float64)
        phi = theta.copy()
        
        c1 = np.all(np.isclose(v_arr, v_ini_arr, 0., acc), axis=1)
        not_resolved = np.logical_not(c1)
        if not_resolved.sum() == 0 : return theta, phi

        for icase in range (1, 6):
            if icase == 1:
                roty_rad = np.arccos(v.z)
                c_case_bis = np.logical_not(np.logical_and(v.x == 0, roty_rad == 0))
                cosphi = np.zeros(nv, dtype=np.float64)
                cosphi[c_case_bis] =  np.clip(v.x[c_case_bis]/np.sin(roty_rad[c_case_bis]), -1., 1.)
                rotz_rad = np.arccos(cosphi)
                theta_bis = np.degrees(roty_rad)
                phi_bis = np.degrees(rotz_rad)
            elif icase == 2:
                rotz_rad = -np.arccos(cosphi)
                phi_bis = np.degrees(rotz_rad)
            elif icase == 3:
                roty_rad = -np.arccos(v.z)
                cosphi = np.zeros(nv, dtype=np.float64)
                cosphi[c_case_bis] =  np.clip(v.x[c_case_bis]/np.sin(roty_rad[c_case_bis]), -1., 1.)
                rotz_rad = np.arccos(cosphi)
                theta_bis = np.degrees(roty_rad)
                phi_bis = np.degrees(rotz_rad)
            elif icase == 4:
                rotz_rad = -np.arccos(cosphi)
                phi_bis = np.degrees(rotz_rad)
            else:
                warn('No rotation has been found for some (or all) vectors!', Warning)
                return theta, phi

            rotzy = get_rotateZ_tf(phi_bis)*get_rotateY_tf(theta_bis)
            v_ini_rotated = normalize(rotzy(v_ini, flatten=True, diag_calc=True))
            c_tmp = np.all(np.isclose(v_arr, v_ini_rotated.to_numpy(), 0., acc), axis=1)
            c_tmp_bis = np.logical_and(not_resolved, c_tmp)
            theta[c_tmp_bis] = theta_bis[c_tmp_bis]
            phi[c_tmp_bis] = phi_bis[c_tmp_bis]
            not_resolved = np.logical_and(not_resolved, np.logical_not(c_tmp))
            if not_resolved.sum() == 0 : return theta, phi
    else: # if only 1 vector
        v_ini = Vector(0., 0., 1.)

        # In case v = v_ini -> no rotations
        if (np.all(np.isclose(v.to_numpy()-v_ini.to_numpy(), 0., 0., acc))):
            return 0., 0.
        
        for icase in range (1, 6):
            if icase == 1:
                roty_rad = math.acos(v.z)
                if (v.x == 0 and roty_rad == 0): cosphi = 0.
                else: cosphi = clamp(v.x/math.sin(roty_rad), -1., 1.)
                rotz_rad = math.acos(cosphi)
            elif(icase == 2):
                roty_rad = math.acos(v.z)
                if (v.x == 0 and roty_rad == 0): cosphi = 0.
                else: cosphi = clamp(v.x/math.sin(roty_rad), -1., 1.)
                rotz_rad = -math.acos(cosphi)
            elif(icase == 3):
                roty_rad = -math.acos(v.z)
                if (v.x == 0 and roty_rad == 0): cosphi = 0.
                else: cosphi = clamp(v.x/math.sin(roty_rad), -1., 1.)
                rotz_rad = math.acos(cosphi)
            elif(icase == 4):
                roty_rad = -math.acos(v.z)
                if (v.x == 0 and roty_rad == 0): cosphi = 0.
                else: cosphi = clamp(v.x/math.sin(roty_rad), -1., 1.)
                rotz_rad = -math.acos(cosphi)
            else:
                raise NameError('No rotation has been found!')
            
            theta = math.degrees(roty_rad)
            phi = math.degrees(rotz_rad)
            rotzy = get_rotateZ_tf(phi)*get_rotateY_tf(theta)
            v_ini_rotated = normalize(rotzy(v_ini))

            if (np.all(np.isclose(v.to_numpy()-v_ini_rotated.to_numpy(), 0., 0., acc))):
                break
        
        return theta, phi
