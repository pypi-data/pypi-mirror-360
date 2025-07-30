#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import geoclide as gc
import pytest
from geoclide.shapes import get_intersect_dataset

Q1 = [gc.Disk(radius=3., inner_radius=1.2),
      gc.Sphere(radius=3.),
      gc.Spheroid(radius_xy=3., radius_z=2.),
      gc.Spheroid(radius_xy=2., radius_z=3.)]


def test_sphere():
    # Take README exemple
    vza = 45.
    vaa = 45.
    sat_altitude = 700.
    origin = gc.Point(0., 0., 0.)
    theta = vza
    phi = -vaa

    dir_to_sat = gc.Vector(0., 0., 1.)
    dir_to_sat = gc.get_rotateY_tf(theta)(dir_to_sat)
    dir_to_sat = gc.get_rotateZ_tf(phi)(dir_to_sat)
    ray = gc.Ray(o=origin, d=dir_to_sat)

    earth_radius = 6378. 
    oTw = gc.get_translate_tf(gc.Vector(0., 0., -earth_radius))
    sphere_sat_alti = gc.Sphere(radius=earth_radius+sat_altitude, oTw=oTw)  # apply oTw to move the sphere center to earth center
    ds_sp = gc.calc_intersection(sphere_sat_alti, ray)

    p = ds_sp['phit'].values

    assert (np.isclose(p[0], 472.61058011386376, 0., 1e-15))
    assert (np.isclose(p[1], -472.61058011386365, 0., 1e-15))
    assert (np.isclose(p[2], 668.3722921180423, 0., 1e-15))
    assert (ds_sp['is_intersection'] == sphere_sat_alti.is_intersection(ray))


def test_spheroid():
    oblate = gc.Spheroid(radius_xy=3., radius_z=1.5)
    prolate = gc.Spheroid(radius_xy=1.5, radius_z=3.)
    r1 = gc.Ray(o=gc.Point(2.5, 0., 10.), d=(gc.Vector(0., 0., -1.)))
    r2 = gc.Ray(o=gc.Point(10., 0., 2.5), d=(gc.Vector(-1., 0., 0.)))
    
    ds = gc.calc_intersection(oblate, r1)
    p = ds['phit'].values
    assert (p[0] == 2.5)
    assert (p[1] == 0.)
    assert (np.isclose(p[2], 0.8291561975888655, 0., 1e-15))
    n = ds['nhit'].values
    assert (np.isclose(n[0], 0.6019292654288356, 0., 1e-15))
    assert (n[1] == 0.)
    assert (np.isclose(n[2], 0.7985494095046983, 0., 1e-15))
    assert (ds['is_intersection'].values == oblate.is_intersection(r1))

    ds = gc.calc_intersection(prolate, r2)
    p = ds['phit'].values
    assert (np.isclose(p[0], 0.8291561975888655, 0., 1e-15))
    assert (p[1] == 0.)
    assert (p[2] == 2.5)
    n = ds['nhit'].values
    assert (np.isclose(n[0], 0.7985494095046906, 0., 1e-15))
    assert (n[1] == 0.)
    assert (np.isclose(n[2], 0.6019292654288461, 0., 1e-15))

    assert (np.isclose(oblate.area(), 78.04694433010546, 0., 1e-15))
    assert (np.isclose(prolate.area(), 48.326479487738396, 0., 1e-15))
    assert (ds['is_intersection'].values == prolate.is_intersection(r2))


def test_disk():
    # 1) particular cases
    disk = gc.Disk(radius=1.5)
    ds = gc.calc_intersection(disk, gc.Ray(gc.Point(5.,0.,0.), gc.Vector(-1.,0.,0.)))
    assert (not ds['is_intersection'])
    ds = gc.calc_intersection(disk, gc.Ray(gc.Point(0.,0.,10.), gc.Vector(0.,0.,-1.), maxt=5.))
    assert (not ds['is_intersection'])

    disk = gc.Disk(radius=1., phi_max=90.)
    ds = gc.calc_intersection(disk, gc.Ray(gc.Point(0.8,-1e-5,10.), gc.Vector(0.,0.,-1.)))
    assert (not ds['is_intersection'])
    ds = gc.calc_intersection(disk, gc.Ray(gc.Point(0.8,1e-5,10.), gc.Vector(0.,0.,-1.)))
    assert (ds['is_intersection'])
    ds = gc.calc_intersection(disk, gc.Ray(gc.Point(-1e-5,0.8,10.), gc.Vector(0.,0.,-1.)))
    assert (not ds['is_intersection'])
    ds = gc.calc_intersection(disk, gc.Ray(gc.Point(+1e-5,0.8,10.), gc.Vector(0.,0.,-1.)))
    assert (ds['is_intersection'])

    # 2) general cases
    roty_90 = gc.get_rotateY_tf(90.)
    disk = gc.Disk(radius=1.5, z_height=5., oTw=roty_90)
    annulus = gc.Disk(radius=1.5, inner_radius=0.8, z_height=5., oTw=roty_90)
    d = gc.Vector(-1.,0.,0.)
    r1 = gc.Ray(gc.Point(10.,0.,1.2), d)
    r2 = gc.Ray(gc.Point(10.,0.,0.2), d)
    r3 = gc.Ray(gc.Point(10.,0.,1.6), d)

    # 2a) disk tests
    ds_disk = gc.calc_intersection(disk, r1)
    p = ds_disk['phit'].values
    assert (np.all(np.isclose(p, r1(disk.z_height).to_numpy(), 0., 1e-15)))
    assert (ds_disk['is_intersection'].values == disk.is_intersection(r1))
    ds_disk = gc.calc_intersection(disk, r2)
    p = ds_disk['phit'].values
    assert (np.all(np.isclose(p, r2(disk.z_height).to_numpy(), 0., 1e-15)))
    assert (ds_disk['is_intersection'].values == disk.is_intersection(r2))
    ds_disk = gc.calc_intersection(disk, r3)
    assert (not ds_disk['is_intersection'])
    assert (ds_disk['is_intersection'].values == disk.is_intersection(r3))

    # 2b) annulus tests
    ds_annulus = gc.calc_intersection(annulus, r1)
    p = ds_annulus['phit'].values
    assert (np.all(np.isclose(p, r1(annulus.z_height).to_numpy(), 0., 1e-15)))
    assert (ds_annulus['is_intersection'].values == annulus.is_intersection(r1))
    ds_annulus = gc.calc_intersection(annulus, r2)
    assert (not ds_annulus['is_intersection'])
    assert (ds_annulus['is_intersection'].values == annulus.is_intersection(r2))
    ds_annulus = gc.calc_intersection(annulus, r3)
    assert (not ds_annulus['is_intersection'])
    assert (ds_annulus['is_intersection'].values == annulus.is_intersection(r3))


