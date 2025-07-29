"""Extract volumes and areas from bath.nc.
"""

# pylint: disable-msg=E1101
import numpy
import netCDF4



def get_bath(bath_nc, out_txt='vol_area_bath.txt', bottom=60):
    """Get data from bath.nc
    """
    nc_file = netCDF4.Dataset(bath_nc, 'r', format='NETCDF3_CLASSIC')
    segs = nc_file.variables['segment_lenght'][:]
    heights = nc_file.variables['layer_height'][:]
    width = nc_file.variables['cell_width']
    areas = width * segs
    vols = areas * heights.reshape(heights.shape[0], 1)
    total_vol = 0
    with open(out_txt, 'w') as fobj:
        fobj.write('{0} {1} {2}\n'.format('layer', 'volume', 'area'))
        for index, (area, vol) in enumerate(zip(reversed(areas),
                                                reversed(vols)), bottom):
            total_vol += numpy.sum(vol)
            fobj.write('{0} {1} {2}\n'.format(index, total_vol,
                                              numpy.sum(area)))


if __name__ == '__main__':
    get_bath(bath_nc=r'c:\Daten\Mike\projekte\models\kami\input\w2\bath.nc',
             out_txt=r'c:\Daten\Mike\projekte\kami\preprocessing'
                     r'\vol_area_bath.txt')
