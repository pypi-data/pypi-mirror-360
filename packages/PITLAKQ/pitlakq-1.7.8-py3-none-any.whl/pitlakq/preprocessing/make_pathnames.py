"""Generate a file for W2 with all files names
to read its input from.
"""

from __future__ import print_function

import os
import sys


class PathNames(object):
    """Path name generator.
    """

    def __init__(self,
                 config,
                 title,
                 number_of_branches,
                 number_of_tributaries,
                 alternate_path=None):
        self.config = config
        self.title = None
        self.w2_path_names = None
        self.split_title(title)
        self.number_of_branches = number_of_branches
        self.number_of_tributaries = number_of_tributaries
        if alternate_path:
            self.file_name = alternate_path
            self.output_path = os.path.join(self.config.w2_node_path, 'ouput')
            self.input_path = os.path.join(self.config.w2_node_path, 'input')
        else:
            self.file_name = config.pre_w2_path_file_name
            self.output_path = os.path.join(self.config.w2_path, 'ouput')
            self.input_path = os.path.join(self.config.w2_path, 'input')

    def split_title(self, title):
        """Split title into several lines.
        """
        title = title.split('\n')
        if len(title) > 6:
            print('Title for W2 input file has to many lines.\n'
                  'Please use less lines')
            sys.exit()
        for line in title:
            if len(line) > 72:
                print('Title lines for W2 input file are to long.\n'
                      'Please lines <= 72 of length')
                sys.exit()
        self.title = title
        # pad up to six
        for _ in range(6 - len(self.title)):
            self.title.append('empty title line')

    def set_path(self):
        """List of all W2 path names.
        """
        self.w2_path_names = [
            ['main input file as netcdf', [os.path.join(self.input_path,
                                                        'w2input.nc')]],
            ['constituent input file as netcdf', [os.path.join(self.input_path,
                                                        'w2constinput.nc')]],
            ['netCDF exchange file', [self.config.nc_file_name]],
            ['bathymetry as netCDF file', [os.path.join(self.input_path,
                                                        'bath.nc')]],
            ['vertical profile', [os.path.join(self.input_path, 'vpr.npt')]],
            ['longitudinal profile', [os.path.join(self.input_path,
                                                   'initconds.nc')]],
            ['restart input', [os.path.join(self.config.ramPath,
                                            'rso365.opt')]],
            ['meteorologic data', [os.path.join(self.input_path, 'met.npt')]],
            ['witdrawl', [os.path.join(self.input_path, 'qwd.npt')]]]
        branches = [['branch inflow', 'qin'],
                    ['branch inflow temperature', 'tin'],
                    ['branch inflow concentration', 'cin'],
                    ['branch outflow', 'qot']]
        precipitation = [['precipitation', 'pre'],
                    ['precipitation temperature', 'tpr'],
                    ['precipitation inflow concentration', 'cpr']]
        tributary = [['tributary inflow', 'qtr'],
                     ['tributary inflow temperature', 'ttr'],
                     ['tributary concentration', 'ctr']]
        self.make_multiple(branches, self.number_of_branches, 'br')
        self.make_multiple(tributary, self.number_of_tributaries, 'tr')
        self.make_multiple(precipitation, self.number_of_branches, 'br')

    def make_multiple(self, base_list, number, obj):
        """Create several path names with the same pattern.
        """
        new_file_names = []
        for item in base_list:
            names = []
            for list_number in range(number):
                names.append(os.path.join(self.input_path, item[1] +
                                          '_%s%d.npt' %(obj,
                                                        list_number + 1)))
            new_file_names.append([item[0], names])
        self.w2_path_names.extend(new_file_names)

    def write_file(self):
        """Write the fuile with all path names.
        """
        fobj = open(self.file_name, 'w')
        for line in self.title:
            fobj.write(line + '\n')
        for item in self.w2_path_names:
            fobj.write('# ' + item[0] + '\n')
            for subitem in item[1]:
                fobj.write(8 * ' ' + "'" + subitem + "'" + '\n')

if __name__ == '__main__':

    def test():
        """Test if ot works.
        """

        class Dummy:
            # No attributes.
            # pylint: disable-msg=R0903
            # No __init__
            # pylint: disable-msg=W0232
            """Mock for config.
            """
            pass
        config = Dummy()
        # Set attributes from outside for testing.
        # pylint: disable-msg=W0201
        config.w2_path = 'path'
        config.nc_file_name = 'w2data.nc'
        title = 'line1.\n   line2\n 3\n 4\n 5\n6'
        number_of_branches = 1
        number_of_tributaries = 4
        path_names = PathNames(config,
                       title,
                       number_of_branches,
                       number_of_tributaries)
        path_names.set_path()
        path_names.write_file()

    test()
