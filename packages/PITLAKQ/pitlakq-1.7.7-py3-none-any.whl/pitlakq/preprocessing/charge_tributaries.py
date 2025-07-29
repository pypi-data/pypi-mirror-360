"""Charge inflow concentrations of tributaries.
"""

from __future__ import print_function

import csv
import datetime
import os
import shutil
import subprocess

from pitlakq.metamodel.configuration.getconfig import read_dot_pitlakq
from pitlakq.numericalmodels.existingmodels.phreeqc.tempenv import \
     make_temp_env, TempDir


class  TributaryCharger(object):
    # pylint: disable-msg=R0902
    # More than 12 instance attributes.
    """Charge balance for tributary inflows.
    """
    def __init__(self, source_file_name, target_dir, charging_species,
                 last_date):
        self.source_file_name = source_file_name
        self.target_dir = target_dir
        self.charging_species = charging_species
        self.last_date = last_date
        self.phreeqc_input_path = 'charge.phc'
        self.selected_output_path = 'charge_out.txt'
        self.phreeqc_exe_path = 'phreeqc2win.exe'
        self.phreeqc_out_path = 'charge_result.out'
        self.phreeqc_database_path = 'phreeqc_w2.dat'
        self.error_file = 'charge_error.txt'
        molar_weights = {'Cl': 35.453, 'Sulfat': 96.064}
        self.molar_weight_cs = molar_weights[charging_species]
        self.c_as_c = True

    def read_input(self):
        """Read input data.
        """
        # pylint: disable-msg=W0201
        # Setting member attributes.
        reader = csv.reader(open(self.source_file_name, newline=''),
                            delimiter=';')  # TODO make
        header_one = next(reader)
        header_two = next(reader)
        conc_start_pos = 3
        self.cequal_names = header_one[conc_start_pos:]
        self.phreeqc_names = header_two[conc_start_pos:]
        locations = {}
        conc = []
        index = 0
        for line in reader:
            if not line:
                continue
            location, date, time_ = line[0], line[1], line[2]
            date = datetime.datetime.strptime(date + time_, '%d.%m.%Y%H:%M:%S')
            locations.setdefault(location, []).append((date, index))
            try:
                conc.append([float(entry) for entry in line[conc_start_pos:]])
            except ValueError:
                print(line)
                raise
            index += 1
        self.locations = locations
        self.conc = conc

    def write_phreeqc_input(self):
        """Write PHREEQC input file.
        """
        fobj = open(self.phreeqc_input_path, 'w')
        fobj.write('Title charge balancing of tributary\n')
        fobj.write('\nSELECTED_OUTPUT\n-high_precision\n')
        fobj.write('-file %s\n-totals %s\n-percent_error true\n\n' %
                   (self.selected_output_path, self.charging_species))
        c_pos = self.phreeqc_names.index('C')
        factor_pos = self.phreeqc_names.index('factor')
        for counter, entry in enumerate(self.conc):
            fobj.write('Solution %03d\n' % counter)
            fobj.write('units              mg/l\ntemp           20\n')
            for name, conc in zip(self.phreeqc_names, entry):
                if name in ('TP', 'C', 'factor', 'skip'):
                    continue
                post_fix = ''
                if name == self.charging_species:
                    post_fix = 'charge'
                if name == 'ks43' and self.c_as_c:
                    name = 'C'
                    post_fix = 'as C'
                    factor = entry[factor_pos]
                    conc = (conc * 12.0111) * factor
                    entry[c_pos] = conc
                fobj.write('%20s %20.5f %s\n' % (name, conc, post_fix))
            fobj.write('END\n')
        for counter, entry in enumerate(self.conc):
            fobj.write('REACTION %03d\n' % counter)
            fobj.write('H2O 1.0\n0.0 moles\nEND\n')
        for counter, entry in enumerate(self.conc):
            fobj.write('USE SOLUTION %03d\nEND\n' % counter)
        fobj.close()

    def run_phreeqc(self):
        """Run PHREEQC
        """
        cmd = '%s %s %s %s' % (self.phreeqc_exe_path, self.phreeqc_input_path,
                               self.phreeqc_out_path,
                               self.phreeqc_database_path)
        print(cmd)
        subprocess.call(cmd)

    def read_selected_output(self):
        """Read data from selected output file.
        """
        charging = []
        error = []
        fobj = open(self.selected_output_path)
        header = next(fobj).split()
        charging_pos = header.index(self.charging_species)
        error_pos = header.index('pct_err')
        for line in fobj:
            data = line.split()
            charging.append(float(data[charging_pos]))
            error.append(float(data[error_pos]))
        return charging, error

    def write_output(self, charging, error):
        """Write result to W2 input file for tributary concentration.
        """
        error_file = open(self.error_file, 'w')
        error_file.write('%5s %25s %25s %25s %25s\n' % (
            'soln', 'old_value', 'new_value', 'percent_added',
            'percent_error'))
        for name, data in self.locations.items():
            fobj = open(os.path.join(self.target_dir, '%s.txt' % name), 'w')
            fobj.write('%10s %10s' % ('date', 'time'))
            for name in self.cequal_names:
                fobj.write(' %25s' % name)
            fobj.write('\n')
            charging_index = self.phreeqc_names.index(self.charging_species)
            for date, sol_counter in sorted(data):
                line = ''
                fobj.write(date.strftime('%d.%m.%Y  %H:%M:%S'))
                for index, value in enumerate(self.conc[sol_counter]):
                    if index == charging_index:
                        new_charging = charging[sol_counter] * \
                                       self.molar_weight_cs * 1000
                        if value == 0.0:
                            percent_added = 100
                        else:
                            percent_added = ((new_charging - value) /
                                             value * 100)
                        error_file.write('%5d %25.5f %25.5f %25.5f %25.5g\n'
                                         % (sol_counter, value, new_charging,
                                            percent_added, error[sol_counter]))
                        value = new_charging
                    line += ' %25.5g' % value
                fobj.write(line + '\n')
            fobj.write(self.last_date.strftime('%d.%m.%Y  %H:%M:%S'))
            fobj.write(line + '\n')
            fobj.close()
        error_file.close()


def main(project_name, in_file_name, out_dir, charging_species,
         last_date):
    """Charge balance tributary concentrations.

    Can be charged with Cl or Sulfate
    """
    temp_path = make_temp_env(project_name, 'charge')
    with TempDir(temp_path):
        charger = TributaryCharger(in_file_name, out_dir,
                                   charging_species, last_date)
        charger.read_input()
        charger.write_phreeqc_input()
        charger.run_phreeqc()
        charging, error = charger.read_selected_output()
        charger.write_output(charging, error)
        print()


if __name__ == '__main__':
    def test():
        """A small test.
        """
        base = (r'c:\Daten\Mike\tmp\ptest\models\pitlakq_test\preprocessing'
                r'\charge')
        in_file_name = os.path.join(base, 'sample_concentration.csv')
        project_name = 'pitlakq_test'
        main(project_name, in_file_name, base, 'Cl',
             datetime.datetime(2012, 1, 5))
    test()
