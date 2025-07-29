"""
Wrapper class for W2 extension module.

It uses w2_poxy which can be a normal module or
a sever that communicates with pyro.
"""
# NumPy, dynamic members.
# pylint: disable-msg=E1101
# pylint: disable-msg=E1103

from __future__ import print_function

import datetime
import os
import subprocess
import sys

import numpy
from Pyro4 import core

from pitlakq.commontools.tools import raise_or_show_info
from pitlakq.commontools.input.resources import Resources
import pitlakq.commontools.input.yamlinput as yamlinput
from pitlakq.numericalmodels.existingmodels.w2 import w2_proxy
from pitlakq.numericalmodels.existingmodels.w2 import geometryupdater
import pitlakq.numericalmodels.existingmodels.w2.jday_converter as jday_con


# pylint: disable=redefined-builtin, invalid-name, undefined-variable
if sys.version_info.major < 3:
    input = raw_input
# pylint: enable=redefined-builtin, invalid-name, undefined-variable


class W2(object):
    """
    Wrapper class for W2 extension module.
    Wraps init process, makes jday instance attribute
    and calls setRestart if restart attribute is set.
    """

    def __init__(self, config):
        self.config = config
        self.jday_offset = 0
        self.temp_path = os.path.join(self.config.ram_path, 'temp')
        self.use_pyro = False #True
        self.show_volume = False
        if self.use_pyro:
            self._start_w2_proxy()
            self.w2_proxy = core.getProxyForURI(
                "PYROLOC://localhost:7766/w2_proxy")
        else:
            self.w2_proxy = w2_proxy.W2Proxy(self.config, self.temp_path)
        self.resourse = Resources(self.config)
        self.number_of_constituents = self.resourse.number_of_constituents
        self.number_of_additional_minerals = \
            self.resourse.number_of_additional_minerals
        self. additional_species = self.config.additional_species
        self.w2_dim_names = set(['imp', 'kmp', 'imc', 'kmc', 'nbp',
                               'nsp', 'ntp', 'nwp', 'ndp', 'ncp',
                               'ndt', 'nwsc', 'ntr'])
        self.time_varying_variables_order = {
            'meteorology':
            ['jday', 'air_temperature', 'dewpoint_temperature', 'wind_speed',
             'wind_direction', 'cloud_cover'],
            'precipitation':
            ['jday', 'precipitation'],
            'precipitation_temperature':
            ['jday', 'precipitation_temperature'],
            'precipitation_concentration':
            ['jday', 'precipitation_active_constituents'],
            'tributary_inflow':
            ['jday', 'tributary_inflow'],
            'tributary_temperature':
            ['jday', 'tributary_temperature'],
            'tributary_concentration':
            ['jday', 'tributary_active_constituents'],
            'branch_inflow':
            ['jday', 'branch_inflow'],
            'branch_outflow':
            ['jday', 'branch_outflow'],
            'branch_inflow_concentration':
            ['jday', 'inflow_active_constituents'],
            'branch_inflow_temperature':
            ['jday', 'branch_inflow_temperature']}
        self.time_varying_groups = self.time_varying_variables_order.keys()
        self.time_padded_data = set(['wsc', 'wscd', 'dltd', 'dltf', 'title'])
        self.convert_to_jday = set(['start', 'end', 'date'])
        self.w2_file_extension = 'npt'
        self.w2_file_global_names = {'meteorology': 'met', 'withdrawl': 'qwd'}
        self.w2_branch_file_names = {'precipitation': 'pre',
                                     'precipitation_temperature': 'tpr',
                                     'precipitation_concentration': 'cpr',
                                     'branch_inflow': 'qin',
                                     'branch_inflow_temperature': 'tin',
                                     'branch_inflow_concentration': 'cin',
                                     'branch_outflow': 'qot'}
        self.w2_tributary_file_names = {'tributary_inflow': 'qtr',
                                        'tributary_temperature': 'ttr',
                                        'tributary_concentration': 'ctr'}
        self.time_padding_period = 30
        self.add_ssp = 0
        self.add_ssgw = 0
        self.add_ssload = 0
        self.w2_code_names = {}
        self.w2_name_map = {}
        self.constituent_names = {}
        self.read_input()
        self.fix_active_constituents()
        self.init_jday_converter()
        self.assign_data()
        self.make_time_varying_code_names()
        self._update_time_varying_data_names()
        self.convert_time_varying_data()
        self.w2_name_map.update(self.additional_species)
        self.new_branch = False
        self.offset_balance = False
        # signal ncoutput to use ph from last time step
        self.ph_output_hack = False
        self.w2_reverse_name_map = {}
        self.make_w2_reverse_name_map()

    def _start_w2_proxy(self):
        """Start external process that we will communicate
           via pyro.
        """
        cmd = r'c:\python24\python.exe'
        arg = self.config.w2_source_path
        self.w2_proxy_pid = subprocess.Popen([cmd, arg]).pid

    def w2_readinput(self):
        """Wrapper for readinput from FORTRAN.
        """
        self.w2_proxy.readinput()

    def w2_hydrodynamics(self):
        """Wrapper for hydrodynamics from FORTRAN.
        """
        self.w2_proxy.hydrodynamics()

    @property
    def jday(self):
        """Current W2 jday."""
        w2_jday = self.w2_proxy.get_shared_data('jday')
        if self.new_branch:
            self.new_branch = False
            self.jday_offset = self.jday
        return self.jday_offset + w2_jday

    def w2_misccalculations(self):
        """Wrapper for misccalculations from FORTRAN.
        """
        self.w2_proxy.misccalculations()
        if self.show_volume:
            self.show_volume = False
            print('curent volume', self.w2_proxy.active_volume)

    @property
    def active_volume(self):
        """Get the active volume of the lake.
        """
        return self.w2_proxy.active_volume

    @property
    def mean_level(self):
        """Mean water level over all active columns.
        """
        elws = self.get_shared_data('elws')
        vactive = self.get_shared_data('vactive')
        if not numpy.any(vactive):
            # no vactive - begin of calculation
            # --> initial values for all columns
            numpy.mean(elws)
        return numpy.mean(elws[numpy.sum(vactive, 0) > 0.1])

    @property
    def date(self):
        """Date as datetime.datetime object.
        """
        return self.jday_converter.make_date_from_jday(self.jday)

    @property
    def water_level_index(self):
        # Switch from Fortran to Python indices.
        return self.get_shared_data('kt') - 1

    @property
    def vactive(self):
        return self.get_shared_data('vactive')

    def read_input(self):
        """Read yaml input.
        """

        def set_data(key):
            """Update tributary data for given key, i.e. tributary name.
            """
            data_file_name = os.path.join(self.config.w2_path,
                                                          key + '.txt')
            try:
                data = self.input.read_columns_whitespace(data_file_name)
            except IndexError:
                print(data_file_name)
                raise
            data['date']['w2_code_name'] = w2_proxy.DUMMY_W2_CODE_NAME
            self.input.data[key] = data

        self.input = yamlinput.YamlInput()
        self.input.load(os.path.join(self.config.template_path, 'w2.yaml'),
                        os.path.join(self.config.w2_path, 'w2.yaml'))
        self._check_number_of_tributaries(self.input)
        self.input.data['bounds']['number_of_constituents'] = {
            'default': self.number_of_constituents, 'w2_code_name': 'ncp'}
        # read tributary inflow, temperature and concentration
        for trib_name in (self.input.data['tributaries']['tributary_names']
                          ['value']):
            for trib_type in ['inflow', 'temperature', 'concentration']:
                key = trib_name + '_' + trib_type
                set_data(key)
        self.geometry_updater = geometryupdater.GeometryUpdater(self.config,
                                                            self.input.data,
                                                                self)
        self.geometry_updater.adjust_branches()
        dump = None
        if self.config.dump_input:
            dump = input(
                'Would you like to dump the input to a file [N/y]:')
        if dump in ['y', 'Y', 'yes', 'Yes']:
            fname = os.path.join(self.config.w2_path, 'w2_dump.yaml')
            print('Writing input to file: %s' % fname)
            import copy
            data = copy.deepcopy(self.input.data)
            for k, val in data.items():
                for inner_k, inner_v in val.items():
                    if isinstance(inner_v, dict):
                        for inner_2k, inner_2v in inner_v.items():
                            if type(inner_2v) == numpy.ndarray:
                                data[k][inner_k][inner_2k] = inner_2v.tolist()
            yamlinput.dump(fname, data)
            print('Input dumped to file: %s' % fname)
            continue_calc = input('Would you like to continue '
                                     'the calculation [N/y]:')
            if continue_calc not in ['y', 'Y', 'yes', 'Yes']:
                sys.exit()
        setattr(self.config, 'w2_input', self.input)
        self.config.w2_name_map = self.w2_name_map

    @staticmethod
    def _check_number_of_tributaries(yaml_input):
        """Due to the W2 data model `number_of_tributaries` is defined at
        two places.

        Both numbers must be the same.
        """
        bounds = yaml_input.data['bounds']['number_of_tributaries']
        tribs = yaml_input.data['tributaries']['number_of_tributaries']
        if bounds['value'] != tribs['value']:
            if bounds['value_given'] and tribs['value_given']:
                msg = ('Inconsitent values for `number_of_tributaries`. ' +
                       'Found {} in section `bounds` '.format(bounds['value']) +
                       'and {} in section tributaries.'.format(tribs['value']) +
                       ' Both values need to be the same.')
                raise ValueError(msg)
            elif bounds['value_given']:
                tribs['value'] = bounds['value']
            elif tribs['value_given']:
                bounds['value'] = tribs['value']
                print(' ' * 20, bounds['value'])
                print(' ' * 20, yaml_input.data['bounds']['number_of_tributaries']['value'])
            else:
                msg =('Wrong template values for `number_of_tributaries '
                       'in `bounds` or `tributaries`.')
                raise ValueError(msg)


    def fix_active_constituents(self):
        """Correction of order of active species needs.

        There is a fixed order of species as defined in resourses.
        Default or given values might be ordered differently.
        """
        name_order = [self.resourse.db_keys[key] for key in
                      self.resourse.all_species_keys]
        mineral_names = set([entry['name'] for entry in
                             self.resourse.mineral_names])
        data = self.input.data['active_constituents']
        names = data['constituent_name']['value']
        default_names = data['constituent_name']['default']
        no_default = set(name_order) - set(default_names)
        if no_default:
            msg = '\nThe following names do not have defaults in '
            msg += '"activeconst.yaml".\n'
            msg += 'Please define them with all active options set to "0":\n'
            msg += '\n'.join('- {0}'.format(name) for name in no_default)
            print(msg)
            sys.exit(1)
        positions = dict((name, pos) for pos, name in enumerate(names))
        default_positions = dict((name, pos) for pos, name in
                                 enumerate(default_names))
        new_active = {}
        new_active['meta_data'] = data.pop('meta_data')
        for key, value in data.items():
            new_active[key] = {'value': [],
                               'default': [],
                               'value_given': value['value_given'],
                               'is_default': value['is_default']}
        active_cols = data.keys()
        for name in name_order:
            value_pos = positions.get(name)
            default_pos = default_positions[name]
            for col in active_cols:
                default_value = data[col]['default'][default_pos]
                new_active[col]['default'].append(default_value)
                if value_pos is None:
                    new_active[col]['value'].append(default_value)
                else:
                    value = data[col]['value'][value_pos]
                    new_active[col]['value'].append(value)
            if not self.config.settle and name in mineral_names:
                for col in ['initial_concentration',
                            'inflow_active_constituents',
                            'tributary_active_constituents',
                            'precipitation_active_constituents']:
                    if new_active[col]['value'][-1]:
                        msg = '\nSettling is off. Either turn it on or '
                        if col == 'initial_concentration':
                            msg += '\nminerals cannot be specified as '
                            msg += 'initial value.\n'
                        else:
                            msg = '\nminerals cannot be specified as inflow.\n'
                        msg += 'Found mineral {0} in {1}.\n'.format(name, col)
                        msg += 'Please deactivate in {0}'.format(
                            new_active['meta_data']['value']['name'])
                        print(msg)
                        sys.exit(1)
        self.input.data['active_constituents'] = new_active

    def make_time_varying_code_names(self):
        """Create code names that vary over time.
        """
        w2_time_vayring_names = []
        self.active_time_varying_groups = []
        for name in self.time_varying_groups:
            if name in self.input.data:
                self.active_time_varying_groups.append(name)
                if 'meta_data' in self.input.data[name]:
                    w2_time_vayring_names.extend(
                        self.input.data[name]['meta_data']['default']
                        ['w2_code_names_map'].values())
                else:
                    for entry in self.input.data[name].values():
                        try:
                            w2_time_vayring_names.append(entry['w2_code_name'])
                        except KeyError:
                            print(entry, name)
                            raise
        self.w2_time_vayring_names = set(w2_time_vayring_names)

    def convert_time_varying_data(self, jday_offset=0):
        """Write time varying data into files for W2.

            Time varying data such as meteorology or river
            inflows are converted form dates to jdays.
            They are written into file in a temp dir.

            Large periods without entries are padded because
            otherwise W2 crashes.
        """
