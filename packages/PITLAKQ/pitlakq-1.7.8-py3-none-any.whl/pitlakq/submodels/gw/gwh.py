"""Groundwater inflow as a function of lake water depths.
"""


from __future__ import print_function, unicode_literals

from collections import defaultdict
try:
    from itertools import zip_longest
except ImportError:
    from itertools import izip_longest as zip_longest
from os.path import join
import sys

# pylint: disable-msg=E1101
import numpy
from openpyxl.reader.excel import load_workbook

from pitlakq.commontools.input.bathhelper import make_bottom
from pitlakq.commontools.input.resources import Resources


class GroundwaterLakeLevel(object):
    """Groundwater infows and outflows as function of lake water level.
    """
    def __init__(self, config):
        self.config = config
        self.w2 = config.w2
        self.w2.set_shared_data('gw_coupling', True)
        self.workbook = load_workbook(filename=self.config.gwh_file)
        self.zone_mapping = None
        self.array_mapping = None
        self.flows = None
        self.concs = None
        self.conc_mapping = None
        self.const_names = Resources(self.config).const_names

    def read_data(self):
        """Read all data from xlsx.
        """
        bottom, zone_distribution = self.read_zones()
        self._check_bottom(bottom)
        flows = self.read_flow()
        concs = self.read_conc()
        zone_mapping, self.array_mapping = self._make_zone_mapping(
            zone_distribution)
        zone_limits, limit_indices = self._make_zone_limits(zone_mapping,
                                                            bottom)
        self._check_flow_concs_names(zone_limits, flows, concs)
        self._check_flow_locations(limit_indices, bottom, flows)
        self.zone_mapping, self.flows, self.concs = zone_mapping, flows, concs
        self.conc_mapping = self._make_conc_mapping()

    def read_zones(self):
        """Read tab with zone distrubution data.
        """
        worksheet = self.workbook['Zones']
        segments = []
        for cell in list(worksheet.rows)[0][1:]:
            if cell.value == 'segments':
                break
            segments.append(cell.value)
        nsegs = len(segments)
        bottom = [0.0]
        zones = [[None for _x in range(nsegs)]]
        for row in list(worksheet.rows)[2:]:
            bottom.append(float(row[0].value))
            zones.append([cell.value for cell in row[1:nsegs]])
        return bottom, zones

    def read_flow(self):
        """Read tab with flow data.
        """
        worksheet = self.workbook['Flow']
        header = [cell.value for cell in list(worksheet.rows)[0][:3]]
        assert header == [u'Zone name', u'Level', u'Flow']
        zone_values = defaultdict(list)
        for row in list(worksheet.rows)[1:]:
            zone_values[row[0].value].append((row[1].value, row[2].value))
        for values in zone_values.values():
            values.sort()
        return dict(zone_values)

    def read_conc(self):
        """Read tab with concentration data.
        """
        worksheet = self.workbook['Conc']
        header = [cell.value for cell in list(worksheet.rows)[0] if cell.value]
        zone_values = {}
        for row in list(worksheet.rows)[1:]:
            concs = [cell.value for cell in row[1:]]
            zone_values[row[0].value] = (dict(zip(header[1:], concs)))
        return zone_values

    @staticmethod
    def _make_zone_mapping(zone_distribution):
        """Create mapping of zone names and coordinate.
        """
        mapping = defaultdict(list)
        for row_index, row in enumerate(zone_distribution):
            for col_index, name in enumerate(row):
                if name and name != u'void':
                    mapping[name].append((row_index, col_index))
        mapping_array = {}
        for zone, value in mapping.items():
            array = numpy.zeros((len(zone_distribution),
                                 len(zone_distribution[0]))).astype(bool)
            for x_coord, y_coord in value:
                array[x_coord, y_coord] = True
            mapping_array[zone] = array
        return dict(mapping), mapping_array

    def _make_conc_mapping(self):
        """Create a dictionay for all concentrations. Values are 2D arrays.
        """
        array_mapping = self.array_mapping
        conc_mapping = {}
        for zone, concs in self.concs.items():
            empty_conc_array = numpy.zeros(array_mapping[zone].shape)
            for conc_name, conc in concs.items():
                conc_array = conc_mapping.get(conc_name,
                                              empty_conc_array.copy())
                conc_array += array_mapping[zone] * conc
                conc_mapping[conc_name] = conc_array
        return conc_mapping

    @staticmethod
    def _make_zone_limits(zone_mapping, bottom):
        """Find upper and lower bounds of zones.
        """
        bounds = {}
        indices = {}
        for zone, coords in zone_mapping.items():
            sorted_coords = sorted(coords)
            lower_index = sorted_coords[-1][0]
            upper_index = sorted_coords[0][0] - 1
            lower = bottom[lower_index]
            upper = bottom[upper_index]
            bounds[zone] = (lower, upper)
            indices[zone] = (lower_index, upper_index)
        return bounds, indices

    def _check_bottom(self, bottom):
        """Check that the bottom from the xlsx files corresponds with the
        one from the bath.nc file.
        """
        check_bottom = make_bottom(self.config.bathymetry_file_name,
                                join(self.config.w2_path, 'w2.yaml'))
        if check_bottom != bottom:
            print('Bottom from xlsx file does not match bottom from bath.nc.')
            print('Make sure you use the right input file.')
            print('Possible fix: Create new xlslx input file with gw zones.')
            print('\n{0:>10s} {1:>10s}'.format('expected', 'found'))
            print('=' * 10 + ' ' + '=' * 10)
            for exp, found in zip_longest(check_bottom, bottom,
                                           fillvalue='---'):
                print('{0:>10} {1:>10}'.format(exp, found))
            sys.exit(1)

    @staticmethod
    def _check_flow_concs_names(zone_limits, flows, concs):
        """Check consistent naming of zones.
        """
        sorted_dist = sorted(zone_limits.keys())
        sorted_flows = sorted(flows.keys())
        sorted_concs = sorted(concs.keys())
        if sorted_dist != sorted_flows != sorted_concs:
            print('Zones in spatial distribution, flow and concentrations'
                  ' do not match.')
            print('\n{0:>15s} {1:>15s} {2:>15s}'.format('distribution', 'flow',
                                                        'concs'))
            print(' '.join(['=' * 15] * 3))
            for dist, flow, conc in zip_longest(sorted_dist, sorted_flows,
                                           sorted_concs, fillvalue='---'):
                print('{0:>15} {1:>15} {2:>15}'.format(dist, flow, conc))
            sys.exit(1)

    @staticmethod
    def _check_flow_locations(limit_indices, bottom, flows):
        """Check location of zones.
        """
        error = False
        msg = ''
        for zone, values in flows.items():
            lowest_flow_border = values[0][0]
            lower_index, upper_index = limit_indices[zone]
            highest_inflow_level = bottom[lower_index - 2]
            if lowest_flow_border < highest_inflow_level:
                error = True
                msg += '\nThe inflow cannot be lower than {0}.\n'.format(
                    highest_inflow_level)
                msg += 'Lowest given level is: {0}.'.format(lowest_flow_border)
            if lower_index - upper_index < 2:
                error = True
                msg += '\nZone must be at least two layers thick.'
            if error:
                print('Error at zone: {0}.'.format(zone))
                print(msg)
                sys.exit(1)

    def set_q(self):
        """Write flows and concentrations to W2
        """
        numpy.seterr(all='raise')
        vactive = self.w2.get_shared_data('vactive')
        lake_level = self.w2.mean_level
        active = vactive > 0
        qgw = numpy.zeros(vactive.shape)
        qgwin = numpy.zeros(vactive.shape)
        qgwout = numpy.zeros(vactive.shape)
        flow = 0
        for zone, zone_array in self.array_mapping.items():
            zone_active = active & zone_array
            zone_vactive = vactive * zone_active
            total = numpy.sum(zone_vactive)
            if total < 1e-38:
                zone_relative = numpy.zeros(zone_vactive.shape)
            else:
                zone_relative = zone_vactive / total
            flow_levels = self.flows[zone]
            for level, flow in reversed(flow_levels):
                if lake_level > level:
                    break
            zone_q = zone_relative * flow
            qgw += zone_q
            if flow >= 0:
                qgwin += zone_q
            else:
                qgwout += zone_q
        self.w2.set_shared_array_data('qgw', qgw)
        self.w2.set_shared_array_data('qgwin', qgwin)
        self.w2.set_shared_array_data('qgwout', qgwout)
        for conc_name, conc in self.conc_mapping.items():
            ssgw = conc * qgwin
            specie = self.const_names[conc_name] + 'ssgw'
            if specie == 'doxssgw':
                specie = 'dossgw'
            self.w2.set_shared_array_data(specie, ssgw)



if __name__ == '__main__':
    from pitlakq.metamodel.configuration.getconfig import read_dot_pitlakq

    # pylint: disable-msg=R0903
    class Null(object):
        """Null pattern stub.
        """

        def __call__(self, *args, **kwargs):
            return None

        def __getattr__(self, name):
            return Null()

    class FakeConfig:
        """Mock for config.
        """

        def __init__(self, project_name):
            user_config = list(read_dot_pitlakq())[0]
            base = join(user_config['model_path'], project_name, 'input')
            self.gwh_file = join(base,  'gwh', 'gwh.xlsx')
            self.w2_path = join(base, 'w2')
            self.bathymetry_file_name = join(base, 'w2', 'bath.nc')
            self.all_const_names = join(user_config['resources_path'],
                                        'const_names.txt')
            self.w2 = Null()

    def test(project_name):
        """Check if it works.
        """
        config = FakeConfig(project_name)
        gwh_test = GroundwaterLakeLevel(config)
        gwh_test.read_data()
        #print(gwh_test.array_mapping)
        #pprint.pprint(gwh_test.read_flow())
        #pprint.pprint(gwh_test.read_conc())

    test('tut_gwh')
