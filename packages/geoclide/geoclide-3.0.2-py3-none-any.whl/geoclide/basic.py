#!/usr/bin/env python
# -*- coding: utf-8 -*-

import math 
import numpy as np
from geoclide.constante import GAMMA3_F64, VERSION
import xarray as xr
from datetime import datetime
import warnings


class Vector(object):
    """
    Parameters
    ----------
    x : float | 1-D ndarray | 2-D ndarray | Point | Vector | Normal, optional
        The x component(s) of the vector (see notes)
    y : float | 1-D ndarray, optional
        The y component(s) of the vector
    z : float | 1-D ndarray, optional
        The z component(s) of the vector

    Notes
    -----
    - if the parameter x is a 1-D ndarray of size 3 and y and z are None, the values of x, y and z
      will be equal to respectively x[0], x[1], and x[2]
    - if the parameter x is a 2-D ndarray of shape (n,3) and y and z are None, the values of x, y 
      and z will be equal to respectively x[:,0], x[:,1], and x[:,2]
    - if the parameter x is a Point, Vector or Normal, it will circumvent the y and z parameters 
      and take the components of the Point/Vector/Normal for x, y and z values

    Examples
    --------
    >>> import geoclide as gc
    >>> v1 = gc.Vector(0.,0.,1.)
    >>> v1
    Vector(0,0,1)
    """
    __array_priority__ = 1
    def __init__(self, x = None, y = None, z = None):
        if (x is None and y is None and z is None):
            self.x = 0.
            self.y = 0.
            self.z = 0.
        elif ( isinstance(x, Vector) or isinstance(x, Point) or isinstance(x, Normal) ):
            self.x = x.x
            self.y = x.y
            self.z = x.z
        elif (isinstance(x, np.ndarray) and (y is None and z is None)):
            if (len(x.shape) == 1 and len(x) == 3):
                self.x = float(x[0])
                self.y = float(x[1])
                self.z = float(x[2])
            elif(len(x.shape) == 2 and x.shape[1] == 3):
                self.x = x[:,0].astype(np.float64)
                self.y = x[:,1].astype(np.float64)
                self.z = x[:,2].astype(np.float64)
            else:ValueError("Wrong parameter value(s)")
        elif (np.isscalar(x) and np.isscalar(y) and np.isscalar(z)):
            self.x = float(x)
            self.y = float(y)
            self.z = float(z)
        elif (isinstance(x, np.ndarray) and isinstance(y, np.ndarray) and isinstance(z, np.ndarray)):
            self.x = x.astype(np.float64)
            self.y = y.astype(np.float64)
            self.z = z.astype(np.float64)
        else:
            raise ValueError("Wrong parameter value(s)")
        self.fmt = '.8f'

    def __eq__(self, v2):
        if isinstance(v2, Vector):
            if isinstance(self.x, np.ndarray) or isinstance(v2.x, np.ndarray) :
                return np.logical_and.reduce((self.x==v2.x, self.y==v2.y, self.z==v2.z))
            else:
                return (self.x==v2.x) and (self.y==v2.y) and (self.z==v2.z)
        else:
            raise ValueError('Equality with a Vector must be only with another Vector')

    def __add__(self, v2):
        if isinstance(v2, Vector):
            return Vector(self.x+v2.x, self.y+v2.y, self.z+v2.z) 
        else:
            raise ValueError('Addition with a Vector must be only with another Vector')

    def __sub__(self, v2):
        if isinstance(v2, Vector):
            return Vector(self.x-v2.x, self.y-v2.y, self.z-v2.z)
        else:
            raise ValueError('Substraction with a Vector must be only with another Vector')

    def __truediv__(self, sca):
        div = (1./sca)
        return Vector(self.x*div, self.y*div, self.z*div) 

    def __mul__(self, sca): 
        return Vector(sca*self.x, sca*self.y, sca*self.z)
        
    def __rmul__(self, sca): 
        return Vector(sca*self.x, sca*self.y, sca*self.z)
    
    def __neg__(self):
        return Vector(-self.x, -self.y, -self.z)

    def __getitem__(self, ind):
        if ( not isinstance(ind, int) or
             not isinstance(ind, np.integer) ):
            IndexError("Only an integer is a valid index")
        if ind == 0:
            return self.x
        elif ind == 1:
            return self.y
        elif ind == 2 :
            return self.z
        else:
            IndexError(f"Index {ind} is out of range") 

    def __str__(self):
        return print_basic(self)
    
    def __repr__(self):
        return print_basic(self, self.__class__.__name__)

    
    def length_squared(self):
        return self.x*self.x + self.y*self.y + self.z*self.z
    
    def length(self):
        if isinstance(self.x, np.ndarray): return np.sqrt(self.length_squared())
        else: return math.sqrt(self.length_squared())

    def to_numpy(self):
        if isinstance(self.x, np.ndarray) : return np.array([self.x, self.y, self.z], dtype=np.float64).T
        else : return np.array([self.x, self.y, self.z], dtype=np.float64)
    