##        def check_dates(name, dates):
##            """Check if dates make scence.
##            """
##            if dates[0] > start_jday:
##                print('Starting date for %s is ' % name, end='')
##                print('later than model starting date.')
##                print('Model start date: %s' % str(self.start_date))
##                print('%s start date: %s' % (name, dates['date']['value'][0]))
##                raise Exception
##            if dates[-1] < end_jday:
##                dates.append(end_jday)
##            return dates
##        optional_branch_file_names = ['tin', 'qot', 'qin', 'cin']
##        end_jday = self.jday_converter.make_jday_from_date(self.end_date)
##        start_jday = self.jday_converter.make_jday_from_date(self.start_date)
        if not os.path.exists(self.temp_path):
            os.mkdir(self.temp_path)
        path_names_file = open(os.path.join(self.temp_path,
                                            'pathnames.txt'), 'w')
        for name in self.active_time_varying_groups:
            data = self.input.data[name]
            dates = data['date']['jday']
            if name in self.w2_file_global_names:
                path = os.path.join(self.temp_path, '%s.npt'
                                    % self.w2_file_global_names[name])
                w2_fn = self.w2_file_global_names[name] + 'fn'
                path_names_file.write(w2_fn + '\n' + path + '\n')
                self._write_time_varying_data(name, 'global', data, dates,
                                              path, jday_offset)
            if name in self.w2_branch_file_names:
                w2_fn = self.w2_branch_file_names[name] + 'fn'
                path_names_file.write(w2_fn + '\n')
                nbranches = self.input.data['bounds']['number_of_branches']['value']
                for branch in range(1, nbranches + 1):
                    path = os.path.join(self.temp_path, '%s_br%d.npt'
                                        % (self.w2_branch_file_names[name],
                                           branch))
                    branch_name = 'branch{0}'.format(branch)
                    self._write_time_varying_data(name, branch_name, data,
                                                  dates, path, jday_offset)
                    path_names_file.write(path + '\n')
            if name in self.w2_tributary_file_names:
                w2_fn = self.w2_tributary_file_names[name] + 'fn'
                path_names_file.write(w2_fn + '\n')
                trib_type = name.split('_')[1]
                for counter, trib_name in enumerate(self.input.data
                        ['tributaries']['tributary_names']['value']):
                    path = os.path.join(self.temp_path, '%s_tr%d.npt'
                                % (self.w2_tributary_file_names[name],
                                   counter + 1))
                    data = self.input.data[trib_name + '_' + trib_type]
                    dates = data['date']['jday']
                    self._write_time_varying_data(name, trib_name, data, dates,
                                                  path, jday_offset)
                    path_names_file.write(path + '\n')
            del self.input.data[name]
            print('deleted', name)
        path_names_file.write('end\n')
        path_names_file.close()

    def _update_time_varying_data_names(self):
        """Update names of time varying data for concentration data.

        Precipitation, branch inflow, and tributary concentration input
        have variable header names that are determined by activeconst.
        We need to update `self.time_varying_variables_order` accordingly.
        """
        constituent_names = (self.input.data['active_constituents']
                             ['constituent_name']['value'])
        for name in self.time_varying_variables_order:

            if name.endswith('_concentration'):
                active = self.time_varying_variables_order[name][1]
                mask = self.input.data['active_constituents'][active]['value']
                new_names = [constituent_name for flag, constituent_name in
                             zip(mask, constituent_names) if flag]
                new_names.insert(0, self.time_varying_variables_order[name][0])
                self.time_varying_variables_order[name] = new_names

    def _write_time_varying_data(self, name, trib_name, data, dates, path,
                                 jday_offset):
        """Write time varying data to a file.
        """
        fobj = open(path, 'w')
        fobj.write('Automatically converted data.'
                   'Dates are replaced with jdays.'
                   'Periods for more than'
                   ' %d days are appended with data from last jday.\n'
                   % self.time_padding_period)

        def write_padding_day(day, offset):
            """Write day before start data.
            """
            fobj.write(format_ %day)
            for entry in \
                self.time_varying_variables_order[name][1:]:
                try:
                    value = data[entry]['value']
                except KeyError:
                    msg = trib_name + '\n'
                    msg += 'Constituent {0} for {1} '.format(
                        entry, trib_name)
                    msg += 'set active but not provided.\n'
                    msg += 'Set inactive or provide concentration.'
                    raise_or_show_info(ValueError, msg)
                fobj.write(format_ % value[n - offset])
            fobj.write('\n')

        for header in self.time_varying_variables_order[name]:
            fobj.write('%30s\t' % header)
        fobj.write('\n')
        check_first = False
        old_jday = 0.0
        first = True
        format_ = '%30.15f\t'
        for n, jday in enumerate(dates):
            jday -= jday_offset
            if jday < 0.0:
                check_first = True
                continue
            else:
                if check_first and jday > 1.0:
                    check_first = False
                    for day in [0.5, 1.0]:
                        write_padding_day(day, 1)
                    first = False
            if first:
                write_padding_day(day=0.0, offset=0)
                first = False
            first = False
            check_first = False
            while jday - old_jday > self.time_padding_period:
                fobj.write(format_ % (old_jday + self.time_padding_period))
                for entry in self.time_varying_variables_order[name][1:]:
                    fobj.write(format_ % data[entry]['value'][n - 1])
                fobj.write('\n')
                old_jday += self.time_padding_period
            fobj.write(format_ %jday)
            for entry in self.time_varying_variables_order[name][1:]:
                try:
                    value = data[entry]['value'][n]
                except IndexError:
                    value = data[entry]['value'][-1]
                fobj.write(format_ %value)
            fobj.write('\n')
            old_jday = jday
        fobj.flush()
        fobj.close()


    def init_jday_converter(self):
        """Initialize the time step converter.
        """

        def make_start_end(date_name):
            """Create start and end dates.
            """
            try:
                date = self.input.data['times'][date_name]['value']
            except KeyError:
                date = self.input.data['times'][date_name]['default']
            return date
        self.start_date = make_start_end('start')
        self.end_date = make_start_end('end')
        self.jday_converter = jday_con.JdayConverter(self.start_date)

    @staticmethod
    def make_date(date_string):
        """Make datetime object from a string.
        """
        date_parts = date_string.split()
        date = [int(x) for x in date_parts[0].split('.')]
        try:
            splitted_date = date_parts[1].split(':')
            hour = splitted_date[0]
            minute = splitted_date[1]
            try:
                decimal_second = splitted_date[2]
            except IndexError:
                decimal_second = '0.0'
            second, second_fraction = divmod(float(decimal_second), 1)
            time_tuple = (int(hour), int(minute), int(second),
                          int(second_fraction * 1e6))
        except IndexError:
            time_tuple = (0, 0, 0, 0)
        # Good magic.
        # pylint: disable-msg=W0142
        return datetime.datetime(date[2], date[1], date[0], *time_tuple)

    def assign_data(self):
        """Assign data to W2.
        """
        make_date = self.jday_converter.make_jday_from_date
        seen = set()
        def recurse(outer_key, map_, meta_data=None):
            """Do one recursion.
            """
            for inner_key, inner_value in map_.items():
                if 'w2_code_name' in inner_value:
                    if inner_value.get('not_used'):
                        print('notused', inner_value['w2_code_name'])
                        continue
                    try:
                        try:
                            value = inner_value['value']
                        except KeyError:
                            value = inner_value['default']
                        if 'dimension' in inner_value:
                            try:
                                dims = tuple([self.dimensions[dim] for dim in
                                              inner_value['dimension']])
                            except KeyError:
                                print('key error')
                                print(inner_value['dimension'])
                                print(self.dimensions)
                                raise
                            if hasattr(value, 'shape'):
                                value = value
                            elif type(value) is list:
                                value = numpy.array(value)
                            else:
                                if not value:
                                    value = 0.0
                                value = numpy.zeros(dims, type(value)) + value
                        if inner_key in self.convert_to_jday:
                            if isinstance(value, list):
                                new_value = []
                                line_number = 2
                                old_date = datetime.datetime(1, 1, 1)
                                complete = False
                                for val in value:
                                    new_date = self.make_date(val)
                                    if new_date <= old_date:
                                        if meta_data:
                                            try:
                                                file_name = \
                                                    meta_data['value']['name']
                                            except KeyError:
                                                file_name = \
                                                  meta_data['default']['name']
                                            msg = ('Error in file %s'
                                                   % file_name +
                                                   ' on line %d!'
                                                   % line_number)
                                            print(msg)
                                        else:
                                            print('Error!')
                                        msg = ('Current date "%s" is earlier'
                                               % (str(new_date),) +
                                               ' than\nprevious date "%s".'
                                               % str(old_date))
                                        print(msg)
                                        print('Dates need to be in increasing',
                                              end='')
                                        print('order.')
                                        sys.exit(1)
                                    else:
                                        if not complete:
                                            if len(new_value):
                                                date = new_date
                                                if new_date >= self.end_date:
                                                    complete = True
                                                    new_value.append(
                                                    make_date(self.end_date))
                                                    break
                                            else:
                                                date = new_date
                                            new_value.append(make_date(date))
                                    old_date = new_date
                                    line_number += 1
                                value = new_value
                                inp = self.input.data[outer_key][inner_key]
                                inp['jday'] = new_value
                            else:
                                value = make_date(value)
                        w2_name = inner_value['w2_code_name']
                        allowed = set(['nxpr1', 'dummy'])
                        if w2_name in seen  and w2_name not in allowed:
                            msg = 'Name "{0}" already used. '.format(w2_name)
                            msg += 'Please use a different name.'
                            raise NameError(msg)
                        seen.add(w2_name)
                        self.w2_code_names[w2_name] = value
                        self.w2_name_map[inner_key] = w2_name
                        self.constituent_names[inner_key] = w2_name
                    except TypeError:
                        print(inner_key)
                        print(inner_value)
                        raise

        def flatten_file_data(map_):
            """Flatten the nested dict.
            """
            result = {}
            try:
                name_map = map_['meta_data']['value']['w2_code_names_map']
            except KeyError:
                try:
                    name_map = \
                             map_['meta_data']['default']['w2_code_names_map']
                except KeyError:
                    return value
            for name, w2_name in name_map.items():
                result[name] = {'w2_code_name': w2_name}
                try:
                    new_value = map_[name]
                except KeyError:
                    new_value = {'not_used': True}
                if name == 'date' and 'time' in map_:
                    date_with_time = [d + ' ' + t for d, t in
                                      zip(map_[name]['value'],
                                          map_['time']['value'])]
                    new_value['value'] = date_with_time
                result[name].update(new_value)
            return result
        self.dimensions = {}
        for key, value in self.input.data.items():
            for inner_key, inner_value in value.items():
                if inner_key.startswith('number_of'):
                    try:
                        self.dimensions[inner_key] = inner_value['value']
                    except KeyError:
                        self.dimensions[inner_key] = inner_value['default']
        for key, value in self.input.data.items():
            if 'meta_data' in value:
                recurse(key, flatten_file_data(value),
                        meta_data=value['meta_data'])
            else:
                recurse(key, value)
        self.constituent_order = (self.input.data['active_constituents']
                                  ['constituent_name']['value'])


    def make_w2_reverse_name_map(self):
        """Create reverse mapping for looking up internal names with W2 names.
        """
        self.w2_reverse_name_map = {value: key for key, value in
                                    self.w2_name_map.items()}
        self.w2_reverse_name_map.update({value: key for key, value in
                                         self.constituent_names.items()})


    def init_w2(self):
        """Initialize W2
        """
        all_w2_code_names = set()
        for name in self.w2_dim_names:
            self.set_shared_data(name, self.w2_code_names[name])
        if self.config.kinetics:
            self.set_shared_data('constituents', True)
        self.set_shared_data('ncp_additional_minerals',
                             self.number_of_additional_minerals)
        self.w2_proxy.allocate_main()
        self.w2_proxy.set_pointers()
        for name in self.w2_code_names.keys():
            own_value = self.w2_code_names[name]
            if name not in self.w2_time_vayring_names:
                w2_value = self.get_shared_data(name)
                shape = None
                try:
                    shape = w2_value.shape
                    if isinstance(own_value, str):
                        own_value = numpy.array(list(own_value))
                    else:
                        own_value = numpy.array(own_value)
                except AttributeError:
                    pass
                if shape:
                    #if name not in self.config.additional_species:
                    try:
                        if w2_value.shape != own_value.shape:
                            if name == 'title':
                                pass
                            else:
                                if name not in self.time_padded_data:
                                    print('Error: W2 variable %s' % name)
                                    print('Error: variable %s' % self.w2_reverse_name_map[name])
                                    msg = ('has dimensions of %s but required are dimensions of %s.'
                                           % (own_value.shape, w2_value.shape))
                                    print(own_value)
                                    print(w2_value)
                                    print(msg)
                                    sys.exit(1)
                                else:
                                    w2_value[:len(own_value)] = own_value
                        else:
                            w2_value[:] = own_value
                    except ValueError:
                        print(w2_value)
                        print(self.w2_code_names[name])
                        raise
                    self.set_shared_array_data(name, w2_value)
                else:
                    if type(self.w2_code_names[name]) == str:
                        if name != 'title':
                            self.set_shared_array_data(name,
                                                       numpy.array(own_value))
                    else:
                        self.set_shared_data(name, own_value)
        self.w2_proxy.initvariables()

    def update_geometry(self):
        """Check if a new branch needs to be added.
        """
        print('checking if new branch needs to be added')
        water_level = max(self.get_shared_data('elws'))
        vactive = self.get_shared_data('vactive')
        self.geometry_updater.adjust_branches(self.w2_proxy.active_volume,
                                              water_level,
                                              vactive)
        if self.geometry_updater.branch_updates:
            print('adding new branch')
            self.new_branch = True
            self.offset_balance = True
            self.ph_output_hack = True
            if self.use_pyro:
                print('pid', self.w2_proxy_pid)
                self.w2_proxy.stop()
                self._start_w2_proxy()
                self.w2_proxy = core.getProxyForURI(
                             "PYROLOC://localhost:7766/w2_proxy")
            else:
                print('volume before', self.w2_proxy.active_volume)
                self.show_volume = True
                self.w2_proxy.close_files()
                self.w2_proxy.deallocate_main()
                self.w2_proxy.deallocate_pointers()
                print('deallocated')
            self.assign_data()
            self.convert_time_varying_data(self.jday)
            self.init_w2()
            self.w2_readinput()
            if self.config.precalc_gw:
                self.config.pre_gw.set_qs(self.config.pitlakq_date)
                if self.config.precalc_gw_conc:
                    self.config.pre_gw.set_conc()
        else:
            print('no new branch added')

    def constituents(self):
        """Do constituent calculations.
        """
        self.w2_proxy.constituentcalculations(self.config.kinetics,
                                              self.add_ssp, self.add_ssgw,
                                              self.add_ssload)

    def set_shared_data(self, name, value, is_ssload=False):
        """Write data to FORTRAN module.
        """
        self.w2_proxy.set_shared_data(name, value, is_ssload)

    def set_shared_array_data(self, name, value, is_ssload=False):
        """Write an array to a FORTRAN module.
        """
        w2_value = self.get_shared_data(name, is_ssload)
        try:
            w2_value[:] = value
        except IndexError:
            # Got a string.
            # This is a an array of shape `()` with dtype `S%d`,
            # i.e. a bytestring of fixed length
            w2_value = value
        except ValueError:
            print('expected:', w2_value.shape, file=sys.stderr)
            print('got:', value.shape, file=sys.stderr)
            print('for:', name, file=sys.stderr)
            raise
        self.w2_proxy.set_shared_data(name, w2_value, is_ssload)

    def get_shared_data(self, name, is_ssload=False):
        """Retrieve data form a FORTRAN module.
        """
        return self.w2_proxy.get_shared_data(name, is_ssload)


class TimeError(ValueError):
    """Own Exception
    """
    pass
