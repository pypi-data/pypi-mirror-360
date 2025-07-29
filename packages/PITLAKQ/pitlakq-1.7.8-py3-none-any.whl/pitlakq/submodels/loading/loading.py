"""Pit wall loadings as function of water level.
"""

from __future__ import print_function

from collections import defaultdict
import os
import textwrap

import numpy
from openpyxl.reader.excel import load_workbook

from pitlakq.commontools.input.xlsx_reader import read_xslx_table
from pitlakq.commontools.tools import raise_or_show_info, interpolate


MIN_LEVEL_DIFF = 0.1

class Loading(object):
    """Pit wall loadings.
    """
    def __init__(self, config):
        self.config = config
        self.w2 = config.w2
        self.upper_layers = self.config.loading_upper_layers
        self.water_temperature = self.config.loading_water_temperature
        self.precip = self.get_precipitation()
        next(self.precip)  # Initialize coroutine.
        self.xlsx_file_name = self.config.loading_file
        self.workbook = None
        self.area = None
        self.raw_conc = None
        self.zones = {}
        self.planar_areas = {}
        self.surface_areas = {}
        self.max_surface_areas = {}
        self.segments = {}
        self.active_cells = {}
        self.conc = {}
        self.mass_storage = {}
        self.water_volumes = {}
        self.read_input()
        self.check_input()
        self.rearrange_data()

    def get_precipitation(self, met_fobj=None):
        """Find precipitation.
        """

        if met_fobj is None:
            met_fobj = open(os.path.join(self.config.ram_path, 'temp',
                                         'pre_br1.npt'))
        next(met_fobj)  # Skip comment.
        next(met_fobj)  # Skpip header.
        next(met_fobj)  # Skip first value line. Padding with zeros.
        precip_sum = 0
        last_jday = 0
        precip = 0
        jday = 0
        end_jday = 0
        last_end_jday = 0
        last = False
        jday, precip = [float(entry) for entry in next(met_fobj).split()]
        while True:
            end_jday = yield precip_sum
            if last:
                return
            if end_jday <= last_end_jday:
                msg = 'Next timestep must be large than previous one.\n'
                msg += 'Last jday was {0}. Current jday is {1}.'.format(
                    last_end_jday, end_jday)
                raise ValueError(msg)
            precip_sum = 0
            if  jday > end_jday:
                dt = (end_jday - last_end_jday) * 86400
                precip_sum += precip * dt
                last_jday = end_jday

            else:
                while jday <= end_jday:
                    dt = (jday - last_jday) * 86400
                    precip_sum += precip * dt
                    last_jday = jday
                    try:
                        line = next(met_fobj).split()
                    except StopIteration:
                        jday = end_jday
                        last = True
                    jday = float(line[0])
                    # pylint: disable-msg=C0103
                    # dt is good name
                    old_precip = precip
                    precip = float(line[1])
                    if last:
                        break
                if last_jday > 10 and not last:
                    diff = end_jday - last_jday
                    last_jday += diff
                    dt = diff * 86400
                    precip_sum += old_precip * dt
            last_end_jday = end_jday

    def read_input(self):
        """Read inputs.
        """
        self.workbook = load_workbook(filename=self.xlsx_file_name)
        self.area = self.read_area()
        self.raw_conc = self.read_conc()

    def read_area(self):
        """Read area data.
        """
        worksheet = self.workbook['Area']
        return read_xslx_table(worksheet, xlsx_file_name=self.xlsx_file_name)

    def read_conc(self):
        """Read conc data.
        """
        worksheet = self.workbook['Conc']
        return read_xslx_table(worksheet, xlsx_file_name=self.xlsx_file_name)

    def check_input(self):
        """Check all inputs.
        """
        self.check_levels()
        self.check_areas()
        self.check_segments()

    def check_levels(self):
        """Check area data.
        """
        water_levels = self.area['water_level']
        sorted_levels = sorted(water_levels)
        if water_levels != sorted_levels:
            msg = 'Please sort water level values in acsending order.'
            raise_or_show_info(ValueError, msg)
        level_diff = [level2 - level1 for level1, level2 in
                      zip(water_levels[:-1], water_levels[1:])]
        wrong_diff = [index for index, diff in enumerate(level_diff)
                      if diff < MIN_LEVEL_DIFF]
        if wrong_diff:
            msg = 'There must be a minium difference between specified lake '
            msg += 'water levels of {0} m.\n'.format(MIN_LEVEL_DIFF)
            msg += 'The following levels are too close:\n'
            msg += '\n'.join(['- {0:7.3f} and {1:7.3f}'.format(
                water_levels[n], water_levels[n + 1]) for n in wrong_diff])
            raise_or_show_info(ValueError, msg)

    def check_areas(self):
        """No negative areas.
        """
        for key, value in self.area.items():
            if key.endswith('_planar') or key.endswith('_surface'):
                negative = [area for area in value if area < 0]
                if negative:
                    msg = 'Found negative values in area {0}.\n'.format(key)
                    msg += 'Please provide non-negative values for:\n'
                    msg += '\n'.join(['- {0:7.3g}'.format(area)
                                      for area in negative])
                    raise_or_show_info(ValueError, msg)

    def check_segments(self):
        """Start segments must be less tahn or equal to end segments.
        """
        start_segments = [key.split('_start_segment')[0] for key in self.area
                          if key.endswith('_start_segment')]
        end_segments = [key.split('_end_segment')[0] for key in self.area if
                        key.endswith('_end_segment')]
        assert sorted(start_segments) == sorted(end_segments)
        for name in start_segments:
            starts = self.area[name + '_start_segment']
            ends = self.area[name + '_end_segment']
            diff = [index for index, (start, end) in
                    enumerate(zip(starts, ends)) if end - start < 0]
            if diff:
                msg = 'Found invalid segment definitions for zone "{0}".\n'
                msg = msg.format(name)
                msg += 'Make sure start segments are lower than or equal to '
                msg += 'end segments.\n'
                msg += 'The following segments are incorrect:\n'
                msg += '\n'.join(
                    ['line: {0:3d} start: {1:3d} end: {2:3d}'.format(
                        lineno, starts[index], ends[index])
                     for lineno, index in enumerate(diff, 2)])
                raise_or_show_info(ValueError, msg)

    def rearrange_data(self):
        """Get data into useable structures.
        """
        self.zones = self.raw_conc['zone']
        area_header = set(self.area.keys())
        area_header.remove('water_level')
        conc_names = list(self.raw_conc.keys())
        conc_names.remove('zone')
        for index, zone in enumerate(self.zones):
            planar = zone + '_planar'
            surface = zone + '_surface'
            start_seg = zone + '_start_segment'
            end_seg = zone + '_end_segment'
            self.planar_areas[zone] = self.area[planar]
            self.surface_areas[zone] = self.area[surface]
            if not self.surface_areas[zone]:
                msg = '\n\nNo entry for areas found for zone "{0}".\n'.format(zone)
                msg += 'Please provide entries in section "Area" '
                msg += 'in file:\n    {0}'.format(self.xlsx_file_name)
                raise_or_show_info(ValueError, msg)
            self.max_surface_areas[zone] = max(self.surface_areas[zone])
            self.segments[zone] = [(start, end) for start, end in
                                   zip(self.area[start_seg],
                                       self.area[end_seg])]
            self.conc[zone] = dict((name, self.raw_conc[name][index]) for
                                   name in conc_names)
            for name in [planar, surface, start_seg, end_seg]:
                area_header.remove(name)
        assert not area_header
        for zone in self.zones:
            self.mass_storage[zone] = {}
            for conc_name in conc_names:
                self.mass_storage[zone][conc_name] = 0.0


    def set_load(self, w2, water_level, jday, dt):
        """Add the loading to the lake.
        """
        water_levels = self.area['water_level']
        seconds = dt.days * 86400 + dt.seconds
        level_pos = self._find_level_pos(water_level, water_levels)
        precip_amount = self.precip.send(jday)
        self._cumulate_mass(level_pos, water_level, water_levels, seconds)
        if precip_amount:
            self.w2.set_shared_array_data('tload', self.water_temperature)
            self._calculate_volumes(level_pos, water_level, water_levels,
                                    precip_amount)
            self._find_active_cells(level_pos)
            vactive = self.w2.vactive
            volumes = numpy.zeros_like(vactive)
            species = {}
            zone_name = list(self.mass_storage.keys())[0]
            for specie_name in self.mass_storage[zone_name]:
                species[specie_name] = numpy.zeros_like(vactive)
            for zone in self.zones:
                zone_active = self.active_cells[zone]
                volume = self.water_volumes[zone]
                w2_volumes = vactive * zone_active
                volume_factions = w2_volumes / numpy.sum(w2_volumes)
                volumes += volume_factions * volume
                for specie_name, mass in self.mass_storage[zone].items():
                    species[specie_name] += (mass * volume_factions) / seconds
            flow = volumes / seconds
            self.w2.set_shared_data('qload', flow)
            #print(str(flow).center(40, '#'))
            for specie_name, conc in species.items():
                self.w2.set_shared_data(specie_name, conc, is_ssload=True)
                #print(specie_name, conc)
            self._set_zero()
        else:
            zeros = numpy.zeros_like(self.w2.vactive)
            self.w2.set_shared_data('qload', zeros)
            zone_name = list(self.mass_storage.keys())[0]
            for specie_name in self.mass_storage[zone_name]:
                self.w2.set_shared_data(specie_name, zeros, is_ssload=True)

    def _find_level_pos(self, water_level, water_levels):
        """Find location of water_level.
        """
        if water_level <= water_levels[0]:
            msg = textwrap.dedent("""
            Water level below lowest specifed water level.
            The water level is {0} but lowest specified water level is {1}.
            Please correct {2}.
            """.format(water_level, water_levels[0], self.config.loading_file))
            raise_or_show_info(ValueError, msg)
        if water_level >= water_levels[-1]:
            msg = textwrap.dedent("""
            Water level above highest specifed water level.
            The water level is {0} but highest specified water level is {1}.
            Please correct {2}.
            """.format(water_level, water_levels[-1],
                       self.config.loading_file))
            raise_or_show_info(ValueError, msg)
        for index, (level1, level2) in enumerate(zip(water_levels[:-1],
                                                     water_levels[1:])):
            if level1 <= water_level < level2:
                break
        return (index, index + 1)

    def _find_area(self, level_pos, water_level, water_levels, areas):
        """Find active are for current waterlevel.

        Linear interpolation between levels.
        """
        lower, upper = level_pos
        lower_level, upper_level = water_levels[lower], water_levels[upper]
        active_area = {}
        for zone in self.zones:
            lower_area, upper_area = areas[zone][lower], areas[zone][upper]
            active_area[zone] = interpolate(lower_level, upper_level,
                                            lower_area, upper_area,
                                            water_level)
        return active_area

    def _cumulate_mass(self, level_pos, water_level, water_levels, seconds):
        """For each zone, add current mass to old mass.
        """
        active_surface_areas = self._find_area(level_pos, water_level,
                                                       water_levels,
                                                       self.surface_areas)
        for zone in self.zones:
            for conc_name in self.mass_storage[zone].keys():
                mass = (active_surface_areas[zone] *
                        self.conc[zone][conc_name]) * seconds
                self.mass_storage[zone][conc_name] += mass

    def _calculate_volumes(self, level_pos, water_level, water_levels,
                           precip_amount):
        """Calculate volumes per zone to add.
        """
        active_planar_areas = self._find_area(level_pos, water_level,
                                                          water_levels,
                                                          self.planar_areas)
        for zone in self.zones:
            vol = precip_amount * active_planar_areas[zone]
            self.water_volumes[zone] = vol

    def _set_zero(self):
        """Set values for volumes and masses back to zero.
        """
        for zone in self.zones:
            self.water_volumes[zone] = 0.0
            for conc_name in self.mass_storage[zone].keys():
                self.mass_storage[zone][conc_name] = 0.0

    def _find_active_cells(self, level_pos):
        """
        Find active lake cells for each zone that will receive the loading.
        """
        upper_index = self.w2.water_level_index
        lower_index = upper_index + self.upper_layers
        lower, upper = level_pos
        active = numpy.where(self.w2.vactive, True, False)
        active[lower_index:] = False
        for zone in self.zones:
            zone_active = active.copy()
            upper_segs = self.segments[zone][upper]
            lower_segs = self.segments[zone][lower]
            start = min(lower_segs[0], upper_segs[0]) -1
            end = max(lower_segs[1], upper_segs[1])
            zone_active[:, :start] = False
            zone_active[:, end:] = False
            self.active_cells[zone] = zone_active
