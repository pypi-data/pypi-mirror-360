"""
Assining ID for polygons on a regular grid.
I.e. gridding of polygons.
No negative coordinates supported!!!
"""

# NumPy, dynamic members.
# pylint: disable-msg=E1101

from __future__ import print_function

import os
import sys

import numpy


class Polygon(object):
    """A polygon with x and y coordinates.
    """

    def __init__(self, x_coords, y_coords):
        if len(x_coords) != len(y_coords):
            raise IndexError('Number of x and y coordinates must be equal.')
        self.x_coords = x_coords
        self.y_coords = y_coords
        self.number_of_points = len(self.x_coords)
        self.range_of_points = range(self.number_of_points)
        self.determine_center()

    def __repr__(self):
        return '\n\tx: %s\n\ty: %s\n' % (repr(self.x_coords),
                                         repr(self.y_coords))

    def determine_center(self):
        """Find the cenzter coordinate.
        """
        # Define attributes here.
        # pylint: disable-msg=W0201
        self.mean_x = sum(self.x_coords) / self.number_of_points
        self.mean_y = sum(self.y_coords) / self.number_of_points

    def contains_point(self, x, y):
        """Check if point is inside the polygon.
        """
        contains = False
        j = self.number_of_points - 1
        for i in self.range_of_points:
            if ((self.y_coords[i] <= y < self.y_coords[j] or
                 self.y_coords[j] <= y < self.y_coords[i])
                 and
                 (x < (self.x_coords[j] - self.x_coords[i]) *
                  (y - self.y_coords[i]) /
                  (self.y_coords[j] - self.y_coords[i]) + self.x_coords[i])):
                contains = not contains
            j = i
        return contains


class Grid(object):
    """Grid with all polygons.
    """

    def __init__(self, x_min, y_min, x_max, y_max, delta_x, delta_y, dir_,
                 z=None, water_level=None, use_names_as_ids=False):
        self.x_coords = numpy.arange(x_min, x_max, delta_x)#[:-1]
        self.y_coords = numpy.arange(y_min, y_max, delta_y)#[:-1]
        self.delta_x = delta_x
        self.delta_y = delta_y
        self.use_names_as_ids = use_names_as_ids
        if z is None:
            self.z = numpy.zeros((self.x_coords.shape[0],
                                  self.y_coords.shape[0]))
            self.water_level = 9999999
        else:
            self.z = numpy.transpose(z)
            self.water_level = water_level
        if self.water_level is None:
            self.water_level = 9999999
        self.dir = dir_
        do_check = 1
        if do_check:
            check = ''
            epsilon = 1e-5
            if (self.x_coords[-1] + delta_x < x_max -epsilon
                or self.x_coords[-1] + delta_x > x_max +epsilon):
                check = 'x'
            if (self.y_coords[-1] + delta_y < y_max -epsilon
                or self.y_coords[-1] + delta_y > y_max +epsilon):
                check += 'y'
            if check:
                for case in check:
                    print('Warning: delta%s' % case.upper(), end='')
                    print('does not divide distance between', end='')
                    print('%sMin and %sMax in equal parts' % (case, case))
                    print(y_min, y_max)
        self.polygon_ids = numpy.zeros((self.z.shape))
        self.polygons = {}
        self.read_all_polygons()
        self.assign_ids()

    def read_polygon(self, name):
        """Read data for one polygon.
        """
        file_name = os.path.join(self.dir, name + '.pol')
        fobj = open(file_name)
        data = fobj.readlines()
        fobj.close()
        x_poly = []
        y_poly = []
        n = 0
        for line in data:
            if line[0] != '#':
                new_line = line.split()
                try:
                    x_poly.append(float(new_line[0]))
                    y_poly.append(float(new_line[1]))
                except ValueError:
                    print('Error reading file % s' % file_name)
                    print('at line %d' % n)
            n += 1
        self.polygons[name] = Polygon(x_poly, y_poly)

    def read_all_polygons(self):
        """Read data for all polygons.
        """
        # Define attributes here.
        # pylint: disable-msg=W0201
        fobj = open(os.path.join(self.dir, 'polygons.txt'))
        data = fobj.readlines()
        fobj.close()
        self.names = ['empty']
        self.colors = ['white']
        self.style = ['none']
        if self.use_names_as_ids:
            self.name_ids = [0]
        for line in data:
            if line[0] != '#':
                new_line = line.split()
                self.names.append(new_line[0])
                self.colors.append(new_line[1])
                self.style.append(' '.join(new_line[2:]))
                if self.use_names_as_ids:
                    self.name_ids.append(int(new_line[0]))
        for name in self.names[1:]:
            self.read_polygon(name)

    def assign_ids(self):
        """Assign IDs to polgons.
        """
        i = 0
        for x in self.x_coords:
            j = 0
            for y in self.y_coords:
                if self.z[i, j] < self.water_level:
                    n = 1
                    for poly_name in self.names[1:]:
                        if self.polygons[poly_name].contains_point(x, y):
                            if self.use_names_as_ids:
                                self.polygon_ids[i, j] = self.name_ids[n]
                            else:
                                self.polygon_ids[i, j] = n
                            break
                        n += 1
                j += 1
            i += 1

