"""Water level visualizer.
"""

import datetime

import matplotlib.pyplot as plt
import netCDF4

from pitlakq.postprocessing.error_statistics import ame, rms


class LevelVisualizer(object):
    """Show the water levels in a graph.
    """

    def __init__(self, nc_path, measured_values_path, lake_name,
                 out_file=None, show_errors=True):
        if not measured_values_path:
            show_errors = False
        self.nc_file = netCDF4.Dataset(nc_path, 'r', format='NETCDF3_CLASSIC')
        self.measured_values_path = measured_values_path
        self.lake_name = lake_name
        self.out_file = out_file
        self.show_errors = show_errors
        self.measured_dates = None
        self.measured_values = None
        self.calculated_dates = None
        self.calculated_values = None

    def read_calculated(self):
        """Read calculated water level and dates.
        """
        self.calculated_dates = [datetime.datetime(*value[:-1]) for value in
                                self.nc_file.variables['timesteps'][:]]
        self.calculated_values = [value[6] for value in
                                 self.nc_file.variables['elws'][:]]
        self.nc_file.close()
        if self.out_file:
            fobj = open(self.out_file, 'w')
            fobj.write('date     waterlevel\n')
            for date, level in zip(self.calculated_dates,
                                   self.calculated_values):
                fobj.write('%s  %8.2f\n' % (date.strftime('%d.%m.%Y'), level))

    def read_measured(self):
        """Read measured water level and dates.
        """
        if self.measured_values_path:
            fobj = open(self.measured_values_path)
            raw_data = [line.split() for line in fobj.readlines()]
            self.measured_dates = [datetime.datetime.strptime(
                                line[0], '%d.%m.%Y') for line in raw_data[1:]]
            self.measured_values = [float(line[1]) for line in raw_data[1:]]
        else:
            self.measured_values = None

    def show(self, loc=None):
        """Show level
        """
        if self.measured_values:
            plt.plot(self.measured_dates, self.measured_values, '-*',
                     self.calculated_dates, self.calculated_values)
            plt.legend(('measured', 'calculated'), loc=loc)
        else:
            plt.plot(self.calculated_dates, self.calculated_values)
            plt.legend(['calculated'], loc=loc)

        plt.xlabel('Date')
        plt.ylabel('Water level m AHD')
        #plt.ylabel('Water level deviation in m')
        plt.title('Water Level of Lake %s - Measured vs. Calculated'
                  % self.lake_name)
        if self.show_errors:
            calculated_values = []
            measured_days = [(date.year, date.month, date.day) for date in
                             self.measured_dates]
            calculated_days_index = {}
            for index, date in enumerate(self.calculated_dates):
                calculated_days_index[(date.year, date.month, date.day)
                                      ] = index
            for day in measured_days:
                index = calculated_days_index[day]
                calculated_values.append(self.calculated_values[index])
            ame_value = ame(self.measured_values, calculated_values)
            rms_value = rms(self.measured_values, calculated_values)
            plt.figtext(0.7, 0.7, 'AME = %5.2f\nRMS = %5.2f' %
                        (ame_value, rms_value))
        plt.show()


def main(nc_path, measured_values_path=None, lake_name='My Lake',
         out_file=None, show_errors=True, loc=None):
    """
    Show graph with measured and calculated water levels.
    """
    viz = LevelVisualizer(nc_path, measured_values_path, lake_name, out_file,
                          show_errors)
    viz.read_measured()
    viz.read_calculated()
    viz.show(loc=loc)

if __name__ == '__main__':
     main(r'c:\Daten\Mike\tmp\ptest\models\pitlakq_test\output\w2\out.nc',
          lake_name='Tutorial Test Lake')