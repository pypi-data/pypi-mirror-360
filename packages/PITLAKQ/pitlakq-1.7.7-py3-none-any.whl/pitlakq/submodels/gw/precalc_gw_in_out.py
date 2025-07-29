"""Use gw exchange data for the lake from previous gw model run.

We run the gw model only ones and save the exchange data.
Then we can just use these data over and over again.
This assumes that there is not concentration feedback
from the lake to the gw.
"""

# NumPy, dynamic members.
# pylint: disable-msg=E1101
# Many attributes defined outside __init__.
# pylint: disable-msg=W0201

from __future__ import print_function

import datetime
import os
import sys

import numpy
import netCDF4

import pitlakq.preprocessing.obswells as obswells
import precalc_gw


class PrecalcGwInOut(object):
    """Read the precomputed gw data.
    """

    def __init__(self,
                 config,
                 q_file_name,
                 key_file_name,
                 distribution_file_name,
                 exchange_species):
        self.config = config
        self.w2 = self.config.w2
        self.w2.set_shared_data('gw_coupling', True)
        self.pre = precalc_gw.PrecalculatedGwQ(q_file_name)
        self.pre.process_input()
        self.key_file_name = key_file_name
        self.distribution_file_name = distribution_file_name
        self.exchange_species = exchange_species
        self.exchange_species = ['tra', 'po4', 'nh4', 'no3', 'dox', 'tic',
                                 'fe', 'al', 'so4', 'ca', 'mg', 'na', 'ka',
                                 'mn', 'cl']
        self.extra_layer = 1
        self.inactive_ids = {1: 1, 8: 8, 31: 31, 75: 75}
        self.get_cell_width()
        self.zero_q_in = {}
        self.zero_q_out = {}
        self.read_keys()
        self.read_distribution()
        self.check_distribution()
        self.match()
        self.read_conc()
        self.match_conc()
        self.date_index = 0
        if self.config.time_dependent_precalc_gw_conc:
            self.read_pore_volumes()
            self.read_time_dependent_conc()
        self.old_date = self.config.w2.date

    def get_cell_width(self):
        """Read the cell width from the batyhmetry file.
        """
        nc_file = netCDF4.Dataset(self.config.bathymetry_file_name, 'r',
                                  format='NETCDF3_CLASSIC')
        self.cell_width = numpy.transpose(nc_file.variables['cell_width'][:])
        nc_file.close()

    def read_keys(self):
        """Read keys for finding regions in VM file.
        """
        key_file = open(self.key_file_name)
        data = [line.split() for line in key_file]
        key_file.close()
        self.ids = {}
        for line in data:
            if len(line) > 1:
                try:
                    self.ids[int(line[0])] = line[1]
                except ValueError:
                    pass

    def read_distribution(self):
        """Read distribution from VM file.
        """
        d_file = open(self.distribution_file_name, 'r')
        orig_data = d_file.readlines()
        d_file.close()
        n = 0
        if sys.platform != 'win32':
            for line in orig_data:
                orig_data[n] = orig_data[n][:-2] + '\n' #win32 file
            n += 1
        columns = int(orig_data[1])
        rows = int(orig_data[2])
        distribution = numpy.zeros((rows, columns))
        number_of_properties = int(orig_data[3])
        start_line = 4 + number_of_properties + 1
        row = 0
        col = 0
        for line in orig_data[start_line:start_line + rows]:
            for value in line.split():
                distribution[row, col] = int(value)
                col += 1
            row += 1
            col = 0
        distribution = numpy.transpose(distribution)
        if self.extra_layer:
            #if layer was added that is not in distrubtion input file
            #8 means inactive
            self.distribution = numpy.zeros((distribution.shape[0],
                                             distribution.shape[1] + 1)) + 8
            self.distribution[:, :-1] = distribution
        else:
            self.distribution = distribution
        flat_dist = numpy.ravel(self.distribution)
        self.number_of_ids = {}
        for id_ in self.ids:
            self.number_of_ids[id_] = sum(numpy.where(flat_dist==id_, 1, 0))
        self.qss_gw = numpy.zeros(self.distribution.shape, numpy.float64)
        self.gw_in = numpy.zeros(self.distribution.shape, numpy.float64)
        self.gw_out = numpy.zeros(self.distribution.shape, numpy.float64)
        self.id_distribution = {}
        for n in range(self.distribution.shape[0]):
            for m in range(self.distribution.shape[1]):
                id_ = self.distribution[n, m]
                if id_ in self.id_distribution:
                    self.id_distribution[id_].append((n, m))
                else:
                    self.id_distribution[id_] = [(n, m)]
        self.reverse_ids = {}
        for id_, zone in self.ids.items():
            self.reverse_ids[zone] = id_

    def check_distribution(self):
        """Check if the distribution is correct.
        """
        error = False
        first = True
        for x in range(self.cell_width.shape[0]):
            for z in range(self.cell_width.shape[1]):
                if self.distribution[x, z] and not self.cell_width[x, z]:
                    if self.distribution[x, z] != 8:
                        if first:
                            print('%10s%10s%15s' % ('x', 'z', 'distribution'))
                            first = False
                            error = True
                        print('%10d%10d%15d' % (x, z, self.distribution[x, z]))
        if error:
            raise ValueError('distribution at zero width')

    def match(self):
        """Match the ids with the values.
        """
        self.dates = self.pre.dates
        self.q_ins = {}
        self.q_outs = {}
        self.all_qs = {}
        for id_ in self.ids:
            try:
                q_in = self.pre.q_ins[self.ids[id_]]
                if numpy.any(q_in):
                    self.q_ins[id_] = q_in
                    self.all_qs[id_] = self.q_ins[id_]
                else:
                    self.zero_q_in[id_] = id_
            except KeyError:
                q_out = self.pre.q_outs[self.ids[id_]]
                if numpy.any(q_out):
                    self.q_outs[id_] = q_out
                    self.all_qs[id_] = - self.q_outs[id_]
                else:
                    self.zero_q_out[id_] = id_
        self.check_q_correspondence()

    def check_q_correspondence(self):
        """Check if all qs have distribution an ID.
        """
        missing_q_ins = []
        for id_ in self.pre.q_ins.keys():
            if id_ not in self.reverse_ids:
                missing_q_ins.append(id_)
        if missing_q_ins:
            print()
            print('The following zones do NOT have a distribution key:')
            for zone in missing_q_ins:
                print(zone)
            raise ValueError('Please add the missing zones to %s'
                             % self.distribution_file_name)

    def read_pore_volumes(self):
        """Read the pore volumes from the input file.
        """
        fobj = open(self.config.pore_volumes_file_name)
        data = [x.split() for x in fobj.readlines()][1:]
        fobj.close()
        self.pore_volumes = {}
        for line in data:
            self.pore_volumes[self.reverse_ids[line[0]]] = float(line[1])

    def read_time_dependent_conc(self):
        """Read the time-dependent concentration values.
        """
        fobj = open(self.config.time_dependent_conc_file_name)
        data = [x.split() for x in fobj.readlines()][1:]
        fobj.close()
        conc_files = {}
        for line in data:
            if line[1] in conc_files:
                conc_files[line[1]].append(line[0])
            else:
                conc_files[line[1]] = [line[0]]
        self.time_dependent_conc = []
        self.time_dependent_ids = {}
        n = 0
        for file_name, zones in conc_files.items():
            full_file_name = os.path.join(
                os.path.dirname(self.config.time_dependent_conc_file_name),
                file_name)
            pore_volume, conc = self._read_single_conc(full_file_name)
            self.time_dependent_conc.append({'pore_volume_factor': pore_volume,
                                             'conc': conc,
                                             'current_pore_volume_pos': 0})
            for zone in zones:
                self.time_dependent_ids[self.reverse_ids[zone]] = n
            n += 1

    @staticmethod
    def _read_single_conc(file_name):
        """Read one concentration.
        """
        fobj = open(file_name)
        data = [line.split(';') for line in fobj]
        fobj.close()
        conc_lines = {}
        start = 3
        n = start
        for line in data[start:]:
            if line[2].strip() == 'Porenvolumen':
                pore_volume_pos = n
            conc_name = line[0].strip()
            if conc_name:
                conc_lines[conc_name] = n
            n += 1
        pore_volume = []
        conc = []
        for column in range(5, len(data[0])):
            pore_volume.append(float(data[pore_volume_pos][column]))
            current_conc = {}
            for name in conc_lines:
                current_conc[name] = float(data[conc_lines[name]][column])
            conc.append(current_conc)
        return pore_volume, conc

    def get_qs(self, date):
        """Read flow data.
        """
        if date >= self.dates[self.date_index]:
            while date > self.dates[self.date_index + 1]:
                self.date_index += 1
            self.date_index -= 1
            row_range = range(self.distribution.shape[1])
            column_range = range(self.distribution.shape[0])
            self.qss_gw[:] = 0.0
            self.gw_out[:] = 0.0
            self.gw_in[:] = 0.0
            for column in column_range:
                for row in row_range:
                    id_ = self.distribution[column, row]
                    if (id_ not in self.inactive_ids and
                        id_ not in self.zero_q_in and
                        id_ not in self.zero_q_out):
                        self.qss_gw[column, row] = (
                            self.all_qs[id_][self.date_index] /
                            self.number_of_ids[id_])
                        try:
                            self.gw_in[column, row] = (
                                self.q_ins[id_][self.date_index] /
                                self.number_of_ids[id_])
                        except KeyError:
                            self.gw_out[column, row] = (
                                self.q_outs[id_][self.date_index] /
                                self.number_of_ids[id_])
            self.date_index += 1
        if self.config.time_dependent_precalc_gw_conc:
            if hasattr(self, 'cumulative_pore_volumes'):
                delta_t = (date - self.old_date).seconds
                self.old_date = date
                # cumulative_pore_volumes will be defined because we check.
                # pylint: disable-msg=E0203
                for id_ in self.cumulative_pore_volumes.keys():
                    self.cumulative_pore_volumes[id_] += \
                        self.q_ins[id_][self.date_index] * delta_t
            else:
                start = self.config.start
                start_date = datetime.datetime(start[0], start[1], start[2])
                delta_t = (date - start_date).seconds
                self.old_date = date
                self.cumulative_pore_volumes = {}
                for id_ in self.id_distribution.keys():
                    if id_ in self.q_ins:
                        self.cumulative_pore_volumes[id_] = \
                            self.q_ins[id_][self.date_index] * delta_t
            self.set_time_dependent_conc()

    def set_time_dependent_conc(self):
        """Set the time-dependent concentration values.
        """
        ids = self.time_dependent_ids
        concs = self.time_dependent_conc
        for id_ in ids:
            pos = concs[ids[id_]]['current_pore_volume_pos']
            pore_volume_factor = concs[ids[id_]]['pore_volume_factor'][pos]
            while (pore_volume_factor * self.pore_volumes[id_] <
                   self.cumulative_pore_volumes[id_]):
                pos += 1
                pore_volume_factor = concs[ids[id_]]['pore_volume_factor'][pos]
            if pos == 0 or pos > concs[ids[id_]]['current_pore_volume_pos']:
                concs[ids[id_]]['current_pore_volume_pos'] = pos
                conc = concs[ids[id_]]['conc'][pos]
                for specie in self.exchange_species:
                    if specie in conc:
                        for x, z in self.id_distribution[id_]:
                            self.species_conc[specie][x, z] = conc[specie]

    def adjust_inactive_cells(self, date):
        """There are inactive cells that need special tretament.
        """
        if date >= self.dates[self.date_index]:
            row_range = range(self.distribution.shape[1])
            column_range = range(self.distribution.shape[0])
            self.find_next_active()
            adj = self.adjusted_species_conc = {}
            conc = self.species_conc
            old_masses = {}
            for specie in self.exchange_species:
                old_masses[specie] = numpy.sum(conc[specie] *
                                               self.gw_in)
                adj[specie] = numpy.zeros(self.qss_gw.shape, numpy.float64)
            new_qss_gw = numpy.zeros(self.qss_gw.shape, numpy.float64)
            new_gw_qout = numpy.zeros(self.gw_out.shape, numpy.float64)
            new_gw_in = numpy.zeros(self.gw_in.shape, numpy.float64)
            for column in column_range:
                for row in row_range:
                    active_x = self.active_x[column, row]
                    active_z = self.active_z[column, row]
                    if active_x != 0.0 and active_z != 0.0:
                        if (self.gw_in[column, row] or
                            new_gw_in[active_x, active_z]):
                            for specie in self.exchange_species:
                                in_flux = (self.gw_in[column, row] *
                                           conc[specie][column, row])
                                adj_flux = (new_gw_in[active_x, active_z] *
                                            adj[specie][active_x, active_z])
                                flow_sum = (self.gw_in[column, row] +
                                            new_gw_in[active_x, active_z])
                                adj[specie][active_x, active_z] = (
                                    (in_flux + adj_flux) /flow_sum)
                            new_gw_in[active_x, active_z] = (
                                new_gw_in[active_x, active_z] +
                                self.gw_in[column, row])
                        new_qss_gw[active_x, active_z] = (
                            new_qss_gw[active_x, active_z] +
                            self.qss_gw[column, row])
                        new_gw_qout[active_x, active_z] = (
                            self.gw_out[active_x, active_z] +
                            self.gw_out[column, row])
            self.qss_gw = new_qss_gw
            self.gw_out = new_gw_qout
            self.gw_in = new_gw_in
            new_masses = {}
            for specie in self.exchange_species:
                new_masses[specie] = sum(sum(adj[specie] * self.gw_in))
                if abs(old_masses[specie] - new_masses[specie]) > 1e-12:
                    diff = old_masses[specie] - new_masses[specie]
                    raise ValueError('Difference in masses for %s: %f'
                                     %(specie, diff))

    def find_next_active(self):
        """Find next active cells.
        """
        v_active = numpy.transpose(self.w2.get_shared_data('vactive'))
        if not numpy.sum(v_active):
            self.w2.w2_hydrodynamics()
            self.w2.constituents()
            v_active = numpy.transpose(self.w2.get_shared_data('vactive'))
        cell_width = self.cell_width
        upper_active = numpy.zeros(cell_width.shape[0])
        self.active_x = numpy.zeros(cell_width.shape)
        self.active_z = numpy.zeros(cell_width.shape)
        row_range = range(cell_width.shape[1])
        column_range = range(cell_width.shape[0])
        column_range.reverse()
        for column in column_range:
            for row in row_range:
                if v_active[column, row] > 0.0:
                    upper_active[column] = row
                    break
        print('upper_active')
        print(upper_active)
        print('sum vactive', numpy.sum(v_active))
        for column in column_range:
            for row in row_range:
                x = 0
                z = 0
                if cell_width[column, row]:
                    x = column
                    z = row
                    if not v_active[column, row]:
                        downwards = 1
                        while True:
                            if upper_active[x]:
                                if upper_active[x] <= z:
                                    break
                                else:
                                    z += 1
                            else:
                                if x > 0 and downwards:
                                    x -= 1
                                else:
                                    x += 1
                                    downwards = 0
                self.active_x[column, row] = x
                self.active_z[column, row] = z

    def set_qs(self, date):
        """Set flow values.
        """
        self.get_qs(date)
        self.adjust_inactive_cells(date)
        trans = numpy.transpose
        self.gw_out = - self.gw_out
        self.qss_gw[:] = self.gw_in + self.gw_out
        self.w2.set_shared_array_data('qgw', trans(self.qss_gw))
        self.w2.set_shared_array_data('qgwin', trans(self.gw_in))
        self.w2.set_shared_array_data('qgwout', trans(self.gw_out))
        print('qgw', numpy.sum(self.qss_gw))
        print('qgwin', numpy.sum(self.gw_in))
        print('qgwout', numpy.sum(self.gw_out))

    def read_conc(self):
        """Read concentration values.
        """
        print('reading gw conc')
        obs_conc_reader = obswells.ObsWellAssociator(self.config)
        obs_conc_reader.read_obs_conc(use_second_key=True)
        self.conc = obs_conc_reader.wells

    def match_conc(self):
        """Match the gw concentrations.
        """
        print('matching gw conc')
        self.species_conc = {}
        for specie in self.exchange_species:
            self.species_conc[specie] = numpy.zeros(
                (self.distribution.shape[0], self.distribution.shape[1]),
                numpy.float64)
        row_range = range(self.distribution.shape[1])
        for column in range(self.distribution.shape[0]):
            for row in row_range:
                id_ = int(self.distribution[column, row])
                if id_ not in self.inactive_ids:
                    for specie in self.exchange_species:
                        try:
                            self.species_conc[specie][column, row] = \
                                self.conc[self.ids[id_]][specie]
                        except KeyError:
                            if id_ in self.q_outs or id_ in self.zero_q_out:
                                pass
                            else:
                                print(specie, id_)
                                print(self.ids)
                                raise

    def set_conc(self):
        """Set the gw concentration.
        """
        print('setting gw conc')
        for specie in self.exchange_species:
            ssgw = self.adjusted_species_conc[specie] * self.gw_in
            ssgw = numpy.transpose(ssgw)
            if specie == 'dox':
                specie = 'do'
            self.w2.set_shared_array_data(specie + 'ssgw', ssgw)