class Point(object):
    """
    Parameters
    ----------
    x : float | 1-D ndarray | 2-D ndarray | Point | Vector | Normal, optional
        The x component(s) of the point (see notes)
    y : float | 1-D ndarray, optional
        The y component(s) of the point
    z : float | 1-D ndarray, optional
        The z component(s) of the point

    Notes
    -----
    - if the parameter x is a 1-D ndarray of size 3 and y and z are None, the values of x, y and z
      will be equal to respectively x[0], x[1], and x[2]
    - if the parameter x is a 2-D ndarray of shape (n,3) and y and z are None, the values of x, y 
      and z will be equal to respectively x[:,0], x[:,1], and x[:,2]
    - if the parameter x is a Point, Vector or Normal, it will circumvent the y and z parameters 
      and take the components of the Point/Vector/Normal for x, y and z values

    Examples
    --------
    >>> import geoclide as gc
    >>> p1 = gc.Point(0.,0.,1.)
    >>> p1
    Point(0,0,1)
    """
    __array_priority__ = 1
    def __init__(self, x = None, y = None, z = None):
        if (x is None and y is None and z is None):
            self.x = 0.
            self.y = 0.
            self.z = 0.
        elif ( isinstance(x, Vector) or isinstance(x, Point) or isinstance(x, Normal) ):
            self.x = x.x
            self.y = x.y
            self.z = x.z
        elif (isinstance(x, np.ndarray) and (y is None and z is None)):
            if (len(x.shape) == 1 and len(x) == 3):
                self.x = float(x[0])
                self.y = float(x[1])
                self.z = float(x[2])
            elif(len(x.shape) == 2 and x.shape[1] == 3):
                self.x = x[:,0].astype(np.float64)
                self.y = x[:,1].astype(np.float64)
                self.z = x[:,2].astype(np.float64)
            else:ValueError("Wrong parameter value(s)")
        elif (np.isscalar(x) and np.isscalar(y) and np.isscalar(z)):
            self.x = float(x)
            self.y = float(y)
            self.z = float(z)
        elif (isinstance(x, np.ndarray) and isinstance(y, np.ndarray) and isinstance(z, np.ndarray)):
            self.x = x.astype(np.float64)
            self.y = y.astype(np.float64)
            self.z = z.astype(np.float64)
        else:
            raise ValueError("Wrong parameter value(s)")
        self.fmt = '.8f'

    def __eq__(self, p2):
        if isinstance(p2, Point):
            if isinstance(self.x, np.ndarray) or isinstance(p2.x, np.ndarray) :
                return np.logical_and.reduce((self.x==p2.x, self.y==p2.y, self.z==p2.z))
            else:
                return (self.x==p2.x) and (self.y==p2.y) and (self.z==p2.z)
        else:
            raise ValueError('Equality with a Point must be only with another Point')

    def __add__(self, v):
        if isinstance(v, Vector) or isinstance(v, Point):
            return Point(self.x+v.x, self.y+v.y, self.z+v.z)
        else:
            raise ValueError('Addition with a Point must be only with a Vector or' +
                             ' (exceptionally tolerated) another Point')

    def __sub__(self, vp2):
        if isinstance(vp2, Vector):
            return Point(self.x-vp2.x, self.y-vp2.y, self.z-vp2.z)
        elif isinstance(vp2, Point):
            return Vector(self.x-vp2.x, self.y-vp2.y, self.z-vp2.z)
        else:
            raise ValueError('Substraction with a Point must be with another Point or a Vector')

    def __truediv__(self, sca):
        div = (1./sca)
        return Point(self.x*div, self.y*div, self.z*div)

    def __mul__(self, sca): 
        return Point(sca*self.x, sca*self.y, sca*self.z)

    def __rmul__(self, sca): 
        return Point(sca*self.x, sca*self.y, sca*self.z)
    
    def __neg__(self):
        return Point(-self.x, -self.y, -self.z)
    
    def __getitem__(self, ind):
        if ( not isinstance(ind, int) or
             not isinstance(ind, np.integer) ):
            IndexError("Only an integer is a valid index")
        if ind == 0:
            return self.x
        elif ind == 1:
            return self.y
        elif ind == 2 :
            return self.z
        else:
            IndexError(f"Index {ind} is out of range")

    def __str__(self):
        return print_basic(self)
    
    def __repr__(self):
        return print_basic(self, self.__class__.__name__)

    def to_numpy(self):
        if isinstance(self.x, np.ndarray) : return np.array([self.x, self.y, self.z], dtype=np.float64).T
        else : return np.array([self.x, self.y, self.z], dtype=np.float64)


class Normal(object):
    """
    Parameters
    ----------
    x : float | 1-D ndarray | 2-D ndarray | Point | Vector | Normal, optional
        The x component(s) of the normal (see notes)
    y : float | 1-D ndarray, optional
        The y component(s) of the normal
    z : float | 1-D ndarray, optional
        The z component(s) of the normal

    Notes
    -----
    - if the parameter x is a 1-D ndarray of size 3 and y and z are None, the values of x, y and z
      will be equal to respectively x[0], x[1], and x[2]
    - if the parameter x is a 2-D ndarray of shape (n,3) and y and z are None, the values of x, y 
      and z will be equal to respectively x[:,0], x[:,1], and x[:,2]
    - if the parameter x is a Point, Vector or Normal, it will circumvent the y and z parameters 
      and take the components of the Point/Vector/Normal for x, y and z values

    Examples
    --------
    >>> import geoclide as gc
    >>> n1 = gc.Normal(0.,0.,1.)
    >>> n1
    Normal(0,0,1)
    """
    __array_priority__ = 1
    def __init__(self, x = None, y = None, z = None):
        if (x is None and y is None and z is None):
            self.x = 0.
            self.y = 0.
            self.z = 0.
        elif ( isinstance(x, Vector) or isinstance(x, Point) or isinstance(x, Normal) ):
            self.x = x.x
            self.y = x.y
            self.z = x.z
        elif (isinstance(x, np.ndarray) and (y is None and z is None)):
            if (len(x.shape) == 1 and len(x) == 3):
                self.x = float(x[0])
                self.y = float(x[1])
                self.z = float(x[2])
            elif(len(x.shape) == 2 and x.shape[1] == 3):
                self.x = x[:,0].astype(np.float64)
                self.y = x[:,1].astype(np.float64)
                self.z = x[:,2].astype(np.float64)
            else:ValueError("Wrong parameter value(s)")
        elif (np.isscalar(x) and np.isscalar(y) and np.isscalar(z)):
            self.x = float(x)
            self.y = float(y)
            self.z = float(z)
        elif (isinstance(x, np.ndarray) and isinstance(y, np.ndarray) and isinstance(z, np.ndarray)):
            self.x = x.astype(np.float64)
            self.y = y.astype(np.float64)
            self.z = z.astype(np.float64)
        else:
            raise ValueError("Wrong parameter value(s)")
        self.fmt = '.8f'

    def __eq__(self, n2):
        if isinstance(n2, Normal):
            if isinstance(self.x, np.ndarray) or isinstance(n2.x, np.ndarray) :
                return np.logical_and.reduce((self.x==n2.x, self.y==n2.y, self.z==n2.z))
            else:
                return (self.x==n2.x) and (self.y==n2.y) and (self.z==n2.z)
        else:
            raise ValueError('Equality with a Normal must be only with another Normal')

    def __add__(self, n2):
        if isinstance(n2, Normal):
            return Normal(self.x+n2.x, self.y+n2.y, self.z+n2.z) 
        else:
            raise ValueError('Addition with a Normal must be only with another Normal')

    def __sub__(self, n2):
        if isinstance(n2, Normal):
            return Normal(self.x-n2.x, self.y-n2.y, self.z-n2.z)
        else:
            raise ValueError('Substraction with a Normal must be only with another Normal')

    def __truediv__(self, sca):
        div = (1./sca)
        return Normal(self.x*div, self.y*div, self.z*div) 

    def __mul__(self, sca):
        return Normal(sca*self.x, sca*self.y, sca*self.z)
    
    def __rmul__(self, sca):
        return Normal(sca*self.x, sca*self.y, sca*self.z)
    
    def __neg__(self):
        return Normal(-self.x, -self.y, -self.z)
        
    def __getitem__(self, ind):
        if ( not isinstance(ind, int) or
             not isinstance(ind, np.integer) ):
            IndexError("Only an integer is a valid index")
        if ind == 0:
            return self.x
        elif ind == 1:
            return self.y
        elif ind == 2 :
            return self.z
        else:
            IndexError(f"Index {ind} is out of range")

    def __str__(self):
        return print_basic(self)
    
    def __repr__(self):
        return print_basic(self, self.__class__.__name__)
    
    def length_squared(self):
        return self.x*self.x + self.y*self.y + self.z*self.z
    
    def length(self):
        if isinstance(self.x, np.ndarray): return np.sqrt(self.length_squared())
        else: return math.sqrt(self.length_squared())

    def to_numpy(self):
        if isinstance(self.x, np.ndarray) : return np.array([self.x, self.y, self.z], dtype=np.float64).T
        else : return np.array([self.x, self.y, self.z], dtype=np.float64)   


