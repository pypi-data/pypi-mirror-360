"""
Running Phreeqc using PhreeqcIO.
"""

# Attributes are set from outside.
# pylint: disable-msg=E1101
# Attributes defined outside __init__.
# pylint: disable-msg=W0201

from __future__ import print_function

import filecmp
import os
import shutil
import subprocess
import sys


from pitlakq.commontools.tools import keep_old_files
import pitlakq.numericalmodels.existingmodels.phreeqc.phreeqc_io as phreeqcIO


class PhreeqcRunner(object):
    """Run a Phreeqc calculation.
    """

    def __init__(self,
                 config,
                 node_name=None):
        self.config = config
        self.node_name = node_name
        self.ram_path = None
        if node_name is not None:
            self.ram_path = os.path.join(config.ram_path, node_name)
            if not os.path.exists(self.ram_path):
                os.mkdir(self.ram_path)
        def make_new_path(name):
            if node_name is None:
                return None
            else:
                return change_base_path(self.ram_path, getattr(config, name))
        self.exe = PhreeqcExe(self.config,
                              phreeqc_input=make_new_path('phreeqc_input'),
                              phreeqc_output=make_new_path('phreeqc_output'),
                              phreeqc_screen=make_new_path('phreeqc_screen'),
                              node_name=node_name,
                              ram_path=self.ram_path)
        self.error = False
        self.erosion_flag = False
        if self.node_name:
            self.punch_file = change_base_path(self.ram_path,
                                               self.config.punch_file)
        else:
            self.punch_file = self.config.punch_file


    def do_first_run(self,
                     config,
                     constituents_dict,
                     temperature,
                     ph,
                     pe,
                     cell_discription,
                     delta_t,
                     equi_phase_amount_dict,
                     header_text,
                     charge,
                     redox_couple,
                     units):
        """
        First run for charge balance
        with most aboundend species
        i.e. Cl.
        Set charge to this species.
        """
        # ph and pe are good names
        # pylint: disable-msg=C0103
        self.p_io = phreeqcIO.PhreeqcIO(config,
                                        constituents_dict,
                                        self.punch_file,
                                        temperature,
                                        ph,
                                        pe,
                                        cell_discription,
                                        delta_t,
                                        equi_phase_amount_dict,
                                        header_text,
                                        charge,
                                        redox_couple,
                                        units)
        self.phreeqc_string = self.p_io.make_input_string()
        self.exe.run(self.phreeqc_string)
        self.error = self.exe.error
        self.error_text = self.exe.error_text
        self.p_io.get_output()
        self.const_result_dict = self.p_io.const_result_dict
        self.ph_result = self.p_io.ph_result

    def do_next_run(self,
                    config,
                    constituents_dict,
                    temperature,
                    ph,
                    pe,
                    run_number,
                    cell_discription,
                    delta_t,
                    kinetics,
                    equi_phase_amount_dict,
                    charge,
                    erosion_active,
                    erosion_cec,
                    erosion_porewater,
                    erosion_flag,
                    erosion_cec_spezies,
                    erosion_cec_valences,
                    porewater_moles):
        """Run for time step except first that charge balances.
        """
        # ph and pe are good names
        # pylint: disable-msg=C0103
        self.config = config
        self.p_io.config = self.config
        self.p_io.header_text = self.header_text
        self.p_io.kinetics_flag = self.kinetics
        self.p_io.reaction_flag = True
        self.p_io.equi_phases_flag = self.equi_phases_flag
        self.p_io.saturation_index = self.saturation_index
        if erosion_flag and self.config.calculate_erosion:
            self.p_io.erosion_flag = True
            self.p_io.erosion_active = erosion_active
            self.p_io.erosion_cec = erosion_cec
            self.p_io.erosion_porewater = erosion_porewater
            self.p_io.erosion_cec_spezies = erosion_cec_spezies
            self.p_io.erosion_cec_valences = erosion_cec_valences
            self.p_io.porewater_moles = porewater_moles
        self.p_io.update(constituents_dict,
                         temperature,
                         ph,
                         pe,
                         run_number,
                         cell_discription,
                         delta_t,
                         self.kinetics,
                         equi_phase_amount_dict,
                         charge)
        self.phreeqc_string = self.p_io.make_input_string()
        self.exe.run(self.phreeqc_string)
        self.error = self.exe.error
        self.error_text = self.exe.error_text
        self.p_io.get_output()
        self.const_result_dict = self.p_io.const_result_dict
        self.ph_result = self.p_io.ph_result
        if self.equi_phases_flag:
            self.equi_phase_result_dict = self.p_io.equi_phase_result_dict
        if self.config.erosion and self.config.calculate_erosion:
            self.exchange_spezies_out = self.p_io.exchange_spezies_out


