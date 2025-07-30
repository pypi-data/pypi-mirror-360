#!/usr/bin/env python
# -*- coding: utf-8 -*-

from geoclide.shapes import Shape, get_intersect_dataset
from geoclide.basic import Vector, Point, Ray
import geoclide.vecope as gv
import numpy as np
from geoclide.constante import GAMMA2_F64, GAMMA3_F64, GAMMA5_F64, VERSION
from geoclide.transform import Transform
import math
import matplotlib.pyplot as plt
import xarray as xr
from datetime import datetime
import trimesh


class Triangle(Shape):
    '''
    Creation of the class Triangle

    Parameters
    ----------
    p0 : Point
        The first point(s) of the triangle(s)
    p1 : Point
        The second point(s) of the triangle(s)
    p2 : Point
        The the third point(s) of the triangle(s)
    oTw : Transform, optional
        From object to world space or the transformation applied to the triangle
    wTo : Transform, optional
        From world to object space or the in inverse transformation applied to the triangle
    p0t : Point, optional
        If given circumvent the automatically computed p0t (p0 after applying transformation)
    p1t : Point, optional
        If given circumvent the automatically computed p1t (p1 after applying transformation)
    p2t : Point, optional
        If given circumvent the automatically computed p2t (p2 after applying transformation)
    '''
    def __init__(self, p0=None, p1=None, p2=None, oTw=None, wTo=None,
                 p0t=None, p1t=None, p2t=None):
        # Manage None cases
        if p0 is None : p0 = Point()
        if p1 is None : p1 = Point()
        if p2 is None : p2 = Point()
        if oTw is None and wTo is None:
            oTw = Transform()
            wTo = Transform()
            self.p0t = p0
            self.p1t = p1
            self.p2t = p2
        elif ( (oTw is None or isinstance(oTw, Transform)) and
               (wTo is None or isinstance(wTo, Transform)) ):
            if (oTw is None): oTw = wTo.inverse() # if oTw is None then wTo should be Transform
            if (wTo is None): wTo = oTw.inverse() # if wTo is None then oTw should be Transform
            if (p0t is None): self.p0t = oTw(p0)
            if (p1t is None): self.p1t = oTw(p1)
            if (p2t is None): self.p2t = oTw(p2)

        if (not isinstance(p0, Point) or not isinstance(p1, Point) or not isinstance(p2, Point)):
            raise ValueError('The parameters p0, p1 and p2 must be all Point')
        if ( (p0t is not None and not isinstance(p0t, Point)) or
             (p1t is not None and not isinstance(p1t, Point)) or
             (p2t is not None and not isinstance(p2t, Point)) ):
            raise ValueError('The parameters p0t, p1t and p2t must be all Point')
        Shape.__init__(self, ObjectToWorld = oTw, WorldToObject = wTo)
        self.p0 = p0
        self.p1 = p1
        self.p2 = p2
        if (p0t is not None): self.p0t = p0t
        if (p1t is not None): self.p1t = p1t
        if (p2t is not None): self.p2t = p2t

    def is_intersection(self, r, method='v3', diag_calc=False):
        """
        Test if a ray/set of rays intersect with the triangle(s)

        Parameters
        ----------
        r : Ray
            The ray(s) to use for the intersection test(s)
        method : str, optional
            Tow choice -> 'v2' (use mainly pbrt v2 intersection test method) or 'v3' (pbrt v3)
        diag_calc : bool, optional
            Perform diagonal calculations in case Triangle and Ray have ndarray point components, 
            meaning the output is a 1-D array instead of a 2-D array where out[i] is calculated using 
            r(i) and triangle(i). The same size for the Triangle and the Ray is required.

        Returns
        -------
        out : bool | 1-D ndarray | 2-D ndarray
            If there is an intersection -> True, else False
        """
        if method == 'v3':
            return self.is_intersection_v3(r, diag_calc=diag_calc)
        elif method == 'v2':
            return self.is_intersection_v2(r, diag_calc=diag_calc)
        else:
            raise ValueError("Only 'v2' and 'v3' are valid values for method parameter")
    
    def is_intersection_t(self, r, method='v3', diag_calc=False):
        """
        Test if a ray/set of rays intersect with the triangle(s)

        Parameters
        ----------
        r : Ray
            The ray(s) to use for the intersection test(s)
        method : str, optional
            Tow choice -> 'v2' (use mainly pbrt v2 intersection test method) or 'v3' (pbrt v3)
        diag_calc : bool, optional
            Perform diagonal calculations in case Triangle and Ray have ndarray point components, 
            meaning the output is a 1-D array instead of a 2-D array where out[i] is calculated using 
            r(i) and triangle(i). The same size for the Triangle and the Ray is required.

        Returns
        -------
        thit : None | float | 1-D ndarray | 2-D ndarray
            The t ray variable(s) for its first intersection at the shape surface
        is_intersection : bool | 1-D ndarray | 2-D ndarray
            If there is an intersection -> True, else False
        """
        if method == 'v3':
            return self.is_intersection_v3_t(r, diag_calc=diag_calc)
        elif method == 'v2':
            return self.is_intersection_v2_t(r, diag_calc=diag_calc)
        else:
            raise ValueError("Only 'v2' and 'v3' are valid values for method parameter")   

    def is_intersection_v2_t(self, r, diag_calc=False):
        """
        :meta private:

        Test if a ray/set of rays intersect with the triangle(s) using mainly pbrt v2 method

        Parameters
        ----------
        r : Ray
            The ray(s) to use for the intersection test(s)
        diag_calc : bool, optional
            Perform diagonal calculations in case Triangle and Ray have ndarray point components, 
            meaning the output is a 1-D array instead of a 2-D array where out[i] is calculated using 
            r(i) and triangle(i). The same size for the Triangle and the Ray is required.
        
        Returns
        -------
        thit : None | float | 1-D ndarray | 2-D ndarray
            The t ray variable(s) for its first intersection at the shape surface
        is_intersection : bool | 1-D ndarray | 2-D ndarray
            If there is an intersection -> True, else False
        """
        if not isinstance(r, Ray): raise ValueError('The given parameter must be a Ray')
        is_r_arr = isinstance(r.o.x, np.ndarray)
        is_p_arr = isinstance(self.p0.x, np.ndarray)

        if (is_p_arr and is_r_arr and not diag_calc):
            # TODO remove the loop in one of the next release
            with np.errstate(divide='ignore', invalid='ignore'):
                nrays = len(r.o.x)
                ntriangles = len(self.p0.x)
                is_intersection_2d = np.full((ntriangles, nrays), True, dtype=bool)
                t_2d = np.zeros((ntriangles, nrays), dtype=np.float64)

                if ntriangles >= nrays:
                    r_o_arr = r.o.to_numpy()
                    r_d_arr = r.d.to_numpy()
                    rmint = np.zeros(nrays, dtype=np.float64)
                    rmaxt = np.zeros_like(rmint)
                    rmint[:] = r.mint
                    rmaxt[:] = r.maxt

                    p0 = self.p0t
                    p1 = self.p1t
                    p2 = self.p2t
                    e1 = p1 - p0
                    e2 = p2 - p0

                    for ir in range (0, nrays):
                        ray = Ray(Point(r_o_arr[ir,:]), Vector(r_d_arr[ir,:]), rmint[ir], rmaxt[ir])

                        s1 = gv.cross(ray.d, e2)
                        divisor = gv.dot(s1, e1)

                        is_intersection = np.full(ntriangles, True, dtype=bool)
                        c1 = divisor == 0
                        invDivisor = 1./divisor

                        # compute the first barycentric coordinate
                        s = ray.o - p0
                        b1 = gv.dot(s, s1) * invDivisor
                        c2 = np.logical_or(b1 < -0.00000001, b1 > 1.00000001)

                        # compute the second barycentric coordinate
                        s2 = gv.cross(s, e1)
                        b2 = gv.dot(ray.d, s2) * invDivisor
                        c3 = np.logical_or(b2 < 0, b1+b2 > 1)

                        # compute the time at the intersection point
                        t = gv.dot(e2, s2) * invDivisor
                        c4 = np.logical_or(t < ray.mint, t > ray.maxt)

                        c5 = np.logical_or.reduce((c1, c2, c3, c4))
                        is_intersection[c5] = False
                        t[c5] = None
                        is_intersection_2d[:,ir] = is_intersection
                        t_2d[:,ir] = t

                    return t_2d, is_intersection_2d
                else: # nrays > npoints
                    ray = Ray(r)
                    p0t_arr = self.p0t.to_numpy()
                    p1t_arr = self.p1t.to_numpy()
                    p2t_arr = self.p2t.to_numpy()

                    for itri in range (0, ntriangles):
                        p0 = Point(p0t_arr[itri,:])
                        p1 = Point(p1t_arr[itri,:])
                        p2 = Point(p2t_arr[itri,:])

                        e1 = p1 - p0
                        e2 = p2 - p0
                        s1 = gv.cross(ray.d, e2)
                        divisor = gv.dot(s1, e1)
                        is_intersection = np.full(nrays, True, dtype=bool)
                        c1 = divisor == 0
                        invDivisor = 1./divisor

                        # compute the first barycentric coordinate
                        s = ray.o - p0
                        b1 = gv.dot(s, s1) * invDivisor
                        c2 = np.logical_or(b1 < -0.00000001, b1 > 1.00000001)

                        # compute the second barycentric coordinate
                        s2 = gv.cross(s, e1)
                        b2 = gv.dot(ray.d, s2) * invDivisor
                        c3 = np.logical_or(b2 < 0, b1+b2 > 1)

                        # compute the time at the intersection point
                        t = gv.dot(e2, s2) * invDivisor
                        c4 = np.logical_or(t < ray.mint, t > ray.maxt)

                        c5 = np.logical_or.reduce((c1, c2, c3, c4))
                        is_intersection[c5] = False
                        t[c5] = None
                        is_intersection_2d[itri,:] = is_intersection
                        t_2d[itri,:] = t
                            
                    return t_2d, is_intersection_2d
        else: # Case 2-D diag, 1-D or scalar
            ray = Ray(r)
            p0 = self.p0t
            p1 = self.p1t
            p2 = self.p2t
            e1 = p1 - p0
            e2 = p2 - p0
            s1 = gv.cross(ray.d, e2)
            divisor = gv.dot(s1, e1)
            if (is_p_arr or is_r_arr):
                with np.errstate(divide='ignore', invalid='ignore'):
                    if is_p_arr: size = len(p0.x)
                    else: size = len(r.o.x)
                    is_intersection = np.full(size, True)

                    c1 = divisor == 0
                    invDivisor = 1./divisor

                    # compute the first barycentric coordinate
                    s = ray.o - p0
                    b1 = gv.dot(s, s1) * invDivisor
                    c2 = np.logical_or(b1 < -0.00000001, b1 > 1.00000001)

                    # compute the second barycentric coordinate
                    s2 = gv.cross(s, e1)
                    b2 = gv.dot(ray.d, s2) * invDivisor
                    c3 = np.logical_or(b2 < 0, b1+b2 > 1)

                    # compute the time at the intersection point
                    t = gv.dot(e2, s2) * invDivisor
                    c4 = np.logical_or(t < ray.mint, t > ray.maxt)

                    c5 = np.logical_or.reduce((c1, c2, c3, c4))
                    is_intersection[c5] = False
                    t[c5] = None
            else:
                if (divisor == 0): return None, False
                invDivisor = 1./divisor

                # compute the first barycentric coordinate
                s = ray.o - p0
                b1 = gv.dot(s, s1) * invDivisor
                if (b1 < -0.00000001 or  b1 > 1.00000001):
                    return None, False

                # compute the second barycentric coordinate
                s2 = gv.cross(s, e1)
                b2 = gv.dot(ray.d, s2) * invDivisor
                if (b2 < 0 or  b1+b2 > 1):
                    return None, False

                # compute the time at the intersection point
                t = gv.dot(e2, s2) * invDivisor
                if (t < ray.mint or t > ray.maxt):
                    return None, False
                
                is_intersection = True

            return t, is_intersection
    
    def is_intersection_v2(self, r, diag_calc=False):
        """
        :meta private:

        Test if a ray/set of rays intersect with the triangle(s) using mainly pbrt v2 method

        Parameters
        ----------
        r : Ray
            The ray(s) to use for the intersection test(s)
        diag_calc : bool, optional
            Perform diagonal calculations in case Triangle and Ray have ndarray point components, 
            meaning the output is a 1-D array instead of a 2-D array where out[i] is calculated using 
            r(i) and triangle(i). The same size for the Triangle and the Ray is required.
        
        Returns
        -------
        out : bool | 1-D ndarray | 2-D ndarray
            If there is an intersection -> True, else False
        """
        _, is_intersection = self.is_intersection_v2_t(r, diag_calc=diag_calc)
        return is_intersection
    
    def is_intersection_v3_t(self, r, diag_calc=False):
        """
        :meta private:

        Test if a ray/set of rays intersect with the triangle(s) using mainly pbrt v3 method

        Parameters
        ----------
        r : Ray
            The ray(s) to use for the intersection test(s)
        diag_calc : bool, optional
            Perform diagonal calculations in case Triangle and Ray have ndarray point components, 
            meaning the output is a 1-D array instead of a 2-D array where out[i] is calculated using 
            r(i) and triangle(i). The same size for the Triangle and the Ray is required.
        
        Returns
        -------
        thit : None | float | 1-D ndarray | 2-D ndarray
            The t ray variable(s) for its first intersection at the shape surface
        is_intersection : bool | 1-D ndarray | 2-D ndarray
            If there is an intersection -> True, else False
        """
        if not isinstance(r, Ray): raise ValueError('The given parameter must be a Ray')
        is_r_arr = isinstance(r.o.x, np.ndarray)
        is_p_arr = isinstance(self.p0.x, np.ndarray)

        if (is_p_arr and is_r_arr and not diag_calc):
            # TODO remove the loop in one of the next release
            with np.errstate(divide='ignore', invalid='ignore'):
                nrays = len(r.o.x)
                ntriangles = len(self.p0.x)
                is_intersection_2d = np.full((ntriangles, nrays), True, dtype=bool)
                t_2d = np.zeros((ntriangles, nrays), dtype=np.float64)

                if ntriangles >= nrays:
                    r_o_arr = r.o.to_numpy()
                    r_d_arr = r.d.to_numpy()
                    rmint = np.zeros(nrays, dtype=np.float64)
                    rmaxt = np.zeros_like(rmint)
                    rmint[:] = r.mint
                    rmaxt[:] = r.maxt

                    p0 = self.p0t
                    p1 = self.p1t
                    p2 = self.p2t

                    # Compute triangle partial derivatives
                    # Below the z components is not needed since we are in 2D with u in x and v un y
                    dpdu = Vector()
                    dpdv = Vector()
                    uv0 = Point(0., 0., 0.)
                    uv1 = Point(1., 0., 0.)
                    uv2 = Point(1., 1., 0.)
                    duv02 = uv0 - uv2
                    duv12 = uv1 - uv2

                    dp02 = p0 - p2
                    dp12 = p1 - p2
                    determinant = duv02.x*duv12.y - duv02.y*duv12.x
                    degenerate = bool(abs(determinant) < 1e-8)

                    if (not degenerate):
                        invdet = 1./ determinant
                        dpdu = (duv12.y*dp02 - duv02.y*dp12)*invdet
                        dpdv = (-duv12.x*dp02 + duv02.x*dp12)*invdet
                    
                    ng = gv.cross(p2-p0, p1-p0)
                    c5_bis_1 = np.logical_or(degenerate, gv.cross(dpdu, dpdv).length_squared() == 0)
                    c5_bis_2 = ng.length_squared() == 0
                    c5 = np.logical_and(c5_bis_1, c5_bis_2)

                    dpdu_bis, dpdv_bis = gv.coordinate_system(gv.normalize(ng))
                    c7 = np.logical_and(c5_bis_1, np.logical_not(c5_bis_2))
                    if np.any(c7):
                        dpdu[c7] = dpdu_bis[c7]
                        dpdv[c7] = dpdv_bis[c7]

                    for ir in range (0, nrays):
                        ray = Ray(Point(r_o_arr[ir,:]), Vector(r_d_arr[ir,:]), rmint[ir], rmaxt[ir])
                        # Get triangle vertices and translate them in based on ray origin
                        p0t = p0 - ray.o
                        p1t = p1 - ray.o
                        p2t = p2 - ray.o
                        is_intersection = np.full(ntriangles, True, dtype=bool)

                        kz = gv.vargmax(gv.vabs(ray.d))
                        kx = kz + 1
                        if(kx == 3): kx = 0
                        ky = kx + 1
                        if(ky == 3): ky = 0

                        d = gv.permute(ray.d, kx, ky, kz)
                        p0t = gv.permute(p0t, kx, ky, kz)
                        p1t = gv.permute(p1t, kx, ky, kz)
                        p2t = gv.permute(p2t, kx, ky, kz)

                        sx = -d.x/d.z
                        sy = -d.y/d.z
                        sz = 1./d.z
                        p0t.x += sx*p0t.z
                        p0t.y += sy*p0t.z
                        p1t.x += sx*p1t.z
                        p1t.y += sy*p1t.z
                        p2t.x += sx*p2t.z
                        p2t.y += sy*p2t.z

                        # Compute edge function coefficients
                        e0 = (p1t.x * p2t.y) - (p1t.y * p2t.x)
                        e1 = (p2t.x * p0t.y) - (p2t.y * p0t.x)
                        e2 = (p0t.x * p1t.y) - (p0t.y * p1t.x)

                        # Perform triangle edge and determinant tests
                        c1 = np.logical_and(np.logical_or.reduce((e0<0, e1<0, e2<0)),
                                            np.logical_or.reduce((e0>0, e1>0, e2>0)))
                        
                        det = e0 + e1 + e2
                        c2 = det == 0

                        p0t.z *=  sz
                        p1t.z *=  sz
                        p2t.z *=  sz

                        tScaled = e0*p0t.z + e1*p1t.z + e2*p2t.z

                        c3_bis_1 = np.logical_and(det < 0, np.logical_or(tScaled >= 0, tScaled < r.maxt*det))
                        c3_bis_2 = np.logical_and(det > 0, np.logical_or(tScaled <= 0, tScaled > r.maxt*det))
                        c3 = np.logical_or(c3_bis_1, c3_bis_2)

                        # Compute barycentric coordinates and t value for triangle intersection
                        invDet = 1./det
                        t = tScaled * invDet
                        
                        # Ensure that computed triangle t is conservatively greater than zero
                        maxZt = np.max(np.abs(np.array([p0t.z, p1t.z, p2t.z])), axis=0)
                        deltaZ = GAMMA3_F64 * maxZt
                        maxXt = np.max(np.abs(np.array([p0t.x, p1t.x, p2t.x])), axis=0)
                        maxYt = np.max(np.abs(np.array([p0t.y, p1t.y, p2t.y])), axis=0)
                        deltaX = GAMMA5_F64 * (maxXt + maxZt)
                        deltaY = GAMMA5_F64 * (maxYt + maxZt)
                        deltaE = 2 * (GAMMA2_F64 * maxXt * maxYt + deltaY * maxXt + deltaX * maxYt)
                        maxE = np.max(np.abs(np.array([e0, e1, e2])), axis=0)
                        deltaT = 3 * (GAMMA3_F64 * maxE * maxZt + deltaE * maxZt + deltaZ * maxE) * abs(invDet)
                        c4 = t <= deltaT
                        
                        c6 = np.logical_or.reduce((c1, c2, c3, c4, c5))
                        is_intersection[c6] = False
                        t[c6] = None
                        is_intersection_2d[:,ir] = is_intersection
                        t_2d[:,ir] = t

                    return t_2d, is_intersection_2d
                else: # nrays > ntriangles
                    p0t_arr = self.p0t.to_numpy()
                    p1t_arr = self.p1t.to_numpy()
                    p2t_arr = self.p2t.to_numpy()

                    dpdu = Vector()
                    dpdv = Vector()
                    uv0 = Point(0., 0., 0.)
                    uv1 = Point(1., 0., 0.)
                    uv2 = Point(1., 1., 0.)
                    duv02 = uv0 - uv2
                    duv12 = uv1 - uv2
                    determinant = duv02.x*duv12.y - duv02.y*duv12.x
                    degenerate = bool(abs(determinant) < 1e-8)

                    kz = gv.vargmax(gv.vabs(r.d))
                    kx = kz + 1
                    kx[kx == 3] = 0
                    ky = kx + 1
                    ky[ky == 3] = 0
                    d = gv.permute(r.d, kx, ky, kz)
                    sx = -d.x/d.z
                    sy = -d.y/d.z
                    sz = 1./d.z
                    
                    for itri in range (0, ntriangles):
                        p0 = Point(p0t_arr[itri,:])
                        p1 = Point(p1t_arr[itri,:])
                        p2 = Point(p2t_arr[itri,:])
                        is_intersection = np.full(nrays, True, dtype=bool)

                        # Get triangle vertices and translate them in based on ray origin
                        p0t = p0 - r.o
                        p1t = p1 - r.o
                        p2t = p2 - r.o

                        p0t = gv.permute(p0t, kx, ky, kz)
                        p1t = gv.permute(p1t, kx, ky, kz)
                        p2t = gv.permute(p2t, kx, ky, kz)

                        p0t.x += sx*p0t.z
                        p0t.y += sy*p0t.z
                        p1t.x += sx*p1t.z
                        p1t.y += sy*p1t.z
                        p2t.x += sx*p2t.z
                        p2t.y += sy*p2t.z

                        # Compute edge function coefficients
                        e0 = (p1t.x * p2t.y) - (p1t.y * p2t.x)
                        e1 = (p2t.x * p0t.y) - (p2t.y * p0t.x)
                        e2 = (p0t.x * p1t.y) - (p0t.y * p1t.x)

                        c1 = np.logical_and(np.logical_or.reduce((e0<0, e1<0, e2<0)),
                                            np.logical_or.reduce((e0>0, e1>0, e2>0)))

                        det = e0 + e1 + e2
                        c2 = det == 0

                        # Compute scaled hit distance to triangle and test against ray $t$ range
                        p0t.z *=  sz
                        p1t.z *=  sz
                        p2t.z *=  sz

                        tScaled = e0*p0t.z + e1*p1t.z + e2*p2t.z

                        c3_bis_1 = np.logical_and(det < 0, np.logical_or(tScaled >= 0, tScaled < r.maxt*det))
                        c3_bis_2 = np.logical_and(det > 0, np.logical_or(tScaled <= 0, tScaled > r.maxt*det))
                        c3 = np.logical_or(c3_bis_1, c3_bis_2)

                        # Compute barycentric coordinates and t value for triangle intersection
                        invDet = 1./det
                        t = tScaled * invDet
                        
                        # Ensure that computed triangle t is conservatively greater than zero
                        maxZt = np.max(np.abs(np.array([p0t.z, p1t.z, p2t.z])), axis=0)
                        deltaZ = GAMMA3_F64 * maxZt
                        maxXt = np.max(np.abs(np.array([p0t.x, p1t.x, p2t.x])), axis=0)
                        maxYt = np.max(np.abs(np.array([p0t.y, p1t.y, p2t.y])), axis=0)
                        deltaX = GAMMA5_F64 * (maxXt + maxZt)
                        deltaY = GAMMA5_F64 * (maxYt + maxZt)
                        deltaE = 2 * (GAMMA2_F64 * maxXt * maxYt + deltaY * maxXt + deltaX * maxYt)
                        maxE = np.max(np.abs(np.array([e0, e1, e2])), axis=0)
                        deltaT = 3 * (GAMMA3_F64 * maxE * maxZt + deltaE * maxZt + deltaZ * maxE) * abs(invDet)
                        c4 = t <= deltaT

                        # Compute triangle partial derivatives
                        # Below the z components is not needed since we are in 2D with u in x and v un y
                        dp02 = p0 - p2
                        dp12 = p1 - p2

                        if (not degenerate):
                            invdet = 1./ determinant
                            dpdu_bis = (duv12.y*dp02 - duv02.y*dp12)*invdet
                            dpdv_bis = (-duv12.x*dp02 + duv02.x*dp12)*invdet
                            
                        ng = gv.cross(p2-p0, p1-p0)
                        c5_bis_1 = degenerate or gv.cross(dpdu_bis, dpdv_bis).length_squared() == 0
                        c5_bis_2 = ng.length_squared() == 0
                        c5 = c5_bis_1 and c5_bis_2
                        c5_arr = np.full(nrays, c5, dtype=bool)
                        
                        c6 = np.logical_or.reduce((c1, c2, c3, c4, c5_arr))
                        is_intersection[c6] = False
                        t[c6] = None
                        is_intersection_2d[itri,:] = is_intersection
                        t_2d[itri,:] = t
                    return t_2d, is_intersection_2d
        else: # Case 2-D diag, 1-D or scalar
            p0 = self.p0t
            p1 = self.p1t
            p2 = self.p2t

            # Get triangle vertices and translate them in based on ray origin
            p0t = p0 - r.o
            p1t = p1 - r.o
            p2t = p2 - r.o

            kz = gv.vargmax(gv.vabs(r.d))
            kx = kz + 1
            if is_r_arr:
                kx[kx == 3] = 0
                ky = kx + 1
                ky[ky == 3] = 0
            else:
                if(kx == 3): kx = 0
                ky = kx + 1
                if(ky == 3): ky = 0

            d = gv.permute(r.d, kx, ky, kz)
            p0t = gv.permute(p0t, kx, ky, kz)
            p1t = gv.permute(p1t, kx, ky, kz)
            p2t = gv.permute(p2t, kx, ky, kz)
            
            sx = -d.x/d.z
            sy = -d.y/d.z
            sz = 1./d.z
            p0t.x += sx*p0t.z
            p0t.y += sy*p0t.z
            p1t.x += sx*p1t.z
            p1t.y += sy*p1t.z
            p2t.x += sx*p2t.z
            p2t.y += sy*p2t.z
            
            # Compute edge function coefficients
            e0 = (p1t.x * p2t.y) - (p1t.y * p2t.x)
            e1 = (p2t.x * p0t.y) - (p2t.y * p0t.x)
            e2 = (p0t.x * p1t.y) - (p0t.y * p1t.x)

            if is_p_arr or is_r_arr:
                with np.errstate(divide='ignore', invalid='ignore'):

                    if is_p_arr: size = len(p0.x)
                    if is_r_arr: size = len(r.o.x)
                    is_intersection = np.full(size, True, dtype=bool)
                    # Perform triangle edge and determinant tests
                    c1 = np.logical_and(np.logical_or.reduce((e0<0, e1<0, e2<0)),
                                        np.logical_or.reduce((e0>0, e1>0, e2>0)))
                    
                    det = e0 + e1 + e2
                    c2 = det == 0

                    # Compute scaled hit distance to triangle and test against ray $t$ range
                    p0t.z *=  sz
                    p1t.z *=  sz
                    p2t.z *=  sz

                    tScaled = e0*p0t.z + e1*p1t.z + e2*p2t.z

                    c3_bis_1 = np.logical_and(det < 0, np.logical_or(tScaled >= 0, tScaled < r.maxt*det))
                    c3_bis_2 = np.logical_and(det > 0, np.logical_or(tScaled <= 0, tScaled > r.maxt*det))
                    c3 = np.logical_or(c3_bis_1, c3_bis_2)

                    # Compute barycentric coordinates and t value for triangle intersection
                    invDet = 1./det
                    t = tScaled * invDet
                    
                    # Ensure that computed triangle t is conservatively greater than zero
                    maxZt = np.max(np.abs(np.array([p0t.z, p1t.z, p2t.z])))
                    deltaZ = GAMMA3_F64 * maxZt
                    maxXt = np.max(np.abs(np.array([p0t.x, p1t.x, p2t.x])))
                    maxYt = np.max(np.abs(np.array([p0t.y, p1t.y, p2t.y])))
                    deltaX = GAMMA5_F64 * (maxXt + maxZt)
                    deltaY = GAMMA5_F64 * (maxYt + maxZt)
                    deltaE = 2 * (GAMMA2_F64 * maxXt * maxYt + deltaY * maxXt + deltaX * maxYt)
                    maxE = np.max(np.abs(np.array([e0, e1, e2])))
                    deltaT = 3 * (GAMMA3_F64 * maxE * maxZt + deltaE * maxZt + deltaZ * maxE) * abs(invDet)
                    c4 = t <= deltaT

                    # Compute triangle partial derivatives
                    # Below the z components is not needed since we are in 2D with u in x and v un y
                    dpdu = Vector()
                    dpdv = Vector()
                    uv0 = Point(0., 0., 0.)
                    uv1 = Point(1., 0., 0.)
                    uv2 = Point(1., 1., 0.)
                    duv02 = uv0 - uv2
                    duv12 = uv1 - uv2
                    dp02 = p0 - p2
                    dp12 = p1 - p2
                    determinant = duv02.x*duv12.y - duv02.y*duv12.x
                    degenerate = bool(abs(determinant) < 1e-8)

                    if (not degenerate):
                        invdet = 1./ determinant
                        dpdu = (duv12.y*dp02 - duv02.y*dp12)*invdet
                        dpdv = (-duv12.x*dp02 + duv02.x*dp12)*invdet

                    ng = gv.cross(p2-p0, p1-p0)
                    c5_bis_1 = np.logical_or(degenerate, gv.cross(dpdu, dpdv).length_squared() == 0)
                    c5_bis_2 = ng.length_squared() == 0
                    c5 = np.logical_and(c5_bis_1, c5_bis_2)
                    if not isinstance(c5, np.ndarray): c5 = np.full(size, c5, dtype=bool)
                    
                    c6 = np.logical_or.reduce((c1, c2, c3, c4, c5))
                    is_intersection[c6] = False
                    t[c6] = None
                    
                    return t, is_intersection
            else:
                # Perform triangle edge and determinant tests
                if ((e0 < 0 or e1 < 0 or e2 < 0) and (e0 > 0 or e1 > 0 or e2 > 0)):
                    return None, False
                det = e0 + e1 + e2
                if (det == 0): return None, False

                # Compute scaled hit distance to triangle and test against ray $t$ range
                p0t.z *=  sz
                p1t.z *=  sz
                p2t.z *=  sz

                tScaled = e0*p0t.z + e1*p1t.z + e2*p2t.z

                if ( (det < 0 and (tScaled >= 0 or tScaled < r.maxt*det)) or
                    (det > 0 and (tScaled <= 0 or tScaled > r.maxt*det)) ):
                    return None, False

                # Compute barycentric coordinates and t value for triangle intersection
                invDet = 1./det
                t = tScaled * invDet
                
                # Ensure that computed triangle t is conservatively greater than zero
                maxZt = np.max(np.abs(np.array([p0t.z, p1t.z, p2t.z])))
                deltaZ = GAMMA3_F64 * maxZt
                maxXt = np.max(np.abs(np.array([p0t.x, p1t.x, p2t.x])))
                maxYt = np.max(np.abs(np.array([p0t.y, p1t.y, p2t.y])))
                deltaX = GAMMA5_F64 * (maxXt + maxZt)
                deltaY = GAMMA5_F64 * (maxYt + maxZt) 
                deltaE = 2 * (GAMMA2_F64 * maxXt * maxYt + deltaY * maxXt + deltaX * maxYt)
                maxE = np.max(np.abs(np.array([e0, e1, e2])))
                deltaT = 3 * (GAMMA3_F64 * maxE * maxZt + deltaE * maxZt + deltaZ * maxE) * abs(invDet)
                if (t <= deltaT): return None, False

                # Compute triangle partial derivatives
                # Below the z components is not needed since we are in 2D with u in x and v un y
                dpdu = Vector()
                dpdv = Vector()
                uv0 = Point(0., 0., 0.)
                uv1 = Point(1., 0., 0.)
                uv2 = Point(1., 1., 0.)
                duv02 = uv0 - uv2
                duv12 = uv1 - uv2
                dp02 = p0 - p2
                dp12 = p1 - p2
                determinant = duv02.x*duv12.y - duv02.y*duv12.x
                degenerate = bool(abs(determinant) < 1e-8)

                if (not degenerate):
                    invdet = 1./ determinant
                    dpdu = (duv12.y*dp02 - duv02.y*dp12)*invdet
                    dpdv = (-duv12.x*dp02 + duv02.x*dp12)*invdet

                if ( degenerate or gv.cross(dpdu, dpdv).length_squared() == 0):
                    ng = gv.cross(p2-p0, p1-p0)
                    if ( ng.length_squared() == 0 ): return None, False

                return t, True

    def is_intersection_v3(self, r, diag_calc):
        """
        :meta private:

        Test if a ray/set of rays intersect with the triangle(s) using mainly pbrt v3 method

        Parameters
        ----------
        r : Ray
            The ray(s) to use for the intersection test(s)
        diag_calc : bool, optional
            Perform diagonal calculations in case Triangle and Ray have ndarray point components, 
            meaning the output is a 1-D array instead of a 2-D array where out[i] is calculated using 
            r(i) and triangle(i). The same size for the Triangle and the Ray is required.
        
        Returns
        -------
        out : bool | 1-D ndarray | 2-D ndarray
            If there is an intersection -> True, else False
        """
        _, is_intersection = self.is_intersection_v3_t(r, diag_calc=diag_calc)
        return is_intersection

    def intersect(self, r, method='v3', diag_calc=False, ds_output=True):
        """
        Test if a ray/set of rays intersect with the triangle(s) and return intersection information

        Parameters
        ----------
        r : Ray
            The ray(s) to use for the intersection test(s)
        method : str, optional
            Tow choice -> 'v2' (use mainly pbrt v2 intersection test method) or 'v3' (pbrt v3)
        diag_calc : bool, optional
            Perform diagonal calculations in case Triangle and Ray have ndarray point components, 
            meaning the output is a 1-D array instead of a 2-D array where out[i] is calculated using 
            r(i) and triangle(i). The same size for the Triangle and the Ray is required.
        ds_output : Bool, optional
            If True the output is a dataset, else return a tuple with intersection information variables
        
        Returns
        -------
        out : xr.Dataset | tuple
            Look-up table with the intersection information if ds_output is True, 
            else return a tuple (ready to be an input for the function get_intersect_dataset in 
            geoclide/shapes.py). Form of the tuple:
            
            * shape_name : str
                -> The shape class name
            * r : Ray
                -> The ray(s) used for the intersection test
            * t : None | float | 1-D ndarray | 2-D ndarray
                -> The t ray variable(s) for its first intersection at the shape surface
            * is_intersection : bool | 1-D ndarray | 2-D ndarray
                -> If there is an intersection return True, else False
            * u : None | float | 1-D ndarray | 2-D ndarray
                -> The u coordinate(s) of the parametric representation
            * v : None | float | 1-D ndarray | 2-D ndarray
                -> The u coordinate(s) of the parametric representation
            * dpdu : None | 1-D ndarray | 2-D ndarray
                -> The surface partial derivative(s) of phit with respect to u
            * dpdv : None | 1-D ndarray | 2-D ndarray
                -> The surface partial derivative(s) of phit with respect to v
            * diag_cal : bool
                -> This indicates whether a diagonal calculation has been performed

        Notes
        -----
        By default the 'v3' method is used since there are more robustness tests.
        But the 'v2' method is at least twice faster than 'v3'.
        """
        if method == 'v3':
            return self.intersect_v3(r, diag_calc=diag_calc, ds_output=ds_output)
        elif method == 'v2':
            return self.intersect_v2(r, diag_calc=diag_calc, ds_output=ds_output)
        else:
            raise ValueError("Only 'v2' and 'v3' are valid values for method parameter")   
        
    def intersect_v2(self, r, diag_calc=False, ds_output=True):
        """
        :meta private:

        Test if a ray/set of rays intersect with the triangle(s) using mainly pbrt v2 method,
        and return intersection information
        
        Parameters
        ----------
        r : Ray
            The ray(s) to use for the intersection test(s)
        diag_calc : bool, optional
            Perform diagonal calculations in case Triangle and Ray have ndarray point components, 
            meaning the output is a 1-D array instead of a 2-D array where out[i] is calculated using 
            r(i) and triangle(i). The same size for the Triangle and the Ray is required.
        ds_output : Bool, optional
            If True the output is a dataset, else return a tuple with intersection information variables
        
        Returns
        -------
        out : xr.Dataset | tuple
            Look-up table with the intersection information if ds_output is True, 
            else return a tuple (ready to be an input for the function get_intersect_dataset in 
            geoclide/shapes.py). Form of the tuple:
            
            * shape_name : str
                -> The shape class name
            * r : Ray
                -> The ray(s) used for the intersection test
            * t : None | float | 1-D ndarray | 2-D ndarray
                -> The t ray variable(s) for its first intersection at the shape surface
            * is_intersection : bool | 1-D ndarray | 2-D ndarray
                -> If there is an intersection return True, else False
            * u : None | float | 1-D ndarray | 2-D ndarray
                -> The u coordinate(s) of the parametric representation
            * v : None | float | 1-D ndarray | 2-D ndarray
                -> The u coordinate(s) of the parametric representation
            * dpdu : None | 1-D ndarray | 2-D ndarray
                -> The surface partial derivative(s) of phit with respect to u
            * dpdv : None | 1-D ndarray | 2-D ndarray
                -> The surface partial derivative(s) of phit with respect to v
            * diag_cal : bool
                -> This indicates whether a diagonal calculation has been performed
        """
        if not isinstance(r, Ray): raise ValueError('The given parameter must be a Ray')
        is_r_arr = isinstance(r.o.x, np.ndarray)
        is_p_arr = isinstance(self.p0.x, np.ndarray)
        sh_name = self.__class__.__name__

        if (is_p_arr and is_r_arr and not diag_calc):
            # TODO remove the loop in one of the next release
            with np.errstate(divide='ignore', invalid='ignore'):
                nrays = len(r.o.x)
                ntriangles = len(self.p0.x)
                is_intersection_2d = np.full((ntriangles, nrays), True, dtype=bool)
                t_2d = np.zeros((ntriangles, nrays), dtype=np.float64)
                u_2d = np.zeros_like(t_2d)
                v_2d = np.zeros_like(t_2d)

                if ntriangles >= nrays:
                    r_o_arr = r.o.to_numpy()
                    r_d_arr = r.d.to_numpy()
                    rmint = np.zeros(nrays, dtype=np.float64)
                    rmaxt = np.zeros_like(rmint)
                    rmint[:] = r.mint
                    rmaxt[:] = r.maxt

                    p0 = self.p0t
                    p1 = self.p1t
                    p2 = self.p2t
                    e1 = p1 - p0
                    e2 = p2 - p0

                    # compute triangle partial derivatives
                    uvs = np.array([[0., 0.], [1., 0.], [1., 1.]])

                    # compute deltas for triangle partial derivatives
                    du1 = uvs[0][0] - uvs[2][0]
                    du2 = uvs[1][0] - uvs[2][0]
                    dv1 = uvs[0][1] - uvs[2][1]
                    dv2 = uvs[1][1] - uvs[2][1]
                    dp1 = p0 - p2
                    dp2 = p1 - p2
                    determinant = du1 * dv2 - dv1 * du2

                    if (determinant == 0):
                        dpdu, dpdv = gv.coordinate_system(gv.normalize(gv.cross(e2, e1)))
                    else:
                        invdet = 1./determinant
                        dpdu = ( dp1*dv2   - dp2*dv1) * invdet
                        dpdv = (dp1*(-du2) + dp2*du1) * invdet

                    for ir in range (0, nrays):
                        ray = Ray(Point(r_o_arr[ir,:]), Vector(r_d_arr[ir,:]), rmint[ir], rmaxt[ir])

                        s1 = gv.cross(ray.d, e2)
                        divisor = gv.dot(s1, e1)

                        is_intersection = np.full(ntriangles, True, dtype=bool)
                        c1 = divisor == 0
                        invDivisor = 1./divisor

                        # compute the first barycentric coordinate
                        s = ray.o - p0
                        b1 = gv.dot(s, s1) * invDivisor
                        c2 = np.logical_or(b1 < -0.00000001, b1 > 1.00000001)

                        # compute the second barycentric coordinate
                        s2 = gv.cross(s, e1)
                        b2 = gv.dot(ray.d, s2) * invDivisor
                        c3 = np.logical_or(b2 < 0, b1+b2 > 1)

                        # compute the time at the intersection point
                        t = gv.dot(e2, s2) * invDivisor
                        c4 = np.logical_or(t < ray.mint, t > ray.maxt)

                        c5 = np.logical_or.reduce((c1, c2, c3, c4))
                        is_intersection[c5] = False
                        t[c5] = None
                        is_intersection_2d[:,ir] = is_intersection
                        t_2d[:,ir] = t

                        # interpolate $(u,v)$ triangle parametric coordinates
                        b0 = 1 - b1 - b2
                        tu = b0*uvs[0][0] + b1*uvs[1][0] + b2*uvs[2][0]
                        tv = b0*uvs[0][1] + b1*uvs[1][1] + b2*uvs[2][1]
                        u_2d[:,ir] = tu
                        v_2d[:,ir] = tv

                    out = sh_name, r, t_2d, is_intersection_2d, u_2d, v_2d, dpdu.to_numpy(), \
                          dpdv.to_numpy(), diag_calc
                    if ds_output : return get_intersect_dataset(*out)
                    else : return out 
                else: # nrays > npoints
                    ray = Ray(r)
                    p0t_arr = self.p0t.to_numpy()
                    p1t_arr = self.p1t.to_numpy()
                    p2t_arr = self.p2t.to_numpy()

                    # compute triangle partial derivatives
                    uvs = np.array([[0., 0.], [1., 0.], [1., 1.]])

                    # compute deltas for triangle partial derivatives
                    du1 = uvs[0][0] - uvs[2][0]
                    du2 = uvs[1][0] - uvs[2][0]
                    dv1 = uvs[0][1] - uvs[2][1]
                    dv2 = uvs[1][1] - uvs[2][1]
                    dpdu = np.zeros((ntriangles, 3), dtype=np.float64)
                    dpdv = np.zeros((ntriangles, 3), dtype=np.float64)
                    for itri in range (0, ntriangles):
                        p0 = Point(p0t_arr[itri,:])
                        p1 = Point(p1t_arr[itri,:])
                        p2 = Point(p2t_arr[itri,:])

                        e1 = p1 - p0
                        e2 = p2 - p0
                        s1 = gv.cross(ray.d, e2)
                        divisor = gv.dot(s1, e1)
                        is_intersection = np.full(nrays, True, dtype=bool)
                        c1 = divisor == 0
                        invDivisor = 1./divisor

                        # compute the first barycentric coordinate
                        s = ray.o - p0
                        b1 = gv.dot(s, s1) * invDivisor
                        c2 = np.logical_or(b1 < -0.00000001, b1 > 1.00000001)

                        # compute the second barycentric coordinate
                        s2 = gv.cross(s, e1)
                        b2 = gv.dot(ray.d, s2) * invDivisor
                        c3 = np.logical_or(b2 < 0, b1+b2 > 1)

                        # compute the time at the intersection point
                        t = gv.dot(e2, s2) * invDivisor
                        c4 = np.logical_or(t < ray.mint, t > ray.maxt)

                        c5 = np.logical_or.reduce((c1, c2, c3, c4))
                        is_intersection[c5] = False
                        t[c5] = None
                        is_intersection_2d[itri,:] = is_intersection
                        t_2d[itri,:] = t

                        dp1 = p0 - p2
                        dp2 = p1 - p2
                        determinant = du1 * dv2 - dv1 * du2

                        if (determinant == 0):
                            dpdu_bis, dpdv_bis = gv.coordinate_system(gv.normalize(gv.cross(e2, e1)))
                        else:
                            invdet = 1./determinant
                            dpdu_bis = ( dp1*dv2   - dp2*dv1) * invdet
                            dpdv_bis = (dp1*(-du2) + dp2*du1) * invdet
                        dpdu[itri,:] = dpdu_bis.to_numpy()
                        dpdv[itri,:] = dpdv_bis.to_numpy()
                        
                        # interpolate $(u,v)$ triangle parametric coordinates
                        b0 = 1 - b1 - b2
                        tu = b0*uvs[0][0] + b1*uvs[1][0] + b2*uvs[2][0]
                        tv = b0*uvs[0][1] + b1*uvs[1][1] + b2*uvs[2][1]

                        u_2d[itri,:] = tu
                        v_2d[itri,:] = tv

                    out = sh_name, r, t_2d, is_intersection_2d, u_2d, v_2d, dpdu, dpdv, diag_calc
                    if ds_output : return get_intersect_dataset(*out)
                    else : return out 
        else: # Case 2-D diag, 1-D or scalar
            ray = Ray(r)
            p0 = self.p0t
            p1 = self.p1t
            p2 = self.p2t
            e1 = p1 - p0
            e2 = p2 - p0
            s1 = gv.cross(ray.d, e2)
            divisor = gv.dot(s1, e1)
            if (is_p_arr or is_r_arr):
                with np.errstate(divide='ignore', invalid='ignore'):
                    if is_p_arr: size = len(p0.x)
                    else: size = len(r.o.x)
                    is_intersection = np.full(size, True)

                    c1 = divisor == 0
                    invDivisor = 1./divisor

                    # compute the first barycentric coordinate
                    s = ray.o - p0
                    b1 = gv.dot(s, s1) * invDivisor
                    c2 = np.logical_or(b1 < -0.00000001, b1 > 1.00000001)

                    # compute the second barycentric coordinate
                    s2 = gv.cross(s, e1)
                    b2 = gv.dot(ray.d, s2) * invDivisor
                    c3 = np.logical_or(b2 < 0, b1+b2 > 1)

                    # compute the time at the intersection point
                    t = gv.dot(e2, s2) * invDivisor
                    c4 = np.logical_or(t < ray.mint, t > ray.maxt)

                    c5 = np.logical_or.reduce((c1, c2, c3, c4))
                    is_intersection[c5] = False
                    t[c5] = None
            else:
                if (divisor == 0):
                    if ds_output : return get_intersect_dataset(sh_name, r, None, False, None, None, None, None, False)
                    else : return sh_name, r, None, False, None, None, None, None, False
                invDivisor = 1./divisor

                # compute the first barycentric coordinate
                s = ray.o - p0
                b1 = gv.dot(s, s1) * invDivisor
                if (b1 < -0.00000001 or  b1 > 1.00000001):
                    if ds_output : return get_intersect_dataset(sh_name, r, None, False, None, None, None, None, False)
                    else : return sh_name, r, None, False, None, None, None, None, False

                # compute the second barycentric coordinate
                s2 = gv.cross(s, e1)
                b2 = gv.dot(ray.d, s2) * invDivisor
                if (b2 < 0 or  b1+b2 > 1):
                    if ds_output : return get_intersect_dataset(sh_name, r, None, False, None, None, None, None, False)
                    else : return sh_name, r, None, False, None, None, None, None, False

                # compute the time at the intersection point
                t = gv.dot(e2, s2) * invDivisor
                if (t < ray.mint or t > ray.maxt):
                    if ds_output : return get_intersect_dataset(sh_name, r, None, False, None, None, None, None, False)
                    else : return sh_name, r, None, False, None, None, None, None, False
                
                is_intersection = True

            # compute triangle partial derivatives
            uvs = np.array([[0., 0.], [1., 0.], [1., 1.]])

            # compute deltas for triangle partial derivatives
            du1 = uvs[0][0] - uvs[2][0]
            du2 = uvs[1][0] - uvs[2][0]
            dv1 = uvs[0][1] - uvs[2][1]
            dv2 = uvs[1][1] - uvs[2][1]
            dp1 = p0 - p2
            dp2 = p1 - p2
            determinant = du1 * dv2 - dv1 * du2

            with np.errstate(divide='ignore', invalid='ignore'):
                if (determinant == 0):
                    dpdu, dpdv = gv.coordinate_system(gv.normalize(gv.cross(e2, e1)))
                else:
                    invdet = 1./determinant
                    dpdu = ( dp1*dv2   - dp2*dv1) * invdet
                    dpdv = (dp1*(-du2) + dp2*du1) * invdet
                
                # interpolate $(u,v)$ triangle parametric coordinates
                b0 = 1 - b1 - b2
                tu = b0*uvs[0][0] + b1*uvs[1][0] + b2*uvs[2][0]
                tv = b0*uvs[0][1] + b1*uvs[1][1] + b2*uvs[2][1]

            out = sh_name, r, t, is_intersection, tu, tv, dpdu.to_numpy(), dpdv.to_numpy(), diag_calc
            if ds_output : return get_intersect_dataset(*out)
            else : return out 
    
    def intersect_v3(self, r, diag_calc=False, ds_output=True):
        """
        :meta private:
        
        Test if a ray/set of rays intersect with the triangle(s) using mainly pbrt v3 method,
        and return intersection information

        Parameters
        ----------
        r : Ray
            The ray(s) to use for the intersection test(s)
        diag_calc : bool, optional
            Perform diagonal calculations in case Triangle and Ray have ndarray point components, 
            meaning the output is a 1-D array instead of a 2-D array where out[i] is calculated using 
            r(i) and triangle(i). The same size for the Triangle and the Ray is required.
        ds_output : Bool, optional
            If True the output is a dataset, else return a tuple with intersection information variables
        
        Returns
        -------
        out : xr.Dataset | tuple
            Look-up table with the intersection information if ds_output is True, 
            else return a tuple (ready to be an input for the function get_intersect_dataset in 
            geoclide/shapes.py). Form of the tuple:
            
            * shape_name : str
                -> The shape class name
            * r : Ray
                -> The ray(s) used for the intersection test
            * t : None | float | 1-D ndarray | 2-D ndarray
                -> The t ray variable(s) for its first intersection at the shape surface
            * is_intersection : bool | 1-D ndarray | 2-D ndarray
                -> If there is an intersection return True, else False
            * u : None | float | 1-D ndarray | 2-D ndarray
                -> The u coordinate(s) of the parametric representation
            * v : None | float | 1-D ndarray | 2-D ndarray
                -> The u coordinate(s) of the parametric representation
            * dpdu : None | 1-D ndarray | 2-D ndarray
                -> The surface partial derivative(s) of phit with respect to u
            * dpdv : None | 1-D ndarray | 2-D ndarray
                -> The surface partial derivative(s) of phit with respect to v
            * diag_cal : bool
                -> This indicates whether a diagonal calculation has been performed
        """
        if not isinstance(r, Ray): raise ValueError('The given parameter must be a Ray')
        is_r_arr = isinstance(r.o.x, np.ndarray)
        is_p_arr = isinstance(self.p0.x, np.ndarray)
        sh_name = self.__class__.__name__

        if (is_p_arr and is_r_arr and not diag_calc):
            # TODO remove the loop in one of the next release
            with np.errstate(divide='ignore', invalid='ignore'):
                nrays = len(r.o.x)
                ntriangles = len(self.p0.x)
                is_intersection_2d = np.full((ntriangles, nrays), True, dtype=bool)
                t_2d = np.zeros((ntriangles, nrays), dtype=np.float64)
                u_2d = np.zeros_like(t_2d)
                v_2d = np.zeros_like(t_2d)

                if ntriangles >= nrays:
                    r_o_arr = r.o.to_numpy()
                    r_d_arr = r.d.to_numpy()
                    rmint = np.zeros(nrays, dtype=np.float64)
                    rmaxt = np.zeros_like(rmint)
                    rmint[:] = r.mint
                    rmaxt[:] = r.maxt

                    p0 = self.p0t
                    p1 = self.p1t
                    p2 = self.p2t

                    # Compute triangle partial derivatives
                    # Below the z components is not needed since we are in 2D with u in x and v un y
                    dpdu = Vector()
                    dpdv = Vector()
                    uv0 = Point(0., 0., 0.)
                    uv1 = Point(1., 0., 0.)
                    uv2 = Point(1., 1., 0.)
                    duv02 = uv0 - uv2
                    duv12 = uv1 - uv2

                    dp02 = p0 - p2
                    dp12 = p1 - p2
                    determinant = duv02.x*duv12.y - duv02.y*duv12.x
                    degenerate = bool(abs(determinant) < 1e-8)

                    if (not degenerate):
                        invdet = 1./ determinant
                        dpdu = (duv12.y*dp02 - duv02.y*dp12)*invdet
                        dpdv = (-duv12.x*dp02 + duv02.x*dp12)*invdet
                    
                    ng = gv.cross(p2-p0, p1-p0)
                    c5_bis_1 = np.logical_or(degenerate, gv.cross(dpdu, dpdv).length_squared() == 0)
                    c5_bis_2 = ng.length_squared() == 0
                    c5 = np.logical_and(c5_bis_1, c5_bis_2)

                    dpdu_bis, dpdv_bis = gv.coordinate_system(gv.normalize(ng))
                    c7 = np.logical_and(c5_bis_1, np.logical_not(c5_bis_2))
                    if np.any(c7):
                        dpdu[c7] = dpdu_bis[c7]
                        dpdv[c7] = dpdv_bis[c7]

                    for ir in range (0, nrays):
                        ray = Ray(Point(r_o_arr[ir,:]), Vector(r_d_arr[ir,:]), rmint[ir], rmaxt[ir])
                        # Get triangle vertices and translate them in based on ray origin
                        p0t = p0 - ray.o
                        p1t = p1 - ray.o
                        p2t = p2 - ray.o
                        is_intersection = np.full(ntriangles, True, dtype=bool)

                        kz = gv.vargmax(gv.vabs(ray.d))
                        kx = kz + 1
                        if(kx == 3): kx = 0
                        ky = kx + 1
                        if(ky == 3): ky = 0

                        d = gv.permute(ray.d, kx, ky, kz)
                        p0t = gv.permute(p0t, kx, ky, kz)
                        p1t = gv.permute(p1t, kx, ky, kz)
                        p2t = gv.permute(p2t, kx, ky, kz)

                        sx = -d.x/d.z
                        sy = -d.y/d.z
                        sz = 1./d.z
                        p0t.x += sx*p0t.z
                        p0t.y += sy*p0t.z
                        p1t.x += sx*p1t.z
                        p1t.y += sy*p1t.z
                        p2t.x += sx*p2t.z
                        p2t.y += sy*p2t.z

                        # Compute edge function coefficients
                        e0 = (p1t.x * p2t.y) - (p1t.y * p2t.x)
                        e1 = (p2t.x * p0t.y) - (p2t.y * p0t.x)
                        e2 = (p0t.x * p1t.y) - (p0t.y * p1t.x)

                        # Perform triangle edge and determinant tests
                        c1 = np.logical_and(np.logical_or.reduce((e0<0, e1<0, e2<0)),
                                            np.logical_or.reduce((e0>0, e1>0, e2>0)))
                        
                        det = e0 + e1 + e2
                        c2 = det == 0

                        p0t.z *=  sz
                        p1t.z *=  sz
                        p2t.z *=  sz

                        tScaled = e0*p0t.z + e1*p1t.z + e2*p2t.z

                        c3_bis_1 = np.logical_and(det < 0, np.logical_or(tScaled >= 0, tScaled < r.maxt*det))
                        c3_bis_2 = np.logical_and(det > 0, np.logical_or(tScaled <= 0, tScaled > r.maxt*det))
                        c3 = np.logical_or(c3_bis_1, c3_bis_2)

                        # Compute barycentric coordinates and t value for triangle intersection
                        invDet = 1./det
                        b0 = e0 * invDet
                        b1 = e1 * invDet
                        b2 = e2 * invDet
                        t = tScaled * invDet
                        
                        # Ensure that computed triangle t is conservatively greater than zero
                        maxZt = np.max(np.abs(np.array([p0t.z, p1t.z, p2t.z])), axis=0)
                        deltaZ = GAMMA3_F64 * maxZt
                        maxXt = np.max(np.abs(np.array([p0t.x, p1t.x, p2t.x])), axis=0)
                        maxYt = np.max(np.abs(np.array([p0t.y, p1t.y, p2t.y])), axis=0)
                        deltaX = GAMMA5_F64 * (maxXt + maxZt)
                        deltaY = GAMMA5_F64 * (maxYt + maxZt)
                        deltaE = 2 * (GAMMA2_F64 * maxXt * maxYt + deltaY * maxXt + deltaX * maxYt)
                        maxE = np.max(np.abs(np.array([e0, e1, e2])), axis=0)
                        deltaT = 3 * (GAMMA3_F64 * maxE * maxZt + deltaE * maxZt + deltaZ * maxE) * abs(invDet)
                        c4 = t <= deltaT
                        
                        c6 = np.logical_or.reduce((c1, c2, c3, c4, c5))
                        is_intersection[c6] = False
                        t[c6] = None
                        is_intersection_2d[:,ir] = is_intersection
                        t_2d[:,ir] = t

                        # phit = b0*p0+b1*p1+b2*p2
                        uvhit =b0*uv0 + b1*uv1 + b2*uv2
                        u_2d[:,ir] = uvhit.x
                        v_2d[:,ir] = uvhit.y

                    out = sh_name, r, t_2d, is_intersection_2d, u_2d, v_2d, dpdu.to_numpy(), dpdv.to_numpy(), diag_calc
                    if ds_output : return get_intersect_dataset(*out)
                    else : return out
                else: # nrays > ntriangles
                    p0t_arr = self.p0t.to_numpy()
                    p1t_arr = self.p1t.to_numpy()
                    p2t_arr = self.p2t.to_numpy()

                    dpdu = Vector()
                    dpdv = Vector()
                    uv0 = Point(0., 0., 0.)
                    uv1 = Point(1., 0., 0.)
                    uv2 = Point(1., 1., 0.)
                    duv02 = uv0 - uv2
                    duv12 = uv1 - uv2
                    determinant = duv02.x*duv12.y - duv02.y*duv12.x
                    degenerate = bool(abs(determinant) < 1e-8)
                    dpdu = np.zeros((ntriangles, 3), dtype=np.float64)
                    dpdv = np.zeros((ntriangles, 3), dtype=np.float64)

                    kz = gv.vargmax(gv.vabs(r.d))
                    kx = kz + 1
                    kx[kx == 3] = 0
                    ky = kx + 1
                    ky[ky == 3] = 0
                    d = gv.permute(r.d, kx, ky, kz)
                    sx = -d.x/d.z
                    sy = -d.y/d.z
                    sz = 1./d.z
                    
                    for itri in range (0, ntriangles):
                        p0 = Point(p0t_arr[itri,:])
                        p1 = Point(p1t_arr[itri,:])
                        p2 = Point(p2t_arr[itri,:])
                        is_intersection = np.full(nrays, True, dtype=bool)

                        # Get triangle vertices and translate them in based on ray origin
                        p0t = p0 - r.o
                        p1t = p1 - r.o
                        p2t = p2 - r.o

                        p0t = gv.permute(p0t, kx, ky, kz)
                        p1t = gv.permute(p1t, kx, ky, kz)
                        p2t = gv.permute(p2t, kx, ky, kz)

                        p0t.x += sx*p0t.z
                        p0t.y += sy*p0t.z
                        p1t.x += sx*p1t.z
                        p1t.y += sy*p1t.z
                        p2t.x += sx*p2t.z
                        p2t.y += sy*p2t.z

                        # Compute edge function coefficients
                        e0 = (p1t.x * p2t.y) - (p1t.y * p2t.x)
                        e1 = (p2t.x * p0t.y) - (p2t.y * p0t.x)
                        e2 = (p0t.x * p1t.y) - (p0t.y * p1t.x)

                        c1 = np.logical_and(np.logical_or.reduce((e0<0, e1<0, e2<0)),
                                            np.logical_or.reduce((e0>0, e1>0, e2>0)))

                        det = e0 + e1 + e2
                        c2 = det == 0

                        # Compute scaled hit distance to triangle and test against ray $t$ range
                        p0t.z *=  sz
                        p1t.z *=  sz
                        p2t.z *=  sz

                        tScaled = e0*p0t.z + e1*p1t.z + e2*p2t.z

                        c3_bis_1 = np.logical_and(det < 0, np.logical_or(tScaled >= 0, tScaled < r.maxt*det))
                        c3_bis_2 = np.logical_and(det > 0, np.logical_or(tScaled <= 0, tScaled > r.maxt*det))
                        c3 = np.logical_or(c3_bis_1, c3_bis_2)

                        # Compute barycentric coordinates and t value for triangle intersection
                        invDet = 1./det
                        b0 = e0 * invDet
                        b1 = e1 * invDet
                        b2 = e2 * invDet
                        t = tScaled * invDet
                        
                        # Ensure that computed triangle t is conservatively greater than zero
                        maxZt = np.max(np.abs(np.array([p0t.z, p1t.z, p2t.z])), axis=0)
                        deltaZ = GAMMA3_F64 * maxZt
                        maxXt = np.max(np.abs(np.array([p0t.x, p1t.x, p2t.x])), axis=0)
                        maxYt = np.max(np.abs(np.array([p0t.y, p1t.y, p2t.y])), axis=0)
                        deltaX = GAMMA5_F64 * (maxXt + maxZt)
                        deltaY = GAMMA5_F64 * (maxYt + maxZt)
                        deltaE = 2 * (GAMMA2_F64 * maxXt * maxYt + deltaY * maxXt + deltaX * maxYt)
                        maxE = np.max(np.abs(np.array([e0, e1, e2])), axis=0)
                        deltaT = 3 * (GAMMA3_F64 * maxE * maxZt + deltaE * maxZt + deltaZ * maxE) * abs(invDet)
                        c4 = t <= deltaT

                        # Compute triangle partial derivatives
                        # Below the z components is not needed since we are in 2D with u in x and v un y
                        dp02 = p0 - p2
                        dp12 = p1 - p2

                        if (not degenerate):
                            invdet = 1./ determinant
                            dpdu_bis = (duv12.y*dp02 - duv02.y*dp12)*invdet
                            dpdv_bis = (-duv12.x*dp02 + duv02.x*dp12)*invdet
                            
                        ng = gv.cross(p2-p0, p1-p0)
                        c5_bis_1 = degenerate or gv.cross(dpdu_bis, dpdv_bis).length_squared() == 0
                        c5_bis_2 = ng.length_squared() == 0
                        c5 = c5_bis_1 and c5_bis_2
                        c5_arr = np.full(nrays, c5, dtype=bool)
                        
                        c6 = np.logical_or.reduce((c1, c2, c3, c4, c5_arr))
                        is_intersection[c6] = False
                        t[c6] = None
                        is_intersection_2d[itri,:] = is_intersection
                        t_2d[itri,:] = t
                            
                        c7 = np.logical_and(c5_bis_1, np.logical_not(c5_bis_2))
                        if (c7): dpdu_bis, dpdv_bis = gv.coordinate_system(gv.normalize(ng))
                        dpdu[itri,:] = dpdu_bis.to_numpy()
                        dpdv[itri,:] = dpdv_bis.to_numpy()

                        # phit = b0*p0+b1*p1+b2*p2
                        uvhit =b0*uv0 + b1*uv1 + b2*uv2
                        u_2d[itri,:] = uvhit.x
                        v_2d[itri,:] = uvhit.y

                    out = sh_name, r, t_2d, is_intersection_2d, u_2d, v_2d, dpdu, dpdv, diag_calc
                    if ds_output : return get_intersect_dataset(*out)
                    else : return out
        else: # Case 2-D diag, 1-D or scalar
            p0 = self.p0t
            p1 = self.p1t
            p2 = self.p2t

            # Get triangle vertices and translate them in based on ray origin
            p0t = p0 - r.o
            p1t = p1 - r.o
            p2t = p2 - r.o

            kz = gv.vargmax(gv.vabs(r.d))
            kx = kz + 1
            if is_r_arr:
                kx[kx == 3] = 0
                ky = kx + 1
                ky[ky == 3] = 0
            else:
                if(kx == 3): kx = 0
                ky = kx + 1
                if(ky == 3): ky = 0

            d = gv.permute(r.d, kx, ky, kz)
            p0t = gv.permute(p0t, kx, ky, kz)
            p1t = gv.permute(p1t, kx, ky, kz)
            p2t = gv.permute(p2t, kx, ky, kz)
            
            sx = -d.x/d.z
            sy = -d.y/d.z
            sz = 1./d.z
            p0t.x += sx*p0t.z
            p0t.y += sy*p0t.z
            p1t.x += sx*p1t.z
            p1t.y += sy*p1t.z
            p2t.x += sx*p2t.z
            p2t.y += sy*p2t.z
            
            # Compute edge function coefficients
            e0 = (p1t.x * p2t.y) - (p1t.y * p2t.x)
            e1 = (p2t.x * p0t.y) - (p2t.y * p0t.x)
            e2 = (p0t.x * p1t.y) - (p0t.y * p1t.x)

            if is_p_arr or is_r_arr:
                with np.errstate(divide='ignore', invalid='ignore'):

                    if is_p_arr: size = len(p0.x)
                    if is_r_arr: size = len(r.o.x)
                    is_intersection = np.full(size, True, dtype=bool)
                    # Perform triangle edge and determinant tests
                    c1 = np.logical_and(np.logical_or.reduce((e0<0, e1<0, e2<0)),
                                        np.logical_or.reduce((e0>0, e1>0, e2>0)))
                    
                    det = e0 + e1 + e2
                    c2 = det == 0

                    # Compute scaled hit distance to triangle and test against ray $t$ range
                    p0t.z *=  sz
                    p1t.z *=  sz
                    p2t.z *=  sz

                    tScaled = e0*p0t.z + e1*p1t.z + e2*p2t.z

                    c3_bis_1 = np.logical_and(det < 0, np.logical_or(tScaled >= 0, tScaled < r.maxt*det))
                    c3_bis_2 = np.logical_and(det > 0, np.logical_or(tScaled <= 0, tScaled > r.maxt*det))
                    c3 = np.logical_or(c3_bis_1, c3_bis_2)

                    # Compute barycentric coordinates and t value for triangle intersection
                    invDet = 1./det
                    b0 = e0 * invDet
                    b1 = e1 * invDet
                    b2 = e2 * invDet
                    t = tScaled * invDet
                    
                    # Ensure that computed triangle t is conservatively greater than zero
                    maxZt = np.max(np.abs(np.array([p0t.z, p1t.z, p2t.z])))
                    deltaZ = GAMMA3_F64 * maxZt
                    maxXt = np.max(np.abs(np.array([p0t.x, p1t.x, p2t.x])))
                    maxYt = np.max(np.abs(np.array([p0t.y, p1t.y, p2t.y])))
                    deltaX = GAMMA5_F64 * (maxXt + maxZt)
                    deltaY = GAMMA5_F64 * (maxYt + maxZt)
                    deltaE = 2 * (GAMMA2_F64 * maxXt * maxYt + deltaY * maxXt + deltaX * maxYt)
                    maxE = np.max(np.abs(np.array([e0, e1, e2])))
                    deltaT = 3 * (GAMMA3_F64 * maxE * maxZt + deltaE * maxZt + deltaZ * maxE) * abs(invDet)
                    c4 = t <= deltaT

                    # Compute triangle partial derivatives
                    # Below the z components is not needed since we are in 2D with u in x and v un y
                    dpdu = Vector()
                    dpdv = Vector()
                    uv0 = Point(0., 0., 0.)
                    uv1 = Point(1., 0., 0.)
                    uv2 = Point(1., 1., 0.)
                    duv02 = uv0 - uv2
                    duv12 = uv1 - uv2
                    dp02 = p0 - p2
                    dp12 = p1 - p2
                    determinant = duv02.x*duv12.y - duv02.y*duv12.x
                    degenerate = bool(abs(determinant) < 1e-8)

                    if (not degenerate):
                        invdet = 1./ determinant
                        dpdu = (duv12.y*dp02 - duv02.y*dp12)*invdet
                        dpdv = (-duv12.x*dp02 + duv02.x*dp12)*invdet

                    ng = gv.cross(p2-p0, p1-p0)
                    c5_bis_1 = np.logical_or(degenerate, gv.cross(dpdu, dpdv).length_squared() == 0)
                    c5_bis_2 = ng.length_squared() == 0
                    c5 = np.logical_and(c5_bis_1, c5_bis_2)
                    if not isinstance(c5, np.ndarray): c5 = np.full(size, c5, dtype=bool)
                    
                    c6 = np.logical_or.reduce((c1, c2, c3, c4, c5))
                    is_intersection[c6] = False
                    t[c6] = None
                        
                    dpdu_bis, dpdv_bis = gv.coordinate_system(gv.normalize(ng))
                    c7 = np.logical_and(c5_bis_1, np.logical_not(c5_bis_2))
                    if np.any(c7):
                        dpdu[c7] = dpdu_bis[c7]
                        dpdv[c7] = dpdv_bis[c7]

                    # phit = b0*p0+b1*p1+b2*p2
                    uvhit =b0*uv0 + b1*uv1 + b2*uv2
                    out = sh_name, r, t, is_intersection, uvhit.x, uvhit.y, dpdu.to_numpy(), dpdv.to_numpy(), diag_calc
                    if ds_output : return get_intersect_dataset(*out)
                    else : return out
            else:
                # Perform triangle edge and determinant tests
                if ((e0 < 0 or e1 < 0 or e2 < 0) and (e0 > 0 or e1 > 0 or e2 > 0)):
                    if ds_output : return get_intersect_dataset(sh_name, r, None, False, None, None, None, None, False)
                    else : return sh_name, r, None, False, None, None, None, None, False
                det = e0 + e1 + e2
                if (det == 0):
                    if ds_output : return get_intersect_dataset(sh_name, r, None, False, None, None, None, None, False)
                    else : return sh_name, r, None, False, None, None, None, None, False

                # Compute scaled hit distance to triangle and test against ray $t$ range
                p0t.z *=  sz
                p1t.z *=  sz
                p2t.z *=  sz

                tScaled = e0*p0t.z + e1*p1t.z + e2*p2t.z

                if ( (det < 0 and (tScaled >= 0 or tScaled < r.maxt*det)) or
                    (det > 0 and (tScaled <= 0 or tScaled > r.maxt*det)) ):
                    if ds_output : return get_intersect_dataset(sh_name, r, None, False, None, None, None, None, False)
                    else : return sh_name, r, None, False, None, None, None, None, False

                # Compute barycentric coordinates and t value for triangle intersection
                invDet = 1./det
                b0 = e0 * invDet
                b1 = e1 * invDet
                b2 = e2 * invDet
                t = tScaled * invDet
                
                # Ensure that computed triangle t is conservatively greater than zero
                maxZt = np.max(np.abs(np.array([p0t.z, p1t.z, p2t.z])))
                deltaZ = GAMMA3_F64 * maxZt
                maxXt = np.max(np.abs(np.array([p0t.x, p1t.x, p2t.x])))
                maxYt = np.max(np.abs(np.array([p0t.y, p1t.y, p2t.y])))
                deltaX = GAMMA5_F64 * (maxXt + maxZt)
                deltaY = GAMMA5_F64 * (maxYt + maxZt) 
                deltaE = 2 * (GAMMA2_F64 * maxXt * maxYt + deltaY * maxXt + deltaX * maxYt)
                maxE = np.max(np.abs(np.array([e0, e1, e2])))
                deltaT = 3 * (GAMMA3_F64 * maxE * maxZt + deltaE * maxZt + deltaZ * maxE) * abs(invDet)
                if (t <= deltaT):
                    if ds_output : return get_intersect_dataset(sh_name, r, None, False, None, None, None, None, False)
                    else : return sh_name, r, None, False, None, None, None, None, False

                # Compute triangle partial derivatives
                # Below the z components is not needed since we are in 2D with u in x and v un y
                dpdu = Vector()
                dpdv = Vector()
                uv0 = Point(0., 0., 0.)
                uv1 = Point(1., 0., 0.)
                uv2 = Point(1., 1., 0.)
                duv02 = uv0 - uv2
                duv12 = uv1 - uv2
                dp02 = p0 - p2
                dp12 = p1 - p2
                determinant = duv02.x*duv12.y - duv02.y*duv12.x
                degenerate = bool(abs(determinant) < 1e-8)

                if (not degenerate):
                    invdet = 1./ determinant
                    dpdu = (duv12.y*dp02 - duv02.y*dp12)*invdet
                    dpdv = (-duv12.x*dp02 + duv02.x*dp12)*invdet

                if ( degenerate or gv.cross(dpdu, dpdv).length_squared() == 0):
                    ng = gv.cross(p2-p0, p1-p0)
                    if ( ng.length_squared() == 0 ):
                        if ds_output : return get_intersect_dataset(sh_name, r, None, False, None, None, None, None, False)
                        else : return sh_name, r, None, False, None, None, None, None, False
                    dpdu, dpdv = gv.coordinate_system(gv.normalize(ng))

                #phit = b0*p0+b1*p1+b2*p2
                uvhit =b0*uv0 + b1*uv1 + b2*uv2
                out = sh_name, r, t, True, uvhit.x, uvhit.y, dpdu.to_numpy(), dpdv.to_numpy(), diag_calc
                if ds_output : return get_intersect_dataset(*out)
                else : return out

    def area(self):
        """
        compute the area of the triangle

        .. warning::
            `the scale transformation is not considered for the area calculation!`
        """
        return 0.5 * gv.cross(self.p1-self.p0, self.p2-self.p0).length()


