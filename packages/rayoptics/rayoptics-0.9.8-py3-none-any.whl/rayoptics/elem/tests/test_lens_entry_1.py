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

fcd100 = create_glass('FCD100', 'Hoya')
bacd15 = create_glass('M-BACD15', 'Hoya')
ve_fcd100 = fcd100.glass_data()['abbe number']['ve']
ve_bacd15 = bacd15.glass_data()['abbe number']['ve']
pwr_a, pwr_b = elements.achromat(1/500, ve_fcd100, ve_bacd15)

opm.add_lens(lbl='L1', power=pwr_a, th=12, t=1, med='FCD100, Hoya')
opm.add_lens(lbl='L2', power=pwr_b, th=7, t=480, med='M-BACD15, Hoya')

opm.update_model()

sm.gaps[-1].thi += pm.thi_ht_solve(pm.ax, -1, 0.)
opm.update_model(src_model=sm)

opm.add_assembly_from_seq(1, 4, label='Doublet')

sm.list_model()
listobj(sm)
listobj(osp)
pm.first_order_data()
pm.list_model()
em.list_elements()
pt.list_tree_full()