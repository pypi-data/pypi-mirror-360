
"""Read configuration data.
"""

# Some dynamic attributes are not recocnized.
# pylint: disable-msg= E1101


import importlib.util
import os
import sys


import yaml

import pitlakq.commontools.input.yamlinput as yamlinput
import pitlakq.metamodel.configuration.configuration as configuration

CONFIG = [None]


class Writer(object):
    """Write to several files, stdout etc.
    """

    def __init__(self, *writers):
        self.writers = writers

    def write(self, text):
        """Write text to all writers.
        """
        for writer in self.writers:
            writer.write(text)

    def flush(self):
        """Flush all writers.
        """
        for writer in self.writers:
            writer.flush()


def get_dot_pitlakq_path(verbose=False):
    """Find path of the file `.pitlakq.

    If dot_pitlakq is given it will be read with yaml. Otherwise search for a
    .pitlakq file starts in PITLAKQHOME and, if not found there, continues in
    the user's home directory. Raises EnvironmentError if no file was found.
    """
    dot_pitlakq = None
    found = False
    pitlakqhome_path = os.getenv('PITLAKQHOME')
    if pitlakqhome_path:
        dot_pitlakq = os.path.join(pitlakqhome_path, '.pitlakq')
        if not os.path.exists(dot_pitlakq):
            if verbose:
                print('Environmental variable PITLAKQHOME is set, but no')
                print('file named `.pitlakq` found there.')
                print('Searching home directory for `.pitlakq`.')
        else:
            found = True
    if not found:
        home_path = os.path.expanduser('~')
        dot_pitlakq = os.path.join(home_path, '.pitlakq')
        if not os.path.exists(dot_pitlakq):
            dot_pitlakq = None
    if not dot_pitlakq:
        msg = """
        No file named `.pitlakq` found.
        Please rename `.pitlakq_sample` to `.pitlakq` modify its
        content to reflect your setup and put it either in your
        home directory or into the directory the environmental variable
        PITLAKQHOME contains."""
        raise EnvironmentError(msg)
    return dot_pitlakq


def read_dot_pitlakq(dot_pitlakq=None, verbose=False):
    """Read site config file with directory names.
    """
    if not dot_pitlakq:
        dot_pitlakq = get_dot_pitlakq_path(verbose)
    if verbose:
        print('Using %s' % dot_pitlakq)
    return yaml.safe_load_all(open(dot_pitlakq).read())


def get_yaml_config(project_name, root_path):
    """Read configuration data from yaml file.
    """
    print(f'{root_path}')
    if CONFIG[0]:
        return CONFIG[0]
    global_config = read_dot_pitlakq(verbose=True)
    global_config = next(global_config)
    model_path = global_config['model_path']
    ram_path = global_config['ram_path']
    pcg_project_name = 'lake'
    pcg_short_path = os.path.join(root_path, 'temp')
    w2_short_path = os.path.join(root_path, 'temp')
    template_path = os.path.join(root_path, 'pitlakq', 'templates')
    config = configuration.Config(project_name,
                                  model_path,
                                  pcg_project_name,
                                  root_path,
                                  ram_path,
                                  pcg_short_path,
                                  w2_short_path,
                                  template_path)
    config.reduced = False
    input_ = yamlinput.YamlInput()
    input_.load(os.path.join(config.template_path, 'pitlakq.yaml'),
                os.path.join(config.main_path, 'pitlakq.yaml'))
    for value in input_.data.values():
        for inner_k, inner_v in value.items():
            setattr(config, inner_k, inner_v['value'])
    config.phreeqc_original_database = os.path.join(
        config.resource_path, config.phreeqc_database_name)
    config.gwh_file = os.path.normpath(os.path.join(config.project_path,
                                                    'input', config.gwh_file))
    config.loading_file = os.path.normpath(os.path.join(config.project_path,
                                                'input', config.loading_file))

    if config.gw_model != 'pcg':
        # dummy if no pcg --> fix later in other modules, e.g. pitlakq.pitlakq
        # needs pcg_names as init paramter
        config.pcg_names = {'pcg3': {'h': 0, 'qw': 0, 'conc': []}}
    for name in config.pcg_names.keys():
        if config.pcg_names[name]['qw']:
            pcg_qw = name
            if config.lake_calculations:
                config.pcg_wa_result_path = os.path.join(
                    config.pcg_short_path, pcg_qw, config.pcg_project_name,
                    'result')
    for obj in [config.rates, config.mineral_rates]:
        if len(obj) == 1 and None in obj:
            obj[:] = []
    CONFIG[0] = config
    return config


def get_config(project_name):
    """Get the configuration object.
    """
    mode, root_path = get_mode()
    config = get_yaml_config(project_name, root_path)
    if not os.path.exists(config.output_path):
         os.mkdir(config.output_path)
    fout = open(config.log_file_name, 'w')
    sys.stdout = Writer(sys.stdout, fout)
    return config


def get_mode():
    """Check if we run in development mode, i.e. with source code
    or in deployment mode, i.e. as frozen executable.
    """
    mode = 'development mode'
    dirn = os.path.dirname
    # go up 4 directories to find root path where dirs resources and
    # templates are
    root_path = dirn(dirn(dirn(dirn(os.path.abspath(__file__)))))
    print(f'{mode=}')
    return mode, root_path


def get_full_template_path(template_name):
    """Get a template.
    """
    dirn = os.path.dirname
    # go up 4 directories to find root path where dirs resources and
    # templates are
    root_path = dirn(dirn(dirn(dirn(os.path.abspath(__file__)))))
    return os.path.join(root_path, 'pitlakq', 'templates', template_name)
