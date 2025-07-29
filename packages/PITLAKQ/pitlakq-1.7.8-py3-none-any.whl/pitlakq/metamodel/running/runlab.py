"""Proof of concept starting a new Jupyterlab instance for each
PITLAKQ project.

"""

import os
import subprocess
import sys


def main(project_name, notebook_dir):
    """Start new Jupyterlab for project `project_name`.

    `notebook_dir` is the root directory for the Notebook server.
    """
    jupyter = os.path.join(os.path.split(sys.executable)[0], 'jupyter')

    if not os.path.exists(notebook_dir):
        os.mkdir(notebook_dir)

    os.environ['PITLAKQ_PROJECT'] = project_name

    subprocess.run([
        jupyter,
        'lab',
        f'--LabApp.notebook_dir={notebook_dir}',
        f'--LabApp.base_url=/{project_name}',
        f'--ContentsManager.untitled_notebook={project_name.capitalize()}'
        ])


if __name__ == '__main__':

    def test():
        """A simple test.
        """
        project_name = 'myproject_37'
        notebook_dir = f'/Users/mike/tmp/{project_name}'
        main(project_name, notebook_dir)

    test()
