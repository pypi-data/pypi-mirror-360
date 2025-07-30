#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import math
import geoclide as gc


def test_dot():
    assert (gc.dot(gc.Vector(0., 0., 1.), gc.Vector(0., 1., 0.)) == 0.)
    assert (gc.dot(gc.Vector(0., 0., 1.), gc.Vector(0., 0., 1.)) == 1.)
    v = gc.Vector(math.sqrt(2.)/2., 0., math.sqrt(2.)/2.)
    assert (gc.dot(gc.Vector(0., 0., 1.), v) == math.sqrt(2.)/2.)
    v_set1 = gc.Vector(np.vstack((np.array([0., 0., 1.]), np.array([0., 0., 1.]))))
    v_set2 = gc.Vector(np.vstack((np.array([0., 1., 0.]), np.array([0., 0., 1.]))))
    assert (gc.dot(v_set1, v_set2)[0] == 0.)
    assert (gc.dot(v_set1, v_set2)[1] == 1.)

    assert (gc.dot(gc.Normal(0., 0., 1.), gc.Vector(0., 1., 0.)) == 0.)
    assert (gc.dot(gc.Normal(0., 0., 1.), gc.Vector(0., 0., 1.)) == 1.)
    v = gc.Normal(math.sqrt(2.)/2., 0., math.sqrt(2.)/2.)
    assert (gc.dot(gc.Vector(0., 0., 1.), v) == math.sqrt(2.)/2.)

    assert (gc.dot(gc.Vector(0., 0., 1.), gc.Normal(0., 1., 0.)) == 0.)
    assert (gc.dot(gc.Vector(0., 0., 1.), gc.Normal(0., 0., 1.)) == 1.)
    v = gc.Normal(math.sqrt(2.)/2., 0., math.sqrt(2.)/2.)
    assert (gc.dot(gc.Vector(0., 0., 1.), v) == math.sqrt(2.)/2.)

    assert (gc.dot(gc.Normal(0., 0., 1.), gc.Normal(0., 1., 0.)) == 0.)
    assert (gc.dot(gc.Normal(0., 0., 1.), gc.Normal(0., 0., 1.)) == 1.)
    v = gc.Normal(math.sqrt(2.)/2., 0., math.sqrt(2.)/2.)
    assert (gc.dot(gc.Normal(0., 0., 1.), v) == math.sqrt(2.)/2.)


def test_cross():
    assert (gc.cross(gc.Vector(0., 0., 1.), gc.Vector(0., 1., 0.)) == gc.Vector(-1.0, 0.0, 0.0))
    assert (gc.cross(gc.Vector(0., 0., 1.), gc.Vector(0., 0., 1.)) == gc.Vector(0.0, 0.0, 0.0))
    v = gc.Vector(math.sqrt(2.)/2., 0., math.sqrt(2.)/2.)
    assert (gc.cross(gc.Vector(0., 0., 1.), v) ==  gc.Vector(0.0, math.sqrt(2.)/2., 0.0))
    v_set1 = gc.Vector(np.vstack((np.array([0., 0., 1.]), np.array([0., 0., 1.]))))
    v_set2 = gc.Vector(np.vstack((np.array([0., 1., 0.]), np.array([0., 0., 1.]))))
    assert (np.all(gc.cross(v_set1, v_set2).to_numpy()[0,:] == np.array([-1.0, 0.0, 0.0])))
    assert (np.all(gc.cross(v_set1, v_set2).to_numpy()[1,:] == np.array([0.0, 0.0, 0.0])))

    assert (gc.cross(gc.Normal(0., 0., 1.), gc.Vector(0., 1., 0.)) == gc.Vector(-1.0, 0.0, 0.0))
    assert (gc.cross(gc.Normal(0., 0., 1.), gc.Vector(0., 0., 1.)) == gc.Vector(0.0, 0.0, 0.0))
    v = gc.Vector(math.sqrt(2.)/2., 0., math.sqrt(2.)/2.)
    assert (gc.cross(gc.Normal(0., 0., 1.), v) ==  gc.Vector(0.0, math.sqrt(2.)/2., 0.0))

    assert (gc.cross(gc.Vector(0., 0., 1.), gc.Normal(0., 1., 0.)) == gc.Vector(-1.0, 0.0, 0.0))
    assert (gc.cross(gc.Vector(0., 0., 1.), gc.Normal(0., 0., 1.)) == gc.Vector(0.0, 0.0, 0.0))
    v = gc.Normal(math.sqrt(2.)/2., 0., math.sqrt(2.)/2.)
    assert (gc.cross(gc.Vector(0., 0., 1.), v) ==  gc.Vector(0.0, math.sqrt(2.)/2., 0.0))


