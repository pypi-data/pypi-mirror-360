#!/usr/bin/env python
# -*- coding: utf-8 -*-

import geoclide as gc


def test_clamp():
    assert (gc.clamp(4., val_min=5., val_max=11.) == 5.)


def test_quadratic():
    a = 2.
    b = -5.
    c = 0.
    assert (gc.quadratic(a, b, c) == (True, 0.0, 2.5))