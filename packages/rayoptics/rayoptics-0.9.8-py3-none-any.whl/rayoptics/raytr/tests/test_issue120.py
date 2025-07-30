#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from rayoptics.environment import *

isdark = False

opm = OpticalModel()
sm  = opm['seq_model']
osp = opm['optical_spec']
pm = opm['parax_model']
em = opm['ele_model']
pt = opm['part_tree']
ar = opm['analysis_results']

osp['pupil'] = PupilSpec(osp, key=['object', 'NA'], value=0.01)
osp['fov'] = FieldSpec(osp, key=['object', 'height'], value=5, flds=[0., 0.707, 1.], is_relative=True)
osp['wvls'] = WvlSpec([(780.2, 1.0)], ref_wl=0)

opm.radius_mode = True


sm.gaps[0].thi=100


sm.add_surface([100, 3, 'N-BK7', "Schott"]) 
sm.add_surface([-100, 98]) # when thi changed to 97, works
sm.add_surface([0,98]) # when thi changed to 97, works
sm.set_stop()
sm.add_surface([100, 3.1, 'N-BK7', "Schott"])
sm.add_surface([-100, 2])
sm.do_apertures = False

sm.list_model()
opm.update_model()
sm.list_model()
pm.list_model()
pm.first_order_data()

list_ray(trace_base(opm, [0, 1], osp['fov'].fields[0], 780.2))


# layout_plt = plt.figure(FigureClass=InteractiveLayout, opt_model=opm, is_dark=isdark).plot()
# plt.show()