#!/usr/bin/env python
# -*- coding: utf-8 -*-

from geoclide.mathope import gamma_f32, gamma_f64
import math

VERSION = '3.0.2'

GAMMA2_F32 = gamma_f32(2)
GAMMA3_F32 = gamma_f32(3)
GAMMA5_F32 = gamma_f32(5)

GAMMA2_F64 = gamma_f64(2)
GAMMA3_F64 = gamma_f64(3)
GAMMA5_F64 = gamma_f64(5)

TWO_PI = math.pi*2.