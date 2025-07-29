"""Preprocessing: Create batyhmetry data for W2.
"""

from __future__ import print_function

import os
import time
import sys

from ZODB import FileStorage, DB
import transaction


import pitlakq.commontools.input.yamlinput as yamlinput
from pitlakq.metamodel.configuration.getconfig import read_dot_pitlakq
from pitlakq.preprocessing import preprocessor
from pitlakq.preprocessing.create_bathgrid import _create_output_path


def clean_dir(path):
    """Delete all files in the given dir.
    """

    for file_name in os.listdir(path):
        if os.path.isfile(os.path.join(path, file_name)):
            os.remove(os.path.join(path, file_name))


def main(project_name=None, del_out=False, del_tmp=True):
    """Run preprocessing for W2 batyhmetry.
    """
    start = time.time()
    if not project_name:
        if len(sys.argv) < 2:
            print('please give project name as command line argument')
            sys.exit()
        else:
            project_name = sys.argv[1]
    dot_pitlakq = list(read_dot_pitlakq())[0]
    project_path = os.path.join(dot_pitlakq['model_path'], project_name)
    _create_output_path(project_path)
    input_data = yamlinput.YamlInput()
    template_file = os.path.join(dot_pitlakq['template_path'],
                                 'preprocessing.yaml')
    value_file = os.path.join(project_path, 'preprocessing', 'input',
                              'preprocessing.yaml')
    input_data.load(template_file, value_file)
    input_path = os.path.join(project_path, 'preprocessing', 'input')
    output_path = os.path.join(project_path, 'preprocessing', 'output')
    tmp_path = os.path.join(project_path, 'preprocessing', 'tmp')
    path = input_data.data['path']
    bath = input_data.data['bathymetry']
    min_width = bath['min_width']['value']
    initial_water_surface = bath['initial_water_surface']['value']
    max_water_surface = bath['max_water_surface']['value']
    orientations = bath['orientations']['value']
    swapped_x_y = bath['swapped_x_y']['value']
    surfer_files = [os.path.join(input_path, f_name) for f_name in
                    path['grid']['value']]
    names = bath['names']['value']
    reservoir_geometry_files = [
        os.path.join(input_path, f_name) for f_name in
        input_data.data['path']['reservoir_data']['value']]
    bath_file_name = os.path.join(output_path, path['bath_file']['value'])
    if del_out:
        clean_dir(output_path)
    if del_tmp:
        clean_dir(tmp_path)

    print('preprocessing is running ...')
    lake = preprocessor.W2Lake(surfer_files,
                               reservoir_geometry_files,
                               bath_file_name,
                               min_width,
                               max_water_surface,
                               orientations,
                               names,
                               swapped_x_y)
    lake.make_bathymetry()
    lake.write_bath_nc()
    storage = FileStorage.FileStorage(os.path.join(project_path,
                                                   project_name + '.fs'))
    db = DB(storage)
    connection = db.open()
    dbroot = connection.root()
    if 'preprocessingData' not in dbroot:
        dbroot['preprocessingData'] = {}
    pre = dbroot['preprocessingData']
    pre['w2Lake'] = lake
    dbroot['preprocessingData'] = pre
    transaction.commit()
    dbroot['initialWaterSurface'] = initial_water_surface
    transaction.commit()
    connection.close()
    print('runtime was %10.1f seconds' % (time.time() - start))

if __name__ == '__main__':
    main()
