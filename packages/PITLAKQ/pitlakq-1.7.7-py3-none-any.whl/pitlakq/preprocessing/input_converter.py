"""Convert mixedCase YAML input to underscore_yaml_input.
"""


import configparser
import os
import shutil
import sys

import netCDF4

from pitlakq.metamodel.configuration.getconfig import read_dot_pitlakq
from pitlakq.commontools.dirs import splitall


# pylint: disable=redefined-builtin, invalid-name, undefined-variable
if sys.version_info.major < 3:
    input = raw_input
# pylint: enable=redefined-builtin, invalid-name, undefined-variable


class InputConverter(object):
    """Convert mixedCase to under_score.
    """

    @staticmethod
    def get_mixed_case(line):
        """Find the mixedCase word.
        """
        # strip off comments
        line = line.split('#')[0]
        words = line.split()
        for word in words:
            if len(word) > 1 and word[0].islower():
                for character in word[1:]:
                    if character == '_':
                        break
                    if character.isupper():
                        return word
        return False

    @staticmethod
    def make_underscore(mixed_case):
        """Convert a mixedCase word into a under_score one.
        """
        underscore_name = ''
        was_upper = False
        was_digit = False
        set_digit = False
        for character, next in zip(mixed_case, mixed_case[1:] + ' '):
            if character.isupper():
                if was_upper and not set_digit:
                    underscore_name += character.lower()
                else:
                    if was_digit and (not next.strip() or next.isupper()):
                        underscore_name = (underscore_name[:-1] + '_' +
                                           underscore_name[-1] +
                                           character.lower())
                        set_digit = True
                    else:
                        underscore_name += '_' + character.lower()
                        set_digit = False
                was_upper = True
            else:
                underscore_name += character
                was_upper = False
            if character.isdigit():
                was_digit = True
            else:
                was_digit = False
        return underscore_name

    @staticmethod
    def get_fobj(name_or_obj, mode='r'):
        """Open a new file object form a path or
        retrun the file object if it is one.
        """
        if isinstance(name_or_obj, str):
            return open(name_or_obj, mode)
        else:
            return name_or_obj

    def convert_yaml(self, in_file, out_file):
        """Do the convertion for one YAML file.

        We only convert the first occurance of the a mixedCase
        per line. All others are ignored.
        """
        self.convert_file(in_file, out_file, limit=1)

    def convert_txt(self, in_file, out_file):
        """Do the convertion for one text file.

        We convert all occurance of the a mixedCase.
        """
        self.convert_file(in_file, out_file)

    def convert_file(self, in_file, out_file, limit=None):
        """Do the convertion for one file.

        We convert no more than 'limit' occurances of mixedCases per line.
        Default is `None` for no limit. A limit less than 1 raises an
        OverflowException (well it is and underflow ;)).
        All limit values (excpet `None`) are converted to integers.
        """
        if limit:
            limit = int(limit)
            if limit < 1:
                raise OverflowError('Limit must be integer greater than zero.'
                                    ' %d given.' % limit)
        in_fobj = self.get_fobj(in_file)
        out_fobj = self.get_fobj(out_file, 'w')
        for line in in_fobj:
            mixed_case = self.get_mixed_case(line)
            counter = 0
            while mixed_case:
                if counter == limit:
                    break
                counter += 1
                underscore = self.make_underscore(mixed_case)
                line = line.replace(mixed_case, underscore)
                mixed_case = self.get_mixed_case(line)
            if line.strip().startswith('CasC'):
                line = line.replace('CasC', 'c_as_c')
            out_fobj.write(line)
        in_fobj.close()
        out_fobj.close()

    def convert_bath(self, in_file_name, out_file_name):
        """Convert dimension and variable names in bythymetry file
        from mixedCase to under_score.
        """
        # Dynamic members of netCDF file.
        # pylint: disable-msg=E1101
        in_fobj = netCDF4.Dataset(in_file_name, 'r', format='NETCDF3_CLASSIC')
        out_fobj = netCDF4.Dataset(out_file_name, 'w', format='NETCDF3_CLASSIC')
        for name, dimension in in_fobj.dimensions.items():
            out_fobj.createDimension(self.make_underscore(name),
                                     len(dimension))
        for name, variable in in_fobj.variables.items():
            dims = tuple((self.make_underscore(name) for name in
                          variable.dimensions))
            new_name = self.make_underscore(name)
            old_value = in_fobj.variables[name][:]
            nc_obj = out_fobj.createVariable(new_name, old_value.dtype.char,
                                             dims)
            nc_obj[:] = old_value
        in_fobj.close()
        out_fobj.close()

    def convert_project(self, src, dst, ini_path):
        """Convert a whole project from mixedCase to under_score.
        """

        def skip(src_file, dst_file):
            """Do nothing here.
            """
            # Arguments are deliberately unused.
            # pylint: disable-msg=W0613
            pass

        def undefined(src_file, dst_file):
            """No action specified.
            """
            # Arguments are deliberately unused.
            # pylint: disable-msg=W0613
            ext = os.path.splitext(src_file)[1][1:]
            print('No action specified for extension "%s".' % ext)
            print('Available actions are:')
            names = sorted(allowed_functions.keys())
            for index, name in enumerate(names):
                print(index, name)
            while True:
                index = input('Please choose the number for the action for'
                              ' all files with this extension: ')
                try:
                    action_name = names[int(index)]
                    converters[ext] = allowed_functions[action_name]
                    converters.get(ext, undefined)(src_file_name,
                                                   dst_file_name)
                    break
                except (ValueError, IndexError, KeyError):
                    print('Invalid choice.')
            print('Using action %s for extension %s.' % (action_name, ext))

        allowed_functions = {'convert_txt': self.convert_txt,
                             'convert_yaml': self.convert_yaml,
                             'convert_bath': self.convert_bath,
                             'copy_unmodfied': shutil.copy,
                             'skip': skip}
        config = configparser.ConfigParser()
        config.read(ini_path)
        actions = dict(config.items('extension_actions'))
        if 'no_extension' in actions:
            actions[''] = actions['no_extension']
            del actions['no_extension']
        converters = {}
        for ext, action in actions.items():
            try:
                converters[ext] = allowed_functions[action]
            except KeyError:
                print('Action %s is not available.' % action)
                print('Please specify a action for extension "%s".' % ext)
                print('Available actions are:')
                for name in allowed_functions.keys():
                    print(name)
                sys.exit(1)
        src_offset = len(splitall.parse_path(src))
        for src_root, _, src_files in os.walk(src):
            dst_root = os.path.join(dst,
                        *tuple(splitall.parse_path(src_root)[src_offset:]))
            if not os.path.exists(dst_root):
                os.mkdir(dst_root)
            for file_name in src_files:
                src_file_name = os.path.join(src_root, file_name)
                if file_name == 'modglue.yaml':
                    file_name = 'pitlakq.yaml'
                dst_file_name = os.path.join(dst_root, file_name)
                ext = os.path.splitext(file_name)[1][1:]
                converters.get(ext, undefined)(src_file_name, dst_file_name)

