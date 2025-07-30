#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
import numpy as np
import geoclide as gc

PHIS = np.linspace(0., 360., 6)
THETAS = np.linspace(-180., 180., 7)


@pytest.mark.parametrize('phi', PHIS)
@pytest.mark.parametrize('theta', THETAS)
def test_vec2ang(phi, theta):
    v1 = gc.ang2vec(theta=theta, phi=phi, vec_view='zenith')
    th, ph = gc.vec2ang(v1, vec_view='zenith')
    v2 = gc.ang2vec(theta=th, phi=ph, vec_view='zenith')
    assert (np.isclose(v1.x, v2.x, 0., 1e-14))
    assert (np.isclose(v1.y, v2.y, 0., 1e-14))
    assert (np.isclose(v1.z, v2.z, 0., 1e-14))

    v1 = gc.ang2vec(theta=theta, phi=phi, vec_view='nadir')
    th, ph = gc.vec2ang(v1, vec_view='nadir')
    v2 = gc.ang2vec(theta=th, phi=ph, vec_view='nadir')
    assert (np.isclose(v1.x, v2.x, 0., 1e-14))
    assert (np.isclose(v1.y, v2.y, 0., 1e-14))
    assert (np.isclose(v1.z, v2.z, 0., 1e-14))

    # test standard values
    v1 = gc.ang2vec(theta=theta, phi=phi)
    th, ph = gc.vec2ang(v1)
    v2 = gc.ang2vec(theta=th, phi=ph)
    th, ph = gc.vec2ang(10*v1) # to test also non normalized vector
    v3 = gc.ang2vec(theta=th, phi=ph)
    assert (np.isclose(v1.x, v2.x, 0., 1e-14))
    assert (np.isclose(v1.y, v2.y, 0., 1e-14))
    assert (np.isclose(v1.z, v2.z, 0., 1e-14))
    assert (np.isclose(v1.x, v3.x, 0., 1e-14))
    assert (np.isclose(v1.y, v3.y, 0., 1e-14))
    assert (np.isclose(v1.z, v3.z, 0., 1e-14))

def test_vec2ang_old_bug():
    # check if bug from 3.0.1 is fixed
    gc.vec2ang(gc.Vector(-0.028830092518596997, 0.004805015419766166, -0.9995727775365759))


def test_ang2vec_diag():
    theta = np.array([20., 30., 45.])
    phi = np.array([0., 0., 180.])
    v_arr_f = gc.ang2vec(theta, phi, diag_calc=True).to_numpy()
    v_arr = np.zeros_like(v_arr_f)
    for i in range (0, len(theta)):
        v_arr[i,:] = gc.ang2vec(theta[i], phi[i]).to_numpy()
    assert (np.allclose(v_arr, v_arr_f))


def test_ang2vec_2d_arr():
    theta = np.array([20., 30., 45.])
    phi = np.array([0., 0., 180.])
    v_arr_f = gc.ang2vec(theta, phi).to_numpy()
    v_arr = np.zeros_like(v_arr_f)
    k = 0
    for j in range (0, len(phi)):
        for i in range (0, len(theta)):
            v_arr[k,:] = gc.ang2vec(theta[i], phi[j]).to_numpy()
            k+=1
    assert (np.allclose(v_arr, v_arr_f)) 


def test_ang2vec_1d_arr1():
    theta = np.array([20., 30., 45.])
    phi = 0.
    v_arr_f = gc.ang2vec(theta, phi).to_numpy()
    v_arr = np.zeros_like(v_arr_f)
    for i in range (0, len(theta)):
        v_arr[i,:] = gc.ang2vec(theta[i], phi).to_numpy()

    assert (np.allclose(v_arr, v_arr_f))


def test_ang2vec_1d_arr2():
    theta = 20.
    phi = np.array([0., 67., 180.])
    v_arr_f = gc.ang2vec(theta, phi).to_numpy()
    v_arr = np.zeros_like(v_arr_f)
    for j in range (0, len(phi)):
        v_arr[j,:] = gc.ang2vec(theta, phi[j]).to_numpy()

    assert (np.allclose(v_arr, v_arr_f))

def test_vec2ang_arr():
    phis = np.linspace(0., 360., 6)
    thetas = np.linspace(-180., 180., 6)
    v_set1 = gc.ang2vec(theta=thetas, phi=phis, vec_view='zenith', diag_calc=True)
    ths, phs = gc.vec2ang(v_set1, vec_view='zenith')
    v_set2 = gc.ang2vec(theta=ths, phi=phs, vec_view='zenith', diag_calc=True)

    assert (np.allclose(v_set1.to_numpy(), v_set2.to_numpy(), 0., 1e-15))

    v_set1 = gc.ang2vec(theta=thetas, phi=phis, vec_view='nadir', diag_calc=True)
    ths, phs = gc.vec2ang(v_set1, vec_view='nadir')
    v_set2 = gc.ang2vec(theta=ths, phi=phs, vec_view='nadir', diag_calc=True)

    assert (np.allclose(v_set1.to_numpy(), v_set2.to_numpy(), 0., 1e-15))