class Ray(object):
    """
    Definition of ray:

    r(t) = o + t*d, where:

    - o is/are the origin point(s) of the ray(s)
    - d is/are the direction(s) of the ray(s)
    - t belongs to stricly positive real numbers

    Parameters
    ----------
    o : Point | Ray
        Origin point(s) of the ray(s).
        If the o parameter is a Ray -> circumvent all the parameters by the ray attributs
    d : Vector
        Direction(s) of the ray(s)
    mint : float, optional
        The minimum t value
    maxt : float, optional
        The maximum t value

    Examples
    --------
    >>> import geoclide as gc
    >>> o = gc.Point(0., 50., 2.)
    >>> d = gc.Vector(0.,0.,1.)
    >>> r = gc.Ray(o, d, mint=20, maxt=100)
    >>> r
    r(t) = (0.0, 50.0, 2.0) + t*(0.0, 0.0, 1.0) with t ∈ [20,100[
    """
    def __init__(self, o, d=None, mint = 0, maxt = float("inf")):
        if isinstance(o, Ray):
            self.o = o.o
            self.d = o.d
            self.mint = float(o.mint)
            self.maxt = float(o.maxt)
        else:
            if (not isinstance(o, Point)):
                raise ValueError("The parameter o must be a Point or a Ray")
            if (not isinstance(d, Vector)):
                raise ValueError("The parameter d must only be a Vector")
            if (not np.isscalar(mint) or not np.isscalar(maxt)):
                raise ValueError("The parameters mint and maxt must be both scalars")
            if (mint > maxt):
                raise ValueError("maxt must be greater than mint")
            self.o = o
            self.d = d
            self.mint = mint
            self.maxt = maxt

    def __call__(self, t):
        """
        Solve ray(s) equation(s)

        Parameters
        ----------
        t : float | 1-D ndarray
            The t rays(s) values(s). The value(s) must lie between mint and maxt
        
        Returns
        -------
        out : Point
            The result(s) of the equation r(t) = o + t*d
        
        Examples
        --------
        >>> import geoclide as gc
        >>> o = gc.Point(0., 0., 0.)
        >>> d = gc.Vector(1., 0., 0.)
        >>> r = gc.Ray(o, d)
        >>> t = 10.
        >>> r(t)
        Point(10., 0., 0.)
        """
        if (  (isinstance(t, np.ndarray) and np.any(np.logical_or(t < self.mint, t > self.maxt))) or
              (not isinstance(t, np.ndarray) and (t < self.mint or t > self.maxt))  ):
            raise ValueError(f"The value {t} is out of bounds. It must be between {self.mint} and {self.maxt}")
        else:
            return (self.o + self.d*t)
        
    def __getitem__(self, t):
        warnings.simplefilter('always', DeprecationWarning)
        warn_message = "\nThe use of square brackets is deprecated as of version 2.1.0 and will be\n" + \
            "no more possible in the future. Please use parenthesis instead."
        warnings.warn(warn_message, DeprecationWarning, stacklevel=1)
        return self(t)
        
    def __str__(self):
        if not isinstance(self.o.x, np.ndarray):
            return f'({self.o.x}, {self.o.y}, {self.o.z}) + t*({self.d.x}, {self.d.y}, {self.d.z})' + \
                f' with t ∈ [{self.mint},{self.maxt}['
        else:
            nrays = len(self.o.x)
            mint = np.zeros(nrays, dtype=np.float64)
            maxt = np.zeros_like(mint)
            mint[:] = self.mint
            maxt[:] = self.maxt
            output = ""
            if nrays <= 100 : 
                for ir in range (0, nrays):
                    output += f'({self.o.x[ir]}, {self.o.y[ir]}, {self.o.z[ir]}) + ' + \
                        f't{str(ir)}*({self.d.x[ir]}, {self.d.y[ir]}, {self.d.z[ir]})' + \
                        f' with t{str(ir)} ∈ [{mint[ir]},{maxt[ir]}['
                    if ir < nrays-1: output+= '\n'
            else:
                for ir in range (0, 97):
                    output += f'({self.o.x[ir]}, {self.o.y[ir]}, {self.o.z[ir]}) + ' + \
                        f't{str(ir)}*({self.d.x[ir]}, {self.d.y[ir]}, {self.d.z[ir]})' + \
                        f' with t{str(ir)} ∈ [{mint[ir]},{maxt[ir]}['
                    output+= '\n'
                output += '       ...\n'
                for ir in range (nrays-3, nrays):
                    output += f'({self.o.x[ir]}, {self.o.y[ir]}, {self.o.z[ir]}) + ' + \
                        f't{str(ir)}*({self.d.x[ir]}, {self.d.y[ir]}, {self.d.z[ir]})' + \
                        f' with t{str(ir)} ∈ [{mint[ir]},{maxt[ir]}['
                    if ir < nrays-1: output+= '\n'
            return output
        
    def __repr__(self):
        if not isinstance(self.o.x, np.ndarray):
            return f'r(t) = ({self.o.x}, {self.o.y}, {self.o.z}) + t*({self.d.x}, {self.d.y}, {self.d.z})' + \
                    f' with t ∈ [{self.mint},{self.maxt}['
        else:
            nrays = len(self.o.x)
            mint = np.zeros(nrays, dtype=np.float64)
            maxt = np.zeros_like(mint)
            mint[:] = self.mint
            maxt[:] = self.maxt
            output = ""
            if nrays <= 100 : 
                for ir in range (0, nrays):
                    output += f'r(t{str(ir)}) = ({self.o.x[ir]}, {self.o.y[ir]}, {self.o.z[ir]}) + ' + \
                        f't{str(ir)}*({self.d.x[ir]}, {self.d.y[ir]}, {self.d.z[ir]})' + \
                        f' with t{str(ir)} ∈ [{mint[ir]},{maxt[ir]}['
                    if ir < nrays-1: output+= '\n'
            else:
                for ir in range (0, 97):
                    output += f'r(t{str(ir)}) = ({self.o.x[ir]}, {self.o.y[ir]}, {self.o.z[ir]}) + ' + \
                        f't{str(ir)}*({self.d.x[ir]}, {self.d.y[ir]}, {self.d.z[ir]})' + \
                        f' with t{str(ir)} ∈ [{mint[ir]},{maxt[ir]}['
                    output+= '\n'
                output += '       ...\n'
                for ir in range (nrays-3, nrays):
                    output += f'r(t{str(ir)}) = ({self.o.x[ir]}, {self.o.y[ir]}, {self.o.z[ir]}) + ' + \
                        f't{str(ir)}*({self.d.x[ir]}, {self.d.y[ir]}, {self.d.z[ir]})' + \
                        f' with t{str(ir)} ∈ [{mint[ir]},{maxt[ir]}['
                    if ir < nrays-1: output+= '\n'
            return output