## This needs to be reprogrammed with matplotlib.
##    def showGrid(self, file_name = ''):
##        import biggles
##        p = biggles.FramedPlot()
##        #p.title = "Grid"
##        p.xlabel = r"$RW$"
##        p.ylabel = r"$HW$"
##        p.xrange = (min(self.x_coords) - self.delta_x/2, max(self.x_coords)
##            + self.delta_x/2)
##        p.yrange = (min(self.y_coords) - self.delta_y/2, max(self.y_coords)
##            + self.delta_y/2)
##        p.aspect_ratio = (p.yrange[1] -p.yrange[0])/(p.xrange[1]-p.xrange[0])
##        i = 0
##        for x in self.x_coords:
##            j = 0
##            for y in self.y_coords:
##                a = biggles.Points( [x], [y],
##                                    type=self.style[self.polygon_ids[i,j]],
##                                    symbolsize = 2,
##                                  color = self.colors[self.polygon_ids[i,j]])
##                p.add(a)
##                j += 1
##            i += 1
##        n = 1
##        areas = []
##        for name in self.names[1:]:
##            a = biggles.Points( [x], [y], type=self.style[n],
##                                    color = self.colors[n])
##
##            a.label = name
##            areas.append(a)
##            n += 1
##        legend1 = biggles.PlotKey(.05, .95 , areas[:4])
##        legend2 = biggles.PlotKey(.25, .95 , areas[4:])
##        p.add(legend1, legend2)
##        p.frame1.ticklabels_style['fontsize'] =1
##
##        p.show()
##        if not file_name:
##            file_name = 'figure.eps'
##        p.write_eps(file_name)

if __name__ == '__main__':

    def test():
        """Tes if it works.
        """
        import pitlakq.metamodel.configuration.getconfig as getconfig

        if len(sys.argv) < 2:
            print('please give project name as command line argument')
            sys.exit()
        else:
            project_name = sys.argv[1]
        dirn = os.path.dirname
        root_path = dirn(dirn(dirn(dirn(os.path.abspath(__file__)))))
        config = getconfig.get_yaml_config(project_name, root_path)
        import surfergrid
        grid = surfergrid.SurferGrid(config.grid_file_name)
        grid.read_surfer_grd__file()
        x_min = grid.geometry_values['rwfrom']
        y_min = grid.geometry_values['hwfrom']
        x_max = grid.geometry_values['rwto'] + grid.geometry_values['delta_x']
        y_max = grid.geometry_values['hwto'] + grid.geometry_values['delta_y']
        delta_x = grid.geometry_values['delta_x']
        delta_y = grid.geometry_values['delta_y']
        print('delta_x', delta_x)
        print('delta_y', delta_y)
        z = grid.geometry_values['z']
        water_level = 125
        my_grid = Grid(x_min, y_min, x_max, y_max, delta_x, delta_y,
                      config.polygonsPath, z, water_level)
        print(my_grid)
        #my_grid.show_grid()

    test()
