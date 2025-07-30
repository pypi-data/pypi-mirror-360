#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from rayoptics.environment import *

opm = OpticalModel()
sm = opm['seq_model']
osp = opm['optical_spec']
pm = opm['parax_model']
em = opm['ele_model']
pt = opm['part_tree']
ss = opm['specsheet']
ar = opm['analysis_results']

pupil_diameter = 100.
pupil_radius = pupil_diameter/2
osp.pupil = PupilSpec(osp, key=['object', 'pupil'], value=pupil_diameter)

# single field on-axis
osp.field_of_view = FieldSpec(osp, key=['object', 'angle'], 
                              is_relative=True, value=1, flds=[0.0, 1.0])

# wavelength for analysis: 550nm
osp.spectral_region = WvlSpec([('e', 1.0)], ref_wl=0)

sm.gaps[0].thi = 1e+11

opm.add_mirror(lbl='M1', profile=Conic, r=-500., cc=-1., t=-250.)

opm.update_model()

sm.list_model()
listobj(sm)
listobj(osp)
pm.first_order_data()
pm.list_model()
em.list_elements()
pt.list_tree_full()