def test_normalize():
    length = math.sqrt(1. + 4. + 9.)
    a_1 = 1. / length
    a_2 = 2./ length
    a_3 = 3. / length
    assert (gc.normalize(gc.Vector(1.,2.,3.)) == gc.Vector(a_1, a_2, a_3))
    assert (gc.normalize(gc.Vector(-1.,-2.,-3.)) == gc.Vector(-a_1, -a_2, -a_3))
    v_set = gc.Vector(np.vstack((np.array([1.,2.,3.]), np.array([-1.,-2.,-3.]))))
    assert (np.all(gc.normalize(v_set).to_numpy()[0,:] == np.array([a_1, a_2, a_3])))
    assert (np.all(gc.normalize(v_set).to_numpy()[1,:] == np.array([-a_1, -a_2, -a_3])))

    assert (gc.normalize(gc.Normal(1.,2.,3.)) == gc.Normal(a_1, a_2, a_3))
    assert (gc.normalize(gc.Normal(-1.,-2.,-3.)) == gc.Normal(-a_1, -a_2, -a_3))


def test_coordinate_system():
    v1 = gc.Vector(0., 0., 1.)
    v2_m1, v3_m1 = gc.coordinate_system(v1, 'm1')
    assert (v2_m1 == gc.Vector(0.0, 1.0, -0.0))
    assert (v3_m1 == gc.Vector(-1.0, 0.0, 0.0))
    v2_m2, v3_m2 = gc.coordinate_system(v1, 'm2')
    assert (v2_m2 == gc.Vector(1.0, -0.0, -0.0))
    assert (v3_m2 == gc.Vector(-0.0, 1.0, -0.0))

    v1 = gc.Vector(5,2,10)
    v2 = gc.Vector(4,2,-1)
    v1v2 = gc.Vector(np.vstack((v1.to_numpy(), v2.to_numpy())))
    v1_u2, v1_u3 = gc.coordinate_system(v1, 'm1')
    v2_u2, v2_u3 = gc.coordinate_system(v2, 'm1')
    v1v2_u2, v1v2_u3 = gc.coordinate_system(v1v2, 'm1')
    assert(v1_u2 == gc.Vector(v1v2_u2.to_numpy()[0,:]))
    assert(v1_u3 == gc.Vector(v1v2_u3.to_numpy()[0,:]))
    assert(v2_u2 == gc.Vector(v1v2_u2.to_numpy()[1,:]))
    assert(v2_u3 == gc.Vector(v1v2_u3.to_numpy()[1,:]))


def test_distance():
    p1 = gc.Point(0., 0., 0.)
    p2 = gc.Point(0., 0., 10.)
    assert (gc.distance(p1,p2) == 10.)
    p1 = gc.Point(1., 2., 1.9)
    p2 = gc.Point(5., 15., 3.)
    a_1 = math.sqrt(16 + 13**2 + 1.1**2)
    assert (gc.distance(p1,p2) == a_1)
    p_set1 = gc.Point(np.array([[0., 0., 0.], [2., 3., 5.]]))
    p_set2 = gc.Point(np.array([[-5., -2., 0.], [-2., 3., 5.]]))
    p1 = gc.Point(p_set1.to_numpy()[0,:])
    p2 = gc.Point(p_set1.to_numpy()[1,:])
    p3 = gc.Point(p_set2.to_numpy()[0,:])
    p4 = gc.Point(p_set2.to_numpy()[1,:])
    assert (gc.distance(p_set1, p_set2)[0] == gc.distance(p1,p3))
    assert (gc.distance(p_set1, p_set2)[1] == gc.distance(p2,p4))


