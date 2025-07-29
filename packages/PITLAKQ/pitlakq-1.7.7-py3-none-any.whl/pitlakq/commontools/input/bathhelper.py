# coding: utf-8

"""Tools for bathymtry.
"""

from __future__ import print_function, unicode_literals

import netCDF4
import yaml

# pylint: disable-msg=W0611
from pitlakq.commontools.input.yamlinput import File
# pylint: enable-msg=W0611


def make_bottom(bath_file_name, w2_yaml_file_name):
    """Create values for bottom height.
    """
    w2_input = yaml.load_all(open(w2_yaml_file_name), Loader=yaml.FullLoader)
    for stream in w2_input:
        if isinstance(stream, dict) and 'waterbody_coordinates' in stream:
            bottom = stream['waterbody_coordinates']['bottom_elevation'] \
                           ['value']
            break

    bath_file = netCDF4.Dataset(bath_file_name, 'r', format='NETCDF3_CLASSIC')
    variables = bath_file.variables
    layer_height = variables['layer_height'][:]
    width = variables['cell_width'][:]
    layer_bottom = [0.0, bottom]
    old_height = layer_height[-2]
    for index in range(len(layer_height) - 3, 0, -1):
        height = layer_height[index]
        layer_bottom.append(layer_bottom[-1] + old_height)
        old_height = height
    layer_bottom.append(0.0)
    layer_bottom.reverse()
    return layer_bottom
