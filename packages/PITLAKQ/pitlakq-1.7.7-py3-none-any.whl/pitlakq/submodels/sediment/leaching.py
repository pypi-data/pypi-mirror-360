"""Leaching of acidity from sediment.

Leaching of acidity from the lake sediment is calculated
for given leaching sectors. Each leaching sector has:

* an area in m2
* one or more associated W2-cells with their active areas
* release rates as function of time and kB
* a composition of material that is released

The release rate is calculated differently for different
periods. For the "acicd" period a function of kB
as specified as input will be use whereas after neutralization
a function of time which is also specified will used.

The rate is multiplied with the active area of the section, which in turn
is calculated from all active cells associated with the the section.

"""

from __future__ import print_function

import datetime
import os
import time

# NumPy, dynamic members.
# pylint: disable-msg=E1101

import numpy

import pitlakq.numericalmodels.existingmodels.phreeqc.kb_calculation as \
       kb_calculation


class Leaching(object):
    """Leaching of acidity from sediment.
    """
    # 12 attributes is a bit too few.
    # pylint: disable-msg=R0902
    def __init__(self, config, constituents):
        self.config = config
        self.constituents = constituents
        self.phreeqc_names, self.molar_weight = self.make_phreeqc_names()
        self.w2 = config.w2
        self.sections = [Section(config, sec) for sec in config.sections]
        leach_balance = {}
        balance_names = self.config.balance_names
        for section in self.sections:
            leach_balance[section.name] = dict([(balance_names[specie], 0.0)
                                                for specie in
                                                section.composition])
            section.balance = leach_balance[section.name]
            section.balance_names = balance_names
        self.config.specie_balances['leaching'] = leach_balance
        self.ph_limit = float(config.leaching_ph_limit)
        self.time_rate_start = datetime.datetime(*time.strptime(
            config.leaching_time_rate_start, '%d.%m.%Y')[:3])
        self.counter = 0
        self.mode = 'kb'
        self.old_date = None
        self.active_constituent_names = self.find_active_constiuents()
        self.running_average_ph = None

    def find_active_constiuents(self):
        """
        Find active w2 names.
        """
        act = 'active_constituents'
        exclude = set(['tra', 'ldom', 'rdom', 'algae', 'lpom', 'sed', 'co2',
                       'feoh3', 'aloh3', 'po4precip'])
        active_names = []
        for n, name in enumerate(self.w2.constituent_order):
            if self.w2.input.data[act][act]['value'][n]:
                w2_name = self.w2.constituent_names[name]
                if w2_name in exclude:
                    continue
                active_names.append(w2_name)
        active_names.append('t2')
        return active_names

    def make_phreeqc_names(self):
        """Make PHREEEQC names
        """
        phreeqc_const = self.constituents
        phreeqc_names = {}
        molar_weight = {}
        for item in phreeqc_const:
            phreeqc_names[item['key']] = item['phreeqc_name']
            molar_weight[item['key']] = item['molar_weight']
        phreeqc_names['ph'] = 'pH'
        phreeqc_names['t2'] = 'temp'
        molar_weight['ph'] = 1
        molar_weight['t2'] = 1
        replace_names = {'Fe_di': 'Fe(+2)', 'Fe_tri': 'Fe(+3)'}
        for conc_name, phreeqc_name in phreeqc_names.items():
            if phreeqc_name in replace_names:
                phreeqc_names[conc_name] = replace_names[phreeqc_name]
        return phreeqc_names, molar_weight

    def leach(self):
        """Add substance from sediment to lake.
        """
        if self.mode == 'kb':
            if self.time_rate_start < self.w2.date:
                if self.stable_ph > self.ph_limit:
                    self.mode = 'time'
                    print()
                    print('switched leaching mode to time at: ', end='')
                    print(self.w2.date)
        self.counter += 1
        if self.mode == 'kb':
            kbs = self.make_kbs()
        if not self.old_date:
            self.old_date = self.config.start
        time_delta = self.w2.date - self.old_date
        duration_days = time_delta.days + time_delta.seconds / 86400.0
        #duration_seconds = duration_days * 86400
        for n, section in enumerate(self.sections):
            if self.mode == 'kb':
                section.leach_kb(kbs[n], duration_days)
            elif self.mode == 'time':
                section.leach_time(duration_days)
            else:
                raise ValueError('mode must be either `kb` or `time` %s found'
                                 % self.mode)
            section.set_constituents()
        self.old_date = self.w2.date
        self.w2.addSsp = 1
        return self.counter

    def make_kbs(self):
        """Calculate KB8.2 with PHREEQC
        """
        w2_const_arrays = {}
        for w2_name in self.phreeqc_names.keys():
            w2_const_arrays[w2_name] = self.w2.get_shared_data(w2_name)
        kbs = []
        constituents = []
        for section in self.sections:
            section.find_active_cells()
            for cell in section.active_cells:
                const_dict = {}
                for w2_name, phreeqc_name in self.phreeqc_names.items():
                    x = cell['x']
                    z = cell['z']
                    conc = w2_const_arrays[w2_name][z, x]
                    const_dict[phreeqc_name] = (conc /
                                                self.molar_weight[w2_name])
                constituents.append(const_dict)
        calculator = kb_calculation.KbCalculator(self.config, 8.2,
                                                 constituents)
        flat_kbs = calculator.calculate()
        kbs = []
        counter = 0
        for section in self.sections:
            section_kbs = []
            for cell in section.active_cells:
                section_kbs.append(flat_kbs[counter])
                counter += 1
            kbs.append(section_kbs)
        return kbs

    @property
    def stable_ph(self):
        """Calculate running average of pH.
        """
        steps = 30
        vactive = self.w2.get_shared_data('vactive')
        all_ph = self.w2.get_shared_data('ph')
        ph = numpy.average(all_ph[vactive > 0.1])  # pylint: disable-msg=C0103
        if self.running_average_ph is None:
            self.running_average_ph = ph - 2  # start conservative
        self.running_average_ph = (self.running_average_ph * (steps - 1)
                                   + ph) / steps
        return self.running_average_ph


