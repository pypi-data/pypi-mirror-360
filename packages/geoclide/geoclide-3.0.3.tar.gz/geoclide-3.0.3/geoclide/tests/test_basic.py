#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
import numpy as np
import math
import geoclide as gc

P1 = [np.array([0.,0.,0.]), np.array([1.,2.,3.])]
V1 = [np.array([0.,0.,1.]), np.array([1.,1.,1.])]
N1 = [np.array([0.,0.,1.]), np.array([1.,1.,1.])]


@pytest.mark.parametrize('v_arr', V1)
def test_vector(v_arr):
    v1 = gc.Vector(v_arr[0], v_arr[1], v_arr[2])
    v2 = gc.Vector(v_arr)
    assert (v1 == v2)
    assert (np.all(v1.to_numpy() == v_arr))
    assert (v1[0] == v_arr[0])
    assert (v1[1] == v_arr[1])
    assert (v1[2] == v_arr[2])
    assert (v1[0] == v1.x)
    assert (v1[1] == v1.y)
    assert (v1[2] == v1.z)
    assert (-v1 == gc.Vector(-v1.x, -v1.y, -v1.z))


@pytest.mark.parametrize('p_arr', P1)
def test_point(p_arr):
    p1 = gc.Point(p_arr[0], p_arr[1], p_arr[2])
    p2 = gc.Point(p_arr)
    assert (p1 == p2)
    assert (np.all(p1.to_numpy() == p_arr))
    assert (p1[0] == p_arr[0])
    assert (p1[1] == p_arr[1])
    assert (p1[2] == p_arr[2])
    assert (p1[0] == p1.x)
    assert (p1[1] == p1.y)
    assert (p1[2] == p1.z)
    assert (-p1 == gc.Point(-p1.x, -p1.y, -p1.z))


@pytest.mark.parametrize('n_arr', N1)
def test_normal(n_arr):
    n1 = gc.Normal(n_arr[0], n_arr[1], n_arr[2])
    n2 = gc.Normal(n_arr)
    assert (n1 == n2)
    assert (np.all(n1.to_numpy() == n_arr))
    assert (n1[0] == n_arr[0])
    assert (n1[1] == n_arr[1])
    assert (n1[2] == n_arr[2])
    assert (n1[0] == n1.x)
    assert (n1[1] == n1.y)
    assert (n1[2] == n1.z)
    assert (-n1 == gc.Normal(-n1.x, -n1.y, -n1.z))


@pytest.mark.parametrize('v_arr', V1)
def test_ope_vector(v_arr):
    v1 = gc.Vector(v_arr)
    v2 = gc.Vector(1., 3., 0.5)
    assert (v1+v2 == gc.Vector(v_arr+v2.to_numpy()))
    assert (v1-v2 == gc.Vector(v_arr-v2.to_numpy()))
    assert (v1*2 == gc.Vector(v_arr*2.))
    assert (2*v1 == gc.Vector(v_arr*2.))
    assert (v1/2 == gc.Vector(v_arr/2.))
    v3 = v1+v2
    assert (v3.length() == math.sqrt(v3[0]**2+v3[1]**2+v3[2]**2))
    assert (v3.length_squared() == v3[0]**2+v3[1]**2+v3[2]**2)


@pytest.mark.parametrize('p_arr', P1)
def test_ope_point(p_arr):
    p1 = gc.Point(p_arr)
    v1 = gc.Vector(1., 3., 0.5)
    p2 = gc.Point(1.,1.,1.)
    assert (p1+v1 == gc.Point(p_arr+v1.to_numpy()))
    assert (p1-p2 == gc.Vector(p_arr-p2.to_numpy()))
    assert (p1-v1 == gc.Point(p_arr-v1.to_numpy()))
    assert (p1*2 == gc.Point(p_arr*2.))
    assert (2*p1 == gc.Point(p_arr*2.))
    assert (p1/2 == gc.Point(p_arr/2.))


@pytest.mark.parametrize('n_arr', N1)
def test_ope_normal(n_arr):
    n1 = gc.Normal(n_arr)
    n2 = gc.Normal(1., 3., 0.5)
    assert (n1+n2 == gc.Normal(n_arr+n2.to_numpy()))
    assert (n1-n2 == gc.Normal(n_arr-n2.to_numpy()))
    assert (n1*2 == gc.Normal(n_arr*2.))
    assert (2*n1 == gc.Normal(n_arr*2.))
    assert (n1/2 == gc.Normal(n_arr/2.))
    assert (n1.length() == math.sqrt(n1[0]**2+n1[1]**2+n1[2]**2))
    assert (n1.length_squared() == n1[0]**2+n1[1]**2+n1[2]**2)