if __name__ == '__main__':

    class FakeConfig:
        """Mock for config.
        """
        # No __init__, no methods.
        # pylint: disable-msg=W0232,R0903
        pass

    def test():
        """Check if it works.
        """
        config = FakeConfig()
        input_path = ''
        join = os.path.join
        config.well_conc_file_name = join(input_path, 'obswells.csv')
        config.bathymetry_file_name = join(input_path, 'bath.nc')
        config.pore_volumes_file_name = join(input_path, 'porevolumes.txt')
        config.time_dependent_conc_file_name = join(input_path,
                                                    'time_dependent_conc.txt')
        config.precalc_gw_conc = True
        config.time_dependent_precalc_gw_conc = True
        gw = PrecalcGwInOut(config,
                            join(input_path, 'qBalance.csv'),
                            join(input_path, 'wkey.txt'),
                            join(input_path, 'gwq.vmp.in'),
                            [])
        gw.read_conc()
        gw.match_conc()
        print(gw.time_dependent_conc)
        print(gw.time_dependent_ids)
        ##for id_, coord in gw.id_distribution.items():
        ##    print(id_, coord)
        #print(gw.species_conc)
        #print(gw.distribution)
        #print(gw.distribution.shape)
        #print(gw.ids)


        #import datetime
        #gw.get_qs(datetime.datetime(1996,1,1))
        #print(gw.gw_in[1])
        #print(gw.all_qs[1])
        #print(sum(gw.qss_gw))
        #print(sum(gw.gw_in))