class TriangleMesh(Shape):
    '''
    Creation of the class TriangleMesh

    Parameters
    ----------
    vertices : 2-D ndarray
        The vertices xyz coordinates. It is a 2d ndarray of size (nvertices, 3) where the 
        first element is the coordinate of first vertex and so on
    faces : 2-D ndarray
        The vertices indices of triangles, a 2d ndarray of shape (ntriangles, 3).
        The 3 first indices are the vertices (p0, p1 and p3) indices of the first triangle and so on
    oTw : Transform, optional
        From object to world space or the transformation applied to the triangle mesh
    wTo : Transform, optional
        From world to object space or the in inverse transformation applied to the triangle mesh
    '''
    def __init__(self, vertices, faces, oTw=None, wTo=None):
        if wTo is None and oTw is None:
            wTo = Transform()
            oTw = Transform()
        elif (wTo is None and isinstance(oTw, Transform)): wTo = oTw.inverse()
        elif (isinstance(wTo, Transform) and oTw is None): oTw = wTo.inverse()
        if (  not isinstance(faces, np.ndarray)                                            or
              not (len(faces.shape) == 2)                                                  or
              not (np.issubdtype(faces.dtype, int) or np.issubdtype(faces.dtype, np.integer))  ):
            raise ValueError('The parameter faces must be a 2d ndarray of intergers')
        if (  not ( isinstance(vertices, np.ndarray) )  or not ( len(vertices.shape) == 2 )  ):
            raise ValueError('The paramerter vertices must be a 2d ndarray')
        Shape.__init__(self, ObjectToWorld = oTw, WorldToObject = wTo)
        self.vertices = vertices
        self.nvertices = vertices.shape[0]
        self.faces = faces
        self.ntriangles = faces.shape[0]

    def intersect(self, r, method='v3', diag_calc=False, ds_output=True, use_loop=False):
        """
        Test if a ray/set of rays intersect with the triangle mesh and return intersection information

        Parameters
        ----------
        r : Ray
            The ray(s) to use for the intersection test(s)
        method : str, optional
            Tow choice -> 'v2' (use mainly pbrt v2 triangle intersection test method) or 'v3' (pbrt v3)
        diag_calc : bool, optional
            Perform diagonal calculations between r(i) and triangle(i). The number of triangles must 
            be equal to the number of rays
        use_loop : bool, optional
            If True -> scalar calculations over a loop (instead of using numpy). It can be useful for 
            debugging
        ds_output : Bool, optional
            If True the output is a dataset, else return a tuple with intersection information variables
        
        Returns
        -------
        out : xr.Dataset | tuple
            Look-up table with the intersection information if ds_output is True, 
            else return a tuple (ready to be an input for the function get_intersect_dataset in 
            geoclide/shapes.py). Form of the tuple:
            
            * shape_name : str
                -> The shape class name
            * r : Ray
                -> The ray(s) used for the intersection test
            * t : None | float | 1-D ndarray
                -> The t ray variable(s) for its first intersection at the shape surface
            * is_intersection : bool | 1-D ndarray
                -> If there is an intersection return True, else False
            * u : None | float | 1-D ndarray
                -> The u coordinate(s) of the parametric representation
            * v : None | float | 1-D ndarray
                -> The u coordinate(s) of the parametric representation
            * dpdu : None | 1-D ndarray | 2-D ndarray
                -> The surface partial derivative(s) of phit with respect to u
            * dpdv : None | 1-D ndarray | 2-D ndarray
                -> The surface partial derivative(s) of phit with respect to v
            * diag_cal : bool
                -> This indicates whether a diagonal calculation has been performed
        """
        if not isinstance(r, Ray): raise ValueError('The parameter r must be a Ray')
        if isinstance(r.o.x, np.ndarray) : nrays = len(r.o.x)
        else : nrays = 1
        if use_loop:
            if nrays > 1 and not diag_calc:
                is_int_1d = np.full((nrays), True, dtype=bool)
                t_1d = np.zeros((nrays), dtype=np.float64)
                p_1d = np.zeros((nrays,3), dtype=np.float64)
                dpdu_1d = np.zeros_like(p_1d)
                dpdv_1d = np.zeros_like(p_1d)
                u_1d = np.zeros_like(t_1d)
                v_1d = np.zeros_like(t_1d)
                o_set_arr = r.o.to_numpy()
                d_set_arr = r.d.to_numpy()

                triangles = np.empty((self.ntriangles), dtype=Triangle)
                for itri in range(0, self.ntriangles):
                    p0 = Point(self.vertices[self.faces[itri,0],:])
                    p1 = Point(self.vertices[self.faces[itri,1],:])
                    p2 = Point(self.vertices[self.faces[itri,2],:])
                    triangles[itri] = Triangle(p0, p1, p2, self.oTw, self.wTo)

                for ir in range (0, nrays):
                    ri = Ray(Point(o_set_arr[ir,:]), Vector(d_set_arr[ir,:]))
                    res = self.__class__.__name__, r, None, False, None, None, None, None, False
                    thit = float("inf")
                    for itri in range(0, self.ntriangles):
                        res_bis = triangles[itri].intersect(ri, method=method, ds_output=False)
                        thit_bis = res_bis[2]
                        is_intersection = res_bis[3]
                        if is_intersection and thit > thit_bis:
                            thit = thit_bis
                            res = self.__class__.__name__, *res_bis[1:]
                    t_1d[ir] = res[2]
                    is_int_1d[ir] = res[3]
                    u_1d[ir] = res[4]
                    v_1d[ir] = res[5]
                    dpdu_1d[ir] = res[6]
                    dpdv_1d[ir] = res[7]
                res_1d = self.__class__.__name__, r, t_1d, is_int_1d, u_1d, v_1d, dpdu_1d, dpdv_1d, diag_calc
                if ds_output : return get_intersect_dataset(*res_1d)
                else : return res_1d
            elif(diag_calc):
                is_int_1d = np.full((nrays), True, dtype=bool)
                t_1d = np.zeros((nrays), dtype=np.float64)
                p_1d = np.zeros((nrays,3), dtype=np.float64)
                dpdu_1d = np.zeros_like(p_1d)
                dpdv_1d = np.zeros_like(p_1d)
                u_1d = np.zeros_like(t_1d)
                v_1d = np.zeros_like(t_1d)
                o_set_arr = r.o.to_numpy()
                d_set_arr = r.d.to_numpy()
                ndiag = nrays

                for idiag in range (0, ndiag):
                    res = self.__class__.__name__, r, None, False, None, None, None, None, False
                    thit = float("inf")
                    ri = Ray(Point(o_set_arr[idiag,:]), Vector(d_set_arr[idiag,:]))
                    p0 = Point(self.vertices[self.faces[idiag,0],:])
                    p1 = Point(self.vertices[self.faces[idiag,1],:])
                    p2 = Point(self.vertices[self.faces[idiag,2],:])
                    triangle = Triangle(p0, p1, p2, self.oTw, self.wTo)
                    res_bis = triangle.intersect(ri, method=method, ds_output=False)
                    thit_bis = res_bis[2]
                    is_intersection = res_bis[3]
                    if is_intersection and thit > thit_bis:
                        thit = thit_bis
                        res = self.__class__.__name__, *res_bis[1:]
                    t_1d[idiag] = res[2]
                    is_int_1d[idiag] = res[3]
                    u_1d[idiag] = res[4]
                    v_1d[idiag] = res[5]
                    dpdu_1d[idiag] = res[6]
                    dpdv_1d[idiag] = res[7]
                res_1d = self.__class__.__name__, r, t_1d, is_int_1d, u_1d, v_1d, dpdu_1d, dpdv_1d, diag_calc
                if ds_output : return get_intersect_dataset(*res_1d)
                else : return res_1d
            else:
                res = self.__class__.__name__, r, None, False, None, None, None, None, False
                thit = float("inf")
                for itri in range(0, self.ntriangles):
                    p0 = Point(self.vertices[self.faces[itri,0],:])
                    p1 = Point(self.vertices[self.faces[itri,1],:])
                    p2 = Point(self.vertices[self.faces[itri,2],:])
                    triangle = Triangle(p0, p1, p2, self.oTw, self.wTo)
                    res_bis = triangle.intersect(r, method=method, ds_output=False)
                    thit_bis = res_bis[2]
                    is_intersection = res_bis[3]
                    if is_intersection and thit > thit_bis:
                        thit = thit_bis
                        res = self.__class__.__name__, *res_bis[1:]
                if ds_output : return get_intersect_dataset(*res)
                else : return res
        else:
            p0 = Point(self.vertices[self.faces[:,0],:])
            p1 = Point(self.vertices[self.faces[:,1],:])
            p2 = Point(self.vertices[self.faces[:,2],:])
            triangles = Triangle(p0, p1, p2, self.oTw, self.wTo)
            res = self.__class__.__name__, r, None, False, None, None, None, None, False
            res_bis = triangles.intersect(r, method=method, diag_calc=diag_calc, ds_output=False)

            is_intersection = res_bis[3]
            if np.any(res_bis[3]):
                thit = res_bis[2].copy()
                thit[np.isnan(thit)] = math.inf
                if nrays > 1 and len(thit.shape) == 2 and thit.shape[0] > 1:
                    id0 = np.nanargmin(thit, axis=0)
                    id1 = np.arange(nrays)
                    res = self.__class__.__name__, r, res_bis[2][id0,id1], \
                        is_intersection[id0,id1], res_bis[4][id0,id1], res_bis[5][id0,id1], \
                        res_bis[6][id0,:], res_bis[7][id0,:], diag_calc
                elif(nrays > 1 and thit.shape[0] == 1):
                     res = self.__class__.__name__, r, res_bis[2][0,:], \
                        is_intersection[0,:], res_bis[4][0,:], res_bis[5][0,:], \
                        res_bis[6][0,:], res_bis[7][0,:], diag_calc
                elif (nrays == 1 and isinstance(thit, np.ndarray)):
                    id0 = np.nanargmin(thit)
                    res = self.__class__.__name__, r, res_bis[2][id0], \
                        is_intersection[id0], res_bis[4][id0], res_bis[5][id0], \
                        res_bis[6][id0], res_bis[7][id0], diag_calc
                else:
                    res = self.__class__.__name__, *res_bis[1:]

            if ds_output : return get_intersect_dataset(*res)
            else : return res
    
    def is_intersection(self, r, method='v3', diag_calc=False, use_loop=False):
        """
        Test if a ray/set of rays intersect with the triangle mesh

        Parameters
        ----------
        r : Ray
            The ray(s) to use for the intersection test(s)
        method : str, optional
            Tow choice -> 'v2' (use mainly pbrt v2 triangle intersection test method) or 'v3' (pbrt v3)
        diag_calc : bool, optional
            Perform diagonal calculations between r(i) and triangle(i). The number of triangles must 
            be equal to the number of rays
        use_loop : bool, optional
            If True -> scalar calculations over a loop (instead of using numpy). It can be useful for 
            debugging
        
        Returns
        -------
        out : bool | 1-D ndarray
            If there is an intersection -> True, else False
        """
        if not isinstance(r, Ray): raise ValueError('The parameter r must be a Ray')
        if isinstance(r.o.x, np.ndarray) : nrays = len(r.o.x)
        else : nrays = 1
        if use_loop:
            if nrays > 1 and not diag_calc:  # nrays > 1 and ntriangles > 1
                is_int_1d = np.full((nrays), False, dtype=bool)
                o_set_arr = r.o.to_numpy()
                d_set_arr = r.d.to_numpy()
                triangles = np.empty((self.ntriangles), dtype=Triangle)
                for itri in range(0, self.ntriangles):
                    p0 = Point(self.vertices[self.faces[itri,0],:])
                    p1 = Point(self.vertices[self.faces[itri,1],:])
                    p2 = Point(self.vertices[self.faces[itri,2],:])
                    triangles[itri] = Triangle(p0, p1, p2, self.oTw, self.wTo)
                for ir in range (0, nrays):
                    ri = Ray(Point(o_set_arr[ir,:]), Vector(d_set_arr[ir,:]))
                    is_intersection = False
                    for itri in range(0, self.ntriangles):
                        if (triangles[itri].is_intersection(ri, method=method)):
                            is_int_1d[ir] = True
                            break
                return is_int_1d
            elif(diag_calc): # nrays > 1 and ntriangles > 1
                is_int_1d = np.full((nrays), False, dtype=bool)
                o_set_arr = r.o.to_numpy()
                d_set_arr = r.d.to_numpy()
                ndiag = nrays
                for idiag in range (0, ndiag):
                    ri = Ray(Point(o_set_arr[idiag,:]), Vector(d_set_arr[idiag,:]))
                    p0 = Point(self.vertices[self.faces[idiag,0],:])
                    p1 = Point(self.vertices[self.faces[idiag,1],:])
                    p2 = Point(self.vertices[self.faces[idiag,2],:])
                    triangle = Triangle(p0, p1, p2, self.oTw, self.wTo)
                    is_int_1d[idiag] = triangle.is_intersection(ri, method=method)
                return is_int_1d
            else: # nrays == 1 and ntriangles >= 1
                is_intersection = False
                for itri in range(0, self.ntriangles):
                    p0 = Point(self.vertices[self.faces[itri,0],:])
                    p1 = Point(self.vertices[self.faces[itri,1],:])
                    p2 = Point(self.vertices[self.faces[itri,2],:])
                    triangle = Triangle(p0, p1, p2, self.oTw, self.wTo)
                    if (triangle.is_intersection(r, method=method)): return True
                return False
        else: # use_loop = False
            p0 = Point(self.vertices[self.faces[:,0],:])
            p1 = Point(self.vertices[self.faces[:,1],:])
            p2 = Point(self.vertices[self.faces[:,2],:])
            triangles = Triangle(p0, p1, p2, self.oTw, self.wTo)
            is_intersection = triangles.is_intersection(r, method=method, diag_calc=diag_calc)
            res_shape = is_intersection.shape
            if np.any(is_intersection):
                if nrays > 1 and len(res_shape) == 2 and res_shape[0] > 1:
                    is_int = np.any(is_intersection, axis=0)
                elif(nrays > 1 and res_shape[0] == 1):
                    is_int = is_intersection[0,:]
                elif (nrays == 1 and isinstance(is_intersection, np.ndarray)):
                    is_int = True
                else:
                    is_int = is_intersection
            else:
                if nrays > 1 : is_int = np.full(nrays, False, dtype=bool)
                else : is_int = False
            return is_int
    
    def is_intersection_t(self, r, method='v3', diag_calc=False, use_loop=False):
        """
        Test if a ray/set of rays intersect with the triangle mesh

        Parameters
        ----------
        r : Ray
            The ray(s) to use for the intersection test(s)
        method : str, optional
            Tow choice -> 'v2' (use mainly pbrt v2 triangle intersection test method) or 'v3' (pbrt v3)
        diag_calc : bool, optional
            Perform diagonal calculations between r(i) and triangle(i). The number of triangles must 
            be equal to the number of rays
        use_loop : bool, optional
            If True -> scalar calculations over a loop (instead of using numpy). It can be useful for 
            debugging
        
        Returns
        -------
        thit : None | float | 1-D ndarray
            The t ray variable(s) for its first intersection at the shape surface
        is_intersection : bool | 1-D ndarray
            If there is an intersection -> True, else False

        Notes
        -----
        If use_loop = True, is_intersection_t can be significantly more consuming than is_intersection. 
        Because it does not stop at the first intersection, but it finalize the complete loop to
        return the thit corresponding to the nearest triangle.
        """
        if not isinstance(r, Ray): raise ValueError('The parameter r must be a Ray')
        if isinstance(r.o.x, np.ndarray) : nrays = len(r.o.x)
        else : nrays = 1
        if use_loop:
            if nrays > 1 and not diag_calc:  # nrays > 1 and ntriangles > 1
                is_int_1d = np.full((nrays), True, dtype=bool)
                t_1d = np.zeros((nrays), dtype=np.float64)
                o_set_arr = r.o.to_numpy()
                d_set_arr = r.d.to_numpy()
                triangles = np.empty((self.ntriangles), dtype=Triangle)
                for itri in range(0, self.ntriangles):
                    p0 = Point(self.vertices[self.faces[itri,0],:])
                    p1 = Point(self.vertices[self.faces[itri,1],:])
                    p2 = Point(self.vertices[self.faces[itri,2],:])
                    triangles[itri] = Triangle(p0, p1, p2, self.oTw, self.wTo)
                for ir in range (0, nrays):
                    ri = Ray(Point(o_set_arr[ir,:]), Vector(d_set_arr[ir,:]))
                    thit = float("inf")
                    is_intersection = False
                    for itri in range(0, self.ntriangles):
                        thit_bis, is_intersection_bis = triangles[itri].is_intersection_t(ri, method=method)
                        if is_intersection_bis and thit > thit_bis:
                            thit = thit_bis
                            is_intersection = True
                    if is_intersection : t_1d[ir] = thit
                    else: t_1d[ir] = None
                    is_int_1d[ir] = is_intersection
                return t_1d, is_int_1d
            elif(diag_calc): # nrays > 1 and ntriangles > 1
                is_int_1d = np.full((nrays), False, dtype=bool)
                t_1d = np.full((nrays), None, dtype=np.float64)
                o_set_arr = r.o.to_numpy()
                d_set_arr = r.d.to_numpy()
                ndiag = nrays
                for idiag in range (0, ndiag):
                    thit = float("inf")
                    ri = Ray(Point(o_set_arr[idiag,:]), Vector(d_set_arr[idiag,:]))
                    p0 = Point(self.vertices[self.faces[idiag,0],:])
                    p1 = Point(self.vertices[self.faces[idiag,1],:])
                    p2 = Point(self.vertices[self.faces[idiag,2],:])
                    triangle = Triangle(p0, p1, p2, self.oTw, self.wTo)
                    thit_bis, is_intersection_bis = triangle.is_intersection_t(ri, method=method)
                    if is_intersection_bis and thit > thit_bis:
                        t_1d[idiag] = thit_bis
                        is_int_1d[idiag] = is_intersection_bis
                return t_1d, is_int_1d
            else: # nrays == 1 and ntriangles >= 1
                thit = float("inf")
                is_intersection = False
                for itri in range(0, self.ntriangles):
                    p0 = Point(self.vertices[self.faces[itri,0],:])
                    p1 = Point(self.vertices[self.faces[itri,1],:])
                    p2 = Point(self.vertices[self.faces[itri,2],:])
                    triangle = Triangle(p0, p1, p2, self.oTw, self.wTo)
                    thit_bis, is_intersection_bis = triangle.is_intersection_t(r, method=method)
                    if is_intersection_bis and thit > thit_bis:
                        thit = thit_bis
                        is_intersection = True
                if (not is_intersection) : thit = None
                return thit, is_intersection
        else: # use_loop = False
            p0 = Point(self.vertices[self.faces[:,0],:])
            p1 = Point(self.vertices[self.faces[:,1],:])
            p2 = Point(self.vertices[self.faces[:,2],:])
            triangles = Triangle(p0, p1, p2, self.oTw, self.wTo)
            thit, is_intersection = triangles.is_intersection_t(r, method=method, diag_calc=diag_calc)
            if np.any(is_intersection):
                thit_bis = thit.copy()
                thit_bis[np.isnan(thit_bis)] = math.inf
                if nrays > 1 and len(thit.shape) == 2 and thit.shape[0] > 1:
                    id0 = np.nanargmin(thit_bis, axis=0)
                    id1 = np.arange(nrays)
                    t = thit[id0,id1]
                    is_int = is_intersection[id0,id1]
                elif(nrays > 1 and thit.shape[0] == 1):
                    t = thit[0,:]
                    is_int = is_intersection[0,:]
                elif (nrays == 1 and isinstance(thit, np.ndarray)):
                    id0 = np.nanargmin(thit_bis)
                    t = thit[id0]
                    is_int = is_intersection[id0]
                else:
                    t = thit
                    is_int = is_intersection
            else:
                if nrays > 1:
                    t = np.full(nrays, None, dtype=np.float64)
                    is_int = np.full(nrays, False, dtype=bool)
                else:
                    t = None
                    is_int = False
            return t, is_int
    
    def area(self):
        """
        compute the area of the triangle mesh

        .. warning::
            `the scale transformation is not considered for the area calculation!`
        """
        area = 0.
        for itri in range (0, self.ntriangles):
            p0 = Point(self.vertices[self.faces[itri,0],:])
            p1 = Point(self.vertices[self.faces[itri,1],:])
            p2 = Point(self.vertices[self.faces[itri,2],:])
            triangle = Triangle(p0, p1, p2, self.oTw, self.wTo)
            area+=triangle.area()
        return area
    
    def apply_tf(self, t):
        """
        Apply transformation to the triangle mesh

        Parameters
        ----------
        t : Tranform
            The transfomation matrix to apply
        """
        if (not isinstance(t, Transform)):
            raise ValueError('A transform can be multiplied only by another Transform')
        
        vertices_t = np.zeros((self.nvertices,3))
        for iver in range (0, self.nvertices):
            vertices_t[iver,:] = t(Point(self.vertices[iver,:])).to_numpy()
        self.vertices = vertices_t
    
    def plot(self, source=None, savefig_name=None, **kwargs):
        """
        Plot the triangle mesh

        Parameters
        ----------
        source : str
            The package used for the plot, only 2 option -> 'matplotlib' or 'trimesh'. 
            If source = None, use matplolib for mesh with ntriangle < 5000, else use trimesh
        savefig_name : str, optional
            If savefig_name is given, the figure is saved with the given name (only 
            if source='matplotlib)
        **kwargs
            All other keyword arguments are passed on to matplotlib plot_trisurf function. 
            For example: alpha, color, shade, ... 
            If source = 'trimesh' then the keyword arguments passed on to show Trimesh method 
        
        Examples
        --------
        >>> import geoclide as gc
        >>> prolate = gc.Spheroid(radius_xy=1.5, radius_z=3.)
        >>> msh = prolate.to_trianglemesh()
        >>> msh.plot(color='green', edgecolor='k')
        image
        """
        if self.oTw.is_identity(): vertices = self.vertices
        else: vertices = self.oTw(Point(self.vertices)).to_numpy()

        if ((source is None and self.ntriangles < 5000) or source == 'matplotlib'):
            fig = plt.figure()
            ax = fig.add_subplot(111, projection='3d')
            if 'color' in kwargs: color = kwargs.pop('color', False)
            else: color = 'blue'
            ax.plot_trisurf(vertices[:,0], vertices[:,1], vertices[:,2],
                            triangles = self.faces, color=color, **kwargs)
            ax.set_aspect('equal', adjustable='box')
            plt.tight_layout()
            if savefig_name is not None: plt.savefig(savefig_name)
            plt.show()
        elif ((source is None and self.ntriangles >= 5000) or source == 'trimesh'):
            msh = trimesh.Trimesh(vertices, self.faces)
            return msh.show(**kwargs)
        else:
            raise ValueError("Unknown source. Please choose between: 'matplotlib' or 'trimesh'")

    def to_dataset(self, name='none'):
        """
        Create an xarray dataset where the triangle mesh information are stored

        Parameters
        ----------
        name : str, optional
            The name of the triangle mesh to be stored
        
        Returns
        -------
        out : xr.Dataset
            The dataset with the triangle mesh information
        """
        ds = xr.Dataset(coords={'xyz':np.arange(3)})
        vertices = np.zeros((1,self.nvertices,3), np.float64)
        faces = np.zeros((1,self.ntriangles,3), np.int32)
        vertices[0,:,:] = self.vertices
        faces[0,:,:] = self.faces
        ds['obj_names'] = xr.DataArray(np.array([name]), dims=['nboj'])
        ds['vertices'] = xr.DataArray(vertices, dims=['nboj', 'nvertices', 'xyz'])
        ds['vertices'].attrs = {'description': 'The vertices xyz coordinates.'}
        ds['faces'] = xr.DataArray(faces, dims=['nobj', 'ntriangles', 'p0p1p2'])
        ds['faces'].attrs = {'description': 'For each triangle, the index of vertices point p0, p1 and p2.'}
        date = datetime.now().strftime("%Y-%m-%d")  
        ds.attrs.update({'date':date, 'version': VERSION})
        return ds
    
    def write(self, path, **kwargs):
        """
        Save the mesh

        - if gcnc format use xarray, else use trimesh

        Parameters
        ----------
        path : str
            The xarray to_netcdf path paramter (or trimesh)
        **kwargs
            The keyword arguments are passed on to xarray to_netcdf or trimesh export method
        """
        if path.endswith('gcnc'):
            self.to_dataset().to_netcdf(path, **kwargs)
        else:
            msh = trimesh.Trimesh(self.vertices, self.faces)
            msh.export(path, **kwargs)


