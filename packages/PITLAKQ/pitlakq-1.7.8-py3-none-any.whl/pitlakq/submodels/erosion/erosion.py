"""Erosion module.
"""
from __future__ import print_function

import copy
import os
import sys

# NumPy, dynamic members.
# pylint: disable-msg=E1101
# Many attributes defined outside __init__.
# pylint: disable-msg=W0201
# Some really long names.
# pylint: disable-msg=C0103

import BTrees.IOBTree as IOBTree
import numpy
import transaction

import pitlakq.metamodel.running.db as db
from . import surfergrid
from . import polygon_gridding


class Erosion:
    """Wind wave and rain erosion.
    """
    def __init__(self, config, water_level):
        self.config = config
        if not self.config.silent:
            print('init erosion')
        self.db = db.SharedDB()
        self.last_water_level = water_level
        self.wind_erosion_depth = self.config.wind_erosion_depth
        self.erosion_density = self.config.erosion_density
        if self.config.half_life < 1e-20:
            self.config.decay_constant = 1e-3
        else:
            self.config.decay_constant = \
                0.693 / (self.config.half_life * 86400)
        self.make_grid()
        self.cec = Cec(config.cec_file_name, config.valence_file_name)
        self.porewater = Porewater(config.porewater_file_name)
        if self.config.erosion_steady_state_mass:
            self.read_steady_state_mass()
        self.make_cec_spezies()
        self.first = 1
        self.total_time = 0.0
        self.erosion_total_moles = 0
        self.interflow_total_moles = 0
        self.cec_out = {}
        self.init_data_base()
        self.time_step = self.old_time_step = 0
        self.number_of_time_steps_between_reduced = self.config.lake_time_step
        if self.config.interflow:
            self.read_interflow_conc()

    def init_data_base(self):
        """Put trees in ZODB database.
        """
        if not self.config.reduced:
            for moles in ['erosion_porewater_moles',
                          'erosion_cec_moles',
                          'interflow_moles']:
                    self.db.root[moles] = IOBTree.IOBTree()
        else:
            for reduced_moles in ['reduced_erosion_porewater_moles',
                                  'reduced_erosion_cec_moles',
                                  'reduced_interflow_moles']:
                if not self.db.root.has_key(reduced_moles):
                    self.db.root[reduced_moles] = IOBTree.IOBTree()
        transaction.commit()

    def make_cec_spezies(self):
        """Generate CEC species.
        """
        self.cec_spezies = self.cec.spezies

    def make_grid(self):
        """Generate the grid.
        """
        surfer_grid = surfergrid.SurferGrid(self.config.grid_file_name)
        surfer_grid.read_surfer_grd_file()
        x_min = surfer_grid.geometry_values['rwfrom']
        y_min = surfer_grid.geometry_values['hwfrom']
        x_max = surfer_grid.geometry_values['rwto'] + \
                surfer_grid.geometry_values['delta_x']
        y_max = surfer_grid.geometry_values['hwto'] + \
                surfer_grid.geometry_values['delta_y']
        delta_x = surfer_grid.geometry_values['delta_x']
        delta_y = surfer_grid.geometry_values['delta_y']
        self.cell_area = surfer_grid.geometry_values['cell_area']
        z = surfer_grid.geometry_values['z']
        self.max_water_level = self.config.max_water_surface
        grid = polygon_gridding.Grid(x_min, y_min, x_max, y_max, delta_x,
                                     delta_y, self.config.polygons_path, z,
                                     self.max_water_level)
        self.z = grid.z
        self.polygon_ids = grid.polygon_ids
        self.polygon_names = grid.names
        self.rain_erosion_area_primary = numpy.zeros(
            (len(self.polygon_names)), float)
        self.wind_erosion_area_primary = copy.copy(
            self.rain_erosion_area_primary)
        self.rain_erosion_area_repeated = copy.copy(
            self.rain_erosion_area_primary)
        self.wind_erosion_area_repeated = copy.copy(
            self.rain_erosion_area_primary)
        # first name is backround, i.e. white color
        self.name_range = range(1, len(self.polygon_names))
        # convert from t/(ha*a) to kg/(m2*s)
        self.rain_erosion_rate_per_sqm = (
            self.config.rain_erosion_rate_per_hectar *
            1e3 / (1e4 * (365.25 * 8.6400)))
        self.rain_erosion_rate_per_sqm_repeated = (
            self.config.rain_erosion_rate_per_hectar_repeated *
            1e3 / (1e4 * (365.25 * 86400)))
        # convert from t/(ha*a) to kg/(m2*s)
        self.active_cells = numpy.less(self.z, self.max_water_level)
        self.repeated = numpy.zeros(self.z.shape)
        if self.config.interflow:
            #mm/a -> m3/m2*s
            self.interflow_rate = (
                self.config.interflow_rate / (86400 * 365.25) / 1000)
            self.interflow_equivalent_mass = copy.copy(
                self.rain_erosion_area_primary)

    def read_steady_state_mass(self):
        """Read input for stead state mass.
        """
        mass_dict = {}
        fobj = open(self.config.steady_state_mass_file_name)
        data = [line.split for line in fobj]
        fobj.close()
        for line in data:
            if line[0][0] != '#':
                mass_dict[line[0]] = float(line[1])
        self.steady_state_mass_rate = [0]
        for name in self.polygon_names[1:]:
            try:
                mass = mass_dict[name]
            except KeyError:
                print('profile %s not in file %s' % (name,
                    self.config.steady_state_mass_mass_file_name))
                sys.exit(1)
            self.steady_state_mass_rate.append(mass)
        self.steady_state_mass_rate = numpy.array(self.steady_state_mass_rate)
        print('rate per year', numpy.sum(self.steady_state_mass_rate))
        self.steady_state_mass_rate = \
            self.steady_state_mass_rate / (365.25 * 86400)
        print('rate per second', numpy.sum(self.steady_state_mass_rate))

    def calculate_areas(self):
        """Calculate the areas from erosion occurs.
        """
        self.lake_area = (numpy.less(self.z, self.water_level) *
                          self.active_cells)
        self.uncoverd_lake_area = (numpy.greater(self.z, self.water_level) *
                                   self.active_cells)
        rain = self.uncoverd_lake_area * self.polygon_ids
        wind = (numpy.greater(self.z, self.last_water_level) * self.lake_area *
                self.polygon_ids)
        rain_primary = rain * numpy.logical_not(self.repeated)
        wind_primary = wind * self.active_cells * numpy.logical_not(
                                                                self.repeated)
        rain_repeated = rain * self.repeated
        wind_repeated = wind  * self.repeated
        self.repeated = numpy.where(self.repeated +
                                    numpy.less(self.z,
                                               self.water_level) *
                                    self.active_cells, 1, 0)
        for n in self.name_range:
            self.rain_erosion_area_primary[n] = \
                numpy.sum(numpy.equal(rain_primary, n)) * self.cell_area
            self.wind_erosion_area_primary[n] = \
                numpy.sum(numpy.equal(wind_primary, n)) * self.cell_area
            self.rain_erosion_area_repeated[n] = \
                numpy.sum(numpy.equal(rain_repeated, n)) * self.cell_area
            self.wind_erosion_area_repeated[n] = \
                numpy.sum(numpy.equal(wind_repeated, n)) * self.cell_area
        self.last_water_level = self.water_level

    def calculate_mass(self):
        """Calculate erored masses.
        """
        # (365.25-28*12)/12 = 2.4375 correcting for month with 28 days
        if self.config.monthly_phreeqc:
            self.delta_t += 2.4375*86400
        self.calculate_areas()
        self.wind_erosion_mass_primary = (self.wind_erosion_area_primary *
                                          self.wind_erosion_depth *
                                          self.erosion_density)
        self.rain_erosion_mass_primary = (self.rain_erosion_area_primary *
                                          self.rain_erosion_rate_per_sqm *
                                          self.delta_t)
        self.wind_erosion_mass_repeated = (self.wind_erosion_area_repeated *
                                    self.config.wind_erosion_depth_repeated *
                                           self.erosion_density)
        self.rain_erosion_mass_repeated = (self.rain_erosion_area_repeated *
                                    self.rain_erosion_rate_per_sqm_repeated *
                                           self.delta_t)
        if self.config.erosion_steady_state_mass:
            self.steady_state_mass = self.steady_state_mass_rate * self.delta_t
        else:
            self.steady_state_mass = 0.0
        self.mass = (self.wind_erosion_mass_primary +
                     self.rain_erosion_mass_primary +
                     self.wind_erosion_mass_repeated +
                     self.rain_erosion_mass_repeated +
                     self.steady_state_mass)
        if numpy.sum(self.mass) < 0.0:
            print('mass negative')
            print(self.mass)
            raise ValueError('mass must be positive')

    def calculate_interflow(self):
        """Calculate the interflow.
        """
        max_ratio = self.config.max_ratio_interflow_areas
        #stronger after being wet?
        effective_area = (self.rain_erosion_area_primary +
                          self.rain_erosion_area_repeated * 2)
        uncoverd = float(numpy.sum(self.uncoverd_lake_area))
        lake = float(numpy.sum(self.lake_area))
        ratio = uncoverd / lake
        if ratio > max_ratio:
            effective_area = effective_area * max_ratio / ratio
        self.interflow_moles = {}
        area = numpy.sum(effective_area)
        for name in self.interflow_conc.keys():
            self.interflow_moles[name] = (area * self.interflow_rate *
                                          self.delta_t *
                                          self.interflow_conc[name])

    def read_interflow_conc(self):
        """Calculate the interflow concnetration.
        """
        fobj = open(self.config.interflow_conc_file_name)
        data = [line.split for line in fobj]
        fobj.close()
        self.interflow_conc = {}
        for line in data:
            if line[0][0] != '#': # line begins with #
                # mmoles/l == moles/m3
                self.interflow_conc[line[0]] = float(line[1])

    def calculate_moles(self):
        """Turn masses in moles.
        """
        if numpy.any(self.mass):
            self.cec.make_moles(self.mass, self.polygon_names[1:],
                                self.water_level)
            self.porewater.make_moles(self.mass, self.polygon_names[1:],
                                      self.water_level)
            self.cec_moles = self.cec.moles
            if self.cec_out:
                n = 0
                for spezie in self.cec_spezies:
                    self.cec_moles[n] = (self.cec_moles[n] +
                                         self.cec_out[spezie])
                    n += 1
            porewater_moles = copy.copy(self.porewater.moles)
            self.porewater_moles = numpy.array(porewater_moles)
            self.erosion_total_moles += (numpy.sum(porewater_moles) +
                                         numpy.sum(self.cec_moles))
            self.db.root['erosion_porewater_moles'][self.time_step] = \
                                                        self.porewater_moles
            self.db.root['erosion_cec_moles'][self.time_step] = self.cec_moles
            transaction.commit()
        if self.config.interflow:
            self.calculate_interflow()
            n = 0
            for spezie in self.porewater.spezies:
                if self.interflow_moles.has_key(spezie):
                    self.porewater_moles[n] = (self.porewater_moles[n] +
                                               self.interflow_moles[spezie])
                n += 1
            self.db.root['interflow_moles'][self.time_step] = \
                                                        self.interflow_moles
        transaction.commit()
        self.time_step += 1

    def make_phreeqc_data(self, water_level, delta_t, water_volume):
        """Pepare data for PHREEQC calculation.
        """
        self.total_time += delta_t
        self.water_level = water_level
        self.delta_t = delta_t
        root = self.db.root
        if self.config.reduced:
            try:
                step = self.time_step
                self.porewater_moles = \
                                root['reduced_erosion_porewater_moles'][step]
                self.cec_moles = root['reduced_erosion_cec_moles'][step]
                self.interflow_moles = root['reduced_interflow_moles'][step]
            except KeyError:
                self.porewater_moles = self.cec_moles = 0.0
                self.interflow_moles = {}
                next_time_step = (self.old_time_step +
                                  self.number_of_time_steps_between_reduced)
                for step in range(self.old_time_step, next_time_step):
                    self.porewater_moles += \
                                         root['erosion_porewater_moles'][step]
                    self.cec_moles += root['erosion_cec_moles'][step]
                    for k in root['interflow_moles'][step].keys():
                        try:
                            self.interflow_moles[k] += \
                                self.db.root['interflow_moles'][step][k]
                        except KeyError:
                            self.interflow_moles[k] = \
                                self.db.root['interflow_moles'][step][k]
                step = self.time_step
                root['reduced_erosion_porewater_moles'][step] = \
                    self.porewater_moles
                root['reduced_erosion_cec_moles'][step] = self.cec_moles
                root['reduced_interflow_moles'][step] = self.interflow_moles
                self.old_time_step = next_time_step
                transaction.commit()
        else:
            self.calculate_mass()
            self.calculate_moles()
        if self.config.reduced or numpy.any(self.mass):
            self.cec_in = {}
            self.porewater_in = {}
            # m3 --> L
            cec_moles_per_liter = self.cec_moles / (water_volume * 1000)
            porewater_moles_per_liter = (self.porewater_moles /
                                         (water_volume * 1000)) # m3 --> L
            # scale max value as 1
            if numpy.any(self.porewater_moles):
                self.porewater_moles = max(porewater_moles_per_liter)
                porewater_moles_per_liter = (porewater_moles_per_liter /
                                             self.porewater_moles)
            else:
                self.porewater_moles = 0.0
                porewater_moles_per_liter[:] = 0.0
            n = 0
            for spezie in self.cec.spezies:
                self.cec_in[spezie] = (cec_moles_per_liter[n] *
                                       self.cec.valence_fractions[spezie])
                n += 1
            n = 0
            for spezie in self.porewater.spezies:
                self.porewater_in[spezie] = porewater_moles_per_liter[n]
                n += 1
            self.config.calculateErosion = 1
        else:
            self.config.calculateErosion = 0

