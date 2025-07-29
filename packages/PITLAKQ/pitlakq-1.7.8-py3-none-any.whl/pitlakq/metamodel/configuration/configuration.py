"""
Configuration file.
"""

from __future__ import print_function

import os
import sys


class Config:
    """Main configuration class.
    """
    # Many instance attributes.
    # pylint: disable=R0902
    # No public methods.
    # pylint: disable=R0903
    # We have 9 arguments instead of 7.
    # pylint: disable=R0913
    def __init__(self,
                 project_name,
                 models_path,
                 pcg_project_name,
                 source_root,
                 ram_path,
                 pcg_short_path,
                 w2_short_path,
                 template_path):
        self.project_name = project_name
        self.models_path = models_path
        self.pcg_project_name = pcg_project_name
        self.source_root = source_root
        self.ram_path = ram_path
        self.pcg_short_path = pcg_short_path
        self.w2_short_path = w2_short_path
        self.template_path = template_path
        self._make_config()

    def _make_config(self):
        """Create all path names.
        """
        # We set lots of attributes here.
        # pylint: disable=W0201
        # Lots of statements.
        # pylint: disable=R0915

        self.w2_source_path = os.path.join(self.source_root, 'pitlakq',
                                           'numericalmodels', 'existingmodels',
                                           'w2', 'w2_proxy.py')
        self.ram_path = os.path.join(self.ram_path, self.project_name)
        if not os.path.isdir(self.ram_path):
            print(self.ram_path)
            os.mkdir(self.ram_path)
        self.project_path = os.path.join(self.models_path, self.project_name)
        self.database = os.path.join(self.project_path,
                                     '%s.fs' % self.project_name)
        self.message_file_name = os.path.join(self.project_path,
                                              '%s.mes' % self.project_name)
        self.w2_path = os.path.join(self.models_path, self.project_name,
                                    'input', 'w2')
        self.gwh_path = os.path.join(self.models_path, self.project_name,
                                     'input', 'gwh')
        self.output_path = os.path.join(self.models_path, self.project_name,
                                        'output')
        self.w2_output_path = os.path.join(self.output_path, 'w2')
        self.w2_output_file = os.path.join(self.w2_output_path, 'out.nc')
        self.erosion_path = os.path.join(self.models_path, self.project_name,
                                         'input', 'erosion')
        self.w2_node_path = os.path.join(self.models_path, self.project_name)
        self.pcg_data_path = os.path.join(self.models_path, self.project_name,
                                          'pcg')
        self.main_path = os.path.join(self.models_path, self.project_name,
                                      'input', 'main')
        self.dual_porosity_input = os.path.join(self.pcg_data_path, 'input',
                                                'dual_porosity.xml')
        self.gw_init_conc = os.path.join(self.pcg_data_path, 'input',
                                         'init_conc.txt')
        self.well_polygons_path = os.path.join(self.pcg_data_path, 'polygons')
        self.well_conc_file_name = os.path.join(self.pcg_data_path, 'input',
                                                'obswells.csv')
        self.w2_input_file_name = os.path.join(self.w2_node_path, 'input',
                                               'w2input.nc')
        self.pre_w2_input_file_name = os.path.join(self.w2_path, 'input',
                                                   'w2input.nc')
        self.w2_const_input_file_name = os.path.join(self.w2_node_path,
                                                     'input',
                                                     'w2constinput.nc')
        self.pre_w2_const_input_file_name = os.path.join(self.w2_path, 'input',
                                                         'w2constinput.nc')
        self.w2_path_filename = os.path.join(self.w2_node_path, 'input',
                                             'path_names.txt')
        self.pre_w2_path_filename = os.path.join(self.w2_path, 'input',
                                                 'path_names.txt')
        self.w2_all_years = os.path.join(self.w2_path, 'input', 'allyears')
        self.pre_w2_input_path = os.path.join(self.w2_path, 'input')
        self.pcg_output_path = os.path.join(self.pcg_data_path, 'output')
        self.pre_output_path = os.path.join(self.w2_path, 'output', 'out.nc')
        self.kb_file_name = os.path.join(self.w2_path, 'output', 'kb43.pic')
        self.kb_mixed_file_name = os.path.join(self.w2_path, 'output',
                                               'kb43_mixed.pic')
        self.w2_output = os.path.join(self.w2_path, 'output')
        self.w2_input = os.path.join(self.w2_path, 'input')
        self.nc_ph_test = os.path.join(self.w2_node_path, 'output',
                                       'ph_test.nc')
        self.phreeqc_output = os.path.join(self.ram_path, 'phreeqc.out')
        self.phreeqc_database = os.path.join(self.ram_path, 'phreeqcw2.dat')
        if sys.platform == 'linux2' or sys.platform == 'darwin':
            self.phreeqc_screen = '/dev/null'
            #self.phreeqc_output = os.path.join('/data/phreeqc.out')
        self.punch_file = os.path.join(self.ram_path, 'phreeqc.pun')
        self.nc_file_name = os.path.join(self.ram_path, 'w2data.nc')
        self.phreeqc_input = os.path.join(self.ram_path, 'phreeqc_input.txt')
        resource_path = os.path.join(self.source_root, 'pitlakq', 'resources')
        self.resource_path = resource_path
        if sys.platform.startswith('linux'):
            self.phreeqc_exe = os.path.join(self.ram_path, 'phreeqc2linux')
            self.phreeqc_exe_original = os.path.join(resource_path,
                                                     'phreeqc2linux')
        elif sys.platform == 'win32':
            self.phreeqc_exe = os.path.join(self.ram_path, 'phreeqc2win.exe')
            self.phreeqc_exe_original = os.path.join(resource_path,
                                                     'phreeqc2win.exe')
        elif sys.platform == 'darwin':
            self.phreeqc_exe = os.path.join(self.ram_path, 'phreeqc2mac')
            self.phreeqc_exe_original = os.path.join(resource_path,
                                                     'phreeqc2mac')
        else:
            raise SystemError('Platform {} not supported.'.format(sys.platform))
        self.all_const_names = os.path.join(resource_path, 'const_names.txt')
        self.all_mineral_names = os.path.join(resource_path,
                                              'mineral_names.txt')
        self.kinetics_file_name = os.path.join(resource_path, 'kinetics.txt')
        self.rates_file_name = os.path.join(resource_path, 'rates.txt')
        self.co2_sat_file_name = os.path.join(resource_path, 'co2sat.nc')
        self.bathymetry_file_name = os.path.join(self.w2_node_path, 'input',
                                                 'w2', 'bath.nc')
        self.pre_bathymetry_file_name = os.path.join(self.w2_path, 'input',
                                                     'bath.nc')
        self.init_conds_file_name = os.path.join(self.w2_node_path, 'input',
                                                 'init_conds.nc')
        self.pre_init_conds_file_name = os.path.join(self.w2_path, 'input',
                                                     'init-conds.nc')
        self.temp_file_name = os.path.join(self.w2_node_path, 'output',
                                           'temp.nc')
        self.pre_temp_file_name = os.path.join(self.w2_path, 'output',
                                               'temp.nc')
        self.pcg_command_file = os.path.join(self.pcg_data_path,
                                             self.pcg_project_name, 'database',
                                             '%s.dbf' % self.pcg_project_name)
        self.pcg_para_file = os.path.join(self.pcg_data_path,
                                          self.pcg_project_name, 'database',
                                          '%spara.dbf' % self.pcg_project_name)
        self.pcg_rabe_file = os.path.join(self.pcg_short_path, 'pcg3',
                                          self.pcg_project_name, 'database',
                                          '%srabe.dbf'
                                          % self.pcg_project_name[:4])
        self.pcg_exe_path = os.path.join(self.source_root, 'pitlakq',
                                         'pcgeofim')
        self.modproj = os.path.join(self.source_root, 'pitlakq', 'pcgeofim',
                                    'modproj.dbf')
        self.pcg_screen = os.path.join(self.ram_path, 'pcgscreen')
        self.project_code = os.path.join(self.main_path, 'project_code.py')
        self.cec_file_name = os.path.join(self.erosion_path,
                                          'materialproperties', 'cec.txt')
        self.porewater_file_name = os.path.join(self.erosion_path,
                                                'materialproperties',
                                                'porewater.txt')
        self.valence_file_name = os.path.join(self.erosion_path,
                                              'materialproperties',
                                              'valences.txt')
        self.steady_state_mass_file_name = os.path.join(self.erosion_path,
                                                        'materialproperties',
                                                        'steadystatemass.txt')
        self.grid_file_name = os.path.join(self.erosion_path, 'lake.grd')
        self.polygons_path = os.path.join(self.erosion_path, 'polygons')
        self.erosion_out_path = os.path.join(self.models_path,
                                             self.project_name,
                                             'output', 'erosion')
        self.sediment_out_path = os.path.join(self.models_path,
                                              self.project_name, 'output',
                                              'sediment')
        self.porewater_in_path = os.path.join(self.erosion_out_path,
                                              'porewater_in.txt')
        self.cec_in_path = os.path.join(self.erosion_out_path, 'cec_in.txt')
        self.cec_out_path = os.path.join(self.erosion_out_path, 'cec_out.txt')
        self.measured_conc_file_name = os.path.join(self.models_path,
                                                    self.project_name,
                                                    'postprocessing',
                                                    'conc_all.csv')
        self.measured_lake_level_file_name = os.path.join(self.models_path,
                                                          self.project_name,
                                                          'postprocessing',
                                                          'wst.txt')
        self.measured_lake_volume_file_name = os.path.join(self.models_path,
                                                           self.project_name,
                                                           'postprocessing',
                                                           'volume.txt')
        self.interflow_path = os.path.join(self.erosion_path, 'interflow')
        self.interflow_conc_file_name = os.path.join(self.interflow_path,
                                                     'interflow_conc.txt')
        self.log_file_name = os.path.join(self.output_path, 'log.txt')
        self.mixed_file_name = os.path.join(self.w2_output, 'mixed.nc')
        self.precal_gw_q_file_name = os.path.join(self.pcg_data_path, 'input',
                                                  'q_balance.csv')
        self.precal_gw_key_file_name = os.path.join(self.pcg_data_path,
                                                    'input', 'wkey.txt')
        self.precal_gw_distrib_file_name = os.path.join(
            self.pcg_data_path, 'input', 'gwq.vmp.in')
        self.treatment_path = os.path.join(self.project_path, 'input',
                                           'treatment')
        self.modmst_path = os.path.join(self.project_path, 'modmst')
        self.pore_volumes_file_name = os.path.join(self.pcg_data_path,
                                                   'input', 'porevolumes.txt')
        self.time_dependent_conc_file_name = os.path.join(
            self.pcg_data_path, 'input', 'time_dependent_conc.txt')
        self.leaching_file_name = os.path.join(self.pcg_data_path, 'input',
                                               'leaching.txt')
        self.leaching_amount_file_name = os.path.join(self.pcg_data_path,
                                                      'input',
                                                      'leaching_amount.txt')
        self.balance_path = os.path.join(self.project_path, 'output',
                                         'balance')
        self.sediment_path = os.path.join(self.project_path, 'input',
                                          'sediment')
        default_attributes = {'gw_model': 'pcg',
                              'time_dependent_precalc_gw_conc': False,
                              'leaching': False,
                              'leaching_step': 1e12,
                              'distributed_gw_temperature': False,
                              'c_as_a': False,
                              'fixed_modmst_water_table': None,
                              'fixed_modmst_temperature': None,
                              'modmst_conc_unmodified': False,
                              'fixed_modmst_conc': False}
        for att, value in default_attributes.items():
            if not hasattr(self, att):
                self.__dict__[att] = value
