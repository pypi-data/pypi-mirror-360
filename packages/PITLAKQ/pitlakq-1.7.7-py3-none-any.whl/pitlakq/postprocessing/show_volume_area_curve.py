"""Show the water-level-volume relation in a graph.
"""


import matplotlib as mpl
import matplotlib.pyplot as plt


mpl.rcParams['mathtext.fontset'] = 'custom'
mpl.rcParams['mathtext.it'] = 'sans'


class VolumeAreaCurve(object):
    """Show the water-level-volume and area relation in a graph.
    """
    def __init__(self, volume_file_name, lake_name, xlabel=None):
        self.volume_file_name = volume_file_name
        self.lake_name = lake_name
        self.xlabel = xlabel

    def read_values(self):
        """Read values from volume file.
        """
        fobj = open(self.volume_file_name)
        header = next(fobj).split()
        header_strings = ['level', 'volume', 'area']
        level_pos, volume_pos, area_pos = [header.index(header_string) for
                                           header_string in header_strings]
        values = []
        for line in fobj:
            line = line.split()
            volume = float(line[volume_pos]) / 1e6
            area = float(line[area_pos]) / 1e6
            if volume > 0:
                level = float(line[level_pos])
                values.append((level, volume, area))
        values.sort()
        level = [value[0] for value in values]
        volume = [value[1] for value in values]
        area = [value[2] for value in values]
        return level, volume, area

    def show(self):
        """Show the curves.
        """
        def make_graph(value, vol_or_area):
            """Make a graph for volume or area.
            """
            plt.plot(level, value)
            if self.xlabel:
                plt.xlabel(self.xlabel)
            else:
                plt.xlabel('Water level m AHD')
            if vol_or_area == 'volume':
                plt.ylabel('Volume in Mio. $m^3$')

            elif vol_or_area == 'area':
                plt.ylabel('Area in $km^2$')
            plt.title('Water Level %s Relation for Lake %s' % (
                vol_or_area.capitalize(), self.lake_name))
            plt.show()
        level, volume, area = self.read_values()
        make_graph(area, 'area')
        make_graph(volume, 'volume')


def main(volume_file_name=r'c:\Daten\Mike\projekte\australien\daten'
         r'\fuer-Modell\kepwari\level_volume_w2.txt', lake_name='Kepwari',
         xlabel=None):
    """Make a graph for one lake.
    """
    vol = VolumeAreaCurve(volume_file_name, lake_name, xlabel)
    vol.show()


if __name__ == '__main__':

    main()