class Material:
    """
    Abstract class for cec and porewater
    """
    def __init__(self, file_name):
        self.file_name = file_name
        self.profiles = {}
        self.water_level_steps = []
        self.read_material()

    def read_material(self):
        """Read the material from a file.
        """
        fobj = open(self.file_name)
        data = [line.split() for line in fobj]
        fobj.close()
        for line in data:
            if line[0][0] != '#':
                if line[0] == 'spezies':
                    self.spezies = line[2:]
                elif line[1] == 'upper_waterlevel':
                    pass
                else:
                    key = line[0]
                    if key not in self.profiles:
                        self.profiles[key] = []
                    # mmol/kg --> mol/kg
                    self.profiles[key].append(
                        (float(line[1]),
                         numpy.array([float(x) for x in line[2:]]) / 1000))
        for key in self.profiles.keys():
            self.profiles[key].sort()

    def make_moles(self, mass, profile_names, water_level):
        """Calculate the moles.
        """
        first = True
        if numpy.any(mass):
            n = 1       # 0 is background value = 0.0!!!!
            for name in profile_names:
                try:
                    profile = self.profiles[name]
                    if first:
                        first = 0
                        self.moles = numpy.zeros(len(profile[0][1]))
                except KeyError:
                    print('profile %s not specfifed in %s' % (name,
                                                              self.file_name))
                    sys.exit(1)
                for level in profile:
                    if level[0] >= water_level:
                        self.moles = self.moles + mass[n]* level[1]
                        break
                n += 1
        else:
            if first:
                first = False
                self.moles = numpy.zeros(len(profile[0][1]))
            else:
                self.moles[:] = 0.0

