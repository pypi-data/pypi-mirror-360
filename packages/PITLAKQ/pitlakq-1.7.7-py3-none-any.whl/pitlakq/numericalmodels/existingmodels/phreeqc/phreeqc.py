"""
Phreeqc module.
Switching between parallel and serial version.
Serial is just a thin wrapper for phreeqc_runner.
"""

from __future__ import print_function

import copy

# NumPy, dynamic members.
# pylint: disable-msg=E1101

import numpy

from pitlakq.commontools import tools
from pitlakq.commontools.input.resources import Resources
from pitlakq.numericalmodels.existingmodels.phreeqc.phreeqc_runner import \
     PhreeqcRunner
from pitlakq.numericalmodels.existingmodels.phreeqc.phreeqc_thread import \
     PhreeqcThread


class Phreeqc(object):
    """Wrapper around PHREEQC.

    This can run in parallel using pyro.
    """
    # Lots of attributes defined outside __init__.
    # pylint: disable-msg=W0201
    def __init__(self,
                 config,
                 active_const_names,
                 active_minerals_names,
                 rates,
                 mineral_rates,
                 w2):
        self.config = config
        self.active_const_names = active_const_names
        self.active_minerals_names = active_minerals_names
        self.rates = rates
        self.mineral_rates = mineral_rates
        self.w2 = w2
        if rates or mineral_rates:
            self.kinetics = True
        else:
            self.kinetics = False
        self._phreeqc_active_species()
        self.header_text = 'Header Text comes here'
        self.charge = self.config.charge #'Sulfate' #'Cl' #
        self.redox_couple = 'O(0)/O'
        self.units = 'mmol/kgw'
        self.epsilon = 1e-12
        if hasattr(config, 'max_conc'):
            self.max_conc = config.max_conc
        else:
            self.max_conc = {}
        self.minerals_dict_1d = {}
        self.parallel = self.config.parallel_phreeqc
        if self.parallel and hasattr(self.config, 'phreeqc_nodes'):
            self.nodes = self.config.phreeqc_nodes
        else:
            self.nodes = range(1, 3)
        if self.parallel:
            print('active phreeqc nodes:', self.nodes)
        else:
            self.nodes = [None]
        self.number_of_threads = len(self.nodes)
        self.node_base_name = '_node'
        self.node_names = []
        self.runners = []
        n = 0
        for node in self.nodes:
            if node is None:
                self.node_names = [None]
            else:
                self.node_names.append(self.node_base_name + str(node))
            self.runners.append(PhreeqcRunner(self.config,
                                              node_name=self.node_names[n]))
            self.runners[n].kinetics = self.kinetics
            n += 1
        self.po4_precip = False
        self.max_successive_errors = 3
        self.current_errors = 1
        self.error = False
        self.config.no_phreeqc_segments = []
        self.unpickleable_attrs = ['w2', 'lake', 'sections','balance_names',
                                   'w2_name_map', 'w2_input',
                                   'all_species_keys',
                                   'fixed_specie_names', 'name_indices']

    @staticmethod
    def split_array(array_length, number_of_threads):
        """Split array in equal size sub arrays for parallel calculations.
        """
        if number_of_threads > array_length:
            min_array_length = 1
            number_of_max_arrays = 0
        else:
            min_array_length, number_of_max_arrays = divmod(array_length,
                                                            number_of_threads)
        bounds = [0] * number_of_threads
        start = 0
        for n, _ in enumerate(bounds):
            if number_of_max_arrays > 0:
                extension = 1
            else:
                extension = 0
            end = start + min_array_length + extension
            bounds[n] = (start, end)
            number_of_max_arrays -= 1
            start = end
        return bounds

    def do_first_run(self):
        """Do first PHREEQC run.
        """
        if self.parallel:
            # Temporally remove unpickleable from config.
            save = []
            for attr in self.unpickleable_attrs:
                save.append(getattr(self.config, attr))
                setattr(self.config, attr, None)

        self.first_run = True
        self.zero_conc = numpy.zeros(self.v_active.shape, float).ravel()
        self._make_discription()
        self._make_1d_array()
        bounds = self.split_array(len(self.ph_1d), self.number_of_threads)
        self.threads = []
        for n, runner in enumerate(self.runners):
            self.threads.append(PhreeqcThread(self.node_names[n]))
            self.threads[n].phreeqc_runner = runner
            self.threads[n].first = True
            self.threads[n].config = self.config
            self.threads[n].constituents_dict = {}
            for const in self.constituents_dict.keys():
                self.threads[n].constituents_dict[const] = \
                    self.constituents_dict_1d[const][bounds[n][0]:bounds[n][1]]
            self.threads[n].temperature = \
                    self.temperature_1d[bounds[n][0]:bounds[n][1]]
            self.threads[n].ph = self.ph_1d[bounds[n][0]:bounds[n][1]]
            self.threads[n].pe = self.pe
            self.threads[n].cell_discription = \
                    self.cell_discription_1d[bounds[n][0]:bounds[n][1]]
            self.threads[n].delta_t = self.delta_t
            self.threads[n].equi_phase_amount_dict = {}
            for amount in self.minerals_dict.keys():
                self.threads[n].equi_phase_amount_dict[amount] = \
                    self.minerals_dict_1d[amount][bounds[n][0]:bounds[n][1]]
            self.threads[n].header_text = self.header_text
            self.threads[n].charge = self.charge
            self.threads[n].redox_couple = self.redox_couple
            self.threads[n].units = self.units
            self.threads[n].start()
        for n, thread in enumerate(self.threads):
            thread.join()
        self.ph_result_1d = copy.copy(self.ph_1d)
        self.ph_result_1d[:] = 0.0
        self.const_result_dict_1d = {}
        for const in self.constituents_dict.keys():
            self.const_result_dict_1d[const] = copy.copy(self.ph_1d)
            self.const_result_dict_1d[const][:] = 0
        for n, thread in enumerate(self.threads):
            if thread.phreeqc_runner.error:
                print('\n error in PHREEQC at %s' % thread.node_name)
                print(thread.phreeqc_runner.error_text)
                import sys
                sys.exit()
            self.phreeqc_string = thread.phreeqc_runner.phreeqc_string
            for const in self.constituents_dict.keys():
                self.const_result_dict_1d[const][bounds[n][0]:bounds[n][1]] = \
                    thread.phreeqc_runner.const_result_dict[const]
            self.ph_result_1d[bounds[n][0]:bounds[n][1]] = \
                thread.phreeqc_runner.ph_result
            self.runners[n] = thread.phreeqc_runner
        self._make_multi_dim_array()
        self.precipated_minerals = {}
        self.find_bottom()
        for phase in self.minerals_dict.keys():
            self.precipated_minerals[phase] = numpy.zeros(self.v_active.shape,
                                                          float)
        if self.settle:
            self.stokes_law()
        if self.parallel:
            # Put unpickleable back into config.
            for attr, saved in zip(self.unpickleable_attrs, save):
                setattr(self.config, attr, saved)

    def do_next_run(self):
        """All other PHREEQC runs.
        """
        if self.parallel:
            # Temporally remove unpickleable from config.
            save = []
            for attr in self.unpickleable_attrs:
                save.append(getattr(self.config, attr))
                setattr(self.config, attr, None)
        self.first_run = 0
        self.threads = []
        self._make_discription()
        self._make_1d_array()
        bounds = self.split_array(len(self.ph_1d), self.number_of_threads)
        if self.minerals_dict:
            if 'po4precip' in self.minerals_dict:
                self.po4_precip = 1
                self.po4_precip_data = self.minerals_dict['po4precip']
                del self.minerals_dict['po4precip']
        for n, runner in enumerate(self.runners):
            runner.header_text = self.header_text
            if self.minerals_dict:
                runner.equi_phases_flag = True
            else:
                runner.equi_phases_flag = False
            runner.saturation_index = self.config.current_saturation_index
            self.threads.append(PhreeqcThread(self.node_names[n]))
            self.threads[n].phreeqc_runner = runner
            self.threads[n].config = self.config
            self.threads[n].first = 0
            self.threads[n].kinetics = self.kinetics
            self.threads[n].constituents_dict = {}
            for const in self.constituents_dict.keys():
                self.threads[n].constituents_dict[const] = \
                    self.constituents_dict_1d[const][bounds[n][0]:bounds[n][1]]
            self.threads[n].temperature = \
                self.temperature_1d[bounds[n][0]:bounds[n][1]]
            self.threads[n].ph = self.ph_1d[bounds[n][0]:bounds[n][1]]
            self.threads[n].pe = self.pe
            self.threads[n].run_number = self.run_number
            self.threads[n].cell_discription = \
                self.cell_discription_1d[bounds[n][0]:bounds[n][1]]
            self.threads[n].delta_t = self.delta_t
            if self.config.calculate_erosion:
                self.threads[n].erosion_active = \
                    self.erosion_active_1d[bounds[n][0]:bounds[n][1]]
                self.threads[n].erosion_cec = self.erosion_cec
                self.threads[n].erosion_porewater = self.erosion_porewater
                self.threads[n].erosion_flag = 1
                self.threads[n].erosion_cec_spezies = self.erosion_cec_spezies
                self.threads[n].erosion_cec_valences = \
                                                     self.erosion_cec_valences
                self.threads[n].porewater_moles = self.porewater_moles
            else:
                self.threads[n].erosion_active = None
                self.threads[n].erosion_cec = None
                self.threads[n].erosion_porewater = None
                self.threads[n].erosion_flag = None
                self.threads[n].erosion_cec_spezies = None
                self.threads[n].erosion_cec_valences = None
                self.threads[n].porewater_moles = None
            self.threads[n].equi_phase_amount_dict = {}
            for amount in self.minerals_dict.keys():
                self.threads[n].equi_phase_amount_dict[amount] = \
                    self.minerals_dict_1d[amount][bounds[n][0]:bounds[n][1]]
            self.threads[n].charge = self.charge
            self.threads[n].start()
        for n, thread in enumerate(self.threads):
            thread.join()
        self.ph_result_1d = copy.copy(self.ph_1d)
        self.const_result_dict_1d = {}
        self.minerals_result_dict_1d = {}
        for const in self.constituents_dict.keys():
            self.const_result_dict_1d[const] = copy.copy(self.ph_1d)
            self.const_result_dict_1d[const][:] = 0.0
        for phase in self.minerals_dict.keys():
            self.minerals_result_dict_1d[phase] = copy.copy(self.ph_1d)
            self.minerals_result_dict_1d[phase][:] = 0.0
        if self.config.calculate_erosion:
            self.exchange_result_1d = {}
            for spezie in self.erosion_cec_spezies:
                self.exchange_result_1d[spezie] = copy.copy(self.ph_1d)
                self.exchange_result_1d[spezie][:] = 0.0
        thread_error = False
        self.error = False
        for n, thread in enumerate(self.threads):
            if thread.phreeqc_runner.error:
                self.error = True
                thread_error = True
                print('\n error in PHREEQC at %s' % thread.node_name)
                print(thread.phreeqc_runner.error_text)
                if self.current_errors > 1:
                    ending = 's'
                else:
                    ending = ''
                print('%d successive error%s' % (self.current_errors, ending))
                print('%d successive errors are allowed'
                       % self.max_successive_errors)
                if self.current_errors > self.max_successive_errors:
                    import sys
                    sys.exit()
                else:
                    for const in self.constituents_dict.keys():
                        self.const_result_dict_1d[const]\
                            [bounds[n][0]:bounds[n][1]] = -9999
                    self.ph_result_1d[bounds[n][0]:bounds[n][1]] = -9999
                    for phase in self.minerals_dict.keys():
                        self.minerals_result_dict_1d[phase]\
                            [bounds[n][0]:bounds[n][1]] = -9999
                    if  self.config.calculate_erosion:
                        for spezie in self.erosion_cec_spezies:
                            if hasattr(thread.phreeqc_runner,
                                       'exchange_spezies_out'):
                                self.exchange_result_1d[spezie]\
                                    [bounds[n][0]:bounds[n][1]] = -9999
            else:
                self.phreeqc_string = thread.phreeqc_runner.phreeqc_string
                for const in self.constituents_dict.keys():
                    self.const_result_dict_1d[const]\
                        [bounds[n][0]:bounds[n][1]] = \
                        thread.phreeqc_runner.const_result_dict[const]
                self.ph_result_1d[bounds[n][0]:bounds[n][1]] = \
                    thread.phreeqc_runner.ph_result
                for phase in self.minerals_dict.keys():
                    self.minerals_result_dict_1d[phase]\
                        [bounds[n][0]:bounds[n][1]] = \
                        thread.phreeqc_runner.equi_phase_result_dict[phase]
                if  self.config.calculate_erosion:
                    for spezie in self.erosion_cec_spezies:
                        if hasattr(thread.phreeqc_runner,
                                   'exchange_spezies_out'):
                            self.exchange_result_1d[spezie]\
                                [bounds[n][0]:bounds[n][1]] = \
                            thread.phreeqc_runner.exchange_spezies_out[spezie]
        if thread_error:
            self.current_errors += 1
        else:
            self.current_errors = 1
        self._make_multi_dim_array()
        if not self.config.settle:
            if self.po4_precip:
                self.minerals_dict['po4precip'] = self.po4_precip_data
                self.minerals_result_dict['po4precip'] = self.po4_precip_data
                self.po4_absorption()
            for phase in self.minerals_dict.keys():
                self.precipated_minerals[phase] += \
                    self.minerals_result_dict[phase] * self.v_active
                self.minerals_result_dict[phase][:] = 0.0
        else:
            self.settle()
            if self.po4_precip:
                self.po4_absorption()
        if self.parallel:
            # Put unpickleable back into config.
            for attr, saved in zip(self.unpickleable_attrs, save):
                setattr(self.config, attr, saved)

    def _make_discription(self):
        """
        Making dicriptive string that preserves names
        of x, y, z coordinates in 1DArray.
        """
        w2_balance_error = self.w2.get_shared_data('balance_error')
        text = ' '
        self.dims = self.v_active.shape
        self.active_cells = numpy.where(self.v_active, 1, 0).astype(int)
        before = numpy.sum(self.active_cells.ravel())
        self.active_cells = numpy.where(numpy.logical_and(
            self.active_cells, numpy.logical_not(w2_balance_error)), 1, 0)
        after_balance = numpy.sum(self.active_cells.ravel())
        if before != after_balance:
            print()
            print('reduced active cells for phreeqc calculation due to'
                  ' balance error from %d to %d' % (before, after_balance))
        for const_name in self.max_conc.keys():
            if const_name in self.constituents_dict:
                self.active_cells = numpy.where(
                    numpy.logical_and(
                        self.active_cells,
                        self.constituents_dict[const_name]
                        < self.max_conc[const_name]),
                    1, 0)
        self.active_cells = self.active_cells.ravel()
        after = numpy.sum(self.active_cells)
        if after_balance != after:
            print()
            print('reduced active cells for phreeqc due to values above'
                  ' max_conc from %d to %d' % (after_balance, after))
        number_of_dims = len(self.dims)
        self.cell_discription = numpy.resize(text, self.dims)
        # tolist is for NumPy arrays.
        # pylint: disable-msg=E1103
        self.cell_discription = self.cell_discription.tolist()
        if number_of_dims >= 1:
            for x in range(self.dims[0]):
                x_discription = str(x)
                if number_of_dims >= 2:
                    for y in range(self.dims[1]):
                        y_discription = x_discription + ', ' + str(y)
                        if number_of_dims >= 3:
                            for z in range(self.dims[2]):
                                z_discription = y_discription + ', ' + str(z)
                                self.cell_discription[x][y][z] = z_discription
                        else:
                            self.cell_discription[x][y] = y_discription
                else:
                    self.cell_discription[x] = x_discription
        self.cell_discription = tools.flatten(self.cell_discription)
        self.cell_discription_1d = []
        for n, cell in enumerate(self.cell_discription):
            if self.active_cells[n]:
                self.cell_discription_1d.append(cell)

    def _make_1d_array(self):
        """
        Change arrays into 1D for Phreeqc input.
        """
        self.indices = numpy.nonzero(self.active_cells)[0]
        indices = self.indices
        self.constituents_dict_1d = {}
        self.ph_1d = numpy.take(self.ph.ravel(), indices)
        self.pe_1d = numpy.take(self.pe.ravel(), indices)
        self.temperature_1d = numpy.take(self.temperature.ravel(), indices)
        # PHREEQC cannot work with negative temperatures.
        # W2 allows small negative values for fluid water.
        self.temperature_1d = numpy.where(self.temperature_1d < 0.01, 0.01,
                                                  self.temperature_1d)
        if self.config.calculate_erosion and not self.first_run:
            self.erosion_active_1d = numpy.take(self.erosion_active.ravel(),
                                                indices)
        self.minerals_dict_1d = {}
        for const in self.constituents_dict.keys():
            self.constituents_dict_1d[const] = numpy.take(
                self.constituents_dict[const].ravel(), indices)
            for n, value in enumerate(self.constituents_dict_1d[const]):
                #set small numbers to zero
                if value < self.epsilon:
                    self.constituents_dict_1d[const][n] = 0.0
        for phase in self.minerals_dict.keys():
            self.minerals_dict_1d[phase] = numpy.take(
                self.minerals_dict[phase].ravel(), indices)

    def _make_multi_dim_array(self):
        """
        Making multidimensional array from 1D array.
        """
        indices = self.indices
        self.ph_result_1d_pad = copy.copy(self.zero_conc)
        numpy.put(self.ph_result_1d_pad, indices, self.ph_result_1d)
        self.ph_result = numpy.reshape(self.ph_result_1d_pad, (self.dims))
        self.const_result_dict_1d_pad = {}
        self.const_result_dict = {}
        for const in self.constituents_dict.keys():
            self.const_result_dict_1d_pad[const] = copy.copy(self.zero_conc)
            numpy.put(self.const_result_dict_1d_pad[const], indices,
                      self.const_result_dict_1d[const])
            self.const_result_dict[const] = numpy.reshape(
                self.const_result_dict_1d_pad[const], (self.dims))
        if self.minerals_dict and not self.first_run:
            self.minerals_result_dict_1d_pad = {}
            self.minerals_result_dict = {}
            for phase in self.minerals_dict.keys():
                self.minerals_result_dict_1d_pad[phase] = \
                    copy.copy(self.zero_conc)
                numpy.put(self.minerals_result_dict_1d_pad[phase], indices,
                          self.minerals_result_dict_1d[phase])
                self.minerals_result_dict[phase] = numpy.reshape(
                    self.minerals_result_dict_1d_pad[phase], (self.dims))
        if not self.first_run and self.config.calculate_erosion:
            self.exchange_result_1d_pad = {}
            self.exchange_result = {}
            for spezie in self.erosion_cec_spezies:
                self.exchange_result_1d_pad[spezie] = copy.copy(self.zero_conc)
                numpy.put(self.exchange_result_1d_pad[spezie], indices,
                          self.exchange_result_1d[spezie])
                self.exchange_result[spezie] = numpy.reshape(
                    self.exchange_result_1d_pad[spezie], (self.dims))

    def _phreeqc_active_species(self):
        """
        Setting active species names and rate names.
        """
        cons = Resources(self.config).phreeqc_species
        mine = Resources(self.config).mineral_names
        self.constituents = []
        self.minerals = []
        for active in self.active_const_names:
            for all_ in cons:
                if active == all_['key']:
                    self.constituents.append(all_)
        for active in self.active_minerals_names:
            for all_ in mine:
                if active == all_['key']:
                    self.minerals.append(all_)
        if self.kinetics:
            for const in self.constituents:
                for rate in self.rates:
                    if const['key'] == rate:
                        const['phreeqc_name'] = const['rate_name']
            for m in self.minerals:
                for mineral_rate in self.mineral_rates:
                    if m['key'] == mineral_rate:
                        m['phreeqc_name'] = m['rate_name']

    def stokes_law(self, rho_w=1000, rho_s =2000, d=4e-6, alpha=1.0, g=9.81,
                   mu=1.4e-3):
        """
        If no settling velocity v_s is specified it
        can be calculated via Stokes' Law.
        Stokes' Law for settling of particles
        (Chapra: Surface Water Modeling. p. 300)
        rho_s    density of particle                 [kg/m^3]
        rho_w    density of water                    [kg/m^3]
        d        effective particle diameter         [m]
        alpha    dimensionless form factor reflecting
                 the effect of particle's shape
                 (sphere = 1.0)
        g        acceleration due to gravity         [m/s^2]
        mu       dynamic viscosity                   [kg/(m*s)]
        v_s      settling velocity                   [m/s]
        """
        # Nice and short formula names.
        # pylint: disable-msg=C0103
        self.v_s = alpha * g / 18 * ((rho_s - rho_w) /mu) * d * d

    def settle(self):
        """
        Moving precipitated minerals down.
        """
        very_large_depth = 9999999
        if self.po4_precip:
            self.minerals_dict['po4precip'] = self.po4_precip_data
            self.minerals_result_dict['po4precip'] = self.po4_precip_data
        for phase in self.minerals_result_dict.keys():
            #preventing division by zero
            self.h_active = numpy.where(self.h_active, self.h_active,
                                        very_large_depth)
            diff = numpy.where(self.h_active, self.v_s / self.h_active *
                               self.minerals_result_dict[phase] * self.delta_t,
                               0.0)
            diff = numpy.where(self.h_active, diff, 0.0)
            diff = numpy.minimum(diff, self.minerals_result_dict[phase])
            self.minerals_result_dict[phase] = \
                self.minerals_result_dict[phase] - diff
            self.minerals_result_dict[phase][:, 1:] = \
                self.minerals_result_dict[phase][:, 1:] + diff[:, :-1]
            for n, bottom_index in enumerate(self.bottom[1:-1], 1):
                self.precipated_minerals[phase][n, bottom_index] += \
                    diff[n, bottom_index] * self.v_active[n, bottom_index]

    def po4_absorption(self):
        """Calculate the absorption of PO_4 with Fe.
        """
        ratio = self.config.fe_po4_ratio #10.0 #1 PO4 to ratio Fe
        lower_limit = 1.0e-4 #mmol/l
        if 'Fe(OH)3(a)' in self.minerals_result_dict:
            key = 'Fe(OH)3(a)'
        elif 'Fe(OH)3(a)r' in self.minerals_result_dict:
            key = 'Fe(OH)3(a)r'
        else:
            msg = 'Fe(OH)3 is not modelled. Can not compute adsorption of PO4!'
            raise Exception(msg)
        precip = numpy.minimum(
            numpy.maximum(0.0, self.minerals_result_dict[key] / ratio),
            numpy.maximum(0.0, (self.const_result_dict['P'] - lower_limit)))
        self.minerals_result_dict['po4precip'] = \
                                self.minerals_result_dict['po4precip'] + precip
        self.const_result_dict['P'] = self.const_result_dict['P'] - precip

    def find_bottom(self):
        """Find the bottom index.
        """
        self.bottom = numpy.zeros((self.v_active.shape[0],), dtype=int)
        m = 0
        for segment in self.v_active:
            n = 1
            # layer is a nice name
            # pylint: disable-msg=W0612
            for layer in segment[1:]:
                if self.v_active[m, n] < 1e-6:
                    self.bottom[m] = n -1
                    if n > 2:
                        break
                n += 1
            m += 1

    @staticmethod
    def average_dicts(dict1, dict2):
        """Average the values of two dicts assumimg both have the same keys.
        """
        result = {}
        for key in dict1.keys():
            try:
                result[key] = (dict1[key] + dict2[key])/2.0
            except KeyError:
                result[key] = dict1[key]
        return result
