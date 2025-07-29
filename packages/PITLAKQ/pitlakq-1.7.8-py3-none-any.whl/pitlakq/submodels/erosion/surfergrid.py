"""Read a surfer ASCII grid.
"""



# NumPy, dynamic members.
# pylint: disable-msg=E1101
# Some attributes defined outside __init__.
# pylint: disable-msg=W0201

import numpy


class SurferGrid:
    """A Surfer grid.
    """

    def __init__(self, surfer_file):
        self.surfer_file = surfer_file

    def read_surfer_grd_file(self):
        """
        Reading Surfer GRD file:
        x, y, z
        In:
            surfer_file
                gridded file from SURFER
        Out:
            x, y ,z
                numeric arrays with coordinates
            geometry_values
                dict with metadata ('#x, min, max etc)
        Side effect:
            none
        """
        fobj = open(self.surfer_file)
        data = fobj.read().split()
        fobj.close()
        geometry_values = {}
        geometry_values['columns'] = float(data[1])
        geometry_values['rows'] = float(data[2])
        geometry_values['rwfrom'] = float(data[3])
        geometry_values['rwto'] = float(data[4])
        geometry_values['hwfrom'] = float(data[5])
        geometry_values['hwto'] = float(data[6])
        geometry_values['zmin'] = float(data[7])
        geometry_values['zmax'] = float(data[8])
        geometry_values['delta_x'] = ((geometry_values['rwto'] -
                                       geometry_values['rwfrom'])
                                      /(geometry_values['columns'] - 1))
        geometry_values['delta_y'] = ((geometry_values['hwto'] -
                                       geometry_values['hwfrom'])
                                      /(geometry_values['rows']-1))
        z = numpy.zeros((geometry_values['rows'], geometry_values['columns']),
                        numpy.float64)
        x = numpy.zeros((geometry_values['columns']), numpy.float64)
        y = numpy.zeros((geometry_values['rows']), numpy.float64)
        x_cumulative = geometry_values['rwfrom']
        y_cumulative = geometry_values['hwfrom']
        for n in range(int(geometry_values['columns'])):
            x[n] = x_cumulative
            x_cumulative = x_cumulative + geometry_values['delta_x']
        for m in range(int(geometry_values['rows'])):
            y[m] = y_cumulative
            y_cumulative = y_cumulative + geometry_values['delta_y']
        n = 0
        m = 0
        for item in data[9:]:
            z[m][n] = float(item)
            n += 1
            if n >= geometry_values['columns']:
                n = 0
                m = m+1
        geometry_values['x'] = x
        geometry_values['y'] = y
        geometry_values['z'] = z
        geometry_values['delta_x'] = x[1] - x[0]
        geometry_values['delta_y'] = y[1] - y[0]
        geometry_values['x_dim'] = geometry_values['x'].shape[0]
        geometry_values['y_dim'] = geometry_values['y'].shape[0]
        geometry_values['range_x_dim'] = range(geometry_values['x_dim'])
        geometry_values['range_y_dim'] = range(geometry_values['y_dim'])
        geometry_values['cell_area'] = (geometry_values['delta_x'] *
                                        geometry_values['delta_y'])
        self.geometry_values = geometry_values

    def geometry_lake(self, waterlevel):
        """Create the lake geometry.
        """
        compare_array = (
            numpy.zeros((self.geometry_values['rows'],
                         self.geometry_values['columns']), numpy.float64) +
            waterlevel)
        self.geometry_values['result'] = numpy.greater_equal(
            self.geometry_values['z'], compare_array)
        self.geometry_values['isLake'] = numpy.where(compare_array, 1, 0)

    def total_grid_volumne(self):
        """Calcualte the total volume.
        """
        total_volume = 0
        volume = 0
        for i in self.geometry_values['range_y_dim']:
            for j in self.geometry_values['range_x_dim']:
                z_diff = float(self.geometry_values['z'][i, j])
                if z_diff > 10000:
                    continue                 # inactive above very high level
                volume = (z_diff * self.geometry_values['delta_x'] *
                          self.geometry_values['delta_y'])
                total_volume = total_volume + volume
        self.total_volume = total_volume
        self.total_mass = (self.total_volume * 1.8) / 1000000