class Porewater(Material):
    """Just a dffrent name.
    """
    pass


class Cec(Material):
    """Cation exchange.
    """
    def __init__(self, file_name, valence_file_name):
        Material.__init__(self, file_name)
        self.valence_file_name = valence_file_name
        self.read_valences()

    def read_valences(self):
        """Read valences for species and calcualte
        the valence fraction for each.
        """
        self.valences = {}
        fobj = open(self.valence_file_name)
        data = [line.split() for line in fobj]
        fobj.close()
        for line in data:
            if line[0][0] != '#':
                self.valences[line[0]] = int(line[1])
        specie_number = len(self.spezies)
        self.valence_fractions = {}
        # The fraction of each specie is the equal share of the exchanger
        # moles divided by the valence of the specie.
        # e.g. K: 1 / number_of_species
        # e.g. Ca: (1 / number_of_species) / 2
        # --> total_exchanger_moles = sum(moles_per_specie * valence_of_specie)
        # See PHREEQC manual under EXCHANGE (p.82 for version 2.0)
        # for more details.
        for spezie in self.spezies:
            self.valence_fractions[spezie] = ((1.0 / specie_number) /
                                              self.valences[spezie])

if __name__ == '__main__':

    def test():
        """Test it.
        """
        class Config:
            """Mock config.
            """
            # No __init__, no methods, too many attributes.
            # pylint: disable-msg=W0232,R0902,R0903
            pass
        config = Config()
        config.silent = 0
        project_path = ''
        join = os.path.join
        material_path = join(project_path, 'erosion', 'materialproperties')
        config.cec_file_name = join(material_path, 'cec.txt')
        config.porewater_file_name = join(material_path, 'porewater.txt')
        config.valence_file_name = join(material_path, 'valences.txt')
        config.steady_state_mass_mass_file_name = join(material_path,
                                                       'steadystatemass.txt')
        config.grid_file_name = join(material_path, 'baer.grd')
        config.polygons_path = join(material_path, 'polygons')
        config.initial_water_surface = 68
        config.max_water_surface = 125
        config.wind_erosion_depth = 0.5             # m
        config.wind_erosion_depth_repeated = 0.0    # m
        config.rain_erosion_rate_per_hectar = 100      # t/(ha*a)
        config.rain_erosion_rate_per_hectar_repeated = 20.0 # t/(ha*a)
        # t/a #20t/(ha*a) * bench_width * bench_length
        config.bench_rain_erosion_rate = 20 * 22 * 16500
        config.erosion_density = 1800           # kg/m3
        config.erosion_steady_state_mass = 0
        config.interflow = 1
        config.interflow_rate = 100 # mm/a
        eros = Erosion(config)
        time_step = 1  *86400 # s
        water_rising_rate = 10 / (365.25 * 86400) # m/s
        model_time = 0
        level = 124
        n = 0
        nmax = 3
        while True:
            model_time += time_step
            level += water_rising_rate * time_step
            eros.make_phreeqc_data(level, time_step, 1e6)
            if level >= 125:
                level = 124
                n += 1
                if n > nmax:
                    break
        print(model_time)