@pytest.mark.parametrize('p_arr', P1)
@pytest.mark.parametrize('v_arr', V1)
def test_ray(p_arr, v_arr):
    p1 = gc.Point(p_arr)
    v1 = gc.Vector(v_arr)
    r1 = gc.Ray(p1,v1)
    assert (r1.o == p1)
    assert (r1.d == v1)
    assert (r1(10.) == gc.Point(p_arr + 10.*v_arr))
    assert (r1.mint == 0)
    assert (r1.maxt == float("inf"))
    r2 = gc.Ray(p1,v1,0.5, 20.)
    assert (r2.mint == 0.5)
    assert (r2.maxt == 20.)
    r3 = gc.Ray(r2)
    assert (r3.o == r2.o)
    assert (r3.d == r2.d)
    assert (r3.mint == r2.mint)
    assert (r3.maxt == r2.maxt)


def test_bbox():
    # test attributs
    p1 = gc.Point(1., 1., 1.)
    p2 = gc.Point(2., 2., 3.)
    b1 = gc.BBox(p1, p2)
    minx = min(p1.x, p2.x)
    miny = min(p1.y, p2.y)
    minz = min(p1.z, p2.z)
    maxx = max(p1.x, p2.x)
    maxy = max(p1.y, p2.y)
    maxz = max(p1.z, p2.z)
    pmin = gc.Point(minx, miny, minz)
    pmax = gc.Point(maxx, maxy, maxz)
    assert (b1.pmin == pmin)
    assert (b1.pmax == pmax)
    p = [pmin]
    p.append(gc.Point(pmax.x,pmin.y,pmin.z))
    p.append(gc.Point(pmax.x,pmax.y,pmin.z))
    p.append(gc.Point(pmin.x,pmax.y,pmin.z))
    p.append(gc.Point(pmin.x,pmin.y,pmax.z))
    p.append(gc.Point(pmax.x,pmin.y,pmax.z))
    p.append(pmax)
    p.append(gc.Point(pmin.x,pmax.y,pmax.z))
    assert (b1.p0 == p[0])
    assert (b1.p1 == p[1])
    assert (b1.p2 == p[2])
    assert (b1.p3 == p[3])
    assert (b1.p4 == p[4])
    assert (b1.p5 == p[5])
    assert (b1.p6 == p[6])
    assert (b1.p7 == p[7])
    for i in range (len(b1.vertices)):
        assert (b1.vertices[i] == p[i])

    # test union method
    p3 = gc.Point(3., 3., 3.)
    b2 = b1.union(p3)
    assert (b2.pmin.x == min(b1.pmin.x, p3.x))
    assert (b2.pmin.y == min(b1.pmin.y, p3.y))
    assert (b2.pmin.z == min(b1.pmin.z, p3.z))
    assert (b2.pmax.x == max(b1.pmax.x, p3.x))
    assert (b2.pmax.y == max(b1.pmax.y, p3.y))
    assert (b2.pmax.z == max(b1.pmax.z, p3.z))
    b3 = b1.union(b2)
    assert (b3.pmin.x == min(b1.pmin.x, b2.pmin.x))
    assert (b3.pmin.y == min(b1.pmin.y, b2.pmin.y))
    assert (b3.pmin.z == min(b1.pmin.z, b2.pmin.z))
    assert (b3.pmax.x == max(b1.pmax.x, b2.pmax.x))
    assert (b3.pmax.y == max(b1.pmax.y, b2.pmax.y))
    assert (b3.pmax.z == max(b1.pmax.z, b2.pmax.z))

    # test is_inside method
    pIn = gc.Point(1.5, 1.5, 1.5)
    pOut = gc.Point(0., 0., 0.)
    assert (b3.is_inside(pIn))
    assert (not b3.is_inside(pOut))

    # test common_vertices method annd function get_common_vertices
    bc1 = gc.BBox(gc.Point(0., 0., 0.), gc.Point(2.5, 2.5, 2.5))
    bc2 = gc.BBox(gc.Point(2.5, 0., 0.), gc.Point(5., 2.5, 2.5))
    # The vertices of bc1 in common with the bc2 vertices are p1, p2, p5 and p6: 
    assert (np.all(bc1.common_vertices(bc2) == np.array([False, True, True, False, False, True, True, False])))
    assert (np.all(gc.get_common_vertices(bc1, bc2) == np.array([False, True, True, False, False, True, True, False])))
    # The vertices of bc2 in common with the bc1 vertices are p0, p3, p4 and p7: 
    assert (np.all(bc2.common_vertices(bc1) == np.array([True, False, False, True, True, False, False, True])))
    assert (np.all(gc.get_common_vertices(bc2, bc1) == np.array([True, False, False, True, True, False, False, True])))

    # test common_face method
    b_ref = gc.BBox(gc.Point(0., 0., 0.), gc.Point(1., 1., 1.))
    b_f0 = gc.BBox(gc.Point(1., 0., 0.), gc.Point(2., 1., 1.))
    b_f1 = gc.BBox(gc.Point(-1., 0., 0.), gc.Point(0., 1., 1.))
    b_f2 = gc.BBox(gc.Point(0., 1., 0.), gc.Point(1., 2., 1.))
    b_f3 = gc.BBox(gc.Point(0., -1., 0.), gc.Point(1., 0., 1.))
    b_f4 = gc.BBox(gc.Point(0., 0., 1.), gc.Point(1., 1., 2.))
    b_f5 = gc.BBox(gc.Point(0., 0., -1.), gc.Point(1., 1., 0.))
    assert (b_ref.common_face(b_f0) == 0)
    assert (b_ref.common_face(b_f1) == 1)
    assert (b_ref.common_face(b_f2) == 2)
    assert (b_ref.common_face(b_f3) == 3)
    assert (b_ref.common_face(b_f4) == 4)
    assert (b_ref.common_face(b_f5) == 5)
    assert (gc.get_common_face(b_ref, b_f0) == 0)
    assert (gc.get_common_face(b_ref, b_f1) == 1)
    assert (gc.get_common_face(b_ref, b_f2) == 2)
    assert (gc.get_common_face(b_ref, b_f3) == 3)
    assert (gc.get_common_face(b_ref, b_f4) == 4)
    assert (gc.get_common_face(b_ref, b_f5) == 5)

    # test method intersect_p
    b_int = gc.BBox(gc.Point(0., 0., 0.), gc.Point(1., 1., 1.))
    r_int_1 = gc.Ray(gc.Point(-0.5, 0.5, 0.5), gc.Vector(1.,0.,0.))
    r_int_2 = gc.Ray(gc.Point(0.5, 0.5, 0.5), gc.Vector(1.,0.,1.))
    r_int_3 = gc.Ray(gc.Point(0.5, 0.5, 2.), gc.Vector(0.,0.,1.))
    # case where the ray origin is outside and where the ray intersect 2 times the BBox
    t0, t1, is_int = b_int.intersect(r_int_1, ds_output=False)
    p_int_t0 = r_int_1(t0)
    p_int_t1 = r_int_1(t1)
    assert (is_int)
    assert (np.isclose(p_int_t0.x, 0., 0., 1e-14))
    assert (np.isclose(p_int_t0.y, 0.5, 0., 1e-14))
    assert (np.isclose(p_int_t0.z, 0.5, 0., 1e-14))
    assert (np.isclose(p_int_t1.x, 1., 0., 1e-14))
    assert (np.isclose(p_int_t1.y, 0.5, 0., 1e-14))
    assert (np.isclose(p_int_t1.z, 0.5, 0., 1e-14))
    # case where the ray origin is inside and where the ray intersect 1 times the BBox
    t0, t1, is_int = b_int.intersect(r_int_2, ds_output=False)
    p_int_t1 = r_int_2(t1)
    assert (is_int)
    assert (np.isclose(p_int_t1.x, 1., 0., 1e-14))
    assert (np.isclose(p_int_t1.y, 0.5, 0., 1e-14))
    assert (np.isclose(p_int_t1.z, 1.0, 0., 1e-14))
    # case where the ray origin is outsie and where the ray does not intersect with the BBox
    t0, t1, is_int = b_int.intersect(r_int_3, ds_output=False)
    assert (not is_int)

    b_int2 = gc.BBox(p1=gc.Point(-500., -500., 0.), p2=gc.Point(500., 500., 700.))
    r_int4 = gc.Ray(o=gc.Point(0., 0., 0.), d=gc.normalize(gc.Vector(0.5, -0.5, 1.)))

    t0, t1, is_int = b_int2.intersect(r_int4, ds_output=False)
    assert (is_int)
    assert (t0 == 0.)
    assert (np.isclose(857.3214099741128, t1, 0., 1e-14))


