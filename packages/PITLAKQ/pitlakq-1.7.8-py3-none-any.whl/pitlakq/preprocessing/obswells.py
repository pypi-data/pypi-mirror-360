"""Associate concentrations of wells with inflow gw zones.
"""

# NumPy and its dynamic members.
# pylint: disable-msg=E1101

from __future__ import print_function

import os

import numpy

import pitlakq.submodels.erosion.polygon_gridding as polygon_gridding
import pitlakq.commontools.dbftools.pcg.pcgdatabase as pcgdatabase


class ObsWellAssociator(object):
    """Associate wells with zones.
    """

    def __init__(self, config, association_dict=None):
        self.config = config
        if association_dict:
            self.association_dict = association_dict
            self.read_pcg_data()
            self.main_dir = self.config.well_polygons_path
            self.associate_obs_wells()
            self.read_obs_conc()

    def read_pcg_data(self):
        """Read data from PCG database.
        """
        # Define attributes here.
        # pylint: disable-msg=W0201
        database = pcgdatabase.PcgDatabase(self.config)
        database.make_3d_arrays()
        self.kf_numbers = database.kf_numbers
        self.x = database.x_pcg
        self.y = database.y_pcg
        self.delta_x = self.x[1] - self.x[0]
        self.delta_y = self.y[1] - self.y[0]
        self.x_min = self.x[0] + self.delta_x / 2.0
        self.y_min = self.y[0] + self.delta_y / 2.0
        self.x_max = self.x[-1] + self.delta_x / 2.0 # +!
        self.y_max = self.y[-1] + self.delta_y / 2.0 # +!

    def associate_obs_wells(self):
        """Match wells and zones.
        """
        # Define attributes here.
        # pylint: disable-msg=W0201
        self.associated_obs = self.kf_numbers * 0
        for key in self.association_dict.keys():
            switch = self.association_dict[key].split('_')
            if switch[0] == 'poly':
                dir_ = os.path.join(self.main_dir, switch[1])
                two_d = self.read_polygons(dir_)
                well_number = self.kf_numbers * 0
                for layer in range(well_number.shape[2])[1:]:
                    well_number[:-1, :-1, layer] = two_d
            elif switch[0] == 'well':
                well_number = int(switch[1])
            else:
                IOError(switch[0] +
                        ' is no valid first part of association_dict\n' +
                        'choose poly or well')
            key_number = int(key.split('f')[1])
            self.associated_obs = (self.associated_obs +
                                   numpy.equal(self.kf_numbers, key_number) *
                                   well_number)
        self.associated_obs = self.associated_obs[:-1, :-1, :]
        cycles = range(self.associated_obs.shape[2]-1)
        for _ in cycles:
            self.eliminate_zero_keys()

    def eliminate_zero_keys(self):
        """Delete all unused keys.
        """
        self.associated_obs[:, :, :-1] = numpy.where(
            self.associated_obs[:,:,:-1], self.associated_obs[:,:,:-1],
            self.associated_obs[:,:,1:])

    def read_polygons(self, dir_):
        """Read polygons.
        """
        grid = polygon_gridding.Grid(self.x_min, self.y_min,
                                     self.x_max, self.y_max,
                                     self.delta_x, self.delta_y,
                                     dir_, use_names_as_ids=True)
        return grid.polygon_ids

    def read_obs_conc(self, use_second_key=None):
        """Read the concentrations for the obs wells.
        """
        # Define attributes here.
        # pylint: disable-msg=W0201
        data = self.read_csv(self.config.well_conc_file_name, ';')
        if use_second_key:
            well_keys = data[3][2:]
        else:
            well_keys = [int(value) for value in data[4][2:]]
        self.wells = {}
        for key in well_keys:
            self.wells[key] = {}
        for line in data[6:-1]:
            spezie = line[1]
            n = 0
            for key in well_keys:
                try:
                    self.wells[key][spezie] = float(line[2:][n])
                except ValueError:
                    pass
                n += 1

    @staticmethod
    def read_csv(file_name, sep):
        """Read a cvs file.
        """
        fobj = open(file_name)
        data = fobj.readlines()
        fobj.close()
        new_data = []
        for line in data:
            line = line.strip()
            new_data.append(line.split(sep))
        return new_data


if __name__ == '__main__':

    def test():
        """tes if it works.
        """
        import pitlakq.metamodel.configuration.getconfig as getconfig
        import sys
        import time
        start = time.time()
        if len(sys.argv) < 2:
            print('please give project name as command line argument')
            sys.exit()
        else:
            project_name = sys.argv[1]
        dirn = os.path.dirname
        root_path = dirn(dirn(dirn(os.path.abspath(__file__))))
        config = getconfig.get_yaml_config(project_name, root_path)
        # key: name in COM-field of PCG must be of form kf + int
        # value: poly_dirname --> reads polygons from this diretory
        # in ../pcg/polygons
        # value: well_int --> uses values from this well for whole area
        association_dict = {'kf1': 'poly_kf1',
                            'kf2': 'poly_kf2',
                            'kf3': 'poly_kf2',
                            'kf4': 'well_3',
                            'kf5': 'well_5',
                            'kf6': 'well_6',
                            'kf7': 'well_6',
                            'kf8': 'well_6',
                            'kf9': 'well_6',
                            'kf10': 'well_6',
                            'kf11': 'well_6',
                            'kf12': 'well_6',
                            'kf13': 'well_6',
                            'kf14': 'well_6',
                            'kf15': 'well_6',
                            'kf16': 'well_6'}
        assoc = ObsWellAssociator(config, association_dict)
        for layer in range(assoc.associated_obs.shape[2]):
            print('layer', layer+1)
            for y in range(assoc.associated_obs.shape[1]):
                for x in range(assoc.associated_obs.shape[0]):
                    print(assoc.associated_obs[x, y, layer], end='')
                print()
        duration = time.time() -start
        print('run time:', duration)

    test()