def create_sphere_trianglemesh(radius, reso_theta=None, reso_phi=None, theta_min=0., theta_max=180.,
                               phi_max=360., oTw=None, wTo=None):
    """
    :meta private:

    Create a sphere / partial sphere triangleMesh

    Parameters
    ----------
    radius : float
        The sphere radius
    reso_theta : int, optional
        The number of lines around the polar theta angle, minimum accepted value is 3
    reso_phi : int, optional
        The number of lines around the azimuth phi angle, minimum accepted value is 3
    theta_min : float, optional
        The minimum theta value in degrees (partial sphere)
    theta_max : float, optional
        The maximum theta value in degrees (partial sphere)
    phi_max : float, optional
        The maxium phi value in degrees (partial sphere)
    oTw : Transform, optional
        From object to world space or the transformation applied to the spheroid
    wTo : Transform, optional
        From world to object space or the in inverse transformation applied to the spheroid

    Results
    -------
    out : TriangleMesh
        The triangle mesh sphere
    
    Examples
    --------
    >>> import geoclide as gc
    >>> msh = gc.create_sphere_trianglemesh(1)
    >>> msh
    <geoclide.trianglemesh.TriangleMesh at 0x7fe3a0ea0950>
    """
    if wTo is None and oTw is None:
            wTo = Transform()
            oTw = Transform()
    if reso_theta is None : reso_theta = max(round(theta_max/10.), 10)
    if reso_phi is None: reso_phi = max(round(theta_max/10.), 10)
    if reso_theta < 3 : raise ValueError("the value of reso_theta must >= 3")
    if reso_phi < 3 : raise ValueError("the value of reso_phi must >= 3")
    if phi_max == 360. : phi_max = math.tau
    else: phi_max = math.radians(phi_max)
    theta_min = math.radians(theta_min)
    if theta_max == 180. : theta_max = math.pi
    else : theta_max = math.radians(theta_max)

    # Create meshgrid with and theta
    theta = np.linspace(theta_min, theta_max, reso_theta)
    if (phi_max < math.tau):
        phi = np.linspace(0., phi_max, reso_phi)
    else:
        phi = np.linspace(0., phi_max, reso_phi+1)
    ph, th = np.meshgrid(phi, theta)

    # Compute the Cartesian coordinates for the vertices
    x = radius * np.sin(th) * np.cos(ph)
    y = radius * np.sin(th) * np.sin(ph)
    z = radius * np.cos(th)

    # Fill unique vertices and order them in a 2d array (nvertices, 3)
    # - from north pole to south along theta
    # - in the trigonometric direction along phi
    if (theta[0] == 0. and theta[-1] == math.pi):
        nvertices = reso_theta*reso_phi - (reso_phi*2) + 2
        ntriangle = (nvertices-2)*2
        if (phi[-1] < math.tau): ntriangle -= 2
    elif(theta[0] == 0. or theta[-1] == math.pi):
        nvertices = reso_theta*reso_phi - reso_phi + 1
        ntriangle = (nvertices-1)*2
        if (phi[-1] < math.tau): ntriangle -= 1
    else:
        nvertices = reso_theta*reso_phi
        ntriangle = nvertices*2
    vertices = np.zeros((nvertices, 3))

    if (phi[-1] < math.tau): ntriangle -= max((reso_theta-3)*2,0)

    ini_id0 = 0
    ini_id1 = nvertices
    id_xyz0 = 0
    id_xyz1 = reso_theta

    if (theta[0] == 0.):
        # Add north pole vertex
        ini_id0 += 1 
        id_xyz0 +=1
        vertices[0] = np.array([x[0, 0], y[0, 0], z[0, 0]])

    if (theta[-1] == math.pi):
        # Add south pole vertex
        ini_id1 -= 1
        id_xyz1 -= 1
        vertices[-1] = [x[-1, 0], y[-1, 0], z[-1, 0]]

    # Add middle vertices
    if (phi_max < math.tau):
        vertices[ini_id0:ini_id1,0] = x[id_xyz0:id_xyz1,:].flatten()
        vertices[ini_id0:ini_id1,1] = y[id_xyz0:id_xyz1,:].flatten()
        vertices[ini_id0:ini_id1,2] = z[id_xyz0:id_xyz1,:].flatten()
    else:
        vertices[ini_id0:ini_id1,0] = x[id_xyz0:id_xyz1,:-1].flatten()
        vertices[ini_id0:ini_id1,1] = y[id_xyz0:id_xyz1,:-1].flatten()
        vertices[ini_id0:ini_id1,2] = z[id_xyz0:id_xyz1,:-1].flatten()

    # === Find faces
    faces = np.zeros((ntriangle,3), dtype=np.int32)
    ini_id = 0
    for ith in range (0, reso_theta-1):
        if (theta[ith] == 0.):
            # Case of direct triangle
            ind_above = 0
            ind_below = np.arange(reso_phi) + 1
            ind_below_p1 = np.concatenate((ind_below[1:], [ind_below[0]]))
            if (phi[-1] < math.tau):
                faces[0:reso_phi-1,0]=np.full(reso_phi, ind_above)[:-1] # p0
                faces[0:reso_phi-1,1]=ind_below[:-1]                    # p1 
                faces[0:reso_phi-1,2]=ind_below_p1[:-1]                 # p2
                ini_id+=reso_phi-1
            else:
                faces[0:reso_phi,0]=np.full(reso_phi, ind_above) # p0
                faces[0:reso_phi,1]=ind_below                    # p1 
                faces[0:reso_phi,2]=ind_below_p1                 # p2
                ini_id+=reso_phi
        elif(theta[ith]>0. and theta[ith+1]<math.pi):
            # case with polygones of 4 vertices, then split in 2 to get triangles
            if (ini_id == 0): p0_id=0
            else: p0_id = np.max(faces)+1 - reso_phi
            ind_above = np.arange(reso_phi) + p0_id
            ind_above_p1 = np.concatenate((ind_above[1:], [ind_above[0]]))
            ind_below = np.arange(reso_phi) + np.max(ind_above) + 1
            ind_below_p1 = np.concatenate((ind_below[1:], [ind_below[0]]))
            if (phi[-1] < math.tau):
                p0_id_t0 = ind_above[:-1]
                p1_id_t0 = ind_below[:-1]
                p2_id_t0 = ind_below_p1[:-1]
                p0_id_t1 = ind_above[:-1]
                p1_id_t1 = ind_below_p1[:-1]
                p2_id_t1 = ind_above_p1[:-1]
                p0_id_t = np.zeros((p0_id_t0.size+p0_id_t1.size), dtype=np.int32)
                p1_id_t = np.zeros((p1_id_t0.size+p1_id_t1.size), dtype=np.int32)
                p2_id_t = np.zeros((p2_id_t0.size+p2_id_t1.size), dtype=np.int32)
                p0_id_t[0::2] = p0_id_t0
                p0_id_t[1::2] = p0_id_t1
                p1_id_t[0::2] = p1_id_t0
                p1_id_t[1::2] = p1_id_t1
                p2_id_t[0::2] = p2_id_t0
                p2_id_t[1::2] = p2_id_t1
                ini_id0 = ini_id
                ini_id1 = (ini_id)+2*(reso_phi-1)
                faces[ini_id0:ini_id1,0] = p0_id_t
                faces[ini_id0:ini_id1,1] = p1_id_t
                faces[ini_id0:ini_id1,2] = p2_id_t
                ini_id += (reso_phi-1)*2   
            else:
                p0_id_t0 = ind_above
                p1_id_t0 = ind_below
                p2_id_t0 = ind_below_p1
                p0_id_t1 = ind_above
                p1_id_t1 = ind_below_p1
                p2_id_t1 = ind_above_p1
                p0_id_t = np.zeros((p0_id_t0.size+p0_id_t1.size), dtype=np.int32)
                p1_id_t = np.zeros((p1_id_t0.size+p1_id_t1.size), dtype=np.int32)
                p2_id_t = np.zeros((p2_id_t0.size+p2_id_t1.size), dtype=np.int32)
                p0_id_t[0::2] = p0_id_t0
                p0_id_t[1::2] = p0_id_t1
                p1_id_t[0::2] = p1_id_t0
                p1_id_t[1::2] = p1_id_t1
                p2_id_t[0::2] = p2_id_t0
                p2_id_t[1::2] = p2_id_t1
                ini_id0 = ini_id
                ini_id1 = (ini_id)+2*reso_phi
                faces[ini_id0:ini_id1,0] = p0_id_t
                faces[ini_id0:ini_id1,1] = p1_id_t
                faces[ini_id0:ini_id1,2] = p2_id_t
                ini_id += reso_phi*2
                
        else:
            if (ini_id == 0): p0_id=0
            else: p0_id = np.max(faces)+1 - reso_phi
            ind_above = np.arange(reso_phi) + p0_id
            ind_below = np.max(ind_above) + 1
            ind_above_p1 = np.concatenate((ind_above[1:], [ind_above[0]]))
            if (phi[-1] < math.tau):
                faces[-(reso_phi-1):,0]=ind_above[:-1]                    # p0
                faces[-(reso_phi-1):,1]=np.full(reso_phi, ind_below)[:-1] # p1
                faces[-(reso_phi-1):,2]=ind_below_p1[:-1]                 # p2
            else:
                faces[-reso_phi:,0]=ind_above                    # p0
                faces[-reso_phi:,1]=np.full(reso_phi, ind_below) # p1
                faces[-reso_phi:,2]=ind_below_p1                 # p2

    return TriangleMesh(vertices, faces, oTw, wTo)


