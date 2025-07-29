#!/usr/local/bin/python
# coding: utf-8

# PITLAKQ
# The Pit Lake Hydrodynamic and Water Quality Model
# http://www.pitlakq.com/
# Author: Mike Mueller
# mmueller@hydrocomputing.com
#
# Copyright (c) 2012, Mike Mueller
# All rights reserved.
#
# This software is BSD-licensed.
# See file license.txt for license.

# NumPy, dynamic members.
# pylint: disable-msg=E1101
# pylint: disable-msg=E1103

"""Generation of W2 bathymetry.
"""

from __future__ import print_function

import netCDF4
import numpy
from persistent.cPersistence import Persistent


class Bathymetry:
    """
    Reading and writing bathymetry.
    """
    def __init__(self, bath_file_name):
        self.bath_file_name = bath_file_name

    def write_bath(self, bath_data):
        """
        Writing bathymetry file.
        NetCDF-File.
        """
        bath_file = netCDF4.Dataset(self.bath_file_name, 'w',
                                    'Bathymetry file created by Python program',
                                    format='NETCDF3_CLASSIC')
        bath_file.createDimension('segment_lenght',
                                  len(bath_data['segment_length']))
        bath_file.createDimension('layer_height',
                                  len(bath_data['layer_heights']))
        segment_length = bath_file.createVariable('segment_lenght', 'd',
                                       ('segment_lenght',))
        water_surface_elevation = bath_file.createVariable(
            'starting_water_level', 'd', ('segment_lenght',))
        segment_orientation = bath_file.createVariable(
            'segment_orientation', 'd', ('segment_lenght',))
        layer_heights = bath_file.createVariable('layer_height', 'd',
                                                 ('layer_height',))
        segment_width = bath_file.createVariable(
            'cell_width', 'd', ('layer_height', 'segment_lenght'))
        segment_length[:] = bath_data['segment_length']
        layer_heights[:] = bath_data['layer_heights']
        water_surface_elevation[:] = bath_data['water_surface_elevation']
        segment_orientation[:] = bath_data['segment_orientation']
        segment_width[:] = numpy.transpose(bath_data['segment_width'])
        bath_file.close()

    def read_bath(self):
        """
        Rading bathymetry.
        """
        # pylint: disable-msg=W0201
        bath_file = netCDF4.Dataset(self.bath_file_name, 'r', format='NETCDF3_CLASSIC')
        var = bath_file.variables
        self.segment_length = var['segment_lenght'][:]
        self.water_surface_elevation = var['starting_water_level'][:]
        self.segment_orientation = var['segment_orientation'][:]
        self.layer_heights = var['layer_height'][:]
        self.segment_width = var['cell_width'][:]
        bath_file.close()


