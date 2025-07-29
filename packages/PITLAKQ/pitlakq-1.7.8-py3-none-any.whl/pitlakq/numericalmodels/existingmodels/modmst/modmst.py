"""Wrapper and exchange for MODMST.
"""

from __future__ import print_function

import os
import sys
import copy

# NumPy, dynamic members.
# pylint: disable-msg=E1101

import numpy

import pitlakq.metamodel.running.db as db
import pitlakq.submodels.gw.activecells as activecells
import modmst_fortran


class Modmst(object):
    """
       Wrapper for MODMST FORTRAN module
    """
    # Lost of attributes initialize outside __init__.
    # pylint: disable-msg=W0201
    def __init__(self, config):
        self.config = config
        self.config.modmst_debug_output = True
        os.chdir(self.config.modmst_path)
        self.repr = modmst_fortran
        print('calling mike_init')
        self.repr.mike_init()
        print('finished mike_init')
        self.get_modmst_names()
        self.get_preprocessing_data()
        self.make_mapping()
        self.first = True
        self.active_cell_adjuster = activecells.ActiveCells(self.config)
        self.total_q_in = 0.0
        self.total_q_out = 0.0
        self.total_w2_q_in = 0.0
        self.total_w2_q_out = 0.0
        if self.config.modmst_conc_unmodified:
            self.old_modmst_conc = {}
        if self.config.modmst_debug_output:
            self.create_debug_files()
        print('finished init')

    def create_debug_files(self):
        """Open files for MODMST debug information.
        """
        self.debug_from_modmst = open(os.path.join(self.config.w2_output_path,
                                                 'flux_from_modmst.txt'), 'w')
        self.debug_to_modmst = open(os.path.join(self.config.w2_output_path,
                                                 'flux_to_modmst.txt'), 'w')
        for fobj in [self.debug_from_modmst, self.debug_to_modmst]:
            fobj.write('%15s%15s' % ('time', 'flow'))
            for name in self.conc_names:
                fobj.write('%15s' % name)
            fobj.write('\n')
            fobj.flush()

    def get_modmst_names(self):
        """Creat short aliase for names vom MODMST.
        """
        # Initialize attributes here.
        # pylint: disable-msg=W0201
        self.nlake = self.repr.fielddata.mike_nlake
        self.dt = self.repr.fielddata.mike_dt  # pylint: disable-msg=C0103
        self.total_time = self.repr.fielddata.mike_totim
        self.layer = self.repr.fielddata.mike_layer
        self.row = self.repr.fielddata.mike_row
        self.column = self.repr.fielddata.mike_column
        self.water_table = self.repr.fielddata.mike_head
        self.flow = self.repr.fielddata.mike_q
        self.temperature = self.repr.fielddata.mike_temperature
        self.density = self.repr.fielddata.mike_density_bottom
        self.conc_names = ['na', 'cl', 'nh4', 'ca', 'so4', 'tic', 'no3',
                           'al', 'mg', 'ka', 'fe3']
        for name in self.conc_names:
            setattr(self, name, getattr(self.repr.fielddata, 'mike_%s' % name))

    def get_preprocessing_data(self):
        """Read the preprocessing data.
        """
        self.db = db.SharedDB()
        if not hasattr(self.db.root, 'has_key'):
            self.db.root = self.db.root.__Broken_state__['_container']
        if 'preprocessingData' not in self.db.root:
            print('No preprocessing data found')
            print('Please do pre processing first')
            raise SystemExit(1)
        pre = self.db.root['preprocessingData']
        mst_lake = pre['mstLake']
        self.pcg_boundry = mst_lake.PCGBoundry
        self.w2_array_shape = self.config.w2.get_shared_data('b').shape

    def make_modmst_index(self):
        """Create indices for mapping between lake and MODMST.
        """
        self.modmst_river_index_dict = {}
        n_row = self.find_n_row()
        for n in range(self.nlake):
            layer = int(self.layer[n] - 1)
            row = n_row - int(self.row[n])
            column = int(self.column[n] - 1)
            if (column, row, layer) in self.modmst_river_index_dict:
                print('double assigment element at', (row, layer, column))
                input('...')
            self.modmst_river_index_dict[(column, row, layer)] = n
        for k in self.modmst_river_index_dict.keys():
            try:
                self.pcg_boundry[k]
            except KeyError:
                print('Element at layer %d, row %d, column %d' %
                       (k[2] + 1, n_row - k[1], k[0] + 1), end='')
                print('not in preprocessing data.')
                print('Please correct data --> new preprocessing.')
                sys.exit(1)
        for k in self.pcg_boundry:
            try:
                self.modmst_river_index_dict[k]
            except KeyError:
                print('Element at layer %d, row %d, column %d\nnot in %s.lak.'
                       % (k[2] + 1, n_row - k[1], k[0] + 1,
                          self.config.project_name))
                print('Please correct data --> new preprocessing.')
                sys.exit(1)

    def find_n_row(self):
        """Find number of rows.
        """
        fobj = file(os.path.join(self.config.modmst_path,
                              '%s.%s' % (self.config.project_name, 'bpi')))
        next(fobj)
        next(fobj)
        data = next(fobj).split()
        fobj.close()
        n_row = int(data[1])
        return n_row

    def make_mapping(self):
        """Map MODMST and lake cells.
        """
        self.make_modmst_index()
        self.modmst_mapping = {}
        self.w2_mapping = {}
        for k, value in self.pcg_boundry.items():
            area_sum = 0.0
            w2_coords = {}
            for w2_item in value:
                w2_coords[(w2_item['nColumn'] + 1,
                           w2_item['nLevel'] + 1)] = w2_item['area']
                area_sum += w2_item['area']
            for key, value in w2_coords.items():
                w2_coords[key] = value / area_sum
            self.modmst_mapping[k] = w2_coords
        for k, value in self.pcg_boundry.items():
            for w2_item in value:
                coord = (w2_item['nColumn'] + 1, w2_item['nLevel'] + 1)
                area = w2_item['area']
                if coord in self.w2_mapping:
                    self.w2_mapping[coord].append([k, area])
                else:
                    self.w2_mapping[coord] = [[k, area]]
        for k, value in self.w2_mapping.items():
            area_sum = 0.0
            for modmst_item in value:
                area_sum += modmst_item[1]
            n = 0
            for modmst_item in value:
                self.w2_mapping[k][n][1] = modmst_item[1] / area_sum
                n += 1
        self.w2_mapping_dict = {}
        for k, value in self.w2_mapping.items():
            new_dict = {}
            for item in value:
                new_dict[item[0]] = item[1]
            self.w2_mapping_dict[k] = new_dict

    def exchange_modmst_to_w2(self):
        """Exchange MODMST --> W2.
        """
        flow = -self.flow / 86400.0  # convert m3/d in m3/s
        temp = self.temperature
        if self.config.fixed_modmst_temperature != None:
            temp[:] = self.config.fixed_modmst_temperature
        q_in = numpy.where(numpy.greater(flow, 0.0), flow, 0.0)
        q_out = numpy.where(numpy.less(flow, 0.0), flow, 0.0)
        self.total_q_in += numpy.sum(q_in) * self.dt * 86400.0 * 1e3
        self.total_q_out += numpy.sum(q_out) * self.dt * 86400.0 * 1e3
        self.modmst_q_out = copy.deepcopy(q_out)
        qss_gw, _ = self.modmst_to_w2_array_q(flow)
        gw_in, _ = self.modmst_to_w2_array_q(q_in)
        gw_out, self.out_back_map = self.modmst_to_w2_array_q(q_out)
        self.gw_out = gw_out
        diff_in = numpy.sum(gw_in) * self.dt * 86400 * 1e3
        self.total_w2_q_in += diff_in
        self.total_w2_q_out += numpy.sum(gw_out) * self.dt * 86400 * 1e3
        self.w2_q_out_original = copy.deepcopy(gw_out)
        species_mass_per_time = {}
        if self.config.modmst_debug_output:
            self.debug_from_modmst.write('%15.10f' % self.total_time)
            self.debug_from_modmst.write('%15.10f' % (sum(q_in)))
        for name in self.conc_names:
            if self.config.fixed_modmst_conc:
                conc = self.config.fixed_modmst_conc[name]
            else:
                conc = self.__dict__[name]
                if self.config.modmst_conc_unmodified:
                    self.old_modmst_conc[name] = conc
            species_mass_per_time[name] = \
                self.modmst_to_w2_array_conc_temp(conc, q_in)
            if self.config.modmst_debug_output:
                flux = sum(conc * q_in)
                self.debug_from_modmst.write('%15.10f' % flux)
        if self.config.modmst_debug_output:
            self.debug_from_modmst.write('\n')
            self.debug_from_modmst.flush()
        gw_heat = self.modmst_to_w2_array_conc_temp(temp, q_in)
        adjust = self.active_cell_adjuster.adjust_non_active_cells
        (flow, gw_in, self.w2_q_out, gw_heat, species_mass_per_time,
         self.dry_cells_out) = adjust(qss_gw, gw_in, gw_out, gw_heat,
                                    species_mass_per_time)
       # intermediate step to prevent division by zero in next line
        gw_in_temp = numpy.where(gw_in == 0.0, -9999, gw_in)
        gw_temp = numpy.where(gw_in_temp == -9999, 0.0, gw_heat / gw_in_temp)
        self.config.w2.set_shared_array_data('qgw', qss_gw)
        self.config.w2.set_shared_array_data('qgwin', gw_in)
        self.config.w2.set_shared_array_data('qgwout', gw_out)
        self.config.w2.add_ssgw = 1
        for k, value in species_mass_per_time.items():
            print(k, numpy.min(value), numpy.max(value))
            self.config.w2.set_shared_array_data(k.lower() + 'ssgw', value)
        self.config.w2.set_shared_array_data('tgw', gw_temp)

    def modmst_to_w2_array_q(self, modmst_array):
        """Convert a modmst array to a w2 array.
        """
        w2_array = numpy.zeros(self.w2_array_shape, float)
        back_map = {}
        for k, value in self.w2_mapping.items():
            for modmst_item in value:
                modmst_coord = self.modmst_river_index_dict[modmst_item[0]]
                modmst_value = modmst_array[modmst_coord]
                modmst_share = self.modmst_mapping[modmst_item[0]][k]
                value = modmst_value * modmst_share
                x = k[0]
                z = k[1]
                w2_array[z, x] = w2_array[z, x] + value
                try:
                    back_map[modmst_coord].append(((z, x), value))
                except KeyError:
                    back_map[modmst_coord] = [((z, x), value)]
        return w2_array, back_map

    def modmst_to_w2_array_conc_temp(self, modmst_array, q_in):
        """Convert concentration and temperature arrays from modmst to w2.
        """
        w2_array = numpy.zeros(self.w2_array_shape, float)
        for k, value in self.w2_mapping.items():
            for modmst_item in value:
                modmst_coord = self.modmst_river_index_dict[modmst_item[0]]
                modmst_value = modmst_array[modmst_coord]
                q_value = q_in[modmst_coord]
                x = k[0]
                z = k[1]
                share = self.modmst_mapping[modmst_item[0]][k] * q_value
                w2_array[z, x] = w2_array[z, x] + modmst_value * share
        return w2_array

    def exchange_w2_to_modmst(self):
        """Exchange W2 --> MODMST.
        """
        if self.config.fixed_modmst_water_table:
            water_table = self.config.fixed_modmst_water_table
        else:
            water_table = self.config.w2.mean_level
        print(72 * '#')
        print('lake water table', water_table)
        self.water_table = water_table.astype(float)
        lake_temperature = self.config.w2.get_shared_data('tlake')
        modmst_lake_temperature = self.w2_to_modmst_array(lake_temperature)
        if self.config.fixed_modmst_temperature != None:
            modmst_lake_temperature[:] = self.config.fixed_modmst_temperature
        self.temperature[:] = modmst_lake_temperature.astype(float)
        if self.config.modmst_lake_density:
            density = self.config.w2.get_shared_data('rho')
            self.hactive = self.config.w2.get_shared_data('hactive')
            depth_density = self.make_depth_density(density)
            modmst_lake_density = self.w2_to_modmst_array(depth_density)
            self.density = modmst_lake_density.astype(float)
        if self.config.modmst_debug_output:
            self.debug_to_modmst.write('%15.10f' % self.total_time)
            self.debug_to_modmst.write('%15.10f' % (sum(self.modmst_q_out)))
        for name in self.conc_names:
            lake_conc = self.config.w2.get_shared_data(name.lower())
            if self.config.modmst_conc_unmodified:
                lake_conc = self.old_modmst_conc[name]
            self.__dict__[name][:] = self.w2_to_modmst_array(lake_conc)
            if self.config.modmst_debug_output:
                flux = sum(self.__dict__[name] * self.modmst_q_out)
                self.debug_to_modmst.write('%15.10f' % flux)
        if self.config.modmst_debug_output:
            self.debug_to_modmst.write('\n')
            self.debug_to_modmst.flush()

    def w2_to_modmst_array(self, w2_array):
        """Convert a w2 array to a modmst array.
        """
        modmst_array = numpy.zeros(self.modmst_q_out.shape, float)
        for k, value in self.modmst_mapping.items():
            modmst_coord = self.modmst_river_index_dict[k]
            modmst_q_out = self.modmst_q_out[modmst_coord]
            if modmst_q_out != 0.0:
                for w2_value in self.out_back_map[modmst_coord]:
                    x = w2_value[0][0]
                    z = w2_value[0][1]
                    try:
                        coord = self.dry_cells_out[(x, z)]
                        flow = w2_array[coord[0], coord[1]]
                    except KeyError:
                        flow = w2_array[x, z]
                    value = flow * w2_value[1]
                    modmst_array[modmst_coord] = \
                        modmst_array[modmst_coord] + value
                modmst_array[modmst_coord] = \
                    modmst_array[modmst_coord] / modmst_q_out
        return modmst_array

    def next(self):
        """Next tiem step.
        """
        if not self.first:
            os.chdir(self.config.modmst_path)
            self.exchange_w2_to_modmst()
        else:
            self.first = False
        done = self.repr.mike_next()
        self.exchange_modmst_to_w2()
        self.dt = self.repr.fielddata.mike_dt
        self.total_time = self.repr.fielddata.mike_totim
        return done

    def make_depth_density(self, density):
        """Calculate the product of depth and density.
        """
        depth_density = numpy.zeros(density.shape, float)
        for column in range(density.shape[0]):
            for layer in range(density.shape[1]):
                if self.hactive[column, layer]:
                    total_heights = 0.0
                    total_density_heights_product = 0.0
                    for layer_above in range(layer + 1):
                        if self.hactive[column, layer_above]:
                            total_heights += self.hactive[column, layer_above]
                            total_density_heights_product += (
                                density[column, layer_above] *
                                self.hactive[column, layer_above])
                    depth_density[column, layer] = \
                        total_density_heights_product / total_heights
        return depth_density

if __name__ == '__main__':

    def test():
        """Test if it works.
        """
        m = Modmst()
        m.getConc()
        done = 0
        while not done:
            done = next(m)
            print('done', done)
            m.getConc()
