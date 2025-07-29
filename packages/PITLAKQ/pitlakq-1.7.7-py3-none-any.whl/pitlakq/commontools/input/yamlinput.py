"""
W2 input in YAML format.

For more information about YAML see http://www.yaml.org
or http://de.wikipedia.org/wiki/YAML.
"""
from __future__ import print_function

import os
import datetime
import yaml
from . import recursiveupdate


class YamlInput(object):
    """Read input data in yaml format.
    """

    def __init__(self):
        self.recursion_depth = 0
        self.main_path = ''
        self.value_type = None
        self.data = None

    def load(self, default_file_name, value_file_name):
        """Load yaml files.
        """
        self.main_path = os.path.dirname(value_file_name)
        self.value_type = 'default'
        default_data = self.load_single(default_file_name)
        self.value_type = 'value'
        value_data = self.load_single(value_file_name)
        recursiveupdate.recursiveupdate(default_data, value_data,
                                        one_sided=True)
        self.data = default_data
        for key, value in self.data.items():
            for inner_k, inner_v in value.items():
                if inner_k == 'meta_data':
                    continue
                inner_v['is_default'] = True
                inner_v['value_given'] = False
                if 'value' in inner_v:
                    inner_v['value_given'] = True
                    try:
                        try:
                            cond = ('default' not in inner_v or inner_v['value']
                                    != inner_v['default'])
                        except ValueError:
                            # NumPy array shapes don't matching
                            cond = False
                        if not isinstance(cond, bool):
                            cond = cond.all()
                        try:
                            if cond:
                                inner_v['is_default'] = False
                        except KeyError as err:
                            print('key', key)
                            print('inner_k', inner_k)
                            print('inner_v', inner_v)
                            raise err
                        except ValueError as err:
                            print('key', key)
                            print('inner_k', inner_k)
                            print('inner_v', inner_v)
                            raise err
                    except KeyError:
                        print(72*'#')
                        print('File:', value_file_name)
                        print('Keyword %s not found.' % inner_k)
                        print(72*'#')
                        raise
                else:
                    inner_v['value'] = inner_v['default']
                if 'type' in inner_v:
                    data_type = inner_v['type']
                    if data_type == 'date':
                        #inner_v['default'], inner_v['value']
                        inner_v['default'] = make_date(inner_v['default'])
                        inner_v['value'] = make_date(inner_v['value'])

    def load_single(self, input_file_name, verbose=False):
        """Load a single YAML file.
        """
        old_path = os.getcwd()
        os.chdir(os.path.split(input_file_name)[0])
        data = self.read_yaml(input_file_name, verbose)
        os.chdir(old_path)
        return data

    def read(self, stream):
        """Read stream and read file into dict.
        """
        if isinstance(stream, dict):
            return stream
        elif isinstance(stream, File):
            read_format = getattr(self, 'read_' + stream.format)
            result = read_format(stream.name)
            if hasattr(stream, 'group_name'):
                result['meta_data'] = {self.value_type: stream.__dict__}
                return {stream.group_name: result}
            else:
                return result

    def read_plain(self, file_name):
        """Read file as one string.
        """
        if file_name.startswith('..'):
            file_name = os.path.join(os.path.dirname(self.main_path),
                                    file_name[3:])
        fobj = open(file_name)
        raw_data = fobj.read()
        fobj.close()
        return raw_data

    def read_yaml(self, file_name, verbose=False):
        """Read one YAML file.
        """
        def recurse(outer_k, data_in, new_data_in, depth):
            """Read data recursively.
            """
            for key in new_data_in.keys():
                if key == 'value':
                    data_in.update(new_data_in)
                    print('updated %s: with %s' % (outer_k, data_in[key]))
                elif key in data_in:
                    data_in[key] = recurse(key, data_in[key], new_data_in[key],
                                           depth)
                else:
                    print(file_name)
                    raise NameError('%s is not defined' % key)
            return data_in
        self.recursion_depth += 1
        raw_data = self.read_plain(file_name)
        data = {}
        verbose = True
        for stream in yaml.load_all(raw_data, Loader=yaml.FullLoader):
            new_data = self.read(stream)
            for k in new_data.keys():
                if k in data:
                    data[k] = recurse(k, data[k], new_data[k],
                                      self.recursion_depth)
                else:
                    data[k] = new_data[k]
                    if verbose:
                        print('setting new values for %s' % k)
        self.recursion_depth -= 1
        return data

    def read_columns_whitespace(self, file_name):
        """Read CSV file with space as delimiter.
        """
        fobj = open(file_name)
        raw_data = [x.split() for x in fobj.readlines()]
        fobj.close()
        data = {}
        header = raw_data[0]
        for entry in header:
            data[entry] = {self.value_type: []}
        for line in raw_data[1:]:
            if line:
                for col, entry in enumerate(header):
                    string_value = line[col]
                    try:
                        value = int(string_value)
                    except ValueError:
                        try:
                            value = float(string_value)
                        except ValueError:
                            value = string_value
                    data[entry][self.value_type].append(value)
        return data

    def read_netcdf(self, file_name):
        """Read a netcdf file.
        """
        import netCDF4
        fobj = netCDF4.Dataset(file_name, 'r', format='NETCDF3_CLASSIC')
        data = {}
        # Dynamic attribute.
        # pylint: disable-msg=E1101
        for name, value in fobj.variables.items():
            data[name] = {self.value_type: value[:]}
        fobj.close()
        return data


class File(yaml.YAMLObject):
    """A YAML file. Will be used if the directive '!File' is encounterted.
    """
    yaml_tag = u'!File'

    def __init__(self, name, format_=yaml, group_name=None,
                 w2_code_names_map=None):
        # Don't call base class?
        # pylint: disable-msg=W0231
        self.name = name
        self.format = format_
        self.group_name = group_name
        self.w2_code_names_map = w2_code_names_map
        self.meta = {'name': self.name, 'format': self.format,
                     'group_name': self.group_name,
                     'w2_code_names_map': self.w2_code_names_map}

    def __repr__(self):
        return "%s(name=%r, format=%r)" % (
               self.__class__.__name__, self.name, self.format)


class RecursionError(Exception):
    """Exception in recursion.
    """
    pass


def make_date(date_string):
    """Create a datetime.datetime object form a string.
    """
    date_parts = date_string.split()
    date = [int(x) for x in date_parts[0].split('.')]
    try:
        hour, minute, decimal_second = date_parts[1].split(':')
        second, second_fraction = divmod(float(decimal_second), 1)
        time_ = (int(hour), int(minute), int(second),
                 int(second_fraction * 1e6))
    except IndexError:
        time_ = (0, 0, 0, 0)
    # Magic is good here.
    # pylint: disable-msg=W0142
    return datetime.datetime(date[2], date[1], date[0], *time_)


def dump(file_name, data):
    """Dump yaml for degugging
    """
    fobj = open(file_name, 'w')
    fobj.write(yaml.dump(data))
    fobj.close()