class W2SubLake:
    """
    Preprocessing for W2 bathymetry.

    Reads geometry values from SURFER GRD file and own text file with rows and
    columns spacing. Convertes the data into a W2 bathymetry and stores them
    in netCDF file.
    """
    def __init__(self,
                 surfer_file,
                 reservoir_geometry_file,
                 min_width,
                 initial_water_surface,
                 orientation,
                 swapped_x_y):
        self.surfer_file = surfer_file
        self.reservoir_geometry_file = reservoir_geometry_file
        self.min_width = min_width
        self.initial_water_surface = initial_water_surface
        self.orientation = orientation
        self.swapped_x_y = swapped_x_y
        self.bottom_elevation = None

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
        rawinput = fobj.read()
        fobj.close()
        geometry_values = {}
        input_file = rawinput.split()
        if self.swapped_x_y:
            geometry_values['columns'] = int(input_file[2])
            geometry_values['rows'] = int(input_file[1])
            geometry_values['rwfrom'] = float(input_file[5])
            geometry_values['rwto'] = float(input_file[6])
            geometry_values['hwfrom'] = float(input_file[3])
            geometry_values['hwto'] = float(input_file[4])
            geometry_values['zmin'] = float(input_file[7])
            geometry_values['zmax'] = float(input_file[8])
            geometry_values['deltax'] = ((geometry_values['rwto']
                                          - geometry_values['rwfrom'])
                                        / (geometry_values['columns'] - 1))
            geometry_values['deltay'] = ((geometry_values['hwto'] -
                                          geometry_values['hwfrom'])
                                        / (geometry_values['rows'] - 1))
            z = numpy.zeros((geometry_values['columns'],
                             geometry_values['rows']), dtype=float)
            x = numpy.zeros((geometry_values['columns']), dtype=float)
            y = numpy.zeros((geometry_values['rows']), dtype=float)
            x_cumulative = geometry_values['rwfrom']
            y_cumulative = geometry_values['hwfrom']
            for n in range(int(geometry_values['columns'])):
                x[n] = x_cumulative
                x_cumulative = x_cumulative + geometry_values['deltax']
            for m in range(int(geometry_values['rows'])):
                y[m] = y_cumulative
                y_cumulative = y_cumulative + geometry_values['deltay']
            n = 0
            m = 0
            for item in input_file[9:]:
                z[m][n] = float(item)
                n += 1
                if n >= geometry_values['rows']:
                    n = 0
                    m += 1
            z = z.transpose()
        else:
            geometry_values['columns'] = int(input_file[1])
            geometry_values['rows'] = int(input_file[2])
            geometry_values['rwfrom'] = float(input_file[3])
            geometry_values['rwto'] = float(input_file[4])
            geometry_values['hwfrom'] = float(input_file[5])
            geometry_values['hwto'] = float(input_file[6])
            geometry_values['zmin'] = float(input_file[7])
            geometry_values['zmax'] = float(input_file[8])
            geometry_values['deltax'] = ((geometry_values['rwto'] -
                                          geometry_values['rwfrom']) /
                                         (geometry_values['columns'] - 1))
            geometry_values['deltay'] = ((geometry_values['hwto'] -
                                          geometry_values['hwfrom']) /
                                         (geometry_values['rows'] - 1))
            z = numpy.zeros((geometry_values['rows'],
                             geometry_values['columns']), dtype=float)
            x = numpy.zeros((geometry_values['columns']), dtype=float)
            y = numpy.zeros((geometry_values['rows']), dtype=float)
            x_cumulative = geometry_values['rwfrom']
            y_cumulative = geometry_values['hwfrom']
            for n in range(int(geometry_values['columns'])):
                x[n] = x_cumulative
                x_cumulative = x_cumulative + geometry_values['deltax']
            for m in range(int(geometry_values['rows'])):
                y[m] = y_cumulative
                y_cumulative = y_cumulative + geometry_values['deltay']
            n = 0
            m = 0
            for item in input_file[9:]:
                z[m][n] = float(item)
                n += 1
                if n >= geometry_values['columns']:
                    n = 0
                    m += 1
        # pylint: disable-msg=W0201
        self.x = x
        self.y = y
        self.z = z
        self.geometry_values = geometry_values

    def read_geometry_def(self):
        """
        Reading file with geometric specifications.
        See example file for format.
        In:
            reservoir_geometry_file
                own text file with column and row spacing
        Out:
            lake_columns, lake_levels
                numeric arrays with W2 coordiantes
        Side effects:
            none
        """
        input_file = open(self.reservoir_geometry_file)
        geometry = input_file.readlines()
        input_file.close()
        geometry = [item.split() for item in geometry]
        #assign variables to input
        geometry_columns = []
        geometry_zu = []
        for line in geometry:
            if line[0] == 'Columns':
                flag = 'c'
                continue
            elif line[0] == 'Layers':
                flag = 'l'
                continue
            if flag == 'c':
                geometry_columns.append(float(line[1]))
            elif flag == 'l':
                geometry_zu.append(float(line[1]))
        geometry_zu.reverse()  # count from up to down
        # pylint: disable-msg=W0201
        self.lake_columns = numpy.array(geometry_columns)
        self.lake_levels = numpy.array(geometry_zu)

    def create_w2_elements(self):
        """
        Creating width and W2 arrays
        with width and y data for W2 input.
        In:
            surfer_xs, surfer_ys, surfer_zs
                numeric arrays wih coordinates from SURFER file
                produced by readSurferGRD()
            geometry_values
                metadata from SURFER file produced by readSurferGRD()
            lake_columns, lake_levels
                numeric arrays with W2 coordiantes produced by
                read_geometry_def()
        Out:
            width, w2_y
                numeric arrays with element width and y coordinate
                y coordinate is not used in W2 but as third space
                coordinated in for coupling with PCG
            w2_y_Draw
                y position for drawing 3D lake
        Side effects:
            none
        """
        offset_last = 1000
        surfer_xs = self.x
        surfer_ys = self.y
        surfer_zs = self.z
        geometry_values = self.geometry_values
        lake_columns = self.lake_columns
        lake_levels = self.lake_levels.copy()
        self.bottom_elevation = lake_levels[-1]
        # go to the very bottom
        lake_levels[-1] = lake_levels[-1] - offset_last
        min_width = self.min_width
        width = numpy.zeros((len(lake_levels) - 1, len(lake_columns) - 1),
                            dtype=float)
        w2_y = numpy.zeros((len(lake_levels) - 1, len(lake_columns) - 1),
                          dtype=float)
        w2_y_draw = numpy.zeros((len(lake_levels) - 1, len(lake_columns) - 1),
                                dtype=float)
        #min_width_diff = 1.0
        #iterate over all surfer points
        #go through all w2 coordinates
        total_volume = 0
        number_of_levels = len(lake_levels) - 1
        for n_level in range(number_of_levels):
            level_volume = 0
            for n_column in range(len(lake_columns) - 1):
                cell_volume = 0
                y_volume_product_sum = 0
                #go through all surfer x coordinates
                for n_surfer_y in range(len(surfer_ys)):
                    for n_surfer_x in range(len(surfer_xs)):
                        #percentage at the left side of surfer element
                        #   W2-grid
                        #   |_
                        #   |*|surfer element
                        #   |
                        factor_left_level = ((surfer_xs[n_surfer_x] +
                                            geometry_values['deltax'] / 2
                                            - lake_columns[n_column])
                                           / geometry_values['deltax'])
                        #percentage at the rigth side of surfer element
                        #   W2-grid
                        #      _|
                        #     |*|surfer element
                        #      -|
                        factor_right_level = ((lake_columns[n_column + 1] -
                                             (surfer_xs[n_surfer_x] -
                                              geometry_values['deltax'] / 2))
                                            / geometry_values['deltax'])
                        if factor_left_level > 0 and factor_right_level > 0:
                            factor = min(factor_left_level, factor_right_level)
                            if factor > 1:
                                factor = 1
                        else:
                            factor = 0
                        height = min((lake_levels[n_level] -
                                      lake_levels[n_level + 1],
                                      lake_levels[n_level] -
                                      surfer_zs[n_surfer_y, n_surfer_x]))
                        if height < 0:
                            height = 0
                        volume = (factor * geometry_values['deltax']
                                  * geometry_values['deltay'] * height)
                        cell_volume = cell_volume + volume
                        if volume > 0.0:
                        #volume weighted average of y coordinates (midpoint)