def create_disk_trianglemesh(radius, inner_radius=0., reso=None, phi_max=360., z_height=0.,
                             oTw=None, wTo=None):
    """
    :meta private:

    Create a disk / partial disk / annulus / partial annulus triangleMesh

    Parameters
    ----------
    radius : float
        The disk radius
    inner_radius : float, optional
        The inner radius (case of annulus)
    reso : int, optional
        The number of lines around the polar phi angle, minimum accepted value is 3
    phi_max : float, optional
        The maximum phi value in degrees of the disk/annulus, where phi is between 0 and 360°
    z_height : float, optional
        the disk height along the z axis
    oTw : Transform, optional
        From object to world space or the transformation applied to the spheroid
    wTo : Transform, optional
        From world to object space or the in inverse transformation applied to the spheroid

    Results
    -------
    out : TriangleMesh
        The triangle mesh sphere
    
    Examples
    --------
    >>> import geoclide as gc
    >>> msh = gc.create_disk_trianglemesh(1)
    >>> msh
    <geoclide.trianglemesh.TriangleMesh at 0x7fa11c504940>
    """
    if wTo is None and oTw is None:
            wTo = Transform()
            oTw = Transform()
    if reso is None : reso = max(round(phi_max/10.), 10)
    if reso < 3 : raise ValueError("the value of reso must >= 3")

    if (phi_max == 360.): phi = np.linspace(0., math.tau, reso+1)[:-1]
    else: phi = np.linspace(0., math.radians(phi_max), reso)

    x = radius*np.cos(phi)
    y = radius*np.sin(phi)

    if inner_radius == 0.:
        # case complete disk
        nvertices = reso + 1
        if (phi_max == 360.): ntriangles = reso
        else: ntriangles = reso - 1
        vertices = np.zeros((nvertices,3), dtype=np.float64)
        vertices[1:,0] = x
        vertices[1:,1] = y
        vertices[:,2] = z_height
        vertices_id_outer = np.arange(reso, dtype=np.int32) + 1
        vertices_id_inner = np.zeros_like(vertices_id_outer)
        if (phi_max == 360.):
            p0_id = vertices_id_inner
            p1_id = vertices_id_outer
            p2_id = np.concatenate((vertices_id_outer[1:], [vertices_id_outer[0]]))
        else:
            p0_id = vertices_id_inner[:-1]
            p1_id = vertices_id_outer[:-1]
            p2_id = vertices_id_outer[1:]
        faces = np.zeros((ntriangles, 3), dtype=np.int32)
        faces[:,0] = p0_id
        faces[:,1] = p1_id
        faces[:,2] = p2_id
    else:
        x_inner = inner_radius*np.cos(phi)
        y_inner = inner_radius*np.sin(phi)
        nvertices = 2*reso
        if (phi_max == 360.): ntriangles = nvertices
        else: ntriangles = nvertices-2
        vertices = np.zeros((nvertices,3), dtype=np.float64)
        vertices[:,0] = np.concatenate((x_inner, x))
        vertices[:,1] = np.concatenate((y_inner, y))
        vertices[:,2] = z_height
        vertices_id_inner = np.arange(reso, dtype=np.int32)
        vertices_id_outer = vertices_id_inner + reso
        if (phi_max == 360.):
            p0_id_t0 = vertices_id_inner
            p1_id_t0 = vertices_id_outer
            p2_id_t0 = np.concatenate((vertices_id_outer[1:], [vertices_id_outer[0]]))
            p0_id_t1 = vertices_id_inner
            p1_id_t1 = np.concatenate((vertices_id_outer[1:], [vertices_id_outer[0]]))
            p2_id_t1 = np.concatenate((vertices_id_inner[1:], [vertices_id_inner[0]]))
        else:
            p0_id_t0 = vertices_id_inner[:-1]
            p1_id_t0 = vertices_id_outer[:-1]
            p2_id_t0 = vertices_id_outer[1:]
            p0_id_t1 = vertices_id_inner[:-1]
            p1_id_t1 = vertices_id_outer[1:]
            p2_id_t1 = vertices_id_inner[1:]
        p0_id_t = np.zeros((p0_id_t0.size+p0_id_t1.size), dtype=np.int32)
        p1_id_t = np.zeros((p1_id_t0.size+p1_id_t1.size), dtype=np.int32)
        p2_id_t = np.zeros((p2_id_t0.size+p2_id_t1.size), dtype=np.int32)
        p0_id_t[0::2] = p0_id_t0
        p0_id_t[1::2] = p0_id_t1
        p1_id_t[0::2] = p1_id_t0
        p1_id_t[1::2] = p1_id_t1
        p2_id_t[0::2] = p2_id_t0
        p2_id_t[1::2] = p2_id_t1
        faces = np.zeros((ntriangles, 3), dtype=np.int32)
        faces[:,0] = p0_id_t
        faces[:,1] = p1_id_t
        faces[:,2] = p2_id_t

    return TriangleMesh(vertices, faces, oTw, wTo)


