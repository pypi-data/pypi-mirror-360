"""Calculation of kB values.
"""

import os

from . import phreeqc_runner


class KbCalculator(object):
    """Calculate kB values
    """
    # TODO: Make precipitants an input parameter.
    def __init__(self, config, kb, constituents, units='mmol/kgw',
                 open_to_atm=False,
                 precipitans=('Fe(OH)3(a)',
                              #'Schwertmanite'
                              'Al(OH)3(a)')):
        # kb is good name
        # pylint: disable-msg=C0103
        self.config = config
        self.kb = kb
        #list of dicts with PHREEQC name and value for specie
        self.constituents = constituents
        self.units = units
        self.open_to_atm = open_to_atm
        self.precipitans = precipitans
        self.input_file_name = os.path.join(self.config.ram_path,
                                            'kbinput.phc')
        self.output_file_name = os.path.join(self.config.ram_path,
                                            'kboutout.out')
        self.selected_output_file_name = os.path.join(self.config.ram_path,
                                                      'kbslectedoutput.out')
        self.screen_file_name = os.path.join(self.config.ram_path,
                                            'kbscreen.out')

    def calculate(self):
        """Calculate values.
        """
        phreeqc_exe = phreeqc_runner.PhreeqcExe(self.config,
                                                self.input_file_name,
                                                self.output_file_name,
                                                self.screen_file_name)
        phreeqc_exe.run(self._make_phreeqc_input())
        if not phreeqc_exe.error:
            return self.read_phreeqc_output()
        else:
            raise ValueError(phreeqc_exe.error_text)

    def _make_phreeqc_input(self):
        """Make string for input file.
        """
        phreeqc_input = []
        phreeqc_input.append('Title kb%3.1f calculation with Python\n'
                             % self.kb)
        phreeqc_input.append('PHASES\n'
                             'Fix_H+\n'
                             'H+ = H+\n'
                             'log_k 0.0\n'
                             'END\n')
        no_calculation = []  # list with indices without calculations
        calculation = []
        for index, const in enumerate(self.constituents):
            if const['pH'] < self.kb:
                titrans = 'NaOH'
            elif const['pH'] > self.kb:
                titrans = 'HCl'
            else:
                no_calculation.append(index)
                continue
            index += 1
            calculation.append((index, titrans))
            phreeqc_input.append('\nSOLUTION %d' % index)
            phreeqc_input.append('units %s' % self.units)
            for name, value in const.items():
                template = '%s\t%16.10f'
                if self.config.c_as_c and name == 'C':
                    template += ' as C'
                elif name == 'pH' and (value == 0.0 or value == 14.0):
                    template += ' charge'
                phreeqc_input.append(template % (name, value))
            phreeqc_input.append('END\n')
        for index, titrans in calculation:
            phreeqc_input.append('EQUILIBRIUM_PHASES %d' % index)
            for precipitant in self.precipitans:
                phreeqc_input.append('%s 0.0 0.0' % precipitant)
            phreeqc_input.append('Fix_H+ -%3.1f %s 10.0' % (self.kb, titrans))
            if self.open_to_atm:
                phreeqc_input.append('O2(g) -0.69897\n'
                                     'CO2(g) -3.5\n'
                                     'END\n')
        for index, _ in calculation:
            phreeqc_input.append('REACTION %d' % index)
            phreeqc_input.append('H2O 1.0\n'
                                 '0.0 moles\n'
                                 'END\n')
        phreeqc_input.append('SELECTED_OUTPUT')
        phreeqc_input.append('-file %s' % self.selected_output_file_name)
        phreeqc_input.append('-high_precision')
        phreeqc_input.append('-equilibrium_phases Fix_H+\n\n')
        for index, _ in calculation:
            phreeqc_input.append('USE SOLUTION %(index)d\n'
                                 'USE EQUILIBRIUM_PHASES %(index)d\n'
                                 'USE REACTION %(index)d\n'
                                 'END\n' % {'index': index})
        return '\n'.join(phreeqc_input)

    def read_phreeqc_output(self):
        """Read from selected output.
        """
        fobj = open(self.selected_output_file_name)
        data = [x.split() for x in fobj.readlines()]
        amount = []
        for line in data[1:]:
            amount.append(-float(line[9]) * 1000.0)
        return amount
