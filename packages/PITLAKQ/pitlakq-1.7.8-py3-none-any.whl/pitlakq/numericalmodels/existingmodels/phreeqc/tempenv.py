import os
import shutil

from pitlakq.metamodel.configuration.getconfig import read_dot_pitlakq

"""Create a temporary environment.
"""

def make_temp_env(project_name, env_name):
    """Create a temporally enviroment for PHREEQC.
    """
    dot_pitlakq = list(read_dot_pitlakq())[0]
    temp_path = os.path.join(dot_pitlakq['ram_path'], project_name, env_name)
    resources_path = dot_pitlakq['resources_path']
    if not os.path.exists(temp_path):
        os.mkdir(temp_path)
    for name in ['phreeqc2win.exe', 'phreeqc_w2.dat']:
        src = os.path.join(resources_path, name)
        dst = os.path.join(temp_path, name)
        shutil.copy(src, dst)
    return temp_path


class TempDir(object):
    # pylint: disable-msg=R0903
    # No public methods.
    """Change into a temp dir and back.
    """
    def __init__(self, temp_dir):
        self.temp_dir = temp_dir
        self.old_dir = os.getcwd()

    def __enter__(self):
        self.old_dir = os.getcwd()
        os.chdir(self.temp_dir)

    def __exit__(self, exc_type, exc_val, exc_tb):
        os.chdir(self.old_dir)