if __name__ == '__main__':

    def main():
        """Command line tool.
        """
        interactive = True
        global_config = read_dot_pitlakq()
        global_config = next(global_config)
        ini_path = os.path.join(global_config['resources_path'],
                                'converter.ini')
        if interactive:
            while True:
                src = input('Source input path'
                         r' (e.g. c:\models\old_project): ')
                src_input_path = os.path.join(src, 'input')
                if not os.path.exists(src_input_path):
                    msg = ('Could NOT find source input path %s.\n'
                           % src_input_path)
                    msg += 'Please enter a valid path for a project.'
                    print(msg)
                    continue
                src_pcg_path = os.path.join(src, 'pcg')
                if not os.path.exists(src_pcg_path):
                    src_pcg_path = None
                src_modmst_path = os.path.join(src, 'modmst')
                if not os.path.exists(src_modmst_path):
                    src_modmst_path = None
                dst = input('Target input path'
                           r' (e.g. c:\models\new_project): ')
                if not os.path.exists(dst):
                    os.mkdir(dst)
                dst_input_path = os.path.join(dst, 'input')
                dst_pcg_path = os.path.join(dst, 'pcg')
                dst_modmst_path = os.path.join(dst, 'modmst')
                print('Will convert:')
                print(src_input_path)
                print('to:')
                print(dst_input_path)
                if src_pcg_path:
                    print('Will also convert:')
                    print(src_pcg_path)
                    print('to:')
                    print(dst_pcg_path)
                if src_modmst_path:
                    print('Will also convert:')
                    print(src_modmst_path)
                    print('to:')
                    print(dst_modmst_path)
                project_name = os.path.split(src)[1]
                src_project_file_path = os.path.join(src, project_name + '.fs')
                if os.path.exists(src_project_file_path):
                    dst_project_file_path = os.path.join(dst,
                                                         project_name + '.fs')
                    print('And copy')
                    print(src_project_file_path)
                    print('to:')
                    print(dst_project_file_path)
                else:
                    src_project_file_path = None
                answer = input('Is this correct[Y/n]?: ')
                if answer not in ['N', 'n', 'No', 'no']:
                    break
        print('Converting ...')
        converter = InputConverter()
        converter.convert_project(src_input_path, dst_input_path, ini_path)
        if src_pcg_path:
            converter.convert_project(src_pcg_path, dst_pcg_path, ini_path)
        if src_modmst_path:
            converter.convert_project(src_modmst_path, dst_modmst_path,
                                      ini_path)
        if src_project_file_path:
            shutil.copy(src_project_file_path, dst_project_file_path)
        print('Sucessfully converted:')
        print(src)
        print('to:')
        print(dst)

    main()
