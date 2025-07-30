#!/usr/bin/env python
# -*- coding: utf-8 -*-

from geoclide.basic import Ray, BBox
from geoclide.quadrics import Sphere, Spheroid, Disk
from geoclide.trianglemesh import Triangle, TriangleMesh
from geoclide.shapes import Shape
import xarray as xr


def calc_intersection(shape, r, **kwargs):
    """
    Performs intersection test between a shape and a ray and returns dataset

    Parameters
    ----------
    shape : BBox | Sphere | Spheroid | Disk | Triangle | TriangleMesh
        The shape used for the intersection(s)
    r : Ray
        The ray(s) used for the intersection(s)
    **kwargs
        The keyword arguments are passed on to intersect method. The ds_output parameter 
        is forced here to always be True.

    Returns
    -------
    out : xr.Dataset
        Look-up table with the intersection information
    
    Examples
    --------
    >>> import geoclide as gc
    >>> sphere = gc.Sphere(radius=1.) # sphere of radius 1
    >>> bbox = gc.BBox(p1=gc.Point(0., 0., 0.), p2=gc.Point(1.,1.,1.))
    >>> ray = gc.Ray(o=gc.Point(-2., 0., 0.8), d=gc.Vector(1.,0.,0.))
    >>> ds_sphere = gc.calc_intersection(sphere, ray)
    >>> ds_sphere
    <xarray.Dataset> Size: 753B
    Dimensions:          (xyz: 3, dim_0: 4, dim_1: 4)
    Coordinates:
    * xyz              (xyz) int64 24B 0 1 2
    Dimensions without coordinates: dim_0, dim_1
    Data variables: (12/20)
        o                (xyz) float64 24B -2.0 0.0 0.8
        d                (xyz) float64 24B 1.0 0.0 0.0
        mint             int64 8B 0
        maxt             float64 8B inf
        is_intersection  bool 1B True
        thit             float64 8B 1.4
        ...               ...
        z_max            float64 8B 1.0
        phi_max          float64 8B 360.0
        wTo_m            (dim_0, dim_1) float64 128B 1.0 0.0 0.0 0.0 ... 0.0 0.0 1.0
        wTo_mInv         (dim_0, dim_1) float64 128B 1.0 0.0 0.0 0.0 ... 0.0 0.0 1.0
        oTw_m            (dim_0, dim_1) float64 128B 1.0 0.0 0.0 0.0 ... 0.0 0.0 1.0
        oTw_mInv         (dim_0, dim_1) float64 128B 1.0 0.0 0.0 0.0 ... 0.0 0.0 1.0
    >>> ds_box = gc.calc_intersection(bbox, ray)
    >>> ds_bbox
    <xarray.Dataset> Size: 169B
    Dimensions:          (xyz: 3)
    Coordinates:
    * xyz              (xyz) int64 24B 0 1 2
    Data variables:
        is_intersection  bool 1B True
        o                (xyz) float64 24B -2.0 0.0 0.8
        d                (xyz) float64 24B 1.0 0.0 0.0
        mint             int64 8B 0
        maxt             float64 8B inf
        pmin             (xyz) float64 24B 0.0 0.0 0.0
        pmax             (xyz) float64 24B 1.0 1.0 1.0
        thit             float64 8B 2.0
        phit             (xyz) float64 24B 0.0 0.0 0.8
    """
    if (not isinstance(r, Ray)):
        raise ValueError('The parameter r1 must a Ray')

    if 'ds_output' in kwargs: kwargs.pop('ds_output', False)
    if (isinstance(shape, BBox)) or issubclass(shape.__class__, Shape):
        ds = shape.intersect(r, ds_output=True, **kwargs)
    else:
        raise ValueError('The only supported shape are: BBox, Sphere, Spheroid, Disk, ' +
                         'Triangle and TriangleMesh')

    if (isinstance(shape, BBox)):
        ds['pmin'] = xr.DataArray(shape.pmin.to_numpy(), dims='xyz')
        ds['pmin'].attrs = {'type': 'Point', 'description':'the x, y and z components of the pmin BBox attribut'}
        ds['pmax'] = xr.DataArray(shape.pmax.to_numpy(), dims='xyz')
        ds['pmax'].attrs = {'type': 'Point', 'description':'the x, y and z components of the pmax BBox attribut'}
    if (isinstance(shape, Sphere)):
        ds['radius'] = shape.radius
        ds['radius'].attrs = {'description':'the sphere radius attribut'}
        ds['z_min'] = shape.zmin
        ds['z_min'].attrs = {'description':'the sphere zmin attribut'}
        ds['z_max'] = shape.zmax
        ds['z_max'].attrs = {'description':'the sphere zmax attribut'}
        ds['phi_max'] = shape.phi_max
        ds['phi_max'].attrs = {'unit':'Degree', 'description':'the sphere phi_max attribut'}
    if (isinstance(shape, Spheroid)):
        ds['radius_xy'] = shape.alpha
        ds['radius_xy'].attrs = {'description':'the equatorial radius of the spheroid (alpha attribut)'}
        ds['radius_z'] = shape.gamma
        ds['radius_z'].attrs = {'description':'the distance between the spheroid center and pole (gamma attribut)'}
    if (isinstance(shape, Disk)):
        ds['radius'] = shape.radius
        ds['radius'].attrs = {'description':'the radius of the disk'}
        ds['inner_radius'] = shape.inner_radius
        ds['inner_radius'].attrs = {'description':'the inner radius of the disk (if > 0 -> annulus case)'}
        ds['phi_max'] = shape.phi_max
        ds['phi_max'].attrs = {'unit':'Degree', 'description':'the disk phi_max attribut'}
        ds['z_height'] = shape.z_height
        ds['z_height'].attrs = {'description':'the disk z_height attribut'}
    if (isinstance(shape, Triangle)):
        ds['p0'] = xr.DataArray(shape.p0.to_numpy(), dims='xyz')
        ds['p0'].attrs = {'description': 'the triangle p0 attribut'}
        ds['p1'] = xr.DataArray(shape.p1.to_numpy(), dims='xyz')
        ds['p1'].attrs = {'description': 'the triangle p1 attribut'}
        ds['p2'] = xr.DataArray(shape.p2.to_numpy(), dims='xyz')
        ds['p2'].attrs = {'description': 'the triangle p2 attribut'}
    if (isinstance(shape, TriangleMesh)):
        ds['vertices'] = xr.DataArray(shape.vertices, dims=['nvertices', 'xyz'])
        ds['vertices'].attrs = {'description': 'The vertices xyz coordinates.'}
        ds['faces'] = xr.DataArray(shape.faces, dims=['ntriangles', 'p0p1p2'])
        ds['faces'].attrs = {'description': 'For each triangle, the index of vertices point p0, p1 and p2 (from variable v).'}
        ds.attrs.update({'ntriangles': shape.ntriangles, 'nvertices' : shape.nvertices})
    if (not isinstance(shape, BBox)):
        ds['wTo_m'] = xr.DataArray(shape.wTo.m)
        ds['wTo_m'].attrs = {'description':'the transformation matrix of the ' + str(ds.attrs['shape']).lower() + ' wTo attribut'}
        ds['wTo_mInv'] = xr.DataArray(shape.wTo.mInv)
        ds['wTo_mInv'].attrs = {'description':'the inverse transformation matrix of the ' + str(ds.attrs['shape']).lower() + ' wTo attribut'}
        ds['oTw_m'] = xr.DataArray(shape.oTw.m)
        ds['oTw_m'].attrs = {'description':'the transformation matrix of the ' + str(ds.attrs['shape']).lower() + ' oTw attribut'}
        ds['oTw_mInv'] = xr.DataArray(shape.oTw.mInv)
        ds['oTw_mInv'].attrs = {'description':'the inverse transformation matrix of the ' + str(ds.attrs['shape']).lower() +' oTw attribut'}

    return ds