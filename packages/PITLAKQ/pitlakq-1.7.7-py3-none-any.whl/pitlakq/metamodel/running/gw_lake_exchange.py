"""
Exchange between lake and groundwater.
"""

# THE NumPy problem.
# pylint: disable-msg=E1101
# Many attributes defined outside __init__.
# pylint: disable-msg=W0201

from __future__ import print_function

import copy
import cmath
import os

import BTrees.OOBTree as OOBTree
import numpy
import netCDF4
import transaction

import pitlakq.commontools.dbftools.flatdbf.flatdbf as flatdbf
import pitlakq.preprocessing.obswells as obswells
import pitlakq.metamodel.running.db as db


class GwLakeExchange:
    """Groundwater and lake exchange.
    """

    def __init__(self, config, exchange_species, gw):
        self.config = config
        self.exchange_species = exchange_species
        self.gw = gw
        self.deepest_segment = self.config.deepest_segment
        self.netcdf_file_name = self.config.nc_file_fame
        self.db = db.SharedDB()
        self.get_preprocessing_data()
        self.down_correcter_float = 6.0
        self.total_mass = 0.0
        self.first = 1
        self.outflow_column = self.deepest_segment
        self.outflow_row = 1
        self.lake_outflow = 0.0
        self.init_db()
        self.get_lake_bottom()
        if self.config.use_fixed_gw_conc:
            self.make_fixed_conc()
            self.zoned_q = {}
        self.gw_in_flag = False
        if self.config.reduced:
            self.init_reduced()

    def init_reduced(self):
        """Initialize reduced gw inflows.
        """
        self.reduced_conc = {}
        self.reduced_qs = {}

    def make_fixed_conc(self):
        """Create constant concentrations.
        """
        assoc = obswells.ObsWellAssociator(self.config,
                                           self.config.association_dict)
        self.conc_of_obs = assoc.wells
        fixed_obs_3d = assoc.associatedObs
        x_range = range(fixed_obs_3d.shape[0])
        y_range = range(fixed_obs_3d.shape[1])
        z_range = range(fixed_obs_3d.shape[2])
        self.fixed_obs = numpy.zeros(fixed_obs_3d.shape).ravel()
        n = 0
        for x in x_range:
            for y in y_range:
                for z in z_range:
                    self.fixed_obs[n] = fixed_obs_3d[x, y, z]
                    n += 1
        self.db.root['saved_gw_obs_conc'] = self.fixed_obs
        transaction.commit()

    def init_db(self):
        """Initialize ZODB.
        """

        if 'saved_gw_q' not in self.db.root or self.config.save_gw_q:
            self.db.root['saved_gw_q'] = OOBTree.OOBTree()
            self.db.root['saved_gw_q_in'] = OOBTree.OOBTree()
            self.db.root['saved_gw_q_out'] = OOBTree.OOBTree()
        if 'saved_1d_gw_q' not in self.db.root or self.config.save_gw_q:
            self.db.root['saved_1d_gw_q'] = OOBTree.OOBTree()
        if ('saved_lake_level' not in self.db.root or
            self.config.save_gw_q):
            self.db.root['saved_lake_level'] = OOBTree.OOBTree()
        if ('saved_lake_outflow' not in self.db.root or
            self.config.save_gw_q):
            self.db.root['saved_lake_outflow'] = OOBTree.OOBTree()
        if ('saved_zoned_q_in' not in self.db.root or
            self.config.save_gw_q):
            self.db.root['saved_zoned_q_in'] = OOBTree.OOBTree()
        if ('saved_zoned_q_out' not in self.db.root or
            self.config.save_gw_q):
            self.db.root['saved_zoned_q_out'] = OOBTree.OOBTree()
        if self.config.use_fixed_gw_conc:
            self.db.root['saved_gw_obs_conc'] = OOBTree.OOBTree()
        if self.config.save_reduced:
            for name in ['reduced_gw_q',
                         'reduced_q_gw_in',
                         'reduced_q_gw_out',
                         'reduced_gw_mass_per_time',
                         'reduced_erosion_moles']:
                self.db.root[name] = OOBTree.OOBTree()
        transaction.commit()

    def get_preprocessing_data(self):
        """Read preprocessing data from ZODB
        """
        if 'preprocessing_data' not in self.db.root:
            print('No preprocessing data found')
            print('Please do pre processing first')
            raise SystemExit
        pre = self.db.root['preprocessing_data']
        pre_lake = pre['pcg_lake']
        self.pcg_boundry = pre_lake.pcg_boundry
        self.pcg_boundry_total = pre_lake.pcg_boundry_total
        self.old_lake_level = self.db.root['initial_water_surface']

    def make_mapping(self):
        """Create association between pcg and w2 elements.
        """
        for name in self.gw.pcg_names.keys():
            if self.gw.pcg_names[name]['qw']:
                self.pcg_qw = name
            if self.gw.pcg_names[name]['h']:
                self.pcg_h = name
        self.qw_pcg = self.gw.pcgs[self.pcg_qw]
        self.h_pcg = self.gw.pcgs[self.pcg_h]
        self.qw_pcg.read_binary_output()
        self.mapping = {}
        self.w2_mapping = {}
        for index in range(len(self.qw_pcg.pcg_bin.m)):
            key = self.one2three(index)
            if key in self.pcg_boundry:
                self.mapping[index] = self.pcg_boundry[key]
                for item in self.pcg_boundry[key]:
                    try:
                        self.w2_mapping[(item['n_column'],
                                         item['n_level'])].append((index,
                                                            item['area']))
                    except KeyError:
                        self.w2_mapping[(item['n_column'],
                                         item['n_level'])] = [(index,
                                                               item['area'])]
        self.w2_area_sum = {}
        for key in self.w2_mapping.keys():
            self.w2_area_sum[key] = 0.0
            for item in self.w2_mapping[key]:
                self.w2_area_sum[key] += item[1]

    def get_pcg_geometry(self):
        """Read geometry data from pcg_bin.
        """
        self.area = self.h_pcg.pcg_bin.delta_x * self.h_pcg.pcg_bin.delta_y
        self.delta_z = self.h_pcg.pcg_bin.delta_z
        self.zu = self.h_pcg.pcg_bin.zu
        self.kf = self.h_pcg.pcg_bin.kf
        #if ne and ns are in dbf file --> must be read from there
        self.ne = numpy.maximum(0.001, 0.4 + 0.05 * numpy.log10(self.kf))
        self.ns = numpy.maximum(0, numpy.minimum(0.6, -0.2 - 0.1 *
                                                 numpy.log10(self.kf)))

    def get_active(self, lake_level):
        """Find the active W2 cells.
        """
        fobj = netCDF4.Dataset(self.netcdf_file_name, 'r', format='NETCDF3_CLASSIC')
        self.v_active = fobj.variables['vactive'][:]#[1:-1,1:-1]
        h_active = fobj.variables['hactive'][1:-1, 1:-1]
        fobj.close()
        self.active = numpy.zeros(h_active.shape)
        m = 0
        for column in h_active:
            level = self.lake_bottom
            n = len(column) - 1
            for row in column[-1::-1]: #reverse
                level += row
                if (level > self.lake_bottom and level <= lake_level and
                    h_active[m, n]):
                    self.active[m, n] = 1
                else:
                    pass
                n -= 1
            m += 1

    def get_lake_bottom(self):
        """Find the lake bottom height.
        """
        fobj = netCDF4.Dataset(self.config.pre_w2_input_file_name, 'r', format='NETCDF3_CLASSIC')
        self.lake_bottom = fobj.variables['waterbody_coordinates'][2]
        fobj.close()

    def make_area_sum(self):
        """Calculate the sum of all mapped elements.
        """
        for index in self.mapping.keys():
            sum_ = 0
            for element in self.mapping[index]:
                sum_ += element['area']
            self.mapping[index].append({'area_sum': sum_})

    def get_min_pcg_level(self, date):
        """Find the lake levl from PCG.
        """
        if not self.first:
            if self.config.use_saved_gw_q:
                self.new_lake_level = self.db.root['saved_lake_level'][date]
                self.lake_outflow = self.db.root['saved_lake_outflow'][date]
            else:
                date_string = 'wa%d%2d.%2d' % date.tuple()[:3]
                self.new_lake_level_file = os.path.join(
                    self.config.pcgWaResultPath, date_string.replace(' ', '0'))
                fobj = open(self.new_lake_level_file)
                data = fobj.readlines()
                fobj.close()
                line = data[4].split()
                self.new_lake_level = float(line[2])
                if len(line) > 6:
                    self.lake_outflow = float(line[6])/60 # m3/min -> m3/s
                else:
                    self.lake_outflow = 0.0
            result = min(self.old_lake_level, self.new_lake_level)
            self.old_lake_level = self.new_lake_level
            return result
        if self.config.restart:
            if self.config.use_saved_gw_q:
                self.new_lake_level = self.db.root['saved_lake_level'][date]
                self.lake_outflow = self.db.root['saved_lake_outflow'][date]
        self.first = False
        self.new_lake_level = self.old_lake_level #?
        return self.old_lake_level

    def make_new_mapping(self, date):
        """
        All w2-elements that don't have water,
        i.e. active == 0 need to redirected to next
        active > 0.
        Look down first than left and right.
        """
        min_lake_level = self.get_min_pcg_level(date)
        self.get_active(min_lake_level)
        if not self.config.reduced:
            self.down_correcter_float -= 0.1
            self.down_correcter = int(self.down_correcter_float)
            if self.down_correcter < 0:
                self.down_correcter = 0
            #number_of_columns = self.active.shape[0]
            number_of_levels = self.active.shape[1]
            self.new_mapping = copy.deepcopy(self.mapping)
            for index in self.mapping.keys():
                if self.qw_pcg.pcg_bin.vectors['qw']['vector'][index] != 0.0:
                    n = 0
                    for element in self.mapping[index][:-1]:
                        sideways = 0
                        if not self.active[element['n_column'],
                                           element['n_level']]:
                            down = 1
                            while down < number_of_levels-n-1:
                                try:
                                    if self.active[element['n_column']+
                                        sideways, element['n_level']+down]:
                                        self.new_mapping[index][n]['n_level'] \
                            = self.new_mapping[index][n]['n_level'] + down
                                        self.new_mapping[index][n]['n_column']\
                            = self.new_mapping[index][n]['n_column']+ sideways
                                        break
                                except IndexError:
                                    if (element['n_column'] >=
                                        self.deepest_segment):
                                        sideways -= 1
                                    else:
                                        sideways += 1
                                    down = 1
                                down += 1
                        n += 1

    def one2three(self, index):
        """Convert 1D to 3D array.
        """
        return (self.qw_pcg.pcg_bin.m[index] - 1,
                self.qw_pcg.pcg_bin.n[index] - 1,
                self.qw_pcg.pcg_bin.l[index] - 1)

    def make_three2one(self):
        """Convert 3D to 1D array.
        """
        self.three2one = {}
        for index in range(len(self.qw_pcg.pcg_bin.m)):
            self.three2one[(self.qw_pcg.pcg_bin.m[index]-1,
                            self.qw_pcg.pcg_bin.n[index]-1,
                            self.qw_pcg.pcg_bin.l[index]-1)] = index

    def put_q(self, date=None):
        """
        Putting flow from PCG into W2.
        """
        fobj = netCDF4.Dataset(self.netcdf_file_name, 'r+', format='NETCDF3_CLASSIC')
        self.gwqss = fobj.variables['gwqss']
        self.gwq_in = fobj.variables['gwqin']
        self.gwq_out = fobj.variables['gwqout']
        self.gwqss_from_w2 = self.gwqss[:, :]
        self.gwqss[:, :] = 0.0
        self.gwq_in[:, :] = 0.0
        self.gwq_out[:, :] = 0.0
        indices = []
        #check = 0
        self.outflow_row = 0
        while self.v_active[self.outflow_column, self.outflow_row] < 1e-3:
            self.outflow_row += 1
        self.inflow_row = self.outflow_row +1
        if self.config.reduced:
            saved_gw_q_out = self.db.root['reduced_q_gw_out'][date]
            saved_gw_q_in = self.db.root['reduced_q_gw_in'][date]
            self.gwq_out[self.outflow_column, self.outflow_row] = (
                self.gwq_out[self.outflow_column, self.outflow_row] +
                self.reduced_qs.get('Qout', 0.0) + saved_gw_q_out)
            self.gwq_in[self.outflow_column, self.inflow_row] = (
                self.gwq_out[self.outflow_column, self.inflow_row] +
                self.reduced_qs.get('Qin', 0.0) + saved_gw_q_in)
            self.gwqss[self.outflow_column, self.outflow_row] = (
                self.gwqss[self.outflow_column, self.outflow_row]
                - self.reduced_qs.get('Qout', 0.0) - saved_gw_q_out)
            self.gwqss[self.outflow_column, self.inflow_row] = (
                self.gwqss[self.outflow_column, self.inflow_row]
                + self.reduced_qs.get('Qin', 0.0) + saved_gw_q_in)
        else:
            if self.config.use_saved_gw_q:
                self.gwqss[:] = self.db.root['saved_gw_q'][date]
                self.gwq_in[:] = self.db.root['saved_gw_q_in'][date]
                self.gwq_out[:] = self.db.root['saved_gw_q_out'][date]
                self.q_1d = self.db.root['saved_1d_gw_q'][date]
            else:
                self.q_1d = []
                for index in self.new_mapping.keys():
                    flow = -self.qw_pcg.pcg_bin.vectors['qw']['vector'][index]
                    self.q_1d.append(flow)
                    indices.append(index)
                    for element in self.new_mapping[index][:-1]:
                        self.gwqss[element['n_column'] + 1,
                                   element['n_level'] + 1] = (
                                       self.gwqss[element['n_column']+1,
                                                  element['n_level']+1] +
                                       flow * element['area'] /
                                       self.new_mapping[index][-1]['areaSum'])
                        if flow >= 0.0:
                            self.gwq_in[element['n_column'] + 1,
                                        element['n_level'] + 1] = (
                                            self.gwq_in[element['n_column']+1,
                                                        element['n_level']+1] +
                                            flow*element['area'] /
                                        self.new_mapping[index][-1]['areaSum'])
                        else:
                            self.gwq_out[element['n_column'] + 1,
                                         element['n_level'] + 1] = (
                                             self.gwq_out[
                                                 element['n_column'] + 1,
                                                 element['n_level']+1] -
                                             flow*element['area'] /
                                        self.new_mapping[index][-1]['areaSum'])
                    #check += flow
            if self.config.save_gw_q:
                self.db.root['saved_gw_q'][date] = self.gwqss[:]
                self.db.root['saved_gw_q_in'][date] = self.gwq_in[:]
                self.db.root['saved_gw_q_out'][date] = self.gwq_out[:]
                self.db.root['saved_lake_level'][date] = self.new_lake_level
                self.db.root['saved_1d_gw_q'][date] = self.q_1d
                self.db.root['saved_lake_outflow'][date] = self.lake_outflow
                transaction.commit()
            if self.config.save_reduced:
                self.db.root['reduced_gw_q'][date] = numpy.sum(self.gwqss[:])
                self.db.root['reduced_q_gw_in'][date] = numpy.sum(
                    self.gwq_in[:])
                self.db.root['reduced_q_gw_out'][date] = numpy.sum(
                    self.gwq_out[:])
                transaction.commit()
            #self.outflow_row += 3 # 4th layer below water table
            # substracting lake_outflow due to Ueberleitung bae --> uab
            self.gwq_out[self.outflow_column, self.outflow_row] = (
                self.gwq_out[self.outflow_column, self.outflow_row] +
                self.lake_outflow)
            self.gwqss[self.outflow_column, self.outflow_row] = (
                self.gwqss[self.outflow_column, self.outflow_row] -
                self.lake_outflow)
        fobj.close()

    def put_conc(self, date):
        """
        Conc from PCG in W2.
        Units !
        W2 in mg/l
        Porosity, PHREEQC in mmol/l
        """
        if not self.config.reduced:
            self.gw.read_binary_output()
        fobj = netCDF4.Dataset(self.netcdf_file_name, 'r+', format='NETCDF3_CLASSIC')
        #v_active = fobj.variables['vactive']
        self.ssgw = {}
        self.zoned_q_in = {}
        self.zoned_q_out = {}
        #total_q = 0
        zone = None
        for zone in self.conc_of_obs.keys():
            self.zoned_q_in[zone] = 0.0
            self.zoned_q_out[zone] = 0.0
        if self.config.reduced:
            for name in self.exchange_species.keys():
                specie_ssgw = fobj.variables[name + 'ssgw']
                specie_ssgw[:] = 0.0
                #specie_conc = fobj.variables[name]
                specie_ssgw[self.outflow_column, self.inflow_row] = (
                    specie_ssgw[self.outflow_column, self.inflow_row] +
                    self.db.root['reduced_gw_mass_per_time'][date][name])
                if name in self.reduced_conc:
                    specie_ssgw[self.outflow_column, self.inflow_row] = (
                        specie_ssgw[self.outflow_column, self.inflow_row] +
                        self.reduced_conc.get(name, 0.0) *
                        self.reduced_qs.get('Qin', 0.0))
                    specie_ssgw[self.outflow_column, self.outflow_row] = (
                        specie_ssgw[self.outflow_column, self.outflow_row] +
                        self.reduced_conc.get(name, 0.0) *
                        self.reduced_qs.get('Qout', 0.0))
        else:
            n = 0
            for index in self.new_mapping.keys():
                flow = self.q_1d[n]
                if flow > 0:
                    if self.config.use_fixed_gw_conc:
                        zone = self.fixed_obs[index]
                        self.zoned_q_in[zone] += flow
                    #total_q += flow
                    for name in self.exchange_species.keys():
                        specie_ssgw = fobj.variables[name + 'ssgw']
                        # delta_t form W2 is used
                        mass_per_time = numpy.zeros(
                            (specie_ssgw.shape[0], specie_ssgw.shape[1]),
                            numpy.Float64)
                        if self.config.use_fixed_gw_conc:
                            conc = self.conc_of_obs[zone][name]
                        else:
                            vectors = self.gw.pcgs[
                                self.exchange_species[name][0]].pcg_bin.vectors
                            conc = vectors[self.exchange_species[name][1]
                                           ]['vector'][index] * 1000
                        for element in self.new_mapping[index][:-1]:
                            mpt = (mass_per_time[element['n_column'] + 1,
                                                 element['n_level']+1] +
                                   conc * flow*element['area'] /
                                   self.new_mapping[index][-1]['areaSum'])
                            mass_per_time[element['n_column'] + 1,
                                          element['n_level'] + 1] = mpt
                        specie_ssgw[:, :] = mass_per_time
                else:
                    if self.config.use_fixed_gw_conc:
                        self.zoned_q_out[zone] += flow
                    #total_q += flow
                n += 1
            if self.config.save_reduced:
                self.db.root['reduced_gw_mass_per_time'
                             ][date] = OOBTree.OOBTree()
                for name in self.exchange_species.keys():
                    specie_ssgw = fobj.variables[name + 'ssgw']
                    self.db.root['reduced_gw_mass_per_time'][date][name] = \
                                                    sum(sum(specie_ssgw))
                transaction.commit()
        fobj.close()
        if self.config.save_gw_q:
            self.db.root['saved_zoned_q_in'][date] = self.zoned_q_in
            self.db.root['saved_zoned_q_out'][date] = self.zoned_q_out
            transaction.commit()

    def get_conc(self, delta_t):
        """
        Get concentration from W2 to be placed in PCG as BC (rabe)
        attention. Only ONE spezies is implemented for 'pcg3' needs
        to be changed --> self.config.pcg_rabe_file is hardwired in
        configuation.py change this.
        Find out if five 5 or 15 species are in rabe_file....
        """
        self.gw.read_binary_output()
        fobj = netCDF4.Dataset(self.netcdf_file_name, 'r+', format='NETCDF3_CLASSIC')
        for name in self.exchange_species.keys():
            specie_ssgw = self.ssgw[name]
            #specie = fobj.variables[name][:, :]
            total_pcg = 0
            #total_w2 = 0
            pcg_mass = {}
            for w2_key in self.w2_mapping.keys():
                for item in self.w2_mapping[w2_key]:
                    index = item[0]
                    area = item[1]
                    mass_w2 = (-specie_ssgw[w2_key[0] + 1,
                                            w2_key[1]+1] * area /
                               self.w2_area_sum[w2_key])
                    #total_w2 += mass_w2
                    try:
                        pcg_mass[index] += mass_w2 / 1000.0
                    except KeyError:
                        pcg_mass[index] = mass_w2 / 1000.0
            for index in self.mapping.keys():
                total_pcg += pcg_mass[index]
        self.total_mass += total_pcg
        dbf = flatdbf.Dbf(self.config.pcg_rabe_file)
        dbf.list = dbf.list[:self.rbs_pos]
        for key in self.pcg_boundry_total.keys():
            index = self.three2one[(key[0], key[1], key[2])]
            mass_man, mass_exp = self.split_exp(pcg_mass[index]/delta_t)
            if mass_man > 0:
                flow = 1.0
            else:
                flow = 0.0
            dbf.list.append(['rbs', 0, key[0]+1, key[1]+1, key[2]+1,
                             '19900101', 0, '', flow, #earliest possible date
                             mass_man, mass_exp,
                             0.0, 0, 0.0, 0, 0.0, 0, 0.0, 0])
        dbf.write()
        fobj.close()

    @staticmethod
    def split_exp(value):
        """Splitting decimal in mantisse and exponet."""
        if value <= 0.0:
            man = 0.0
            exp = 0
        elif value < 1.0:
            exp = int((cmath.log10(value).real) - 1)
            man = 10 ** (abs((exp)+abs(cmath.log10(value))))
            if man == 10.0:
                man = man/10
                exp = exp + 1
            if exp < -9:
                man = 0.0
                exp = 0
        else:
            split_value = ('%e' % value).split('e')
            man = float(split_value[0])
            exp = int(split_value[1])
        return man, exp

    def get_rabe_info(self):
        """Find position of boundary condition.
        """
        dbf = flatdbf.Dbf(self.config.pcg_rabe_file)
        n = 0
        for line in dbf.list:
            if line[0] == 'rbs':
                n += 1
        self.rbs_pos = len(dbf.list) - n

    def make_bottom(self):
        """
        Making dict with index as key and
        bottom (SOHLE) as value from pcg
        preprocessing data.
        """
        self.bottom = {}
        self.pcg_area_part = {}
        for index in range(len(self.qw_pcg.pcg_bin.m)):
            key = self.one2three(index)
            if key in self.pcg_boundry_total.has_key:
                self.bottom[index] = self.pcg_boundry_total[key][1]
                self.pcg_area_part[index] = (self.pcg_boundry_total[key][0] /
                                             self.area[index])


if __name__ == '__main__':

    def test():
        """Small test.
        """
        ex = GwLakeExchange()
        for key in ex.pcg_boundry.keys():
            print(key, ex.pcg_boundry[key])

    test()
