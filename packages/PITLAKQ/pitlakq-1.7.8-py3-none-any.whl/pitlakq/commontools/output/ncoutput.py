"""Write output to netCDF file.
"""

from __future__ import print_function

import os
import sys

import numpy
import netCDF4

# NumPy, dynamic members.
# pylint: disable-msg=E1101

class NcOutput(object):
    """NetCDF access.
    """

    def __init__(self,
                 config,
                 w2,
                 **exclude_include):
        self.config = config
        self.w2 = w2
        self.output_file_name = self.config.w2_output_file
        self.phreeqc = self.config.phreeqc_coupling_lake
        self.outputs = {'elws': ('w2x',),
                        'iceth': ('w2x',),
                        'hactive':('w2z', 'w2x'),
                        'vactive':('w2z', 'w2x'),
                        'balance_error':('w2z', 'w2x'),
                        't2':('w2z', 'w2x'),
                        'rho':('w2z', 'w2x'),
                        'tds':('w2z', 'w2x'),
                        't1':('w2z', 'w2x'),
                        'u':('w2z', 'w2x'),
                        'volpr':('nbp',),
                        'voltbr':('nbp',),
                        'quh1_cum_plus': ('w2z', 'nbp'),
                        'quh2_cum_plus': ('w2z', 'nbp'),
                        'qdh1_cum_plus': ('w2z', 'nbp'),
                        'qdh2_cum_plus': ('w2z', 'nbp'),
                        'quh1_cum_minus': ('w2z', 'nbp'),
                        'quh2_cum_minus': ('w2z', 'nbp'),
                        'qdh1_cum_minus': ('w2z', 'nbp'),
                        'qdh2_cum_minus': ('w2z', 'nbp')}
        self.exclude_gw = set(['sed', 'algae', 'feoh3', 'aloh3', 'po4precip',
                               'co2', 'ph', 'co3', 'hco3', 'tds', 'pyrite',
                               'alkal'])
        self.exclude_phreeqc = set(['sed', 'algae', 'tds', 'co2', 'ph', 'co3',
                                    'hco3', 'alkal'])
        for n, name in enumerate(self.w2.constituent_order):
            if (self.w2.input.data['active_constituents']
                ['active_constituents']['value'][n]):
                try:
                    w2_name = self.w2.constituent_names[name]
                except KeyError:
                    print('\nThe name "{0}" is not defined.'.format(name))
                    print('Please check that it is correct or define it in a '
                          'yaml template.')
                    sys.exit(1)
                self.outputs[w2_name] = ('w2z', 'w2x')
                if w2_name == 'dox':
                    w2_name = 'do'
                if self.config.phreeqc_coupling_lake:
                    if w2_name not in self.exclude_phreeqc:
                        self.outputs[w2_name + 'ssp'] = ('w2z', 'w2x')
                if self.config.gw_lake_coupling or self.config.gwh:
                    if w2_name not in self.exclude_gw:
                        self.outputs[w2_name + 'ssgw'] = ('w2z', 'w2x')
                #self.outputs[w2_name + 'ss'] = ('w2z', 'w2x')
        if 'exclude' in exclude_include:
            ex = exclude_include['exclude']
            if type(ex) != type([]):
                ex = [ex]
            self.exclude = ex
        if 'include' in exclude_include:
            include = exclude_include['include']
            if type(include) != type([]):
                include = [include]
            self.include = include
        self.time_independent_output = set(['zu', 'deltax'])
        self.make_outputs()
        self.make_output_file()
        self.did_ph_hack = False

    def make_outputs(self):
        """Figure out what to output.
        """
        variables = self.outputs.keys()
        if hasattr(self, 'exclude'):
            delete = []
            for ex in self.exclude:
                if ex[0] == '*':
                    for variable in variables:
                        if variable.endswith(ex[1:]):
                            delete.append(variable)
                elif ex[-1] == '*':
                    for variable in variables:
                        if variable.startswith(ex[:-1]):
                            delete.append(variable)
                else:
                    for variable in variables:
                        if ex == variable:
                            delete.append(variable)

        if hasattr(self, 'include'):
            delete = set(delete)
            include = set(self.include)
            delete = delete - include
        for variable in delete:
            try:
                del self.outputs[variable]
            except KeyError:
                pass

    def make_output_file(self):
        """Initilaze the netCDF file.
        """
        dir_ = os.path.dirname(self.output_file_name)
        if not os.path.exists(dir_):
            os.makedirs(dir_)
        try:
            output = netCDF4.Dataset(self.output_file_name, 'w',
                                     format='NETCDF3_CLASSIC')
        except RuntimeError as err:
            print(self.output_file_name)
            raise err
        output.createDimension('scalar', 1)
        output.createDimension('time_step_size', 7)
        output.createDimension('time', None)
        output.createDimension('ncp', int(self.w2.get_shared_data('ncp')))
        output.createDimension('nbp', int(self.w2.get_shared_data('nbp')))
        output.createDimension('w2z', self.w2.get_shared_data('w2z').shape[0])
        output.createDimension('w2x', self.w2.get_shared_data('w2x').shape[0])
        output.createVariable('timesteps', 'i', ('time', 'time_step_size'))
        for k, value in self.outputs.items():
            if len(value) == 1:
                output.createVariable(k, 'd', ('time', value[0]))
            elif len(value) == 2:
                output.createVariable(k, 'd', ('time', value[0], value[1]))
            else:
                raise Exception('Array size not supported')
        output.createVariable('zu', 'd', ('w2z',))
        output.createVariable('deltax', 'd', ('w2x',))
        output.close()

    def write_independent_output(self):
        """Write time independent output to nc file.

        cell bottom - zu and
        cell width - deltax
        do not change over time --> store only once
        """
        bott = self.w2.input.data['waterbody_coordinates']['bottom_elevation']
        try:
            bottom = float(bott['value'])
        except KeyError:
            bottom = float(bott['default'])
        bath = netCDF4.Dataset(self.config.bathymetry_file_name, 'r+',
                               format='NETCDF3_CLASSIC')
        deltax = bath.variables['segment_lenght'][:]
        deltaz = bath.variables['layer_height'][:]
        vactive = self.w2.get_shared_data('vactive')
        bottom_indices = len(vactive)
        for bottom_index in range(bottom_indices - 1, 0, -1):
            if numpy.sum(vactive[bottom_index]):
                break
        output= netCDF4.Dataset(self.output_file_name, 'r+',
                                format='NETCDF3_CLASSIC')
        zu = numpy.zeros_like(output.variables['zu'])
        zu[:bottom_index] = (numpy.add.accumulate(deltaz[bottom_index:0:-1])[::-1]
                             + bottom)
        zu[bottom_index] = bottom
        output.variables['zu'][:] = zu
        output.variables['deltax'][:] = deltax
        output.close()
        bath.close()

    def write_output(self, time_step):
        """Write the data for one time step to netCDF file.
        """
        output= netCDF4.Dataset(self.output_file_name, 'r+',
                                format='NETCDF3_CLASSIC')
        nc_obj = output.variables['timesteps']
        nc_obj[time_step, :] = self.w2.jday_converter.make_date_from_jday(
            self.w2.jday).timetuple()[:7]
        for name in self.outputs.keys():
            if name in self.time_independent_output:
                continue
            nc_obj = output.variables[name]
            if self.w2.ph_output_hack and name == 'ph':
                # set the ph for the two time steps following a branch
                # addition to the values of the previous time step
                if self.did_ph_hack:
                    self.did_ph_hack = False
                    self.w2.ph_output_hack = False
                nc_obj[time_step, :] = nc_obj[time_step - 1, :]
                self.did_ph_hack = True
                continue
            if name == 'do':
                name = 'dox'
            try:
                nc_obj[time_step, :] = self.w2.get_shared_data(name)
            except ValueError:
                pass
        output.close()

    @staticmethod
    def is_1_d_array(name):
        """Check if array is 1D.
        """
        if name in ['etbr', 'eibr']:
            return True
        if name.startswith('vol') or name.startswith('tss'):
            return True
        return False

    @staticmethod
    def is_surface_array(name):
        """Chekc i array is at water surface.
        """
        if name in ['elws', 'iceth']:
            return True

    @staticmethod
    def is_mass_balance_array(name):
        """Is ait mass balance array?
        """
        if name.startswith('css'):
            return True
        return False
