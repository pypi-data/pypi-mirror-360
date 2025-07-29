"""Find and adjust active cells for exchange.
"""

# NumPy, dynamic members.
# pylint: disable-msg=E1101

import numpy
import copy


class ActiveCells(object):
    """Active exchange cells.
    """

    def __init__(self, config):
        self.config = config
        self.width = self.config.w2.get_shared_data('b')
        self.active_x = None
        self.active_z = None

    def adjust_non_active_cells(self, qss_gw, gw_in, gw_out, gw_temp,
                                species_conc):
        """Make sure pmly active cells do exchange.
        """
        dry_cells_out = {}
        self.find_next_active()
        adjusted_species_conc = copy.deepcopy(species_conc)
        for column in range(qss_gw.shape[0]):
            for row in range(qss_gw.shape[1]):
                active_x = self.active_x[column, row]
                active_z = self.active_z[column, row]
                if (active_x != 0.0 and active_z != 0.0 and
                    (active_x != column or active_z != row)):
                    if gw_in[column, row] or gw_in[active_x, active_z]:
                        for specie in species_conc.keys():
                            adjusted_species_conc[specie][active_x,
                                                          active_z] = (
                                (gw_in[column, row] *
                                 adjusted_species_conc[specie][column, row] +
                                 gw_in[active_x, active_z] *
                                 adjusted_species_conc[specie][active_x,
                                                               active_z]) /
                                (gw_in[column, row] + gw_in[active_x,
                                                            active_z]))
                        gw_in[active_x, active_z] = \
                            gw_in[active_x, active_z] + gw_in[column, row]
                        gw_in[column, row] = 0.0
                        gw_temp[active_x, active_z] = \
                            gw_temp[active_x, active_z] + gw_temp[column, row]
                        gw_temp[column, row] = 0.0
                    qss_gw[active_x, active_z] = \
                        qss_gw[active_x, active_z] + qss_gw[column, row]
                    gw_out[active_x, active_z] = \
                        gw_out[active_x, active_z] + gw_out[column, row]
                    qss_gw[column, row] = 0.0
                    gw_out[column, row] = 0.0
                    dry_cells_out[(column, row)] = (active_x, active_z)
        return qss_gw, gw_in, gw_out, gw_temp, species_conc, dry_cells_out

    def find_next_active(self):
        """Find next active cells.
        """
        v_active = self.config.w2.get_shared_data('vactive')
        width = self.width
        upper_active = numpy.zeros(width.shape[0])
        self.active_x = numpy.zeros(width.shape)
        self.active_z = numpy.zeros(width.shape)
        row_range = range(width.shape[1])
        column_range = range(width.shape[0])
        column_range.reverse()
        for column in column_range:
            for row in row_range:
                if v_active[column, row] > 0.0:
                    upper_active[column] = row
                    break
        for column in column_range:
            for row in row_range:
                x = 0
                z = 0
                if width[column, row]:
                    x = column
                    z = row
                    if not v_active[column, row]:
                        downwards = True
                        while True:
                            if upper_active[x]:
                                if upper_active[x] <= z:
                                    break
                                z += 1
                            else:
                                if x > 0 and downwards:
                                    x -= 1
                                else:
                                    x += 1
                                    downwards = False
                self.active_x[column, row] = x
                self.active_z[column, row] = z
