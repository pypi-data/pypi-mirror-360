"""Calculate water level - volume relation from W2 results.
"""

# warns for missing members but ehey are there
# pylint: disable-msg=E1101


import numpy
import pynetcdf


class LevelVolumeRelation(object):
    """Calculate water level - volume relation from W2 results.
    """
    def __init__(self, outnc_file_name, pos):
        self.netcdf_file = pynetcdf.NetCDFFile(outnc_file_name, mode='r')
        self.pos = pos
        self.relation = []
        self.interpolate_relation = []

    def read_values(self):
        """Read values from netCDF file.
        """
        time_steps = self.netcdf_file.variables['timesteps']
        water_level = self.netcdf_file.variables['elws']
        vactive = self.netcdf_file.variables['vactive']
        relation = []
        pos = self.pos
        for step in range(len(time_steps)):
            level = water_level[step][pos]
            volume = numpy.sum(vactive[step])
            if numpy.isnan(level) or numpy.isnan(volume):
                continue
            relation.append((level, volume))
        relation.sort()
        self.relation = relation

    def interpolate(self, start, end, step):
        """Interpolate volumes to given start, end, step (exclusive).
        """
        first_level = self.relation[0][0]
        last_level = self.relation[-1][0]
        interpolate_relation = []
        pos = 0
        for target_level in numpy.arange(start, end, step):
            level, volume = self.relation[pos]
            found = False
            incr = 1
            while not found:
                if first_level < target_level < last_level:
                    next_level, next_volume = self.relation[pos + incr]
                    if level <= target_level <= next_level:
                        target_volume = (volume + ((next_volume - volume) /
                                                   (next_level - level)) *
                                         (target_level - level))
                        interpolate_relation.append((target_level,
                                                     target_volume))
                        found = True
                        potential_next = self.relation[pos + 1][0]
                        if target_level + step > last_level:
                            pos += 1
                            break
                        # Make sure next level is smaller than next
                        # target_level. Otherwise stay with old level as lower
                        # boundray.
                        while potential_next < target_level + step:
                            pos += 1
                            potential_next = self.relation[pos + 1][0]
                    else:
                        incr += 1
                else:
                    interpolate_relation.append((target_level, 0.0))
                    found = True
        self.interpolate_relation = interpolate_relation


def main(outnc_file_name=r'c:\Daten\Mike\projekte\modglue\models\kepwari_neu'
                         r'\output\w2\out.nc',
         pos_level=16,
         level_range=(110, 200.1, 0.1),
         output_file_name=r'c:\Daten\Mike\projekte\australien\daten'
                          r'\fuer-Modell\kepwari\level_volume_w2.txt'):
    """Save relation to a file.
    """
    lvr = LevelVolumeRelation(outnc_file_name, pos=pos_level)
    lvr.read_values()
    # A little bit of magic.
    # pylint: disable-msg=W0142
    lvr.interpolate(*level_range)
    fobj = open((output_file_name), 'w')
    fobj.write('%15s %15s\n' % ('level', 'volume'))
    for entry in lvr.interpolate_relation:
        fobj.write('%15.2f %15.2f\n' % entry)


if __name__ == '__main__':

    main()
