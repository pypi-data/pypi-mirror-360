"""Bathymetry visualizer
"""


import sys

import numpy
import netCDF4

import matplotlib.pyplot as plt


class BathVisualizer(object):
    """Visualize the bathymetry. Very simple. No to scale.
    """
    def __init__(self, nc_path):
        self.nc_file = netCDF4.Dataset(nc_path, 'r', format='NETCDF3_CLASSIC')

    def show(self):
        """Show bathymetry
        """
        # NumPy again.
        # pylint: disable-msg= E1101
        active = numpy.where(self.nc_file.variables['cell_width'][:], 0, 1)
        plt.matshow(active)  # , cmap=cm.gray)
        plt.show()


def main(bath_file_name):
    """Show the bathymetry.
    """
    viz = BathVisualizer(bath_file_name)
    viz.show()


if __name__ == '__main__':
    main(sys.argv[1])
