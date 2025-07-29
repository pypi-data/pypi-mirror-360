"""Lake. This contains W2, PHREEQC, Sediment, and Treatment.
"""
from __future__ import print_function

import pickle
import copy
import os
import sys

import numpy

# NumPy, dynamic members.
# pylint: disable-msg=E1101
# pylint: disable-msg=E1103
# Many attributes defined outside __init__.
# pylint: disable-msg=W0201

import pitlakq.numericalmodels.existingmodels.phreeqc.phreeqc as phreeqc
import pitlakq.submodels.lake.co2sat as co2sat
import pitlakq.submodels.treatment.substance_addition.addition as addition
import pitlakq.submodels.erosion.erosion as erosion
import pitlakq.submodels.sediment.leaching as leaching

import pitlakq.commontools.output.ncoutput as ncoutput
import pitlakq.metamodel.running.db as db
import pitlakq.numericalmodels.existingmodels.w2.w2 as w2
import pitlakq.numericalmodels.existingmodels.w2.balance as balance


class Lake(object):
    """
    Lake consisting of W2 and Phreeqc.
    """

    def __init__(self,
                 config,
                 active_const_names,
                 active_minerals_names,
                 rates,
                 mineral_rates,
                 begin):
        """
        Starting calculation.
        Instances of W2 and Phreeqc are created.
        First run is done:
        short W2 calcualtion and Phreeqc
        calculation to loadbalance.
        Results from initial calculations are
        not to be outputted; for clean intial conditions
        only
        """
        config.lake = self
        config.specie_balances = {}
        self.config = config
        if not self.config.silent:
            print('start of module lake')
        self.active_const_names = active_const_names
        self.active_minerals_names = active_minerals_names
        self.rates = rates
        self.mineral_rates = mineral_rates
        self.begin = begin
        self.phreeqc_coupling = self.config.phreeqc_coupling_lake
        self.gw_coupling = config.gw_lake_coupling
        self.db = db.SharedDB()
        self.w2_short_path = config.w2_short_path
        if self.phreeqc_coupling:
            self.co2_sat = co2sat.CO2Sat(config.co2_sat_file_name)
        self.first_time_step()
        self.step_corrector = 0.0
        self.reduced = config.reduced
        self.apply_treatment = False
        if self.config.leaching:
            self.leaching = leaching.Leaching(self.config,
                                              self.phreeqc.constituents)
        self.balance = balance.W2Balance(self.config)
        if self.phreeqc_coupling:
            self.phreeqc_put = False
        self.old_year = 100000
        self.old_erosion_balance = {}

    def first_time_step(self):
        """Calculate the first time step.
        """
        self.w2 = w2.W2(self.config)
        self.config.w2 = self.w2
        self.w2.init_w2()
        balance_names = {}
        for key, value in self.w2.w2_name_map.items():
            balance_names[value] = key
        self.config.balance_names = balance_names
        if self.config.loading:
            self.w2.add_ssload = True
            self.w2.set_shared_data('loading', True)
        if self.config.treatment:
            self.addition = addition.AllAdditions(self.config.additions,
                                                  self.config.treatment_path,
                                                  self.config.w2_output_file,
                                                  self.w2)
        self.year = self.w2.date.year
        self.add_ssp = self.phreeqc_coupling or self.config.treatment
        self.add_ssgw = (self.gw_coupling or self.config.precalc_gw_conc or
                         self.config.gwh)
        self.w2.add_ssgw = self.add_ssgw
        if self.gw_coupling:
            self.w2.set_shared_data('gw_coupling', True)
        self.w2.w2_readinput()
        self.time_old = self.w2.jday * 86400
        for name in ['elws', 'ds', 'us', 'uhs', 'dhs', 'kt', 'kb']:
            print(name, self.w2.get_shared_data(name))
        self.w2.w2_hydrodynamics()
        self.w2.constituents()
        ex_list = self.config.lake_ex_list
        in_list = self.config.lake_inc_list
        if self.phreeqc_coupling:
            self.phreeqc_put = False
            self.phreeqc = phreeqc.Phreeqc(self.config,
                                           self.active_const_names,
                                           self.active_minerals_names,
                                           self.rates,
                                           self.mineral_rates,
                                           self.w2)
            self.get_w2_values()
            self.get_init_conc()
            self.phreeqc.pe = self.phreeqc.ph
            self.phreeqc.header_text = ('Run 0 for load balancing with charge'
                                        ' of abundant species')
            if not self.config.silent:
                print('charge balancing solution...')
            self.phreeqc.do_first_run()
            self.make_diff()
            self.co2_sat_data = numpy.zeros(self.phreeqc.v_active.shape[1],
                                            float)
            self.z_dimension = self.phreeqc.v_active.shape[0]
            # change this later
            self.make_co2_sat()
            self.w2.add_ssp = 1
            phreeqc_balance = {}
            phreeqc_balance[''] = {}
            self.phreeqc_balance = phreeqc_balance['']
            self.config.specie_balances['phreeqc'] = phreeqc_balance
            balance_names = self.config.balance_names
            for constituent in self.phreeqc.constituents:
                self.phreeqc_balance[balance_names[constituent['key']]] = 0.0
            for mineral in self.phreeqc.minerals:
                self.phreeqc_balance[balance_names[mineral['key']]] = 0.0
            self.balance_names = balance_names
            self.put_phreeqc_results()
            self.w2.constituents()
            self.w2.add_ssp = 0
            self.phreeqc.run_number = 1
            self.output = ncoutput.NcOutput(self.config,
                                            self.w2,
                                            exclude=ex_list,
                                            include=in_list)
        else:
            self.output = ncoutput.NcOutput(self.config,
                                            self.w2,
                                            exclude=ex_list,
                                            include=in_list)
        self.w2.w2_misccalculations()
        print('mean water level:', self.w2.mean_level)
        self.output_number = 0
        if self.config.erosion:
            dir_name = os.path.dirname(self.config.porewater_in_path)
            if not os.path.exists(dir_name):
                os.mkdir(dir_name)
            self.porewater_in_file = open(self.config.porewater_in_path, 'w')
            self.cec_in_file = open(self.config.cec_in_path, 'w')
            self.cec_out_file = open(self.config.cec_out_path, 'w')
            self.erosion = erosion.Erosion(self.config, self.w2.mean_level)
            self.ordered_porewater_names = sorted(
                                           self.erosion.porewater.spezies)
            self.ordered_cec_names = sorted(self.erosion.cec.spezies)
            # hack: read this numbers from input file
            valences = {'Al': 3, 'Fe(+2)': 2, 'Fe_di': 2, 'Ca': 2, 'Mg': 2,
                        'Na': 1, 'K': 1}
            self.balance_porewater_names = []
            self.porewater_molar_weights = []
            self.erosion_valences = []
            name_map = {}
            weight_map = {}
            for constituent in self.phreeqc.constituents:
                value = self.config.balance_names[constituent['key']]
                key = constituent['phreeqc_name']
                name_map[key] = value
                weight_map[key] = constituent['molar_weight']
            for name in self.ordered_porewater_names:
                self.balance_porewater_names.append(name_map[name])
                self.porewater_molar_weights.append(weight_map[name])
                self.erosion_valences.append(valences[name])
            self.balance_cec_names = []
            self.cec_molar_weights = []
            for name in self.ordered_cec_names:
                if name == 'H':
                    self.balance_cec_names.append(name)
                    self.cec_molar_weights.append(0.0)
                else:
                    self.balance_cec_names.append(name_map[name])
                    self.cec_molar_weights.append(weight_map[name])
            for fobj in [self.porewater_in_file, self.cec_in_file,
                         self.cec_out_file]:
                fobj.write('%10s %5s %16s' % ('date', 'time', 'volume'))
            for name in self.ordered_porewater_names:
                self.porewater_in_file.write(' %16s' % name)
            self.porewater_in_file.write('\n')
            for fobj in [self.cec_in_file, self.cec_out_file]:
                for name in self.ordered_cec_names:
                    fobj.write(' %16s' % name)
                fobj.write('\n')
            self.erosion_balance = {'porewater': {}, 'cec': {}}
            for name in self.balance_porewater_names:
                self.erosion_balance['porewater'][name] = 0.0
            for name in self.balance_cec_names:
                self.erosion_balance['cec'][name] = 0.0
            self.config.specie_balances['erosion'] = self.erosion_balance
            self.erosion_balance['porewater']['sulfate'] = 0.0
        self.old_output_day = 0

    def get_trib_names(self):
        """Get tributaries fom ZODB.
        """
        if 'trib_names' not in self.db.root:
            raise KeyError('no tributary names set in database')
        self.trib_names = self.db.root['trib_names']

    def run(self, until, step, output_step='step'):
        """
        Run until jday 'until' with
        step size 'step':
        lake.run(31, 1)
        i.e. until end of january,
        with 1 d exchange time step with Phreeqc.
        output_step defaults to step.
        """
        self.year = self.w2.date.year
        leaching_step = None
        if self.old_year < self.year:
            # check for branch addition every year
            self.w2.update_geometry()
            if self.gw_coupling:
                self.w2.set_shared_data('gw_coupling', True)
        self.old_year = self.year
        phreeqc_read = False
        phreeqc_step = self.config.phreeqc_step
        leaching_step = self.config.leaching_step
        self.reduced_coupling = False
        if self.reduced:
            self.reduced_coupling = self.phreeqc_coupling
        if output_step == 'step':
            output_step = step
        old_day = float(self.w2.jday)
        old_phreeqc_day = old_day
        old_leaching_day = old_day
        print_day = old_day
        w2_counter = 0
        if self.phreeqc_coupling:
            self.phreeqc.header_text = 'Phreeqc run as part of lake model'
            self.phreeqc.charge = 'pH'
        for name in ['elws', 'ds', 'us', 'uhs', 'dhs', 'kt', 'kb']:
            print(name, self.w2.get_shared_data(name))
        print('mean water level:', self.w2.mean_level)
        while self.w2.jday <= until:
            if (self.config.loading and
                self.w2.date - self.last_loading_date >= self.loading_step):
                self.loading.set_load(w2=self.w2,
                                      water_level=self.w2.mean_level,
                                      jday=self.w2.jday,
                                      dt=self.loading_step)
                self.last_loading_date = self.w2.date
            if self.config.phreeqc_coupling_lake:
                if hasattr(self.config, 'phreeqc_steps'):
                    self.config.current_phreeqc_steps = 1
                    for steps in self.config.phreeqc_steps:
                        if self.year == steps['year']:
                            if (self.w2.jday >= steps['start'] and
                                self.w2.jday <= steps['end']):
                                self.config.current_phreeqc_steps = \
                                                        steps['steps']
                                break
                if hasattr(self.config, 'phreeqc_conditions'):
                    self.config.current_conditions = []
                    for condition in self.config.phreeqc_conditions:
                        if self.year == condition['year']:
                            if (self.w2.jday >= condition['start'] and
                                self.w2.jday <= condition['end']):
                                self.config.current_conditions.append(
                                    condition['name'])
                if hasattr(self.config, 'saturation_index'):
                    for condition in self.config.saturation_index:
                        if self.year == condition['year']:
                            if (self.w2.jday >= condition['start'] and
                                self.w2.jday <= condition['end']):
                                self.config.current_saturation_index = \
                                                        condition['SI']
                else:
                    self.config.current_saturation_index = {}
                    for name in self.phreeqc.minerals_dict.keys():
                        self.config.current_saturation_index[name] = 0.0
                if hasattr(self.config, 'no_phreeqc'):
                    self.config.no_phreeqc_segments = []
                    for no_phreeqc in self.config.no_phreeqc:
                        if self.year == no_phreeqc['year']:
                            if (self.w2.jday >= no_phreeqc['start'] and
                                self.w2.jday <= no_phreeqc['end']):
                                self.config.no_phreeqc_segments = \
                                                    no_phreeqc['segments']
            w2_counter += 1
            if self.phreeqc_coupling:
                phreeqc_string = ('Phreeqc Run %d is active   '
                                  % self.phreeqc.run_number)
                phreeqc_finished_string = ('Phreeqc Run %d has finished'
                                           % self.phreeqc.run_number)
            empty = ' ' * 40
            if self.w2.jday > print_day + 1:
                print_day = int(self.w2.jday)
                if not self.config.silent:
                    sys.stdout.write('jday = %6.2f  W2 runs = %6d %s\r'
                                         %(round(self.w2.jday, 2), w2_counter,
                                           empty))
                    sys.stdout.stdout.flush()
            self.w2.w2_hydrodynamics()
            self.w2.constituents()
            self.w2.add_ssp = 0
            if self.w2.jday >= old_day + step:
                if hasattr(self.config, 'variable_phreeqc_step'):
                    for v_step in self.config.variable_phreeqc_step:
                        if (self.year == v_step['year'] and
                                self.w2.jday >= v_step['start'] and
                                self.w2.jday <= v_step['end']):
                            phreeqc_step = v_step['step']
                            break
                        else:
                            phreeqc_step = self.config.phreeqc_step
                if (self.phreeqc_coupling and self.w2.jday >=
                    old_phreeqc_day + phreeqc_step):
                    self.phreeqc_put = False
                    old_phreeqc_day = float(self.w2.jday)
                    self.get_w2_values()
                    if self.config.erosion:
                        self.erosion.make_phreeqc_data(self.water_level,
                                                        self.phreeqc.delta_t,
                                                        self.erosion_volume)
                        if self.config.calculate_erosion:
                            self.phreeqc.erosion_active = self.erosion_active
                            self.phreeqc.erosion_cec = self.erosion.cec_in
                            self.phreeqc.erosion_porewater = \
                                                    self.erosion.porewater_in
                            self.phreeqc.erosion_cec_spezies = \
                                                    self.erosion.cec_spezies
                            self.phreeqc.erosion_cec_valences = \
                                                    self.erosion.cec.valences
                            self.phreeqc.porewater_moles = \
                                                self.erosion.porewater_moles
                    if not self.config.silent:
                        sys.stdout.write('jday = %6.2f  W2 runs = %6d %s\r'
                                         % (round(self.w2.jday, 2),
                                            w2_counter, phreeqc_string))
                        sys.stdout.stdout.flush()
                    self.phreeqc.do_next_run()
                    if not self.config.silent:
                        sys.stdout.write('jday = %6.2f  W2 runs = %6d %s\r'
                                         % (round(self.w2.jday, 2), w2_counter,
                                            phreeqc_finished_string))
                        sys.stdout.stdout.flush()
                    if self.config.calculate_erosion:
                        date_string = self.w2.date.strftime('%d.%m.%Y')
                        time_string = self.w2.date.strftime('%H:%M')
                        for fobj in [self.porewater_in_file, self.cec_in_file,
                                     self.cec_out_file]:
                            fobj.write('%10s %5s %16.3f' % (date_string,
                                                            time_string,
                                                        self.erosion_volume))
                        sulfate_mass = 0.0
                        for index, name in enumerate(
                                       self.ordered_porewater_names):
                            balance_name = self.balance_porewater_names[index]
                            molar_weight = self.porewater_molar_weights[index]
                            try:
                                porewater_in = numpy.sum(
                                    self.phreeqc.erosion_porewater[name] *
                                    self.phreeqc.porewater_moles *
                                    self.erosion_layer_volumes) * 1000
                                value = porewater_in * molar_weight / 1e6
                                sulfate_mass += (value *
                                                 self.erosion_valences[index])
                                self.erosion_balance['porewater']\
                                                [balance_name] += value
                            except ValueError:
                                print(name)
                                print('self.phreeqc.erosion_porewater', end='')
                                print(self.phreeqc.erosion_porewater[name])
                                print('self.phreeqc.porewater_moles', end='')
                                print(self.phreeqc.porewater_moles)
                                print('self.erosionLayer_volumes', end='')
                                print(self.erosionLayer_volumes)
                                raise
                            self.porewater_in_file.write(' %16.5f' %
                                                         porewater_in)
                        self.erosion_balance['porewater']['sulfate'] += \
                                                            sulfate_mass / 2
                        self.porewater_in_file.write('\n')
                        self.porewater_in_file.flush()
                        for index, name in enumerate(self.ordered_cec_names):
                            balance_name = self.balance_cec_names[index]
                            molar_weight = self.cec_molar_weights[index]
                            cec_in = (numpy.sum(self.phreeqc.erosion_cec[name]
                                                * self.erosion_layer_volumes)
                                      * 1000)
                                        #/self.phreeqc.erosionCecValences[name]
                            cec_out = numpy.sum(numpy.where(
                                self.phreeqc.exchange_result[name] > -0.01,
                                self.phreeqc.exchange_result[name] *
                                self.erosion_active, 0.0)) * 1000
                                #/self.phreeqc.erosionCecValences[name]
                            value = (cec_in - cec_out) * molar_weight / 1e6
                            self.erosion_balance['cec'][balance_name] += value
                            self.erosion.cec_out[name] = cec_out
                            self.cec_in_file.write(' %16.5f' % cec_in)
                            self.cec_out_file.write(' %16.5f' % cec_out)
                        self.cec_in_file.write('\n')
                        self.cec_out_file.write('\n')
                        self.cec_in_file.flush()
                        self.cec_out_file.flush()
                    self.make_diff()
                    self.make_co2_sat()
                    if not self.config.treatment:
                        self.put_phreeqc_results()
                    phreeqc_read = True
                    self.phreeqc.run_number += 1
                    self.w2.add_ssp = 1
                if self.config.treatment:
                    if phreeqc_read:
                        set_zero = False
                        phreeqc_read = False
                        self.put_phreeqc_results()
                    else:
                        set_zero = True
                    apply_treatment = self.addition.add_substances(
                        self.year, float(self.w2.jday), set_zero)
                    self.addition.output = 0
                    if apply_treatment:
                        self.w2.add_ssp = 1
                if (self.config.leaching and self.w2.jday >=
                    old_leaching_day + leaching_step):
                    old_leaching_day = float(self.w2.jday)
                    #if self.leaching.hasStorage:
                    #    set_zero = 0
                    #    self.leaching.leach(self.year, self.w2.jday, set_zero)
                    leaching_step = self.leaching.leach()
            if self.w2.jday >= self.old_output_day + output_step:
                self.output.write_output(self.output_number)
                if self.output_number == 0:
                    self.output.write_independent_output()
                self.output_number += 1
                self.old_output_day = float(self.w2.jday)
                if self.config.treatment:
                    self.addition.output = 1
            if self.w2.jday > old_day + step:
                old_day = float(self.w2.jday)
            self.w2.w2_misccalculations()
        if leaching_step:
            print()
            print('leaching step %d' % leaching_step)
            print()

    def get_w2_values(self):
        """
        Get values from CE-QUAL-W2.
        """
        self.phreeqc.constituents_dict = {}
        self.phreeqc.minerals_dict = {}
        for constituent in self.phreeqc.constituents:
            #if concentrations are negative (-> numerical problems in w2),
            # set them to zero
            w2_value = self.w2.get_shared_data(constituent['key'])
            try:
                molar_weight = constituent['molar_weight']
            except KeyError:
                print('\nNo molar_weight found for specie {0}.'.format(
                    constituent['name']))
                print('Please specify molar_weight in "const_names.txt".')
                sys.exit(1)
            try:
                w2_value = numpy.where(w2_value > 1.0e-40, w2_value, 0.0)
                self.phreeqc.constituents_dict[constituent['phreeqc_name']] = \
                    numpy.where(w2_value > 1.0e-40, w2_value / molar_weight,
                                0.0)
            except FloatingPointError as err:
                numpy.set_printoptions(threshold=int(1e4))
                print(w2_value, molar_weight)
                raise err
        for mineral in self.phreeqc.minerals:
            self.phreeqc.minerals_dict[mineral['phreeqc_name']] = \
                self.w2.get_shared_data(
                    mineral['key']) / mineral['molar_weight']
        self.phreeqc.ph = self.w2.get_shared_data('ph')
        self.phreeqc.temperature = self.w2.get_shared_data('t2')
        self.phreeqc.v_active = self.w2.get_shared_data('vactive')
        self.time_new = self.w2.jday * 86400
        self.phreeqc.delta_t = self.time_new - self.time_old
        if self.phreeqc.delta_t < 0:
            self.phreeqc.delta_t = self.time_new
        self.time_old = self.time_new
        self.phreeqc.h_active = self.w2.get_shared_data('hactive')
        if self.config.erosion:
            self.water_level = self.w2.mean_level
            self.find_erosion_active()

    def put_phreeqc_results(self):
        """
        Set values in  CE-QUAL-W2.
        """
        if self.phreeqc_put:
            return
        vactive = self.w2.get_shared_data('vactive')[:]
        for constituent in self.phreeqc.constituents:
            if constituent['key'] == 'dox':
                name = 'dossp'
            else:
                name = constituent['key'] + 'ssp'
            value = (
                self.phreeqc.const_result_dict[constituent['phreeqc_name']]
                * constituent['molar_weight'])
            if constituent['key'] == 'ldom':
                value = (self.phreeqc.const_result_dict[
                         constituent['phreeqc_name']] *
                         constituent['molar_weight'] + 0.0)
            self.w2.set_shared_array_data(name, value)
            bal_key = self.balance_names[constituent['key']]
            bal_value = numpy.sum(value * vactive) / 1e6
            self.phreeqc_balance[bal_key] += bal_value
            if self.config.erosion and hasattr(self, 'erosion_balance'):
                erosion_balance = (
                    self.erosion_balance['porewater'].get(bal_key, 0)
                    + self.erosion_balance['cec'].get(bal_key, 0))
                self.phreeqc_balance[bal_key] -= (erosion_balance -
                                    self.old_erosion_balance.get(bal_key, 0))
                self.old_erosion_balance[bal_key] = erosion_balance
        if hasattr(self.phreeqc, 'minerals_result_dict'):
            for mineral in self.phreeqc.minerals:
                mineral_name = mineral['key'] + 'ssp'
                # different index from const
                value = (self.phreeqc.minerals_result_dict[mineral[
                         'phreeqc_name']] * mineral['molar_weight'])
                self.w2.set_shared_array_data(mineral_name, value)
                bal_key = self.balance_names[mineral['key']]
                bal_value = numpy.sum(value * vactive) / 1e6
                self.phreeqc_balance[bal_key] += bal_value
                if self.config.erosion and hasattr(self, 'erosion_balance'):
                    erosion_balance = (self.erosion_balance[
                        'porewater'].get(bal_key, 0) +
                                self.erosion_balance['cec'].get(bal_key, 0))
                    self.phreeqc_balance[bal_key] -= (erosion_balance -
                                    self.old_erosion_balance.get(bal_key, 0))
                    self.old_erosion_balance[bal_key] = erosion_balance
        self.w2.set_shared_array_data('ph',
                                      numpy.where(self.phreeqc.ph_result > -10,
                                                  self.phreeqc.ph_result,
                                                self.w2.get_shared_data('ph')))
        self.w2.set_shared_array_data('co2sat', self.co2_sat_data)
        self.phreeqc_put = True

    def find_erosion_active(self):
        """
        Finding lake cells that eluate eroded
        material. v_active + rule
        rule: 2cd row
        """
        row_summed_volume = numpy.sum(self.phreeqc.v_active, 0)
        met_upper_layer = False
        limit = 0.1
        active_layer = 0
        for volume in row_summed_volume:
            if met_upper_layer:
                self.erosion_volume = volume
                break
            elif volume > limit:
                met_upper_layer = True
            active_layer += 1
        self.erosion_active = copy.deepcopy(self.phreeqc.v_active)
        self.erosion_active[:, :active_layer] = \
                                self.erosion_active[:, active_layer + 1:] = 0
        self.erosion_layer_volumes = self.phreeqc.v_active[:, active_layer]

    def get_init_conc(self):
        """Get initial concentration.
        """
        self.phreeqc.constituents_dict = {}
        self.phreeqc.minerals_dict = {}
        x = self.w2.dimensions['number_of_constituents_segments']
        z = self.w2.dimensions['number_of_constituents_layers']
        dims = z, x
        self.phreeqc.temperature = numpy.zeros(dims, float)
        self.phreeqc.temperature[:] = \
        self.config.w2_input.data['initial_conditions']['temperature']['value']
        for constituent in self.phreeqc.constituents:
            value = numpy.zeros(dims, float)
            try:
                value[:] = (numpy.array(
                    self.config.w2_input.data['initial_concentrations']
                                             [constituent['name']]['value'])
                    / constituent['molar_weight'])
            except ValueError:
                print(constituent['name'])
                raise
            self.phreeqc.constituents_dict[constituent['phreeqc_name']] = value
        value = numpy.zeros(dims, float)
        value[:] = \
            self.config.w2_input.data['initial_concentrations']['ph']['value']
        self.phreeqc.ph = value
        for mineral in self.phreeqc.minerals:
            self.phreeqc.minerals_dict[mineral['phreeqc_name']] = \
                                    numpy.zeros(self.phreeqc.ph.shape, float)

    def make_diff(self):
        """
        Calcualting difference between
        old W2 and new Phreeqc concentration
        to calculate ssp = source sink phreeqc
        """
        if self.phreeqc.error:
            print()
            print('no phreeqc sink/sources because of error in its calculation')
            for const in self.phreeqc.constituents_dict.keys():
                self.phreeqc.const_result_dict[const][:] = 0.0
            if hasattr(self.phreeqc, 'minerals_result_dict'):
                for mineral in self.phreeqc.minerals_dict.keys():
                    self.phreeqc.minerals_result_dict[mineral][:] = 0.0
        else:
            result = self.phreeqc.const_result_dict
            constituents = self.phreeqc.constituents_dict
            for const in constituents.keys():
                result[const] = result[const] - constituents[const]
            if hasattr(self.phreeqc, 'minerals_result_dict'):
                minerals = self.phreeqc.minerals_dict
                res = self.phreeqc.minerals_result_dict
                for mineral in minerals.keys():
                    res[mineral] = res[mineral] - minerals[mineral]

    def make_co2_sat(self):
        """Retrieve CO2 for saturation.
        """
        p_co2 = min(410, round(1.25956 * self.year - 2151.86, -1))
        if p_co2 < 370:
            p_co2 = 370
        n = 0
        #print(self.phreeqc.v_active)
        for _ in self.co2_sat_data:
            row = 1
            while row < self.z_dimension:
                if self.phreeqc.v_active[row, n]:
                    value = self.co2_sat.get_co2_sat(
                        p_co2, round(self.phreeqc.temperature[row, n], 1),
                        round(self.phreeqc.ph[row, n], 2))
                    try:
                        self.co2_sat_data[n] = value
                    except ValueError as err:
                        print()
                        print('n:', n, 'row:', row, 'value:', value)
                        print(round(self.phreeqc.ph[row, n], 2))
                        raise err
                    break
                else:
                    row += 1
            n += 1
        if self.config.c_as_c:
            # different molar weight of C if treated as C and not HCO3
            self.co2_sat_data = self.co2_sat_data / 5.07955

    def cleanup(self):
        """Cleanup. Close files etc.
        """
        if self.config.phreeqc_coupling_lake:
            fobj = open(os.path.join(self.config.w2_output_path,
                                     'precipitation.pic'), 'wb')
            pickle.dump(self.phreeqc.precipated_minerals, fobj)
            fobj.close()
        if self.config.erosion:
            self.elutionFile.close()
