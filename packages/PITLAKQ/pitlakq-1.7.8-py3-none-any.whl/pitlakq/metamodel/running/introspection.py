"""Information about the model.
"""
from __future__ import print_function

import os

from pitlakq.commontools.input import yamlinput
from pitlakq.metamodel.configuration.getconfig import (
    get_full_template_path, read_dot_pitlakq)


def get_w2_name_mapping():
    """Get the mapping of w2 to pitlakq names and vise versa.
    """
    yaml_input = yamlinput.YamlInput()
    data = yaml_input.load_single(get_full_template_path('w2.yaml'),
                                  verbose=False)
    pitlakq_names = {}
    w2_names = {}
    for outer_value in data.values():
        for pitlakq_name, value in outer_value.items():
            try:
                w2_name = value['w2_code_name']
            except KeyError:
                continue
            pitlakq_names[pitlakq_name] = w2_name
            w2_names[w2_name] = pitlakq_name
    return pitlakq_names, w2_names


def show_w2_names():
    """Show mapping of names.
    """
    pitlakq_names, _w2_names = get_w2_name_mapping()
    print('%-50s %-40s' % ('PITLAKQ name', 'W2 name'))
    print('=' * 79)
    for name in sorted(pitlakq_names):
        print('%-50s %-40s' % (name, pitlakq_names[name]))


def show_projects():
    """Show all projects.
    """
    global_config = read_dot_pitlakq()
    global_config = next(global_config)
    model_path = global_config['model_path']
    print('Model path:\n    ', model_path)
    print()
    project_names = [name for name in os.listdir(model_path)
                     if os.path.isdir(os.path.join(model_path, name))]
    print('Projects:')
    if project_names:
        for name in project_names:
            print('    ', name)
    else:
        print('Currently no projects.')
