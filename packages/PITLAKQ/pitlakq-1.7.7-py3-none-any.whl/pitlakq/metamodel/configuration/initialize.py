"""Intialize the project layout.
"""


from collections import OrderedDict
import os
import sys

from pitlakq.metamodel.configuration.getconfig import get_mode

# pylint: disable=redefined-builtin, invalid-name, undefined-variable
if sys.version_info.major < 3:
    input = raw_input
# pylint: enable=redefined-builtin, invalid-name, undefined-variable


def initialize_pitlakq(args):
    """Create a default `.pitlakq` and the need path for RAM and models.
    """
    # pylint: disable=unused-argument
    home_path = os.path.expanduser('~')
    dot_pitlakq = os.path.join(home_path, '.pitlakq')
    if os.path.exists(dot_pitlakq):
        print('File {} already exists.'.format(dot_pitlakq))
        overwrite = input('Overwrite? [y/N]')
        if overwrite not in ['y', 'Y', 'yes', 'Yes']:
            print('Stop initializing PITLAKQ.')
            return
        else:
            print('Overwriting file: {}'.format(dot_pitlakq))
    else:
        print('Creating file: {}'.format(dot_pitlakq))
    paths = _make_paths(home_path)
    _write_dot_pitlakq(paths, dot_pitlakq)
    _make_dir_or_skip(paths['model_path'])
    _make_dir_or_skip(paths['ram_path'])
    print('Initialized PITLAKQ.')


def _make_paths(home_path):
    """Create path names for config file.
    """
    paths = OrderedDict()
    base_path = os.path.join(home_path, 'pitlakq_work')
    paths['model_path'] = os.path.join(base_path, 'models')
    paths['ram_path'] = os.path.join(base_path, 'RAM')
    mode, rootpath = get_mode()
    if mode == 'deployment mode':
        mod_path = os.path.join(base_path, 'pitlakq_exe', 'pitlakq')
    else:
        import pitlakq
        mod_path = os.path.dirname(pitlakq.__file__)
    paths['resources_path'] = os.path.join(mod_path, 'resources')
    paths['template_path'] = os.path.join(mod_path, 'templates')
    return paths


def _write_dot_pitlakq(paths, dot_pitlakq, verbose=True):
    """Write file pitlakq.
    """
    with open(dot_pitlakq, 'w') as fobj:
        for name, path in paths.items():
            fobj.write('{}:\n'.format(name))
            fobj.write('    {}\n\n'.format(path))
            if verbose:
                print('    {}: {}'.format(name, path))


def _make_dir_or_skip(path):
    """Create a new directory. Do nothing if it already exists.
    """
    try:
        os.makedirs(path)
    except OSError:
        print('Cannot create directory "{}". It already exists. '.format(path))