class BBox(object):
    '''
    Bounding Box

    Parameters
    ----------
    p1 : Point, optional
        Frist point(s) to use to create the bounding box(es)
    p2 : Point, optional
        Second point(s) to use to create the bounding box(es)

    Examples
    --------
    >>> import geoclide as gc
    >>> p1 = gc.Point(0., 0., 0.)
    >>> p2 = gc.Point(1., 1., 1.)
    >>> b1 = gc.BBox(p1, p2)
    >>> b1
    pmin=Point(0.0, 0.0, 0.0), pmax=Point(1.0, 1.0, 1.0)
    '''
    def __init__(self, p1=None, p2=None):
        if (isinstance(p1, Point) and isinstance(p2, Point)):
            if isinstance(p1.x, np.ndarray) or isinstance(p2.x, np.ndarray):
                self.pmin = Point(np.minimum(p1.x, p2.x), np.minimum(p1.y, p2.y), np.minimum(p1.z, p2.z))
                self.pmax = Point(np.maximum(p1.x, p2.x), np.maximum(p1.y, p2.y), np.maximum(p1.z, p2.z))  
            else:
                self.pmin = Point(min(p1.x, p2.x), min(p1.y, p2.y), min(p1.z, p2.z))
                self.pmax = Point(max(p1.x, p2.x), max(p1.y, p2.y), max(p1.z, p2.z))
        elif (p1 is None and p2 is None):
            self.pmin = Point(float("inf"), float("inf"), float("inf"))
            self.pmax = Point(float("-inf"), float("-inf"), float("-inf"))
        elif (isinstance(p1, Point) and p2 is None):
            self.pmin = p1
            self.pmax = p1
        elif (p1 is None and isinstance(p2, Point)):
            self.pmin = p2
            self.pmax = p2
        else:
            raise ValueError('The only parameters accepted are Point objects')
        
        # The 8 vertices of the BBox
        # - p0=pmin, then next 3 points are in the XY plane at z=pmin.z the order being anti-clockwise
        # - next 4 points are in the XY plane at z=pmax.z, starting with point p4 just above p0, so p6=pmax
        self.p0 = Point(self.pmin.x,self.pmin.y,self.pmin.z)
        self.p1 = Point(self.pmax.x,self.pmin.y,self.pmin.z)
        self.p2 = Point(self.pmax.x,self.pmax.y,self.pmin.z)
        self.p3 = Point(self.pmin.x,self.pmax.y,self.pmin.z)
        self.p4 = Point(self.pmin.x,self.pmin.y,self.pmax.z)
        self.p5 = Point(self.pmax.x,self.pmin.y,self.pmax.z)
        self.p6 = Point(self.pmax.x,self.pmax.y,self.pmax.z)
        self.p7 = Point(self.pmin.x,self.pmax.y,self.pmax.z)
        self.vertices = [self.p0, self.p1, self.p2, self.p3,
                         self.p4, self.p5, self.p6, self.p7]
        
    def __str__(self):
        return f'pmin=({self.pmin.x}, {self.pmin.y}, {self.pmin.z}), pmax=({self.pmax.x}, {self.pmax.y}, {self.pmax.z})'
        
    def __repr__(self):
        return f'pmin=Point({self.pmin.x}, {self.pmin.y}, {self.pmin.z}), pmax=Point({self.pmax.x}, {self.pmax.y}, {self.pmax.z})'
        
    def union(self, b):
        """
        Union with a point/set of points or a bounding box/set of bounding boxes

        Parameters
        ----------
        b : Point | BBox
            The point(s) or bounding box(es) to use for the union

        Returns
        -------
        b_union : BBox
            The new bounding box(es) after the union
        
        Examples
        --------
        >>> import geoclide as gc
        >>> p1 = gc.Point(0., 0., 0.)
        >>> p2 = gc.Point(1., 1., 1.)
        >>> p3 = gc.Point(1., 1., 3.)
        >>> b1 = gc.BBox(p1, p2)
        >>> b1
        pmin=Point(0.0, 0.0, 0.0), pmax=Point(1.0, 1.0, 1.0)
        >>> b2 = b1.union(p3)
        >>> b2
        pmin=Point(0.0, 0.0, 0.0), pmax=Point(1.0, 1.0, 3.0)
        """
        pmin = Point()
        pmax = Point()
        if isinstance(b, Point):
            if isinstance(b.x, np.ndarray) or isinstance(self.p0.x, np.ndarray):
                pmin.x = np.minimum(self.pmin.x, b.x)
                pmin.y = np.minimum(self.pmin.y, b.y)
                pmin.z = np.minimum(self.pmin.z, b.z)
                pmax.x = np.maximum(self.pmax.x, b.x)
                pmax.y = np.maximum(self.pmax.y, b.y)
                pmax.z = np.maximum(self.pmax.z, b.z)
            else:
                pmin.x = min(self.pmin.x, b.x)
                pmin.y = min(self.pmin.y, b.y)
                pmin.z = min(self.pmin.z, b.z)
                pmax.x = max(self.pmax.x, b.x)
                pmax.y = max(self.pmax.y, b.y)
                pmax.z = max(self.pmax.z, b.z)
        elif isinstance(b, BBox):
            if isinstance(b.p0.x, np.ndarray) or isinstance(self.p0.x, np.ndarray):
                pmin.x = np.minimum(self.pmin.x, b.pmin.x)
                pmin.y = np.minimum(self.pmin.y, b.pmin.y)
                pmin.z = np.minimum(self.pmin.z, b.pmin.z)
                pmax.x = np.maximum(self.pmax.x, b.pmax.x)
                pmax.y = np.maximum(self.pmax.y, b.pmax.y)
                pmax.z = np.maximum(self.pmax.z, b.pmax.z)
            else:
                pmin.x = min(self.pmin.x, b.pmin.x)
                pmin.y = min(self.pmin.y, b.pmin.y)
                pmin.z = min(self.pmin.z, b.pmin.z)
                pmax.x = max(self.pmax.x, b.pmax.x)
                pmax.y = max(self.pmax.y, b.pmax.y)
                pmax.z = max(self.pmax.z, b.pmax.z)
        else:
            raise ValueError('The union must be with another BBox or Point')

        return BBox(pmin, pmax)

    def is_inside(self, p):
        """
        Test if point(s) p is/are included in the bounding box(es)
        """
        if isinstance(self.p0.x, np.ndarray) or isinstance(p.x, np.ndarray):
            return np.logical_and.reduce(((p.x >= self.pmin.x), (p.x <= self.pmax.x), \
                                          (p.y >= self.pmin.y), (p.y <= self.pmax.y), \
                                          (p.z >= self.pmin.z), (p.z <= self.pmax.z)))
        else:
            return (p.x >= self.pmin.x) and (p.x <= self.pmax.x) and \
                   (p.y >= self.pmin.y) and (p.y <= self.pmax.y) and \
                   (p.z >= self.pmin.z) and (p.z <= self.pmax.z)

    def is_intersection(self, r, diag_calc=False) :
        """
        Test if a ray/rays intersect(s) the bounding box(es)

        Parameters
        ----------
        r : Ray
            The ray(s) to use for the intersection test(s)
        diag_calc : bool
            Perform diagonal calculations in case of multiple bounding boxes and rays, 
            the output is a 1-D array instead of a 2-D array where out[i] is calculated using 
            r(i) and bbox(i). The same size for the BBox and Ray objects is required.

        Returns
        -------
        out : bool | 1-D ndarray| 2-D ndarray
            If there is at least 1 intersection returns True, else False.

        Examples
        --------
        >>> import geoclide as gc
        >>> p1 = gc.Point(0., 0., 0.)
        >>> p2 = gc.Point(1., 1., 1.)
        >>> b1 = gc.BBox(p1, p2)
        pmin=Point(0.0, 0.0, 0.0), pmax=Point(1.0, 1.0, 1.0)
        >>> p3 = gc.Point(0.5, 0.5, 0.1)
        >>> v1 = gc.Vector(0., 0., 1.)
        >>> r1 = gc.Ray(p3, v1)
        >>> r1
        r(t) = (0.5, 0.5, 0.1) + t*(0.0, 0.0, 1.0) with t ∈ [0,inf[
        >>> b1.is_intersection(r1)
        True
        """
        t0, t1, is_intersection = self.intersect(r, diag_calc=diag_calc, ds_output=False)
        return is_intersection

    def intersect(self, r, diag_calc=False, ds_output=True) :
        """
        Test if a ray/rays intersect(s) the bounding box(es)

        There are 3 possibilities:

        - no intersection
        - only 1 intersection (case of ray located initially inside the BBox)
        - 2 intersections

        Parameters
        ----------
        r : Ray
            The ray(s) to use for the intersection test(s)
        diag_calc : bool, optional
            Perform diagonal calculations in case of multiple bounding boxes and rays, 
            the output is a 1-D array instead of a 2-D array where out[i] is calculated using 
            r(i) and bbox(i). The same size for the BBox and Ray objects is required.
        ds_output : Bool, optional
            If True the output is a dataset, else returns a tuple with intersection information variables

        Returns
        -------
        out : xr.Dataset | tuple
            Look-up table with the intersection information if ds_output is True, 
            else return a tuple. Form of the tuple:

            * t0 : None | float | 1-D ndarray | 2-D ndarray
                -> The t ray variable of the first intersection. In case of only 1 intersection 
                it represents nothing. 
            * t1 : None | float | 1-D ndarray | 2-D ndarray
                -> The t ray variable of the second intersection. In case of only 1 intersection, 
                t1 becomes the t ray variable of the first intersection.
            * is_intersection : bool | 1-D ndarray | 2-D ndarray
                -> If there is at least 1 intersection return True, else False.

        Examples
        --------
        >>> import geoclide as gc
        >>> p1 = gc.Point(0., 0., 0.)
        >>> p2 = gc.Point(1., 1., 1.)
        >>> b1 = gc.BBox(p1, p2)
        pmin=Point(0.0, 0.0, 0.0), pmax=Point(1.0, 1.0, 1.0)
        >>> p3 = gc.Point(0.5, 0.5, 0.1)
        >>> v1 = gc.Vector(0., 0., 1.)
        >>> r1 = gc.Ray(p3, v1)
        >>> r1
        r(t) = (0.5, 0.5, 0.1) + t*(0.0, 0.0, 1.0) with t ∈ [0,inf[
        >>> t0, t1, is_intersection = b1.intersect(r1, ds_output=False)
        >>> t0, t1, is_intersection
        (0.0, 0.9, True)
        >>> r1[t1]
        Point(0.5, 0.5, 1.0)
        """
        if not isinstance(r, Ray): raise ValueError('The given parameter must be a Ray')
        is_r_arr = isinstance(r.o.x, np.ndarray)
        is_bbox_arr = isinstance(self.pmin.x, np.ndarray)
        if is_r_arr and is_bbox_arr and not diag_calc:
            with np.errstate(divide='ignore', invalid='ignore'):
                b_size = len(self.pmin.x)
                r_size = len(r.o.x)
                t0 = np.zeros((b_size, r_size), dtype=np.float64)
                t1 = np.full((b_size, r_size), r.maxt, dtype=np.float64)
                is_intersection = np.full((b_size, r_size), True)
                invRayDir = np.zeros(r_size, dtype=np.float64)
                for i in range(3):
                        c0 = r.d[i] != 0
                        invRayDir[:] = math.inf
                        invRayDir[c0] = 1. / r.d[i][c0]
                        tNear = (self.pmin[i][:,None] - r.o[i][None,:]) * invRayDir
                        tFar  = (self.pmax[i][:,None] - r.o[i][None,:]) * invRayDir
                        c1 = tNear > tFar
                        tNear[c1], tFar[c1] = tFar[c1], tNear[c1]
                        tFar *= 1 + 2*GAMMA3_F64
                        c2 = np.logical_and(tNear > t0, is_intersection)
                        c3 = np.logical_and(tFar < t1, is_intersection)
                        t0[c2] = tNear[c2]
                        t1[c3] = tFar[c3]
                        c4 = t0>t1
                        is_intersection[c4] = False
                        t0[c4] = 0.
                        t1[c4] = 0.
            if ds_output : return get_bbox_intersect_dataset(self, r, t0, t1, is_intersection)
            else : return t0, t1, is_intersection
        elif is_r_arr or is_bbox_arr:
            with np.errstate(divide='ignore', invalid='ignore'):
                size = 1
                if is_bbox_arr: size = max(size, len(self.pmin.x))
                if is_r_arr: size = max(size, len(r.o.x))
                t0 = np.zeros(size, dtype=np.float64)
                t1 = np.full(size, r.maxt, dtype=np.float64)
                is_intersection = np.full(size, True)
                if is_r_arr:
                    invRayDir = np.zeros(size, dtype=np.float64)
                for i in range(3):
                    c0 = r.d[i] != 0
                    if is_r_arr:
                        invRayDir[:] = math.inf
                        invRayDir[c0] = 1. / r.d[i][c0]
                    else:
                        invRayDir = math.inf
                        if c0 : invRayDir = 1. / r.d[i]
                        else : invRayDir = math.inf
                    tNear = (self.pmin[i] - r.o[i]) * invRayDir
                    tFar  = (self.pmax[i] - r.o[i]) * invRayDir
                    c1 = tNear > tFar
                    tNear[c1], tFar[c1] = tFar[c1], tNear[c1]
                    tFar *= 1 + 2*GAMMA3_F64
                    c2 = np.logical_and(tNear > t0, is_intersection)
                    c3 = np.logical_and(tFar < t1, is_intersection)
                    t0[c2] = tNear[c2]
                    t1[c3] = tFar[c3]
                    c4 = t0>t1
                    is_intersection[c4] = False
                    t0[c4] = 0.
                    t1[c4] = 0.
            if ds_output : return get_bbox_intersect_dataset(self, r, t0, t1, is_intersection)
            else : return t0, t1, is_intersection
        else:
            t0 = 0.
            t1 = r.maxt
            for i in range(3):
                if r.d[i]!= 0 : invRayDir = 1. / r.d[i]
                else : invRayDir = math.inf
                tNear = (self.pmin[i] - r.o[i]) * invRayDir
                tFar  = (self.pmax[i] - r.o[i]) * invRayDir
                if (tNear > tFar): tNear, tFar = tFar, tNear
                tFar *= 1 + 2*GAMMA3_F64
                t0 = tNear if tNear > t0 else t0
                t1 = tFar  if  tFar < t1 else t1
                if (t0 > t1) :
                    if ds_output : get_bbox_intersect_dataset(self, r, 0., 0., False)
                    else : return 0., 0., False
            if ds_output : return get_bbox_intersect_dataset(self, r, t0, t1, True)
            else : return t0, t1, True

    def common_vertices(self, b):
        """
        Get a list of boolean checking which vertices (self) are common to
        the bounding box(es) b

        Parameters
        ----------
        b : BBox
            The secondary bounding box(es)
        
        Returns
        -------
        out : 1-D ndarray | 2D ndarray
            Returns an array of boolean values indicating if the bounding box(es) vertices 
            are common to the secondary b bounding box(es) vertices

        Examples
        --------
        >>> import geoclide as gc
        >>> b0 = gc.BBox(gc.Point(0., 0., 0.), gc.Point(1., 1., 1.))
        >>> b1 = gc.BBox(gc.Point(1., 0., 0.), gc.Point(2., 1., 1.))
        >>> b0.common_vertices(b1)
        array([False,  True,  True, False, False,  True,  True, False])
        >>> b1.common_vertices(b0)
        array([ True, False, False,  True,  True, False, False,  True])
        """
        return get_common_vertices(self,b)

    def common_face(self, b, fill_value=None):
        """
        Get the face index/indices which is/are common with one of the face(s) of 
        bounding box(es) b2
    
        The convention of index from face 0 to 5, for +X,-X,+Y,-Y,+Z,-Z:

        >>>    |F2|                     |+Y|
        >>> |F1|F4|F0|F5|  where ->  |-X|+Z|+X|-Z|
        >>>    |F3|                     |-Y|

        `More information <https://en.wikipedia.org/wiki/Cube_mapping>`_

        Parameters
        ----------
        b : BBox
            The secondary bounding box(es)
        fill_value : integer, optional
            In case there is no common face(s) returns fill_value

        Returns
        -------
        out : integer | fill_value | 1-D ndarray
            Returns the index/indices of the common face(s) or fill_value
        
        Examples
        --------
        >>> import geoclide as gc
        >>> b0 = gc.BBox(gc.Point(0., 0., 0.), gc.Point(1., 1., 1.))
        >>> b1 = gc.BBox(gc.Point(1., 0., 0.), gc.Point(2., 1., 1.))
        >>> gc.get_common_face(b1, b2)
        0
        >>> gc.get_common_face(b2, b1)
        1
        """
        return get_common_face(self, b, fill_value=fill_value)