@pytest.mark.parametrize('quadric', Q1)
def test_quadric_1d_arr(quadric):
    x_, y_, z_ = np.meshgrid(np.linspace(-1.5, 1.5, 10, np.float64),
                         np.linspace(-1.5, 1.5, 10, np.float64),
                         5., indexing='ij')
    o_set_arr = np.vstack((x_.ravel(), y_.ravel(), z_.ravel())).T
    nrays = o_set_arr.shape[0]
    d_set_arr = np.zeros_like(o_set_arr)
    d_set_arr[:,0] = 0.
    d_set_arr[:,1] = 0.
    d_set_arr[:,2] = -1.
    o_set = gc.Point(o_set_arr)
    d_set = gc.Vector(d_set_arr)
    r_set = gc.Ray(o_set, d_set)

    ds = quadric.intersect(r_set, ds_output=True)

    is_int_1d = np.full((nrays), True, dtype=bool)
    t_1d = np.zeros((nrays), dtype=np.float64)
    p_1d = np.zeros((nrays,3), dtype=np.float64)
    n_1d = np.zeros_like(p_1d)
    dpdu_1d = np.zeros_like(p_1d)
    dpdv_1d = np.zeros_like(p_1d)
    u_1d = np.zeros_like(t_1d)
    v_1d = np.zeros_like(t_1d)
    list_rays = []
    for ir in range (0, nrays):
        list_rays.append(gc.Ray(gc.Point(o_set_arr[ir,:]), gc.Vector(d_set_arr[ir,:])))

    for ir in range (0, nrays):
        res_sca = quadric.intersect(list_rays[ir], ds_output=False)
        if (res_sca[2] is not None):
            ds_sca = get_intersect_dataset(*res_sca)
            is_int_1d[ir] = ds_sca['is_intersection'].values
            t_1d[ir] = ds_sca['thit'].values
            p_1d[ir,:] = ds_sca['phit'].values
            n_1d[ir,:] = ds_sca['nhit'].values
            dpdu_1d[ir,:] = ds_sca['dpdu'].values
            dpdv_1d[ir,:] = ds_sca['dpdv'].values
            u_1d[ir] = ds_sca['u'].values
            v_1d[ir] = ds_sca['v'].values
        else:
            is_int_1d[ir] = False
            t_1d[ir] = None
            p_1d[ir,:] = None
            n_1d[ir,:] = None
            dpdu_1d[ir,:] = None
            dpdv_1d[ir,:] = None
            u_1d[ir] = None
            v_1d[ir] = None
    
    assert (np.array_equal(ds['is_intersection'].values, is_int_1d, equal_nan=True))
    assert (np.array_equal(ds['thit'].values, t_1d, equal_nan=True))
    assert (np.array_equal(ds['phit'].values, p_1d, equal_nan=True))
    assert (np.allclose(ds['nhit'].values, n_1d, 0., 1e-15, equal_nan=True))
    assert (np.allclose(ds['u'].values, u_1d, 0., 1e-15, equal_nan=True))
    assert (np.allclose(ds['v'].values, v_1d, 0., 1e-15, equal_nan=True))
    assert (np.allclose(ds['dpdu'].values, dpdu_1d, 0., 1e-15, equal_nan=True))
    assert (np.allclose(ds['dpdv'].values, dpdv_1d, 0., 1e-14, equal_nan=True))

    thit, is_int = quadric.is_intersection_t(r_set)

    assert (np.array_equal(ds['is_intersection'].values, is_int, equal_nan=True))
    assert (np.array_equal(ds['thit'].values, thit, equal_nan=True))
