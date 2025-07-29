"""
Input output for Phreeqc from/to arrays.
"""

# NumPy, dynamic members.
# pylint: disable-msg=E1101

from __future__ import print_function

import numpy

from pitlakq.commontools.tools import keep_old_files


class PhreeqcIO(object):
    """
    Writing array based Phreeqc input.
    """
    # Lots of attributes defined outside __init__.
    # pylint: disable-msg=W0201
    # ph and pe are good names
    # pylint: disable-msg=C0103
    def __init__(self,
                 config,
                 constituents_dict,
                 punch_file,
                 temperature,
                 ph,
                 pe,
                 cell_discription,
                 delta_t,
                 equi_phase_amount_dict,
                 header_text = 'Header Text comes here',
                 charge = 'pH',
                 redox_couple = 'O(0)/O',
                 units = 'mmol/kgw'):
        self.config = config
        self.input = []     #list of input lines
        self.header = []
        self.solution = []
        self.equi_phases = []
        self.kinetics = []
        self.punch_file = []
        self.use = []
        self.constituents_dict = constituents_dict
        self.equi_phase_amount_dict = equi_phase_amount_dict
        self.cell_discription = cell_discription
        self.delta_t = delta_t
        self.units = units
        self.charge = charge
        self.punch_file_name = punch_file
        self.temperature = temperature
        self.ph = ph
        self.pe = pe
        self.redox_couple = redox_couple
        self.header_text = header_text
        self.array_shape = (
            self.constituents_dict[
                list(self.constituents_dict.keys())[0]].shape)
        self.number_of_cells = len(self.cell_discription)
        self.number_of_cells_range = range(self.number_of_cells)
        self.equi_phases_flag = False
        self.kinetics_flag = False
        self.reaction_flag = True
        self.erosion_flag = False
        self.steps = 1
        self._read_kinetics()
        self._read_rates()
        self.update(self.constituents_dict,
                 self.temperature,
                 self.ph,
                 self.pe,
                 0,
                 self.cell_discription,
                 self.delta_t,
                 self.kinetics_flag,
                 self.equi_phase_amount_dict,
                 self.charge)
        self.fixed_sat_index = 0.01
        self.saturation_index = {'Fe(OH)3(a)r': 0.2, 'Al(OH)3(a)': 0.2}

    def _read_kinetics(self):
        """Read the kinetics data.
        """
        fobj = open(self.config.kinetics_file_name)
        data = fobj.readlines()
        fobj.close()
        self.kinetics_text_list = [text.strip() for text in data]

    def _read_rates(self):
        """Read rates data.
        """
        fobj = open(self.config.rates_file_name, encoding='utf-8')
        data = fobj.readlines()
        fobj.close()
        self.conditional_rates = {}
        first = True
        condition = None
        current_rates_text = None
        for line in data:
            if line.split(':')[0].strip() == 'condition':
                if not first:
                    self.conditional_rates[condition] = \
                        ''.join(current_rates_text)
                current_rates_text = []
                condition = line.split(':')[1].strip()
                first = False
            else:
                current_rates_text.append(line.strip())
        self.conditional_rates[condition] = '\n'.join(current_rates_text)

    def update(self,
               constituents_dict,
               temperature,
               ph,
               pe,
               run_number,
               cell_discription,
               delta_t,
               kinetics_flag,
               equi_phase_amount_dict,
               charge = 'pH'):
        """Update the information.
        """
        # ph and pe are good names
        # pylint: disable=C0103
        self.number_of_cells = len(ph)
        self.number_of_cells_range = range(self.number_of_cells)
        self.constituents_dict = constituents_dict
        self.equi_phase_amount_dict = equi_phase_amount_dict
        self.cell_discription = cell_discription
        self.delta_t = delta_t
        self.charge = charge
        self.temperature = temperature
        self.ph = ph
        self.pe = pe
        self.kinetics_flag = kinetics_flag
        self.set_header(self.header_text, run_number)
        self.set_solutions()
        self.set_rates()
        if self.equi_phases_flag:
            self.set_equi_phases()
        else:
            self.equi_phases = []
        if self.kinetics_flag:
            self.set_kinetics()
        else:
            self.kinetics = []
        if self.reaction_flag:
            self.set_reaction()
        else:
            self.reaction = []
        if self.erosion_flag:
            self.set_exchange()
        else:
            self.exchange = []
        self._set_punch_file()
        self.set_use()

    def _make_punch_names(self):
        """Create the names for the punch file.
        """
        self.const_punch_names = ''
        self.const_punch_name_dict = {}
        for key in self.constituents_dict.keys():
            short_key = key.replace('+', '')
            short_key = short_key.replace('-', '')
            if short_key == 'N(5)':
                short_key = 'N'
            self.const_punch_names = self.const_punch_names + ' ' + short_key
            self.const_punch_name_dict[key] = short_key

    def set_header(self, header_text, run_number):
        """
        Wrting Header to Phreeqc input list:
        """
        self.header = []
        self.header.append('TITLE ' + header_text + '\tRun # %d' % run_number)
        self.header.append('PRINT\n-reset false')
        self.header.append('KNOBS')
        #self.header.append('KNOBS\n-convergence_tolerance\t1e-8')
        self.header.append('-iterations 300')
        self.header.append('-c 1e-12')
        self.header.append('-t 1e-15')
        #self.header.append('KNOBS\n-l True')
        self.header.append('-s 10')

    def set_solutions(self):
        """
        Writing initial solutions to input list.
        """
        self.solution = []
        for cell in self.number_of_cells_range:
            self.solution.append("SOLUTION %d at %s"
                                 % (cell+1, self.cell_discription[cell]))
            self.solution.append("-units %s" % self.units)
            ph_string = "pH " + str(self.ph[cell]) + "\t"
            if self.charge == 'pH':
                ph_string = ph_string + "charge"
            self.solution.append(ph_string)
            self.solution.append('temp %f' %self.temperature[cell])
            for const in self.constituents_dict.keys():
                if const =='C' and self.config.c_as_c:
                    postfix = ' as C'
                else:
                    postfix = ''
                if const == self.charge:
                    const_string = (const + ' ' +
                        str(self.constituents_dict[const][cell]) + '\t charge')
                else:
                    const_string = (const + ' ' +
                        str(self.constituents_dict[const][cell])+ postfix)
                self.solution.append(const_string)
            self.solution.append(' ')
            self.solution.append('END\n')

    def set_equi_phases(self):
        """
        Writing input for equilibrium phases.
        """
        self.equi_phases = []
        for cell in self.number_of_cells_range:
            self.equi_phases.append("EQUILIBRIUM_PHASES %d at %s"
                                    % (cell+1, self.cell_discription[cell]))
            for phase in self.equi_phase_amount_dict.keys():
                if self.config.settle:
                    # Using mmol here because singles in CE-QUAL-W2 are too
                    # small.
                    old_conc = self.equi_phase_amount_dict[phase][cell] / 1e3
                else:
                    old_conc = 0.0

                # Fixed saturation indices to `self.fixed_sat_index`.
                # Could make it specie-specifc with
                # `self.saturation_index[phase]`
                self.equi_phases.append('%s %10.2f %20.15f' %
                                        (phase, self.fixed_sat_index,
                                         old_conc))

            self.equi_phases.append('END\n')

    def set_rates(self):
        """
        Writing rates in input file if certain conditions are fullfilled
        """
        self.rates = []
        if hasattr(self.config, 'current_conditions'):
            if self.config.current_conditions:
                self.rates.append("RATES")
                for condition in self.config.current_conditions:
                    self.rates.append(self.conditional_rates[condition])
                    self.rates.append('\n')

    def set_kinetics(self):
        """
        Writing input for kinetics.
        """
        self.kinetics = []
        for cell in self.number_of_cells_range:
            self.kinetics.append("KINETICS %d at %s"
                                 % (cell + 1, self.cell_discription[cell]))
            self.kinetics += self.kinetics_text_list
            if hasattr(self.config, 'current_phreeqc_steps'):
                self.steps = self.config.current_phreeqc_steps
            self.kinetics.append("-steps %f in %d steps" % (self.delta_t,
                                                            self.steps))
            self.kinetics.append('END\n')

    def set_reaction(self):
        """
        Writing input for reaction.
        """
        self.reaction = []
        erosion_porewater_string = ''
        positive_equivalents = 0
        if self.erosion_flag:
            for spezie in self.erosion_porewater.keys():
                if spezie == 'Fe(+2)':
                    erosion_porewater_string += '%s %16.14f\n' % ('Fe',
                                            (self.erosion_porewater[spezie]))
                else:
                    erosion_porewater_string += '%s %16.14f\n' % (spezie,
                                            (self.erosion_porewater[spezie]))
                positive_equivalents += (self.erosion_cec_valences[spezie] *
                                         self.erosion_porewater[spezie])
            erosion_porewater_string += \
                    'Sulfat %16.14f' % (positive_equivalents / 2)
        for n, cell in enumerate(self.number_of_cells_range):
            self.reaction.append("REACTION %d at %s"
                                 % (cell + 1, self.cell_discription[cell]))
            if (self.erosion_flag and self.erosion_active[n] and
                (positive_equivalents > 1e-12)):
                self.reaction.append(erosion_porewater_string)
                self.reaction.append(str(self.porewater_moles) + ' moles')
            else:
                self.reaction.append("H2O 1.0")
                self.reaction.append("0.0 moles")
            self.reaction.append("END\n")

    def set_exchange(self):
        """
        Writing input for exchange.
        """
        self.exchange = []
        erosion_cec_list = []
        for spezie in self.erosion_cec_spezies:
            if spezie == 'Fe(+2)':
                erosion_cec_list.append('%sX%d\t%16.14e'
                    % ('Fe', self.erosion_cec_valences[spezie],
                       self.erosion_cec[spezie]))
            else:
                erosion_cec_list.append('%sX%d\t%16.14e'
                    % (spezie, self.erosion_cec_valences[spezie],
                       self.erosion_cec[spezie]))
        for n, cell in enumerate(self.number_of_cells_range):
            if self.erosion_active[n]:
                self.exchange.append("EXCHANGE %d at %s"
                                     % (cell+1, self.cell_discription[cell]))
                self.exchange.extend(erosion_cec_list)
                self.exchange.append("END\n")

    def _set_punch_file(self):
        """
        Appending Information for SELECTED OUTPUT.
        """
        self.punch_file = []
        self.punch_file.append("SELECTED_OUTPUT")
        self.punch_file.append("-file " + self.punch_file_name)
        self.punch_file.append("-high_precision")
        self._make_punch_names()
        self.punch_file.append("-totals " + self.const_punch_names)
        if self.equi_phases_flag:
            equi_phase_names = ''
            for phase in self.equi_phase_amount_dict.keys():
                equi_phase_names = equi_phase_names + ' ' + phase
            self.punch_file.append('-equilibrium_phases' + equi_phase_names)
        if self.erosion_flag:
            exchange_names = ''
            for spezie in self.erosion_cec_spezies:
                if spezie == 'Fe(+2)':
                    exchange_names = (exchange_names + ' ' + 'Fe' + 'X%d'
                                      % self.erosion_cec_valences[spezie])
                else:
                    exchange_names = (exchange_names + ' ' + spezie + 'X%d'
                                      % self.erosion_cec_valences[spezie])
            self.punch_file.append('-molalities' + exchange_names)

    def set_use(self):
        """
        Appending USE SOLUTION
        USE EQUILIBRIUM_PHASES etc.
        """
        self.use = []
        n = 0
        for cell in self.number_of_cells_range:
            self.use.append('USE SOLUTION %d' %(cell+1))
            if self.kinetics_flag:
                self.use.append('USE KINETICS %d' %(cell+1))
            if self.equi_phases_flag:
                self.use.append('USE EQUILIBRIUM_PHASES %d' %(cell+1))
            if self.erosion_flag:
                if self.erosion_active[n]:
                    self.use.append('USE EXCHANGE %d' %(cell+1))
            if self.reaction_flag:
                self.use.append('USE REACTION %d' %(cell+1))
            self.use.append('END\n')
            n += 1

    def make_input_string(self):
        """
        Making string from list of strings.
        """
        self.input = []
        for part in (self.header,
                     self.solution,
                     self.equi_phases,
                     self.exchange,
                     self.rates,
                     self.kinetics,
                     self.reaction,
                     self.punch_file,
                     self.use):
            self.input.extend(part)
        return '\n'.join(self.input)

    def _get_output_positions(self):
        """
        Reading putput file.
        Finding position of constitiuents, equilibrium phases etc.
        """
        keep_old_files(self.punch_file_name, 10)
        output = open(self.punch_file_name, 'r')
        self.output_header = output.readline()
        self.output_header = self.output_header.replace('"', ' ')
        self.output_header = self.output_header.split()
        self.const_position = {}
        self.equi_phase_position = {}
        for const in self.const_punch_name_dict.keys():
            for item in self.output_header:
                if item == self.const_punch_name_dict[const]:
                    self.const_position[const] = \
                        self.output_header.index(item)
        if self.equi_phases_flag:
            for phase in self.equi_phase_amount_dict.keys():
                for item in self.output_header:
                    if item == phase:
                        self.equi_phase_position[phase] = \
                            self.output_header.index(item)
        if self.erosion_flag:
            self.exchange_spezie_position = {}
            for spezie in self.erosion_cec_spezies:
                for item in self.output_header:
                    if spezie == 'Fe(+2)':
                        if (item == 'm_' + 'Fe' +'X%d'
                            % self.erosion_cec_valences['Fe(+2)']):
                            self.exchange_spezie_position[spezie] = \
                                self.output_header.index(item)
                    else:
                        if (item == 'm_' + spezie +'X%d'
                            % self.erosion_cec_valences[spezie]):
                            self.exchange_spezie_position[spezie] = \
                                self.output_header.index(item)
        self.ph_position = self.output_header.index('pH')
        self.pe_position = self.output_header.index('pe')
        output.close()

    def _read_output(self):
        """
        Reading output from PHREEQC punch file.
        """
        self.const_result_dict = {}
        if self.erosion_flag:
            self.exchange_spezies_out = {}
            for spezie in self.erosion_cec_spezies:
                self.exchange_spezies_out[spezie] = \
                    numpy.zeros((self.number_of_cells), float)
        for key in self.constituents_dict.keys():
            self.const_result_dict[key] = numpy.zeros((self.number_of_cells),
                                                      float)
        if self.equi_phases_flag:
            self.equi_phase_result_dict = {}
            for key in self.equi_phase_amount_dict.keys():
                self.equi_phase_result_dict[key] = \
                    numpy.zeros((self.number_of_cells), float)
        self.ph_result = numpy.zeros((self.number_of_cells), float)
        self.pe_result = numpy.zeros((self.number_of_cells), float)
        output = open(self.punch_file_name, 'r')
        lines = output.readlines()
        n = 0
        m = 0
        try:
            for cell in self.number_of_cells_range:
                if self.kinetics_flag:
                    n += self.steps # use only last output per time step
                else:
                    n += 1
                line = lines[n].split()
                for const in self.constituents_dict.keys():
                    self.const_result_dict[const][cell] = \
                    float(line[self.const_position[const]])*1000 #mol -> mmol
                self.ph_result[cell] = float(line[self.ph_position])
                self.pe_result[cell] = float(line[self.pe_position])
                if self.equi_phases_flag:
                    for phase in self.equi_phase_amount_dict.keys():
                        try:
                            # in mol-->mmol
                            self.equi_phase_result_dict[phase][cell] = \
                            float(line[self.equi_phase_position[phase]]) * 1e3
                        except ValueError:
                            print('no mineral')
                            self.equi_phase_result_dict[phase][cell] = 0.0
                if self.erosion_flag:
                    if self.erosion_active[m]:
                        for spezie in self.exchange_spezies_out.keys():
                            #mol!!!
                            self.exchange_spezies_out[spezie][cell] = \
                                float(
                                line[self.exchange_spezie_position[spezie]])
                m += 1
        except IndexError:
            print('IndexError occured continue with old values')
        output.close()

    def get_output(self):
        """Retrun the read output.
        """
        self._get_output_positions()
        self._read_output()