def get_common_vertices(b1, b2):
    """
    Check which vertices of bounding box(es) b1 are common to the vectices 
    of bounding box(es) b2

    Parameters
    ----------
    b1 : BBox
        The principal bounding box(es)
    b2 : BBox
        The secondary bounding box(es)
    
    Returns
    -------
    out : 1-D ndarray | 2D ndarray
        Returns an array of boolean values indicating whether the principal 
        bounding box(es) b1 vertices are common to the secondary bounding box(es) 
        b2 vertices.

    Examples
    --------
    >>> import geoclide as gc
    >>> b0 = gc.BBox(gc.Point(0., 0., 0.), gc.Point(1., 1., 1.))
    >>> b1 = gc.BBox(gc.Point(1., 0., 0.), gc.Point(2., 1., 1.))
    >>> gc.get_common_vertices(b1, b2)
    array([False,  True,  True, False, False,  True,  True, False])
    >>> gc.get_common_vertices(b1, b2)
    array([ True, False, False,  True,  True, False, False,  True])
    """
    if not isinstance(b1, BBox) or not isinstance(b2, BBox):
        raise ValueError("The parameters b1 and b2 must be both BBox objects")
    
    size = 1
    if isinstance(b1.p0.x, np.ndarray): size = max(len(b1.p0.x), size)
    if isinstance(b2.p0.x, np.ndarray): size = max(len(b2.p0.x), size)
        
    if size > 1:
        res = np.full((size, 8), False, dtype=bool)
        for i in range (0, 8):
            res[:,i] = np.logical_or.reduce((b1.vertices[i]==b2.vertices[0],
                                             b1.vertices[i]==b2.vertices[1],
                                             b1.vertices[i]==b2.vertices[2],
                                             b1.vertices[i]==b2.vertices[3],
                                             b1.vertices[i]==b2.vertices[4],
                                             b1.vertices[i]==b2.vertices[5],
                                             b1.vertices[i]==b2.vertices[6],
                                             b1.vertices[i]==b2.vertices[7]))
        return res
    else:
        return np.array(list((map(lambda x: x in b2.vertices, b1.vertices))))