def test_basic_array():
    p1 = gc.Point(5,2,10)
    p2 = gc.Point(4,2,1)
    parr = np.vstack((p1.to_numpy(), p2.to_numpy()))
    p1p2 = gc.Point(parr)
    assert (p1 == gc.Point(p1p2.x[0], p1p2.y[0], p1p2.z[0]))
    assert (p2 == gc.Point(p1p2.x[1], p1p2.y[1], p1p2.z[1]))
    assert (np.all(p1p2 == gc.Point(parr[:,0], parr[:,1], parr[:,2])))

    n1 = gc.Normal(5,2,10)
    n2 = gc.Normal(4,2,1)
    narr = np.vstack((n1.to_numpy(), n2.to_numpy()))
    n1n2 = gc.Normal(narr)
    assert (n1 == gc.Normal(n1n2.x[0], n1n2.y[0], n1n2.z[0]))
    assert (n2 == gc.Normal(n1n2.x[1], n1n2.y[1], n1n2.z[1]))
    assert (np.all(n1n2 == gc.Normal(narr[:,0], narr[:,1], narr[:,2])))

    v1 = gc.Vector(5,2,10)
    v2 = gc.Vector(4,2,1)
    arr = np.vstack((v1.to_numpy(), v2.to_numpy()))
    v1v2 = gc.Vector(arr)
    assert (v1 == gc.Vector(v1v2.x[0], v1v2.y[0], v1v2.z[0]))
    assert (v2 == gc.Vector(v1v2.x[1], v1v2.y[1], v1v2.z[1]))
    assert (np.all(v1v2 == gc.Vector(arr[:,0], arr[:,1], arr[:,2])))
    v1v2_x3 = 3*v1v2
    v1_x3 = 3*v1
    v2_x3 = 3*v2
    assert (np.all(v1_x3.to_numpy() == v1v2_x3.to_numpy()[0,:]))
    assert (np.all(v2_x3.to_numpy() == v1v2_x3.to_numpy()[1,:]))