def test_face_forward():
    n1 = gc.Normal(1., 0., 0.)
    v1 = gc.Vector(-1., 0., 0.)
    assert (gc.face_forward(v1, n1) == gc.Vector(1.0, -0.0, -0.0))
    n1 = gc.Normal(-1., 0., 0.)
    v1 = gc.Vector(-1., 0., 0.)
    assert (gc.face_forward(v1, n1) == gc.Vector(-1.0, 0.0, 0.0))

    v1 = gc.Vector(5,2,10)
    v2 = gc.Vector(-4,-2,-1)
    v1v2 = gc.Vector(np.vstack((v1.to_numpy(), v2.to_numpy())))
    v2v1 = gc.Vector(v1v2.to_numpy()[::-1,:])
    assert(gc.face_forward(v1, v2) == gc.Vector(gc.face_forward(v1v2, v2v1).to_numpy()[0,:]))
    assert(gc.face_forward(v2, v1) == gc.Vector(gc.face_forward(v1v2, v2v1).to_numpy()[1,:]))


def test_vmax():
    v1 = gc.Vector(2.,3.,1.)
    assert (gc.vmax(v1) == 3.)

    v1 = gc.Vector(5,2,10)
    v2 = gc.Vector(-4,-2,-1)
    v1v2 = gc.Vector(np.vstack((v1.to_numpy(), v2.to_numpy())))
    assert(gc.vmax(v1) == gc.vmax(v1v2)[0])
    assert(gc.vmax(v2) == gc.vmax(v1v2)[1])


def test_vmin():
    v1 = gc.Vector(2.,3.,1.)
    assert (gc.vmin(v1) == 1.)

    v1 = gc.Vector(5,2,10)
    v2 = gc.Vector(-4,-2,-1)
    v1v2 = gc.Vector(np.vstack((v1.to_numpy(), v2.to_numpy())))
    assert(gc.vmin(v1) == gc.vmin(v1v2)[0])
    assert(gc.vmin(v2) == gc.vmin(v1v2)[1])


def test_vargmax():
    v1 = gc.Vector(2.,3.,1.)
    assert (gc.vargmax(v1) == 1)

    v1 = gc.Vector(5,2,10)
    v2 = gc.Vector(-4,-2,-1)
    v1v2 = gc.Vector(np.vstack((v1.to_numpy(), v2.to_numpy())))
    assert(gc.vargmax(v1) == gc.vargmax(v1v2)[0])
    assert(gc.vargmax(v2) == gc.vargmax(v1v2)[1])


def test_vargmin():
    v1 = gc.Vector(2.,3.,1.)
    assert (gc.vargmin(v1) == 2)

    v1 = gc.Vector(5,2,10)
    v2 = gc.Vector(-4,-2,-1)
    v1v2 = gc.Vector(np.vstack((v1.to_numpy(), v2.to_numpy())))
    assert(gc.vargmin(v1) == gc.vargmin(v1v2)[0])
    assert(gc.vargmin(v2) == gc.vargmin(v1v2)[1])


def test_vabs():
    v1 = gc.Vector(5,-2,10)
    v2 = gc.Vector(-4,-2,-1)
    v1v2 = gc.Vector(np.vstack((v1.to_numpy(), v2.to_numpy())))
    assert (gc.vabs(v1) == gc.Vector(5, 2, 10))
    assert (gc.vabs(v2) == gc.Vector(4, 2, 1))
    assert (gc.Vector(gc.vabs(v1v2).to_numpy()[0,:]) == gc.Vector(5, 2, 10))
    assert (gc.Vector(gc.vabs(v1v2).to_numpy()[1,:]) == gc.Vector(4, 2, 1))

def test_permute():
    v1 = gc.Vector(2., 3., 1.)
    assert (gc.permute(v1, 1, 0, 2) == gc.Vector(3.0, 2.0, 1.0))

    v1 = gc.Vector(5,2,10)
    v2 = gc.Vector(-4,-2,-1)
    v1v2 = gc.Vector(np.vstack((v1.to_numpy(), v2.to_numpy())))
    assert(gc.permute(v1, 1, 2, 0) == gc.Vector(gc.permute(v1v2, 1, 2 , 0).to_numpy()[0,:]))
    assert(gc.permute(v2, 1, 2, 0) == gc.Vector(gc.permute(v1v2, 1, 2 , 0).to_numpy()[1,:]))