##                            yFactor = (volume / ((lake_levels[n_level] -
##                                                    lake_levels[n_level+1])*
##                                               geometry_values['deltax'] *
##                                               geometry_values['deltay']))
                            surfer_y_mean = (surfer_ys[n_surfer_y] +
                                           geometry_values['deltay'] / 2)
                            y_volume_product = surfer_y_mean * volume
                            y_volume_product_sum += y_volume_product
                upper_level = lake_levels[n_level]
                lower_level = lake_levels[n_level + 1]
                if number_of_levels == n_level + 1:
                    lower_level += offset_last
                width[n_level, n_column] = (cell_volume /
                                            ((lake_columns[n_column + 1] -
                                              lake_columns[n_column]) *
                                             (upper_level - lower_level)))
                #print('%2d %2d %10.0f %10.0f' % (n_level, n_column,
                #                                 width[n_level, n_column],
                #                                 cell_volume))
                if cell_volume > 0.0:
                    # is valid for lower border of cell
                    y = (y_volume_product_sum / cell_volume -
                          width[n_level, n_column] / 2)
                if width[n_level, n_column] > 0:
                    w2_y[n_level, n_column] = y
                    w2_y_draw[n_level, n_column] = surfer_y_mean
                level_volume = level_volume + cell_volume
            total_volume = total_volume + level_volume
        # setting cells with width < min_width to zero and adding this width
        # to cell above
        for _ in range(len(width) - 1):     # do recursively
            for n in range(len(width) - 1, 0, -1):
                for m in range(len(width[n]) - 1, -1, -1):
                    if width[n, m] < min_width and width[n, m] > 0.0:
                        width[n - 1, m] += width[n, m]
                        width[n, m] = 0.0
                    if width[n, m] > width[n - 1, m]:
                        if (width[n - 1, m] + width[n, m]) > 2 * min_width:
                            average = (width[n - 1, m] + width[n, m]) / 2.0
                            width[n - 1, m] = average
                            width[n, m] = average  # - min_width_diff
                        else:
                            width[n - 1, m] += width[n, m]
                            width[n, m] = 0.0
        # pylint: disable-msg=W0201
        self.total_volume = total_volume
        if self.orientation == 0.0:         # reverse 2ed axis
            self.width = width[::, ::-1]
            self.w2_y = w2_y[::, ::-1]
            self.w2_y_draw = w2_y_draw[::, ::-1]
        else:
            self.width = width
            self.w2_y = w2_y
            self.w2_y_draw = w2_y_draw

    def w2_y_real_to_model_w2_y(self):
        """
        Volume weighted position of elements may
        produce odd looking y-coordinates. Since W2 does NOT
        have a y-diretion they have to be adjusted,
        that elements are always connected with elements above them.
        --> So no lakes that widen when they get lower are created and
        no caves will occured.
        In:
            w2_y_real, width
                numeric arrays as retruned by create_w2_elements()
            lake_columns, lake_levels
                numeric arrays with W2 coordiantes produced by
                read_geometry_def()
        Out:
            w2_y
                numeric array with model adjusted y
        """
        w2_y = self.w2_y
        width = self.width
        lake_columns = self.lake_columns
        lake_levels = self.lake_levels
        w2_y_real = self.w2_y[:]
        for n_level in range(len(lake_levels) - 2):
            for n_column in range(len(lake_columns) - 1):
                try:
                    w2_y_real[n_level, n_column]
                except:
                    print(n_level, n_column)
                    raise
                #w2_y_real[n_level + 1, n_column]
                if w2_y_real[n_level, n_column] > w2_y_real[n_level + 1,
                                                            n_column]:
                    w2_y[n_level + 1, n_column] = w2_y_real[n_level, n_column]
                if (w2_y_real[n_level, n_column] + width[n_level, n_column] <
                    w2_y_real[n_level + 1, n_column] + width[n_level + 1,
                                                           n_column]):
                    w2_y[n_level + 1, n_column] = (w2_y_real[n_level, n_column]
                                                + width[n_level, n_column]
                                                - width[n_level + 1, n_column])
        self.w2_y = w2_y

    def make_bathymetry(self):
        """
        Main method producing bathymetry.
        In:
            surfer_file
                gridded file from SURFER
            reservoir_geometry_file
                own text file with column and row spacing
        Out:
            width, w2_y
                numeric arrays with element width an y coordinate
                y coordinate is not used in W2 but as third space
                coordinated in for coupling with PCG
            lakeCoumns, lake_levels
                numeric arrays with W2 coordiantes
        Side effects:
            none
        """

        self.read_surfer_grd_file()
        self.read_geometry_def()
        self.create_w2_elements()
        #self.w2_y_real_to_model_w2_y()