def get_common_face(b1, b2, fill_value=None):
    """

    Get the face index/indices of the bounding box(es) b1 which is/are common 
    to the bounding box(es) b2
    
    The convention of index from face 0 to 5, for +X,-X,+Y,-Y,+Z,-Z:

    >>>    |F2|                     |+Y|
    >>> |F1|F4|F0|F5|  where ->  |-X|+Z|+X|-Z|
    >>>    |F3|                     |-Y|

    `More information <https://en.wikipedia.org/wiki/Cube_mapping>`_

    Parameters
    ----------
    b1 : BBox
        The principal bounding box(es)
    b2 : BBox
        The secondary bounding box(es)
    fill_value : integer, optional
            In case there is no common face(s) returns fill_value

    Returns
    -------
    out : integer | fill_value | 1-D ndarray
        Returns the index/indices of the common face(s) or fill_value

    Examples
    --------
    >>> import geoclide as gc
    >>> b0 = gc.BBox(gc.Point(0., 0., 0.), gc.Point(1., 1., 1.))
    >>> b1 = gc.BBox(gc.Point(1., 0., 0.), gc.Point(2., 1., 1.))
    >>> gc.get_common_face(b1, b2)
    0
    >>> gc.get_common_face(b2, b1)
    1
    """
    ok = get_common_vertices(b1,b2)
    if len(ok.shape) > 1 :
        size1 = ok.shape[0]
        cond = ok.sum(axis=1) == 4
        res = np.full(size1, fill_value, dtype=np.float64)
        if any(cond):
            n = np.zeros((size1,8), dtype=np.int32)
            for i in range (0, 8):
                n[:,i] = i
            size2 = cond.sum()
            res_bis = res[cond]
            n = n[cond][ok[cond]].reshape(size2,4)
            m1 = np.repeat(np.array([[1, 2, 5, 6]]), size2, axis=0)
            m2 = np.repeat(np.array([[0, 3, 4, 7]]), size2, axis=0)
            m3 = np.repeat(np.array([[2, 3, 6, 7]]), size2, axis=0)
            m4 = np.repeat(np.array([[0, 1, 4, 5]]), size2, axis=0)
            m5 = np.repeat(np.array([[4, 5, 6, 7]]), size2, axis=0)
            m6 = np.repeat(np.array([[0, 1, 2, 3]]), size2, axis=0)
            res_bis[np.all(n == m1, axis=1)] = 0
            res_bis[np.all(n == m2, axis=1)] = 1
            res_bis[np.all(n == m3, axis=1)] = 2
            res_bis[np.all(n == m4, axis=1)] = 3
            res_bis[np.all(n == m5, axis=1)] = 4
            res_bis[np.all(n == m6, axis=1)] = 5
        res[cond] = res_bis
        return res
    else:
        if ok.sum()==4:
            n  = np.arange(8)[ok]
            if   np.array_equal(n, np.array([1,2,5,6])):
                return 0
            elif np.array_equal(n, np.array([0,3,4,7])):
                return 1
            elif np.array_equal(n, np.array([2,3,6,7])):
                return 2
            elif np.array_equal(n, np.array([0,1,4,5])):
                return 3
            elif np.array_equal(n, np.array([4,5,6,7])):
                return 4
            elif np.array_equal(n, np.array([0,1,2,3])):
                return 5
            else: return fill_value

        else :
            return fill_value


