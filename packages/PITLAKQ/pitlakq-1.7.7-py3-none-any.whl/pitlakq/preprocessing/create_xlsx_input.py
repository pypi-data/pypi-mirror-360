# coding: utf-8

"""Tool for creating an Excel for gw zones.
"""

from __future__ import print_function, unicode_literals

from itertools import cycle
import os
from os.path import exists, join
try:
    from string import uppercase  # pylint: disable-msg=W0402
except ImportError:
    from string import ascii_uppercase as uppercase

import netCDF4
import xlsxwriter

from pitlakq.commontools.input.bathhelper import make_bottom
from pitlakq.metamodel.configuration.getconfig import read_dot_pitlakq


class XLSXRepresentation(object):
    """Excel file in 2007 format for gw inflow zones.
    """
    def __init__(self, bath_nc, xlsx_file_name, w2_yaml):
        self.bath_file = netCDF4.Dataset(bath_nc, 'r',
                                         format='NETCDF3_CLASSIC')
        self.workbook = xlsxwriter.Workbook(xlsx_file_name)
        self.layer_bottoms = make_bottom(bath_nc, w2_yaml)
        self.bold = self.workbook.add_format()
        self.bold.set_bold()

    def create_xlsx(self):
        """Create the file.
        """
        self.add_zones()
        self.add_flow()
        self.add_conc()
        self.workbook.close()

    def add_zones(self):
        """Add 2D "graphic".
        """
        variables = self.bath_file.variables
        segment_lenght = variables['segment_lenght'][:]
        layer_height = variables['layer_height'][:]
        width = variables['cell_width'][:]
        letter_pool = cycle(uppercase)
        left_col = next(letter_pool)
        layer_indices = range(len(layer_height))
        cell_letters = [next(letter_pool) for _x in segment_lenght]
        worksheet = self.workbook.add_worksheet('Zones')

        unlocked = self.workbook.add_format({'locked': 0})
        unlocked.set_border(1)
        unlocked.set_border_color('black')
        gray = self.workbook.add_format()
        gray.set_bg_color('gray')
        gray.set_border(1)
        gray.set_border_color('black')
        silver = self.workbook.add_format()
        silver.set_bg_color('silver')
        silver.set_border(1)
        silver.set_border_color('black')
        worksheet.protect()
        worksheet.write(0, 0, 'bottom', self.bold)
        worksheet.write(0, len(cell_letters) + 1, 'segments', self.bold)
        for index, letter in enumerate(cell_letters, 1):
            worksheet.write('{0}1'.format(letter), index, silver)
        for index, height in enumerate(self.layer_bottoms, 2):
            worksheet.write('{0}{1:d}'.format(left_col, index), height, silver)
        for row, bath_row_index in enumerate(layer_indices, 2):
            for bath_col_index, letter in enumerate(cell_letters):
                address = '{0}{1:d}'.format(letter, row)
                if width[bath_row_index, bath_col_index] < 1e-6:
                    worksheet.write(address, '', gray)
                else:
                    worksheet.write(address, 'void', unlocked)

    def add_sheet(self, name, col_names):
        """Add an empty sheet with name and column names only.
        """
        worksheet = self.workbook.add_worksheet(name)
        for col, name in enumerate(col_names):
            worksheet.write(0, col, name, self.bold)
            worksheet.set_column(0, col, 20)  # width

    def add_flow(self):
        """Add column headers for flow.
        """
        self.add_sheet('Flow', ['Zone name', 'Level', 'Flow'])

    def add_conc(self):
        """Add column headers for concentrations.
        """
        self.add_sheet('Conc', ['Zone name', 'Conc1', 'Conc2', '...'])


def main(project_name, dot_pitlakq=None):
    """Create an empty xlsx file to be used for specifying gw inflow zones.
    """
    config = list(read_dot_pitlakq(dot_pitlakq))[0]
    base_base = join(config['model_path'], project_name)
    bath_nc = join(base_base, 'input', 'w2', 'bath.nc')
    xslx_path = join(base_base, 'input', 'gwh')
    if not exists(xslx_path):
        os.makedirs(xslx_path)
    xlsx_file_name = join(xslx_path, 'gwh_template.xlsx')
    w2_yaml = join(base_base, 'input', 'w2', 'w2.yaml')
    xlsx = XLSXRepresentation(bath_nc=bath_nc, xlsx_file_name=xlsx_file_name,
                              w2_yaml=w2_yaml)
    xlsx.create_xlsx()


if __name__ == '__main__':
    main('tut_gwh')
