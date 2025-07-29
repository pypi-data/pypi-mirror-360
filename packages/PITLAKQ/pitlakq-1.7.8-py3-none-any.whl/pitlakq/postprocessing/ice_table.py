"""Process ice output.
"""

import datetime

import netCDF4
import numpy

class Ice(object):
    """Process ice output.
    """

    def __init__(self, nc_path):
        self.nc_file = netCDF4.Dataset(nc_path, 'r', format='NETCDF3_CLASSIC')
        self.calculated_dates = []
        self.calculated_values = []
        self.met_values = {}
        self.add_met = False
        self.statistics = {}


    def read_calculated(self):
        """Read calculated ice level and dates.
        """
        self.calculated_dates = [datetime.datetime(*value[:-1]) for value in
                                self.nc_file.variables['timesteps'][:]]
        variables = self.nc_file.variables
        for index in range(len(variables['iceth'])):
            values = variables['iceth'][index]
            vactive = variables['vactive'][index]
            mask = numpy.sum(vactive, axis=0).astype(bool)
            values = values[mask]
            if len(values) == 0:
                self.calculated_values.append(
                    {'min': 0.0, 'max': 0.0, 'avg': 0.0})
            else:
                self.calculated_values.append(
                                      {'min': numpy.min(values),
                                       'max': numpy.max(values),
                                       'avg': numpy.mean(values)})
        self.nc_file.close()

    def read_met(self, met_file_name):
        """Read air temperature.
        """

        def get_date(str_date):
            """Convert a date string into a date.
            """
            return datetime.date(*datetime.datetime.strptime(
                                   str_date, '%d.%m.%Y').timetuple()[:3])

        self.add_met = True
        start_date = datetime.date(*self.calculated_dates[0].timetuple()[:3])
        end_date = datetime.date(*self.calculated_dates[-1].timetuple()[:3])
        end_date += datetime.timedelta(days=2)
        with open(met_file_name) as fobj:
            header = next(fobj).split()
            pos = dict((name, index) for index, name in enumerate(header))
            for raw_line in fobj:
                line = raw_line.split()
                date = get_date(line[pos['date']])
                if date == start_date:
                    temp_sum = float(line[pos['air_temperature']])
                    old_date = date
                    counter = 1
                    break
            for raw_line in fobj:
                line = raw_line.split()
                date = get_date(line[pos['date']])
                if start_date <= date <= end_date:
                    if date == old_date:
                        temp_sum += float(line[pos['air_temperature']])
                        counter += 1
                    else:
                        self.met_values[old_date] = temp_sum / counter
                        temp_sum = 0.0
                        counter = 0
                    old_date = date

    def calc_ice_periods(self):

        def average_date(dates):
            normalized_dates = [datetime.date(2000, date.month, date.day) for
                                date in dates]
            if len(normalized_dates) == 0:
                return (None, None)
            mean_date = datetime.date.fromordinal(
                sum(date.toordinal() for date in normalized_dates) /
                len(normalized_dates))
            return mean_date.month, mean_date.day

        freeze_over_dates = {}
        ice_free_dates = {}
        for date, value in zip(self.calculated_dates, self.calculated_values):
            if date.month == 1:
                ice_free_count = 0
                ice_count = 0
            if not value['max'] and 1 < date.month < 8:
                ice_free_count += 1
            if value['min'] and date.month > 8:
                ice_count += 1
            if ice_free_count > 3 and date.year not in ice_free_dates:
                ice_free_dates[date.year] = datetime.date(*date.timetuple()[:3])
                ice_count = 0
                ice_free_count = 0
            if (ice_count > 3 and
                date.year not in freeze_over_dates and
                date.year in ice_free_dates):
                freeze_over_dates[date.year] = datetime.date(
                                                        *date.timetuple()[:3])
                ice_count = 0
                ice_free_count = 0
        self.statistics = {'ice_free_dates': ice_free_dates,
                           'freeze_over_dates': freeze_over_dates,
                           'mean_ice_free_date':
                               average_date(ice_free_dates.values()),
                           'mean_freeze_over_date':
                               average_date(freeze_over_dates.values())
                           }


    def write_ice(self, out_file_name):
        """Write the values to a text file.
        """
        fobj = open(out_file_name, 'w')
        fobj.write('date        average   min     max ice thickness')
        if self.add_met:
            fobj.write('%30s' % 'mean air temperature')
        fobj.write('\n')
        for datet, value in zip(self.calculated_dates,
                               self.calculated_values):
            date = datetime.date(*datet.timetuple()[:3])
            fobj.write('%s' % date.strftime('%d.%m.%Y'))
            fobj.write('%8.2f' % value['avg'])
            fobj.write('%8.2f' % value['min'])
            fobj.write('%8.2f' % value['max'])
            if self.add_met:
                fobj.write('%30.2f' % self.met_values[date])
            fobj.write('\n')


def main(nc_path, out_file_name='ice.txt', met_file_name=None):
    """
    Make table with ice thickness over time.
    """
    ice = Ice(nc_path)
    ice.read_calculated()
    if met_file_name:
        ice.read_met(met_file_name)
    ice.write_ice(out_file_name)
    ice.calc_ice_periods()
    import pprint
    pprint.pprint(ice.statistics)

if __name__ == '__main__':
    main(r'c:\Daten\Mike\projekte\models\kami\output\w2\out.nc',
         r'c:\Daten\Mike\projekte\models\kami\postprocessing\ice.txt')#,
         #r'c:\Daten\Mike\projekte\models\kami\input\w2\meteorology.txt')