def get_bbox_intersect_dataset(bbox, r, t0=None, t1=None, is_intersection=False, diag_calc=False):
    """
    Create dataset containing the intersection test information

    - The intersect method return of BBox class gives the t0, t1 and is_intersection 
      inputs of this function

    Parameters
    ----------
    bbox : BBox
        The bounding box(es) used for the intersection test
    r : Ray
        The ray(s) used for the intersection test
    t0 : float | 1-D ndarray | 2-D ndarray
        The t ray variable of the first intersection
    t1 : float | 1-D ndarray | 2-D ndarray
        The t ray variable of the second intersection
    is_intersection : bool | 1-D ndarray | 2-D ndarray, optional
        If there is an intersection returns True, else False
    diag_cal : bool, optional
            This indicates whether diagonal calculations have been performed

    Returns
    -------
    out : xr.Dataset
        Look-up table with the intersection information
    """
    is_r_arr = isinstance(r.o.x, np.ndarray)
    is_bbox_arr = isinstance(bbox.pmin.x, np.ndarray)

    ds = xr.Dataset(coords={'xyz':np.arange(3)})

    if is_r_arr:
        nrays = len(r.o.x)
        ro = r.o.to_numpy()
        rd = r.d.to_numpy()
        ds['o'] = xr.DataArray(ro, dims=['nrays', 'xyz'])
        ds['d'] = xr.DataArray(rd, dims=['nrays', 'xyz'])
        mint = np.zeros(nrays, dtype=np.float64)
        maxt = np.zeros_like(mint)
        mint[:] = r.mint
        maxt[:] = r.maxt
        ds['mint'] = xr.DataArray(mint, dims=['nrays'])
        ds['maxt'] = xr.DataArray(maxt, dims=['nrays'])
    else:
        ds['o'] = xr.DataArray(r.o.to_numpy(), dims=['xyz'])
        ds['d'] = xr.DataArray(r.d.to_numpy(), dims=['xyz'])
        ds['mint'] = xr.DataArray(r.mint)
        ds['maxt'] = xr.DataArray(r.maxt)

    if is_r_arr or is_bbox_arr:
        c1 = t0 > 0
        not_c1 = np.logical_not(c1)
        thit = np.full((t0.shape), np.nan, dtype=np.float64)
        c2 = np.logical_and(is_intersection, c1)
        c3 = np.logical_and(is_intersection, not_c1)
        if np.any(c2): thit[c2] = t0[c2]
        if np.any(c3): thit[c3] = t1[c3]

    if is_r_arr and is_bbox_arr and not diag_calc:
        nobj = len(bbox.p0.x)
        ds.attrs.update({'nobj': nobj, 'nrays': nrays})
        ds['is_intersection'] = xr.DataArray(is_intersection, dims=['nobj', 'nrays'])
        ds['thit'] = xr.DataArray(thit, dims=['nobj', 'nrays'])
        phit = np.zeros((nobj, nrays, 3), dtype=np.float64)
        for ir in range (0, nrays):
            ri = Ray(Point(ro[ir,:]), Vector(rd[ir,:]), mint[ir], maxt[ir])
            phit[:,ir,:] = ri[thit[:,ir]].to_numpy()
        ds['phit'] = xr.DataArray(phit, dims=['nobj', 'nrays', 'xyz'])
    elif is_r_arr or is_bbox_arr:
        if diag_calc :
            dim_name = 'ndiag'
            size = nrays
            ds.attrs.update({'nobj': size, 'nrays': size})
        elif is_r_arr:
            dim_name = 'nrays'
            size = nrays
        else:
            dim_name = 'nobj'
            size = len(bbox.p0.x)
        ds.attrs.update({dim_name: size})
        phit = r(thit).to_numpy()
        ds['is_intersection'] = xr.DataArray(is_intersection, dims=[dim_name])
        ds['thit'] = xr.DataArray(thit, dims=[dim_name])
        ds['phit'] = xr.DataArray(phit, dims=[dim_name, 'xyz'])
    else:
        if (t0 is None) : thit = None
        elif (t0 > 0) : thit = t0
        else : thit = t1
        phit = r(thit).to_numpy()
        ds['is_intersection'] = xr.DataArray(is_intersection)
        ds['thit'] = xr.DataArray(thit)
        ds['phit'] = xr.DataArray(phit, dims=['xyz'])
        
    ds['o'].attrs = {'type': 'Point', 'description':'the x, y and z components of the ray point'}
    ds['d'].attrs = {'type': 'Vector', 'description':'the x, y and z components of the ray vector'}
    ds['mint'].attrs = {'description':'the mint attribut of the ray'}
    ds['maxt'].attrs = {'description':'the maxt attribut of the ray'}
    ds['is_intersection'].attrs = {'description':'this variable tells if there is an intersection between the ray and the shape'}
    ds['thit'].attrs = {'description':'the t ray factor for the intersection point calculation'}
    ds['phit'].attrs = {'type': 'Point', 'description':'the x, y and z components of the intersection point'}
    ds.attrs = {'shape': bbox.__class__.__name__}
    date = datetime.now().strftime("%Y-%m-%d")  
    ds.attrs.update({'date':date, 'version': VERSION})
    return ds


