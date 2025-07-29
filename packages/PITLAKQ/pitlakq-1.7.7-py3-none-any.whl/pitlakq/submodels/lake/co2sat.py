"""CO2 saturation in netCDF file.
"""

from __future__ import print_function

import sys

# NumPy, dynamic members.
# pylint: disable-msg=E1101
# ph is a good name.
# pylint: disable-msg=C0103

import netCDF4


class CO2Sat:
    """Access to netCDF file with stored values for CO2 saturation
    concentrations as function of temperature and pH-value.
    """

    def __init__(self, co2_sat_file_name):
        self.co2_sat_file_name = co2_sat_file_name
        self.read_file()

    def read_file(self):
        """Read the netCDF file.
        """
        # Create attributes here.
        # pylint: disable-msg=W0201
        self.fobj = netCDF4.Dataset(self.co2_sat_file_name, 'r',
                                    format='NETCDF3_CLASSIC')
        co2_sat = self.fobj.variables['co2Sat']
        p_co2 = self.fobj.variables['pCO2']
        temp = self.fobj.variables['temp']
        ph = self.fobj.variables['ph']
        self.co2_sat = co2_sat[:]
        self.p_co2_min = float(p_co2[0])
        self.p_co2_max = float(p_co2[1])
        self.p_co2_step_size = float(p_co2[2])
        self.temp_min = float(temp[0])
        self.temp_max = float(temp[1])
        self.temp_step_size = float(temp[2])
        self.ph_min = float(ph[0])
        self.ph_max = float(ph[1])
        self.ph_step_size = float(ph[2])
        self.fobj.close()

    def get_co2_sat(self, p_co2, temp, ph):
        """Read one value.
        """
        if p_co2 > self.p_co2_max or p_co2 < self.p_co2_min:
            print('error')
            print('partial pressure out of bounds')
            print('must be between %f and %f' % (self.p_co2_min,
                                                 self.p_co2_max))
            self.print_error(p_co2, temp, ph)
            sys.exit()
        if temp > self.temp_max:
            print('error')
            print('temperature out of bounds')
            print('must be < %f' % self.temp_max)
            self.print_error(p_co2, temp, ph)
            sys.exit()
        if temp < self.temp_min:
            temp = self.temp_min
        if ph > self.ph_max:
            ph = self.ph_max
        if ph < self.ph_min:
            ph = self.ph_min
        p_co2_pos = int((p_co2 - self.p_co2_min) / self.p_co2_step_size)
        temp_pos = int((temp - self.temp_min) / self.temp_step_size)
        ph_pos = int((ph - self.ph_min) / self.ph_step_size)
        if ph_pos > 696: # There are missing values in netCDF file.
            ph_pos = 696
        return min(self.co2_sat[p_co2_pos, temp_pos, ph_pos], 110.0)

    @staticmethod
    def print_error(p_co2, temp, ph):
        """Show the wrong values.
        """
        print('p_co2: ', p_co2)
        print('temp: ', temp)
        print('pH: ', ph)

if __name__ == '__main__':

    def test():
        """Check if it works.
        """
        sat = CO2Sat('../../resources/co2sat.nc')
        print(sat.get_co2_sat(370, 0.0, 2.02))
        print(sat.get_co2_sat(370, 0.0, 7.02))
        print(sat.get_co2_sat(410, 0.0, 8.9))

    test()
