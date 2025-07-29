"""Update geometry at run time.

Lakes with more than one branch can have inactive branches
that may become active if the water level reaches a specified value.
The values in self.input.data['branch_geometry']['activationLevel']
determine which branch is active.

There is a check at the beginning of very year if the
action level is exceeded.
"""

# NumPy, dynamic members.
# pylint: disable-msg=E1101
# Many attributes defined outside __init__.
# pylint: disable-msg=W0201

from __future__ import print_function

import copy
import datetime
import pprint

import numpy

from pitlakq.commontools import tools


class GeometryUpdater(object):
    """Add a new branch at run time.
    """

    def __init__(self, config, input_data, w2):
        self.config = config
        self.input_data = input_data
        self.w2 = w2
        self.orig_branch_geometry = copy.deepcopy(input_data['branch_geometry'])
        self.branch_updates = False
        self.first = True
        self.number_of_old_active_branches = 0

    def adjust_branches(self, current_volume=None, water_level=None,
                        vactive=None):
        """Figure out which banches are active and set them.
        """
        data = self.input_data
        activation_levels = self.orig_branch_geometry['activation_level']['value']
        self.branch_updates = False
        if len(activation_levels) == 1:
            print('one branch only')
            # one-banch lakes need no special treatmemt
            return
        if not self.first:
            if len(activation_levels) == (data['bounds']['number_of_branches']
                                          ['value']):
                # all branches are active, no need to do anything
                print('all branches active')
                return
        if water_level is None:
            level_value = data['bathymetry']['starting_water_level']['value']
            try:
                water_level = level_value[1]
            except TypeError:
                water_level = level_value
        active_branches = [water_level >= a_level for a_level in
                           activation_levels]
        number_of_active_branches = sum(active_branches)
        if not number_of_active_branches:
            print('water_level', water_level)
            print('activation_levels', activation_levels)
            raise Exception('no active branches')
        if (self.first or
           number_of_active_branches > self.number_of_old_active_branches):
            self.branch_updates = True
            self.number_of_old_active_branches = number_of_active_branches
        else:
            return
        data['bounds']['number_of_branches']['value'] = \
                                                      number_of_active_branches
        for key, entry in self.orig_branch_geometry.items():
            new_value = [value for value, active in
                         zip(entry['value'], active_branches) if active]
            data['branch_geometry'][key]['value'] = new_value
        if not self.first:
            level, new_vactive = self.make_new_level(current_volume, vactive)
            print('water level', level)
            data['bathymetry']['starting_water_level']['value'] = level
            old_date = data['times']['start']['value']
            data['times']['start']['value'] = datetime.datetime(old_date.year,
                                                                1, 1)
            if self.config.kinetics:
                self.make_new_conc(vactive, new_vactive)
            self.make_new_temp(vactive, new_vactive)
            self.make_new_icethickness(vactive)
        print('new geometry data:')
        pprint.pprint(data['branch_geometry'])
        print('new number of branches:', number_of_active_branches)
        print('new active branches:', active_branches)
        self.first = False

    def make_new_level(self, current_volume, vactive):
        """Find water level after branch is added.
        """
        us_segs = (self.input_data['branch_geometry']
                   ['branch_upstream_segments']['value'])
        ds_segs = (self.input_data['branch_geometry']
                   ['branch_downstream_segments']['value'])
        bottom = float(self.input_data['waterbody_coordinates']
                       ['bottom_elevation']['value'])
        # b and h are good names here.
        # pylint: disable-msg=C0103
        b = self.input_data['bathymetry']['cell_width']['value']
        h = self.input_data['bathymetry']['layer_height']['value']
        # pylint: enable-msg=C0103
        x = self.input_data['bathymetry']['segment_lenght']['value']
        assert abs(numpy.sum(vactive) - current_volume) < 1e-3
        remainig_volume = current_volume
        new_vactive = numpy.zeros(vactive.shape, numpy.float64)
        column_indices = []
        for start, end in zip(us_segs, ds_segs):
            index = start
            while index <= end:
                column_indices.append(index - 1)
                index += 1
        print('column_indices', column_indices)
        level = bottom
        volume_level = bottom
        # Provoke IndexError if row_index doesn't get defined.
        row_index = int(1e30)
        for row_index in reversed(range(len(h))):
            row_area = 0
            for column_index in column_indices:
                area = b[row_index, column_index] * x[column_index]
                new_vactive[row_index, column_index] = area * h[row_index]
                row_area += area
            row_volume = row_area * h[row_index]
            if row_volume:
                volume_level += h[row_index]
                if row_volume > remainig_volume:
                    print(row_volume, remainig_volume, row_area)
                    level += remainig_volume / row_area
                    remainig_volume = 0
                else:
                    level += h[row_index]
                    remainig_volume -= row_volume
            if remainig_volume <= 0:
                break
        h_upper = h[row_index] - (volume_level - level)
        assert h_upper <= h[row_index]
        for column_index in column_indices:
            area = b[row_index, column_index] * x[column_index]
            new_vactive[row_index, column_index] = area * h_upper
        old_vol = numpy.sum(vactive)
        new_vol = numpy.sum(new_vactive)
        print(old_vol, new_vol)
        if abs(old_vol - new_vol) > 1e-3:
            raise ValueError(tools.make_debug_string(
                ['h_upper', 'level', 'volume_level', 'old_vol', 'new_vol',
                 'old_vol - new_vol']))
        print('remainig_volume', remainig_volume)
        return float(level), new_vactive

    def make_new_conc(self, vactive, new_vactive):
        """Calculate new concentration as an averaged concentration.

        We assume that the whole water body is totally mixed.
        Total mass will be preserved.
        """
        data = self.input_data
        for specie in data['initial_concentrations']:
            print('calculating new concentration for %s' % (specie,))
            w2_name = data['initial_concentrations'][specie]['w2_code_name']
            old_conc = self.w2.get_shared_data(w2_name)
            mass = numpy.sum(vactive * old_conc)
            conc = numpy.where(new_vactive, mass / numpy.sum(vactive), 0.0)
            try:
                assert abs(mass - numpy.sum(new_vactive * conc)) < 1e-3
            except AssertionError:
                print(specie)
                #print('conc', conc)
                print('mass', mass)
                print('new_mass', numpy.sum(new_vactive * conc))
            data['initial_concentrations'][specie]['value'] = conc

    def make_new_temp(self, vactive, new_vactive):
        """Calculate new temperature as an averaged temperature.

        We assume that the whole water body is totally mixed.
        Total mass will be preserved.
        """
        data = self.input_data
        old_temp = self.w2.get_shared_data('t2')
        heat = numpy.sum(vactive * old_temp)
        temp = numpy.where(new_vactive, heat / numpy.sum(vactive), 0.0)
        try:
            assert abs(heat - numpy.sum(new_vactive * temp)) < 1e-3
        except AssertionError:
            print('old tempearture', old_temp)
            print('new tempearture', temp)
            print('old heat', heat)
            print('new_heat', numpy.sum(new_vactive * temp))
        data['initial_conditions']['temperature']['value'] = temp

    def make_new_icethickness(self, vactive):
        """Calculate new ice thickness as an averaged ice thickness.
        """
        data = self.input_data
        old_ice = self.w2.get_shared_data('iceth')
        average_ice = numpy.mean(old_ice[numpy.sum(vactive, 0) > 0.001])
        new_ice = numpy.zeros(old_ice.shape) + average_ice
        print('old_ice', old_ice)
        print('average_ice', average_ice)
        print('new_ice', new_ice)
        data['initial_conditions']['ice_thickness']['value'] = new_ice