def print_basic(basic, name=""):
    """
    :meta private:

    Parameters
    ----------
    basic : Vector | Point | Normal
        The basic object
    name : str, optional
        The str name to show at the start

    Returns
    -------
    out : str
        The return for the method __repr__ or __str___
    """
    if not isinstance(basic.x, np.ndarray):
        return name + '(' + str(basic.x) + ', ' + str(basic.y) + ', ' + str(basic.z) + ')'
    else:
        size_name = len(name)
        if (size_name >0) : first_space = f"{'':{size_name+2}}"
        else : first_space = "  "
        ncomponents = len(basic.x)
        values = basic.to_numpy()
        space = np.empty_like(values, dtype=str)
        space[values>=0] = " "
        space[values<0] = ""
        fmt = basic.fmt
        output = ""
        if ncomponents <= 100 :
            for i in range (0, ncomponents):
                if i == 0:
                    output += f'{name}([[{space[i,0]}{basic.x[i]:{fmt}}, {space[i,1]}{basic.y[i]:{fmt}}, {space[i,2]}{basic.z[i]:{fmt}}],\n'
                elif i == ncomponents-1:
                    output += f'{first_space}[{space[i,0]}{basic.x[i]:{fmt}}, {space[i,1]}{basic.y[i]:{fmt}}, {space[i,2]}{basic.z[i]:{fmt}}]])'
                else:
                    output += f'{first_space}[{space[i,0]}{basic.x[i]:{fmt}}, {space[i,1]}{basic.y[i]:{fmt}}, {space[i,2]}{basic.z[i]:{fmt}}],\n'
        else:
            for i in range (0, 97):
                if i == 0:
                    output += f'{name}([[{space[i,0]}{basic.x[i]:{fmt}}, {space[i,1]}{basic.y[i]:{fmt}}, {space[i,2]}{basic.z[i]:{fmt}}],\n'
                else:
                    output += f'{first_space}[{space[i,0]}{basic.x[i]:{fmt}}, {space[i,1]}{basic.y[i]:{fmt}}, {space[i,2]}{basic.z[i]:{fmt}}],\n'
            output += '       ...\n'
            for i in range (ncomponents-3, ncomponents):
                if i == ncomponents-1:
                    output += f'{first_space}[{space[i,0]}{basic.x[i]:{fmt}}, {space[i,1]}{basic.y[i]:{fmt}}, {space[i,2]}{basic.z[i]:{fmt}}]])'
                else:
                    output += f'{first_space}[{space[i,0]}{basic.x[i]:{fmt}}, {space[i,1]}{basic.y[i]:{fmt}}, {space[i,2]}{basic.z[i]:{fmt}}],\n'
        return output