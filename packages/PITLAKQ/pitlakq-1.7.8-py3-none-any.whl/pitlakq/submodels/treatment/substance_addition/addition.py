"""Added substances to the lake.
"""

from __future__ import print_function

import datetime
import os

import netCDF4


class Substance(object):
    """One substance with some proreties.
    """
    def __init__(self,
                 volume,
                 molar_masses,
                 molar_ratios):
        self.volume = volume
        self.convertions = {'t/h': 277.77777777777777,
                            'kg/h': 0.277777777777777,
                            't/d': 11.574074074074074,
                            'kg/d': 0.011574074074074074}
        self.possible_units = self.convertions.keys()
        n = 0
        total = 0.0
        self.fractions = []
        for molar_mass in molar_masses:
            total += molar_ratios[n] * molar_mass
            n += 1
        n = 0
        for molar_mass in molar_masses:
            self.fractions.append(molar_ratios[n] * molar_mass / total)
            n += 1
        self.unit = 'g/s'
        self.rate = 0

    def set_volume(self, volume):
        """Set the volume.
        """
        self.volume = volume

    def set_rate(self, rate, unit='t/h'):
        """Set the addition rate.
        """
        if unit not in self.possible_units:
            allowed_units = ', '.join(self.possible_units)
            raise UnitError('Unit %s is not define.\n Use one of %s.'
                            % (unit, allowed_units))
        self.rate = rate * self.convertions[unit]

    def get_conc_increase(self, delta_t):
        """Calculate the increase in concentration.
        """
        cons = []
        for frac in self.fractions:
            # delta_t in seconds
            cons.append((frac * self.rate * delta_t) / self.volume)
        return cons


class Treatment(object):
    """Add substance at one location with schedule to the lake.
    """
    # Lots of instance attributes.
    # pylint: disable-msg=R0902
    def __init__(self,
                 addition,
                 schedule_file_name,
                 output_path,
                 w2):
        self.schedule_file_name = schedule_file_name
        self.output_path = output_path
        self.name = addition['name']
        self.location = addition['location']
        self.w2 = w2
        self.constituents = addition['constituents']
        self.molar_masses = addition['molar_masses']
        self.molar_ratios = addition['molar_ratios']
        self.old_jday = 0.0
        self.old_year = 0
        self.n = 0
        self.first = 1
        self.rate = 0.0
        self.delta_t = 0.0
        self.current_year = 0
        self.current_jday = 0
        self.scheduled_dates = []
        self.scheduled_rates = []
        self.unit = None
        self.read_schedule()
        self.jday = None
        self.get_date()
        self.set_current_period()
        self.masses = {}
        for const in self.constituents:
            self.masses[const] = 0.0
        self.counter = 0
        self.total_soda_mass = 0.0
        self.total_time = 0.0
        self.volume = 0.0
        self.substance = None
        self.concs = None

    def read_schedule(self):
        """Read the schedule with a addition rates.
        """
        schedule_file = open(self.schedule_file_name)
        data = [line.split() for line in schedule_file]
        schedule_file.close()
        self.unit = data[0][3].split('=')[1].strip()
        for line in data[1:]:
            # filter out empty lines
            if not line:
                continue
            year = int(line[0][6:10])
            month = int(line[0][3:5])
            day = int(line[0][0:2])
            float_hour = float(line[1])
            hour = int(float_hour)
            if hour:
                minute = int(float_hour % hour * 60)
            else:
                minute = 0
            self.scheduled_dates.append(datetime.datetime(year,
                                                          month,
                                                          day,
                                                          hour,
                                                          minute))
            self.scheduled_rates.append(float(line[2]))

    def set_time_till(self, year, jday):
        """Set the until the rate is valid.
        """
        self.current_year = year
        self.current_jday = jday

    def get_date(self):
        """Retrieve the current date from w2.
        """
        self.jday = self.w2.jday_converter.make_jday_from_date(
            self.scheduled_dates[self.n])

    def set_current_period(self):
        """Set period for substance addition.
        """
        if self.current_jday > self.jday:
            try:
                if self.old_jday and self.old_jday < self.jday:
                    self.rate = ((self.scheduled_rates[self.n] *
                                  (self.current_jday - self.jday) +
                                  self.scheduled_rates[self.n - 1] *
                                  (self.jday - self.old_jday)) /
                                 (self.current_jday - self.old_jday))
                    self.first = 0
                else:
                    self.rate = self.scheduled_rates[self.n]
            except IndexError:
                self.rate = self.scheduled_rates[self.n]
            self.delta_t = (self.current_jday - self.old_jday) * 86400
            self.n += 1
            self.get_date()
            if  self.current_jday > self.jday:
                print('current_year', self.current_year)
                print('current_jday', self.current_jday)
                print('jday', self.jday)
                print('old_jday', self.old_jday)
                print('delta_t', self.delta_t)
                raise TimeStepError('W2 time step to big. Reduce by %f'
                                    % (self.current_jday - self.old_jday))
        else:
            if not self.first:
                self.rate = self.scheduled_rates[self.n - 1]
                if self.current_jday > self.old_jday:
                    self.delta_t = (self.current_jday - self.old_jday) * 86400
                else:
                    self.delta_t = (self.current_jday - 0) * 86400
        self.old_jday = self.current_jday
        self.old_year = self.current_year

    def get_volume(self):
        """Retrieve volume form w2.
        """
        if self.location[0] == 'top':
            z_index = self.w2.get_shared_data('kt') + 1
        else:
            z_index = self.location[0]
        self.volume = self.w2.get_shared_data('vactive')[z_index,
                                                         self.location[1]]

    def make_substance(self, year, jday):
        """Generate a substance.
        """
        self.set_time_till(year, jday)
        try:
            self.substance.set_volume(self.volume)
        except AttributeError:
            self.substance = Substance(self.volume,
                                       self.molar_masses,
                                       self.molar_ratios)
        self.set_current_period()
        self.substance.set_rate(self.rate, self.unit)
        self.concs = self.substance.get_conc_increase(self.delta_t)

    def add_substance(self, output):
        """Add a substancce to the lake.
        """
        n = 0
        current_masses = {}
        if self.location[0] == 'top':
            z_index = self.w2.get_shared_data('kt') + 1
        else:
            z_index = self.location[0]
        for conc in self.concs:
            name = self.constituents[n]
            constituent_name = '%sssp' % name
            w2_conc = self.w2.get_shared_data(constituent_name)
            w2_conc[z_index, self.location[1]] = conc
            self.w2.set_shared_array_data(constituent_name, w2_conc)
            current_masses[name] = conc * self.volume / 1e6
            self.masses[name] += current_masses[name]
            n += 1
        for name in self.constituents:
            self.total_soda_mass += current_masses[name]
        if output:
            nc_out_file = netCDF4.Dataset(self.output_path, 'r+', format='NETCDF3_CLASSIC')
            try:
                nc_out_file.variables[self.name + 'mass'][-1] = \
                                                self.total_soda_mass
            except KeyError:
                nc_out_file.createVariable(self.name + 'mass', 'd', ('time',))
            nc_out_file.close()