class W2Lake(Persistent):
    """
    Preprocessing for bathymetry
    from SURFER GRD file und own text file
    with rows and columns spacing.
    output file can be used with win2d
    """
    def __init__(self,
                 surfer_files,
                 reservoir_geometry_files,
                 bath_file_name,
                 min_width,
                 initial_water_surface,
                 orientations,
                 names,
                 swapped_x_y):
        self.surfer_files = surfer_files
        self.reservoir_geometry_files = reservoir_geometry_files
        self.bath_file_name = bath_file_name
        self.min_width = min_width
        self.initial_water_surface = initial_water_surface
        self.orientations = orientations
        self.names = names
        self.swapped_x_y = swapped_x_y
        self.sub_bathymetries = []

    def make_bathymetry(self):
        """Calculate the bathymetry.
        """
        n = 0
        total_volume = 0.0
        bottom_elevation  = 1e300
        for reservoir_geometry_file in self.reservoir_geometry_files:
            surfer_file = self.surfer_files[n]
            orientation = self.orientations[n]
            if orientation not in [0.0, 1.57]:
                self.swapped_x_y = True
            sub_lake = W2SubLake(surfer_file,
                                 reservoir_geometry_file,
                                 self.min_width,
                                 self.initial_water_surface,
                                 orientation,
                                 self.swapped_x_y)
            sub_lake.make_bathymetry()
            self.sub_bathymetries.append(sub_lake)
            print('total_volume %s = %16.12f Mio m3' % (
                self.names[n], sub_lake.total_volume / 1e6))
            total_volume += sub_lake.total_volume
            n += 1
        print('total_volume entire lake= %16.12f Mio m3' % (total_volume / 1e6))


    def write_bath_nc(self):
        """
        Write bathymetry to netCDF-file.
        """
        zu = self.sub_bathymetries[0].lake_levels
        layer_heights = [1.0]
        n = 0
        for level in zu[:-1]:
            layer_heights.append(level - zu[n + 1])
            n += 1
        layer_heights.append(1.0)
        bath_nc = Bathymetry(self.bath_file_name)
        segment_length = []
        segment_orientation = []
        n = 0
        for bath in self.sub_bathymetries:
            segment_length.append(100.0)
            segment_orientation.append(9.99)
            m = 0
            for col in bath.lake_columns[:-1]:
                segment_length.append(bath.lake_columns[m + 1] - col)
                segment_orientation.append(self.orientations[n])
                m += 1
            n += 1
            segment_length.append(100.0)
            segment_orientation.append(9.99)
        x_dim = len(segment_length)
        z_dim = (len(layer_heights))
        # initial
        water_surface_elevation = x_dim * [self.initial_water_surface]
        w2_width = numpy.zeros((x_dim, z_dim),  dtype=float)
        first_column = 1
        last_column = 0
        for sub_lake in self.sub_bathymetries:
            last_column = first_column + sub_lake.width.shape[1]
            w2_width[first_column:last_column, 1:-1] = numpy.transpose(
                numpy.array(sub_lake.width))
            first_column = last_column + 2
        surface_area = w2_width[1:-1, 1] * segment_length[1:-1]
        print('surface_area', sum(surface_area))
        bottom_index = 0
        for segment in w2_width[1:-1]:
            for index, layer in enumerate(segment[1:], 1):
                if layer == 0:
                    bottom_index = max(bottom_index, index)
                    break
        bottom_elevation = zu[bottom_index -1]
        print(f'set bottom_elevation to: {bottom_elevation:.2f}')
        bath_data = {'segment_length': segment_length,
                     'layer_heights': layer_heights,
                     'water_surface_elevation': water_surface_elevation,
                     'segment_orientation': segment_orientation,
                     'segment_width': w2_width}
        bath_nc.write_bath(bath_data)
