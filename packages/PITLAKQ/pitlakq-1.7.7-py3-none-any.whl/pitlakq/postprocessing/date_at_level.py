"""Find date for water level.
"""

from __future__ import print_function

import datetime
import os

import netCDF4


def find_date(target_level, nc_file='out.nc'):
    """Find date for a certain water table.
    """
    fobj = netCDF4.Dataset(nc_file, mode='r', format='NETCDF3_CLASSIC')
    time_steps = fobj.variables['timesteps']
    levels = fobj.variables['elws']
    steps = fobj.dimensions['time']
    for step in range(len(steps)):
        date = time_steps[step]
        level = levels[step][11]
        if level >= target_level:
            return datetime.datetime(*tuple(date)), step


def get_conc(step, nc_file='out.nc',
             names=os.path.join(os.path.dirname(__file__),
                                '../resources/const_names.txt.'),
             pos=(-10, 7)):
    """Reading the concentration for a given step.
    """
    fobj = open(names)
    header = next(fobj).split()
    key_pos, name_pos, phreeqc_name_pos = [header.index(entry) for  entry in
                                           ['key', 'name', 'phreeqc_name']]
    name_map = {}
    for raw_line in fobj:
        line = raw_line.split()
        if not line:
            continue
        name_map[line[key_pos]] = line[name_pos], line[phreeqc_name_pos]
    fobj = netCDF4.Dataset(nc_file, 'r', format='NETCDF3_CLASSIC')
    for var in fobj.variables:
        if var in name_map:
            print('{1:20s} {2:10s} {0:15.10f}'.format(
                   fobj.variables[var][step][pos[0], pos[1]], *name_map[var]))

if __name__ == '__main__':

    def main():
        """Run the script.
        """
        date, step = find_date(225, 'out.nc')
        print(date, get_conc(step))