class AllAdditions(object):
    """All additions to one lake.
    """
    def __init__(self,
                 additions,
                 treatment_path,
                 output_path,
                 w2):
        self.additions = additions
        self.treatments = []
        self.w2 = w2
        self.last_rate = 0
        self.output = 1
        for addition in self.additions:
            schedule_file_name = os.path.join(treatment_path,
                                    'schedule_%s.txt' % addition['name'])
            self.treatments.append(Treatment(addition,
                                             schedule_file_name,
                                             output_path,
                                             w2))

    def has_rate(self):
        """Is there a rate currently?
        """
        for treatment in self.treatments:
            if treatment.rate > 0.0:
                return
        return 0

    def add_substances(self, year, step, set_zero):
        """Add all substances.
        """
        if set_zero:
            names = self.w2.w2_proxy.w2_fortran.shared_data.__dict__.keys()
            for variable in names:
                if len(variable) >= 3 and variable[-3:] == 'ssp':
                    self.w2.set_shared_array_data(variable, 0.0)
        for treatment in self.treatments:
            treatment.get_volume()
            treatment.make_substance(year, step)
            treatment.add_substance(self.output)
        rate = self.has_rate()
        if rate or self.last_rate:
            self.last_rate = rate
            return True
        return False


class UnitError(TypeError):
    """Got the wrong unit.
    """
    pass


class TimeStepError(AssertionError):
    """Time step is wrong.
    """
    pass

if __name__ == '__main__':

    def test():
        """Check if it works.
        """
        additions = [{'name':'soda_south',
                      'molar_masses':[22.9898, 12.0111 + 16 * 3],
                      'molar_ratios':[2, 1],
                      'constituents':['na', 'co3'],
                      'location':(10, 3)}]
        treats = AllAdditions(additions,
                              '/tmp/ramdisk0/w2data.nc',
                '/home/mmueller/projects/bockwitz/models/bock1/treatment/soda')
        step = 58.0
        for day in range(155 * 24):  # pylint: disable-msg=W0612
            step += 0.5 / 24.0
            for treat in treats.treatments:
                treat.get_volume()
                treat.make_substance(2002, step)
                print('current: %5.2f \t jday: %5.2f \t old: %5.2f \t'
                       % (treat.current_jday, treat.jday, treat.old_jday),
                       end='')
                print('rate: %5.2f' % treat.rate)

    test()
