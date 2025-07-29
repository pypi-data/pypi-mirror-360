"""Check if the measured kb matches the concentrations.

This is important for water that are in equlibrium with atmopshere.
We titra aginats a pH like 5.6 and see how much
"""

from __future__ import print_function

import os
import time
from pitlakq.postprocessing import kb_balance
from pitlakq.metamodel.configuration.getconfig import read_dot_pitlakq
from pitlakq.numericalmodels.existingmodels.phreeqc.tempenv import make_temp_env

class DummyConfig(object):
    # Only one emthod is ok.
    # pylint: disable-msg=R0903
    """Faking config.
    """
    def __init__(self, project_name):
        dot_pitlakq = list(read_dot_pitlakq())[0]
        ram_path = dot_pitlakq['ram_path']
        resource_path = dot_pitlakq['resources_path']
        temp_path = make_temp_env(project_name, 'check_kb')
        self.ram_path = ram_path
        self.c_as_c = True
        self.phreeqc_input = os.path.join(temp_path, 'phreeqc.inp')
        self.phreeqc_output = os.path.join(temp_path, 'phreeqc.out')
        self.phreeqc_database = os.path.join(temp_path, 'phreeqcw2.dat')
        self.phreeqc_original_database = os.path.join(resource_path,
                                                        'phreeqc_w2.dat')
        self.phreeqc_exe = os.path.join(temp_path, 'phreeqc2win.exe')
        self.phreeqc_exe_original = os.path.join(resource_path,
                                                   'phreeqc2win.exe')
        self.silent = False


def main(project_name, file_name, kb):
    """Check for kb.
    """
    # Name `kb` is fine.
    # pylint: disable-msg=C0103
    start = time.time()
    const, ks43, dates = kb_balance.read_river_input(file_name)
    config = DummyConfig(project_name)
    balance = kb_balance.KbBalance(config, kb, const)
    calc_kbs = balance.calculate()
    diff = [kb_calc - ks_measure for kb_calc, ks_measure in
            zip(calc_kbs, ks43)]
    print('%20s %5s %5s %5s' % ('date', 'calc', 'meas', 'ratio'))
    for date, calc, measure in zip(dates, calc_kbs, ks43):
        print('%20s %5.2f %5.2f %5.2f' % (date, calc, measure, calc / measure))
    print('min', min(diff))
    print('max', max(diff))
    print('average', sum(diff) / len(diff))
    print('abs average', sum(abs(value) for value in diff) / len(diff))
    print('run time', time.time() - start)

if __name__ == '__main__':
    main('pitlakq_test',
         r'c:\Daten\Mike\tmp\ptest\models\pitlakq_test\preprocessing\charge'
         r'\Collie_River.txt', 4.3)