class Section(object):
    """One leaching section.
    """
    # 12 attributes is a bit too few.
    # pylint: disable-msg=R0902
    def __init__(self, config, properties):
        self.config = config
        self.w2 = config.w2
        self.name = properties['name']
        self.w2_cells_x = numpy.array([entry[0] for entry in
                                       properties['w2_cells']], dtype=int)
        self.w2_cells_z = numpy.array([entry[1] for entry in
                                       properties['w2_cells']], dtype=int)
        self.w2_cells_area = numpy.array([entry[2] for entry in
                                          properties['w2_cells']], dtype=float)
        self.w2_cells_acidity = numpy.zeros(self.w2_cells_x.shape)
        self.total_area = numpy.sum(self.w2_cells_area)
        self.composition = self.read_compostion(properties['composition'])
        self.kb_rates = self.read_kb_rates(properties['rates_kb'])
        self.time_rates = self.read_time_rates(properties['rate_time'])
        self.old_area_fraction = None
        self.old_rate_type = None
        self.old_days = numpy.zeros(self.w2_cells_x.shape, dtype=float)
        self.days = numpy.zeros(self.w2_cells_x.shape, dtype=float)
        self.area_out_file = self.init_area_file()
        self.active_cells = None

    def init_area_file(self):
        """Open file for saving active area.
        """
        fobj = open(os.path.join(self.config.sediment_out_path,
                                 '%s_area.txt' % self.name), 'w')
        fobj.write('%10s %25s %25s %25s %25s\n' % ('date', 'total_area',
                                                   'current_area', 'fraction',
                                                   'rate_type'))
        return fobj

    def read_compostion(self, composition_file_name):
        """Read composition of material per mol of acidity
        """
        fobj = open(os.path.join(self.config.sediment_path,
                                 composition_file_name))
        header = next(fobj).split()[:2]
        assert header == ['specie', 'amount']
        composition = {}
        for line in fobj:
            if line.strip():
                specie, amount = line.split()
                composition[specie] = float(amount)
        fobj.close()
        return composition

    def read_kb_rates(self, kb_rate_file_name):
        """Read kB-dependent rates.
        """
        fobj = open(os.path.join(self.config.sediment_path,
                                 kb_rate_file_name))
        header = next(fobj).split()[:2]
        units = next(fobj).split()[:2]
        assert header == ['kb8.2', 'rate']
        assert units == ['[mmol/l]',  '[mol/m2/d]']
        kb_rates = []
        for line in fobj:
            if line.strip():
                kb, rate = line.split()  # pylint: disable-msg=C0103
                kb_rates.append((float(kb), - float(rate)))
        kb_rates.sort()  # make sure they are ordered
        fobj.close()
        return kb_rates

    def read_time_rates(self, time_rate_file_name):
        """Read time dependent rates
        """
        fobj = open(os.path.join(self.config.sediment_path,
                                 time_rate_file_name))
        header = next(fobj).split()[:2]
        units = next(fobj).split()[:2]
        assert header == ['time', 'rate']
        assert units == ['[d]',  '[mol/m2/d]']
        time_rates = {}
        for line in fobj:
            if line.strip():
                try:
                    time_, rate = line.split()
                except ValueError:
                    print(time_rate_file_name)
                    print(line)
                    raise
                time_rates[float(time_)] = - float(rate)
        fobj.close()
        time_rates[0.0] = 0.0  # add rate for time before start
        return time_rates

    def find_active_cells(self):
        """Find cell with active volume.
        """
        vactive = self.w2.get_shared_data('vactive')
        self.active_cells = numpy.where(
            vactive[self.w2_cells_z, self.w2_cells_x] > 0.1,
                                        True, False).ravel()

    def leach_time(self, duration):
        """Do leaching with time-dependent rate.
        """
        self.find_active_cells()
        self.days[self.active_cells] += int(duration)
        rate1 = numpy.array([self.time_rates[day] for day in self.old_days])
        rate2 = numpy.array([self.time_rates[day] for day in self.days])
        rate = (rate1 + rate2) / 2.0
        self.w2_cells_acidity[:] = 0.0
        active_area = numpy.sum(self.w2_cells_area[self.active_cells])
        self.w2_cells_acidity[self.active_cells] = (self.w2_cells_area * rate
                                                    * duration)
        self.write_area_fraction(active_area, 'time')
        self.old_days = self.days

    def leach_kb(self, kbs, duration):
        """Do leaching with time-dependent rate.
        """
        self.find_active_cells()
        for cell in self.w2_cells:
            cell['acidity'] = 0.0
        active_area = 0.0
        for n, cell in enumerate(self.active_cells):
            rate = self.find_kb_rate(kbs[n])
            cell['acidity'] = cell['area'] * rate * duration
            active_area += cell['area']
        self.write_area_fraction(active_area, 'kb')

    def write_area_fraction(self, active_area, rate_type):
        """Write active area for leaching if it changed since last write.
        """
        frac = active_area / self.total_area
        write_areas = False
        if frac != self.old_area_fraction:
            self.old_area_fraction = frac
            write_areas = True
        if rate_type != self.old_rate_type:
            self.old_rate_type = rate_type
            write_areas = True
        if write_areas:
            date_string = self.config.w2.date.strftime('%d.%m.%Y')
            self.area_out_file.write('%10s %25.2f %25.2f %25.2f %25s\n' %
                                     (date_string, self.total_area,
                                      active_area, frac, rate_type))
            self.area_out_file.flush()

    def set_constituents(self):
        """Add mass of species to lake.
        """
        for specie, amount in self.composition.items():
            total_mass = 0.0
            name = specie + 'ssp'
            w2_value = self.w2.get_shared_data(name)
            vactive = self.w2.get_shared_data('vactive')
            mass = self.w2_cells_acidity * amount
            z = self.w2_cells_z
            x = self.w2_cells_x
            numpy.seterr(divide='ignore', invalid='ignore')
            conc = numpy.where(mass == 0.0, 0.0, mass / vactive[z, x])
            numpy.seterr(divide='print', invalid='print')
            w2_value[z, x] = w2_value[z, x] + conc
            total_mass = numpy.sum(mass)
            self.w2.set_shared_data(name, w2_value)
            total_mass /= 1e6  # g --> t
            self.balance[self.balance_names[specie]] += total_mass

    def find_kb_rate(self, kb_value):
        """Interpolate rate for kb.
        """
        for n, rate in enumerate(self.kb_rates):
            next_ = self.kb_rates[n + 1]
            if  rate[0] <= kb_value <= next_[0]:
                x_0 = rate[0]
                x_1 = next_[0]
                y_0 = rate[1]
                y_1 = next_[1]
                break
        x = kb_value
        return y_0 + ((y_1 - y_0) / (x_1 - x_0)) * (x - x_0)