def test_bbox_array():
    size = 4
    set_1 = np.zeros((size, 3), dtype=np.float64)
    set_2 = np.ones_like(set_1)
    set_1[:,0] = np.arange(size)
    set_2[:,0] = np.arange(size) + 1
    set_p1 = gc.Point(set_1)
    set_p2 = gc.Point(set_2)
    b_set = gc.BBox(set_p1, set_p2)
    b1 = gc.BBox(gc.Point(set_1[0,:]), gc.Point(set_2[0,:]))
    b2 = gc.BBox(gc.Point(set_1[1,:]), gc.Point(set_2[1,:]))
    b3 = gc.BBox(gc.Point(set_1[2,:]), gc.Point(set_2[2,:]))
    b4 = gc.BBox(gc.Point(set_1[3,:]), gc.Point(set_2[3,:]))

    assert (np.all(gc.get_common_vertices(b_set, b1)[0,:] == gc.get_common_vertices(b1, b1)))
    assert (np.all(gc.get_common_vertices(b_set, b1)[1,:] == gc.get_common_vertices(b2, b1)))
    assert (np.all(b_set.common_vertices(b1)[0,:] == b1.common_vertices(b1)))
    assert (np.all(b_set.common_vertices(b1)[1,:] == b2.common_vertices(b1)))

    assert(gc.get_common_face(b_set, b2, fill_value=-1)[0] == gc.get_common_face(b1, b2, fill_value=-1))
    assert(gc.get_common_face(b_set, b2, fill_value=-1)[1] == gc.get_common_face(b2, b2, fill_value=-1))
    assert(gc.get_common_face(b_set, b2, fill_value=-1)[2] == gc.get_common_face(b3, b2, fill_value=-1))
    assert(gc.get_common_face(b_set, b2, fill_value=-1)[3] == gc.get_common_face(b4, b2, fill_value=-1))