class PhreeqcExe(object):
    """Execute PHREEQC.
    """

    def __init__(self, config, phreeqc_input=None, phreeqc_output=None,
                 phreeqc_screen=None, node_name=None, ram_path=None):
        self.config = config
        self.node_name = node_name
        self.ram_path = ram_path
        def get_default(value, default):
            """Get value if it is true else get default.
            """
            if value:
                return value
            else:
                return default
        self.phreeqc_input = get_default(phreeqc_input, config.phreeqc_input)
        self.phreeqc_output = get_default(phreeqc_output,
                                          config.phreeqc_output)
        self.copy_exe()
        self.error = False
        self.error_text = ''

    def copy_exe(self):
        """Copy executable and database to ram path if not done yet.
        """
        def make_new_path(name):
            if self.node_name is None:
                return getattr(self.config, name)
            else:
                return change_base_path(self.ram_path,
                                        getattr(self.config, name))
        self.phreeqc_database = make_new_path('phreeqc_database')
        self.phreeqc_exe = make_new_path('phreeqc_exe')
        if not os.path.exists(self.phreeqc_database) or not filecmp.cmp(
            self.config.phreeqc_original_database, self.phreeqc_database):
            if not self.config.silent:
                print('copying database to ramdrive')
            shutil.copyfile(self.config.phreeqc_original_database,
                            self.phreeqc_database)
        if not os.path.exists(self.phreeqc_exe) or not filecmp.cmp(
            self.config.phreeqc_exe_original, self.phreeqc_exe):
            if not self.config.silent:
                print('copying phreeqc2 to ramdrive')
            shutil.copyfile(self.config.phreeqc_exe_original, self.phreeqc_exe)
            shutil.copymode(self.config.phreeqc_exe_original, self.phreeqc_exe)
        os.chdir(os.path.dirname(self.phreeqc_exe))
        if sys.platform == 'linux2':
            os.system('chmod +x ' + self.phreeqc_exe)

    def run(self, phreeqc_string):
        """
        Running PHREEQC.
        """
        keep_old_files(self.phreeqc_input, 10)
        keep_old_files(self.phreeqc_output, 10)
        fobj = open(self.phreeqc_input, 'w')
        fobj.write(phreeqc_string)
        fobj.close()
        if sys.platform == 'win32':
            self._run_windows_exe()
        else:
            self._run_other_exe()
        if self.error:
            try:
                fobj = open(self.phreeqc_output)
                data = fobj.readlines()
                fobj.close()
                self.error_text = 'Message from Phreeqc: \n'
                self.error_text += '#'*72 +'\n'
                for line in data[-5:]:
                    self.error_text += line
                self.error_text += '#'*72 +'\n'
                self.error_text += 'Phreeqc error occured for more ' \
                                  'information see %s\n" ' % fobj.name
            except OSError:
                self.error_text = "PhreeqcRun was NOT succesful, "+ \
                "check settings for ram_path, OSError occured"

    def _run_windows_exe(self):
        """Run PHREEQC executable on Windows using win32process.

        This way we can supress screen putput
        """
        timeout = int(1e7) # milliseconds
        import win32event
        import win32process
        info = win32process.CreateProcess(
            None, # AppName
            self.phreeqc_exe + ' ' +
            self.phreeqc_input + ' ' +
            self.phreeqc_output + ' ' +
            self.phreeqc_database, # Command line
            None, # Process Security
            None, # Thread Security
            0, # Inherit Handles?
            win32process.NORMAL_PRIORITY_CLASS|win32process.DETACHED_PROCESS,
            None, # New Environment
            None, # Current directiory
            win32process.STARTUPINFO())
        retrun_code = win32event.WaitForSingleObject(info[0], timeout)
        if retrun_code == win32event.WAIT_OBJECT_0:
            fobj = open(self.phreeqc_output)
            data = fobj.readlines()
            fobj.close()
            for line in data[-10:]:
                if len(line) > 2 and line.split()[0] == 'ERROR:':
                    self.error = True
                    break
                else:
                    self.error = False
        else:
            print('retrun code', retrun_code)
            self.error = True

    def _run_other_exe(self):
        """Run PHREEQC exe on bash-type shell.
        """
        proc =  subprocess.Popen([self.phreeqc_exe, self.phreeqc_input,
                                       self.phreeqc_output, self.phreeqc_database],
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE)
        proc.communicate()
        self.error = proc.returncode


def change_base_path(base_path, abs_file_name):
    """Put different base path in an absolute file_name.
    """
    return os.path.join(base_path, os.path.basename(abs_file_name))
