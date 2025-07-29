"""Reading fo PCG information.
"""

# NumPy, dynamic members.
# pylint: disable-msg=E1101

import numpy

import pitlakq.commontools.dbftools.flatdbf.flatdbf as flatdbf


class PcgDatabase:
    """
    Tool box for reading (and later also writing)
    data to and from dbase files for pcg.
    """

    def __init__(self, config):
        self.config = config

    def make_3d_arrays(self):
        """Creta 3d arrays
        """
        # Define attributes here.
        # pylint: disable-msg=W0201
        self.x_pcg, self.y_pcg, self.m_pcg, self.zu_pcg = \
                   self.pcg_data_to_array(read_kf_numbers=True)

    def pcg_data_to_array(self, read_kf_numbers=False):
        """
        Convert PCG data into an array.
        """
        # Define attributes here.
        # pylint: disable-msg=W0201
        dbf = flatdbf.Dbf(self.config.pcg_para_file)
        x_n_pcg = 0
        y_n_pcg = 0
        z_n_pcg = 0
        rw_pcg = []
        hw_pcg = []
        m_pcg = []
        zu_pcg = []
        kf_numbers = []
        lupe = dbf.list[0][2]
        if not lupe:
            lupe = 1
        for line in dbf.list:
            if x_n_pcg < line[3]:
                rw_pcg.append(line[0])
            x_n_pcg = max(x_n_pcg, line[3])
            if y_n_pcg < line[4]:
                hw_pcg.append(line[1])
            y_n_pcg = max(y_n_pcg, line[4])
            z_n_pcg = max(z_n_pcg, line[5])
            m_pcg.append(line[7])
            zu_pcg.append(line[6])
            if read_kf_numbers:
                try:
                    kf_numbers.append(int(line[29].split('f')[1]))
                except ValueError:
                    kf_numbers.append(0)
        x_pcg = numpy.array(rw_pcg)
        y_pcg = numpy.array(hw_pcg)
        m_pcg = numpy.array(m_pcg)
        zu_pcg = numpy.array(zu_pcg)
        kf_numbers = numpy.array(kf_numbers)
        m_pcg.shape = (x_n_pcg, y_n_pcg, z_n_pcg)
        zu_pcg.shape = (x_n_pcg, y_n_pcg, z_n_pcg)
        if read_kf_numbers:
            kf_numbers.shape = (x_n_pcg, y_n_pcg, z_n_pcg)
            self.kf_numbers = kf_numbers
        return x_pcg, y_pcg, m_pcg, zu_pcg
