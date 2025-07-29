"""Show cell layout with active and inactive
cells.
"""


import pylab
import numpy
import netCDF4

ACTIVE_COLOR = 'white'
INACTIVE_COLOR = 'gray'

# NumPy again.
# pylint: disable-msg=E1101


class DiscritizatonDisplay(object):
    """Show discritatzion of bathymetry.
    """
    def __init__(self, bath_file_name, bottom=None, column_order=None,
                 properties=None):
        self.bath_file_name = bath_file_name
        self.bottom = bottom
        self.column_order = column_order
        properties = {} if properties is None else properties
        allowed_proterties = set(['xlabel', 'ylabel', 'xoffset', 'linewidth',
                                 'edgecolor'])
        given_properties = set(properties.keys())
        unkown = given_properties - allowed_proterties
        if unkown:
            print('Found unknown properties (ignoring):')
            for entry in sorted(unkown):
                print(' ' * 4,  entry)
            print('Allowed properties are:')
            for entry in sorted(allowed_proterties):
                print(' ' * 4,  entry)
        self.xlabel = properties.get('xlabel', 'Horizontal dimension in m')
        self.ylabel = properties.get('ylabel', 'm ADH')
        self.xoffset = properties.get('xoffset', 0.0)
        self.linewidth = properties.get('linewidth', 0.1)
        self.edgecolor = properties.get('edgecolor', 'k')
        self._read_netcdf()
        self._find_grid_bottom()

    def _read_netcdf(self):
        """Read data from bath.nc
        """
        # pylint: disable-msg=W0201
        nc_file = netCDF4.Dataset(self.bath_file_name, 'r',
                                  format='NETCDF3_CLASSIC')
        self.dxs = nc_file.variables['segment_lenght'][:]
        if self.column_order:
            self.dxs = numpy.take(self.dxs, self.column_order)
        self.dzs = nc_file.variables['layer_height'][::-1]
        width = nc_file.variables['cell_width'][:]
        if self.column_order:
            width = numpy.take(width, self.column_order, 1)
        width = width.transpose()
        self.width = width[:, ::-1]
        nc_file.close()

    def _find_grid_bottom(self):
        """Find elevation where the grid starts
        """
        if self.bottom is None:
            self.bottom = 0.0
            return
        self.bottom -= 1 # Add one layer for the inactive BC layer.

    def show(self):
        """Show bathymetry with matplotlib.
        """
        len_dx = len(self.dxs)
        bottom = self.bottom
        pos = numpy.add.accumulate(self.dxs) + self.xoffset
        pos[1:] = pos[:-1]
        pos[0] = self.xoffset

        for row, dzi in enumerate(self.dzs):
            color = numpy.where(self.width[:, row] > 0.01, ACTIVE_COLOR,
                                INACTIVE_COLOR)
            color = [str(entry) for entry in color]
            height = [dzi] * len_dx
            pylab.bar(pos, height, self.dxs, bottom=bottom, color=color,
                      linewidth=self.linewidth, edgecolor=self.edgecolor,
                      align='edge')
            bottom += dzi
        axis = pylab.gca()
        axis.set_xlabel(self.xlabel)
        axis.set_ylabel(self.ylabel)
        pylab.show()


def main(bath_path, bottom, column_order=None, properties=None):
    """Display the bathymetry.
    """
    dis = DiscritizatonDisplay(bath_path, bottom, column_order, properties)
    dis.show()


if __name__ == '__main__':
    def test():
        """See if it works.
        """
        main(r'c:\Daten\Mike\tmp\ptest\models\pitlakq_test\preprocessing'
             r'\output\bath.nc', bottom=150.0)
        # ,
        #     column_order=[0, 1, 2, 3, 4, 5, 6, 7, 16, 15, 14, 13, 12, 11, 10,
        #                   17, 8, 9])

    test()