def read_gcnc_trianglemesh(path, **kwargs):
    """
    Read geoclide netcdf4 format and convert it to a TriangleMesh class object

    Parameters
    ----------
    path : str
        The xarray filename_or_obj parameter
    **kwargs
        The keyword arguments are passed on to xarray open_dataset method

    Returns
    -------
    out : TriangleMesh
        The triangle mesh
    """
    if 'filename_or_obj' in kwargs: kwargs.pop('filename_or_obj', False)
    if not path.endswith('gcnc'):
        raise ValueError("Only the geoclide netcdf4 format (ending with 'gcnc') is accepted")
    if 'engine' in kwargs: engine = kwargs.pop('engine', False)
    else: engine = 'netcdf4'
    ds = xr.open_dataset(path, engine=engine, **kwargs)
    return TriangleMesh(ds['vertices'].values[0,:,:], ds['faces'].values[0,:,:])


def read_trianglemesh(path, **kwargs):
    """
    Open mesh file

    - if gcnc format use xarray, else use trimesh

    Parameters
    ----------
    path : str
        The xarray filename_or_obj or trimesh file_obj parameter
    **kwargs
        The keyword arguments are passed on to xarray open_dataset or trimesh load method
    
    Returns
    -------
    out : TriangleMesh
        The triangle mesh
    """

    if path.endswith('gcnc'):
        return read_gcnc_trianglemesh(path, **kwargs)
    else:
        msh = trimesh.load(path, **kwargs)
        return TriangleMesh(msh.vertices, msh.faces)
