"""Setup the directory structure for a new project.
"""

import os
import sys

import yaml

from pitlakq.metamodel.configuration.getconfig import read_dot_pitlakq


class ProjectCreator(object):
    """Create all necessary directories.
    """
    # one public method is fine
    # pylint: disable-msg=R0903
    def __init__(self, project_name, dot_pitlakq=None, erosion=None,
                 sediment=None):
        self.project_name = project_name
        self.config = list(read_dot_pitlakq(dot_pitlakq))[0]
        self.erosion = erosion
        self.sediment = sediment

    def create(self):
        """Create a new directory structure.
        """

        def create_dirs(base, dirs):
            """Create dirs recrusively.
            """
            for dir_ in dirs:
                path = os.path.join(base, dir_)
                if not os.path.exists(path):
                    os.mkdir(path)
                sub_dirs = dirs[dir_]
                if sub_dirs:
                    create_dirs(os.path.join(base, dir_), sub_dirs)
        base_base = os.path.join(self.config['model_path'], self.project_name)
        if not os.path.exists(base_base):
            os.mkdir(base_base)
        dirs = {'input': {'main': None, 'w2': None},
                'output': {'w2': None, 'sediment': None, 'balance': None,},
                'postprocessing': None,
                'preprocessing': {'input': None, 'output': None, 'tmp': None}}
        create_dirs(base_base, dirs)


def main(project_name):
    """Do it.
    """
    creator = ProjectCreator(project_name)
    creator.create()
    print('Created project {} in {}.'.format(project_name,
                                             creator.config['model_path']))

if __name__ == '__main__':

    main(project_name)
