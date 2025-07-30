#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan  6 10:27:33 2023

@author: Mike
"""
from rayoptics.environment import *

opm=open_model('/Users/Mike/Developer/PyProjects/ro_test_files/fourf.roa')
sm=opm.seq_model
osp=opm.optical_spec
pm=opm.parax_model
osp['pupil'].key = 'object', 'NA'
osp['pupil'].value = .2
osp['fov'].key = 'object', 'height'
osp['fov'].value = -0.75
osp['fov'].is_relative=True
osp['fov'].set_from_list([0., 1.])
listobj(osp)
opm.update_model(src_model=osp)
pm.list_model()
pm.first_order_data()