def test_bbox_ray_array():
    arr1 = np.array([[0., 0., 0.], [1., 1., 1.]], dtype=np.float64)
    arr2 = np.array([[0., 0., 1.], [1., 0., 0.]], dtype=np.float64)
    size = 4
    arr1_bis = np.zeros((size, 3), dtype=np.float64)
    arr2_bis = np.zeros((size, 3), dtype=np.float64)
    arr1_bis[0::2,:] = arr1[0,:]
    arr1_bis[1::2,:] = arr1[1,:]
    arr2_bis[0::2,:] = arr2[0,:]
    arr2_bis[1::2,:] = arr2[1,:]
    p_set = gc.Point(arr1_bis)
    v_set = gc.Vector(arr2_bis)
    r_set = gc.Ray(p_set, v_set)
    r1 = gc.Ray(gc.Point(0., 0., 0.), gc.Vector(0., 0., 1.))
    r2 = gc.Ray(gc.Point(1., 1., 1.), gc.Vector(1., 0., 0.))
    b1 = gc.BBox(gc.Point(-2., -2., 0.25), gc.Point(2., 2., 0.75))

    is_int1 = b1.is_intersection(r1)
    is_int2 = b1.is_intersection(r2)
    is_int_set = b1.is_intersection(r_set)
    assert (is_int1 == is_int_set[0])
    assert (is_int2 == is_int_set[1])
    assert (is_int1 == is_int_set[2])
    assert (is_int2 == is_int_set[3])

    t0_1, t1_1, is_int1 = b1.intersect(r1, ds_output=False)
    t0_2, t1_2, is_int2 = b1.intersect(r2, ds_output=False)
    t0_set, t1_set, is_int_set = b1.intersect(r_set, ds_output=False)
    assert (t0_1 == t0_set[0])
    assert (t1_1 == t1_set[0])
    assert (t0_2 == t0_set[1])
    assert (t1_2 == t1_set[1])
    assert (t0_1 == t0_set[2])
    assert (t1_1 == t1_set[2])
    assert (t0_2 == t0_set[3])
    assert (t1_2 == t1_set[3])

    size = 2
    set_1 = np.zeros((size, 3), dtype=np.float64)
    set_2 = np.ones_like(set_1)
    set_1[:,0] = np.arange(size)
    set_2[:,0] = np.arange(size) + 1
    set_p1 = gc.Point(set_1)
    set_p2 = gc.Point(set_2)
    b_set = gc.BBox(set_p1, set_p2)
    assert (np.all(b_set.is_inside(gc.Point(set_1[0,:])) == np.array([True, False])))
    assert (np.all(b_set.is_inside(gc.Point(set_2[0,:])) == np.array([True, True])))
    assert (np.all(b_set.is_inside(set_p1) == np.array([True, True])))
    assert (np.all(b_set.is_inside(set_p2) == np.array([True, True])))

    b_set_bis = gc.BBox(set_p1)
    b_set_bis = b_set_bis.union(set_p2)
    assert (np.all(b_set.pmin == b_set_bis.pmin))
    assert (np.all(b_set.pmax == b_set_bis.pmax))

    nx = 2
    ny = 2
    nz = 2
    x = np.linspace(0., 1., nx)
    y = np.linspace(0., 1., ny)
    z = np.linspace(0., 1., nz)
    x_, y_, z_ = np.meshgrid(x,y,z, indexing='ij')
    pmin_arr = np.vstack((x_.ravel(), y_.ravel(), z_.ravel())).T
    x = np.linspace(1., 2., nx)
    y = np.linspace(1., 2., ny)
    z = np.linspace(1., 2., nz)
    x_, y_, z_ = np.meshgrid(x,y,z, indexing='ij')
    pmax_arr = np.vstack((x_.ravel(), y_.ravel(), z_.ravel())).T
    r0 = gc.Ray(gc.Point(-2., 0., 0.25), gc.normalize(gc.Vector(1, 0., 0.5)))
    pmin = gc.Point(pmin_arr)
    pmax = gc.Point(pmax_arr)
    b_set = gc.BBox(pmin, pmax)
    t0, t1, is_int1 = b_set.intersect(r0, ds_output=False)
    nboxes = pmin_arr.shape[0]
    t0_ = np.zeros(nboxes, dtype=np.float64)
    t1_ = np.zeros_like(t0)
    is_int_ = np.full(nboxes, False, dtype=bool)
    for ib in range (0, nboxes):
        bi = gc.BBox(gc.Point(pmin_arr[ib,:]), gc.Point(pmax_arr[ib,:]))
        t0_[ib], t1_[ib], is_int_[ib] = bi.intersect(r0, ds_output=False)
    assert (np.all(t0 == t0_))
    assert (np.all(t1 == t1_))
    assert (np.all(is_int1 == is_int_))
