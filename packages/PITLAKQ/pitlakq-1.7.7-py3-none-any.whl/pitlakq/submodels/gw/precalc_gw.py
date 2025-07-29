"""Process precalculated gw values.
"""

# NumPy, dynamic members.
# pylint: disable-msg=E1101
# Many attributes defined outside __init__.
# pylint: disable-msg=W0201

import datetime
import time

import numpy


class PrecalculatedGwQ(object):
    """Precalcualted GW.
    """

    def __init__(self, q_file_name):
        self.q_file_name = q_file_name
        self.read_qs()

    def read_qs(self):
        """Read flow values.
        """
        q_file = open(self.q_file_name)
        self.data = [line.split(';') for line in q_file]
        q_file.close()

    def process_input(self):
        """Process the input.
        """
        pos = {}
        n = 1
        all_ids = self.data[0][1:] #-1]
        self.ids = []
        for id_ in all_ids:
            if len(id_)>0 and id_ != 'void' and id_ != '\n':
                new_id = id_.strip()
                pos[new_id] = n
                self.ids.append(new_id)
            n += 1
        self.q_ins_pos = {}
        self.q_outs_pos = {}
        self.description_short = {}
        self.description_long = {}
        for id_ in pos.keys():
            self.description_short[id_] = self.data[3][pos[id_]].strip()
            self.description_long[id_] = self.data[4][pos[id_]].strip()
            value = self.data[1][pos[id_]].strip()
            if value == 'in':
                self.q_ins_pos[id_] = pos[id_]
            elif value == 'out':
                self.q_outs_pos[id_] = pos[id_]
            else:
                if value !='void' and value != '':
                    raise IndexError(
                        'no in or out specified for %s at column %d'
                         %(value, pos[id_]))
        self.dates = []
        self.q_ins = {}
        self.q_outs = {}
        for key in self.q_ins_pos.keys():
            self.q_ins[key] = []
        for key in self.q_outs_pos.keys():
            self.q_outs[key] = []
        for line in self.data[5:]:
            if len(line[0]) < 10:
                break
            self.dates.append(datetime.datetime(*time.strptime(
                              line[0], '%d.%m.%Y')[:3]))
            for key in self.q_ins.keys():
                try:
                    value = float(line[self.q_ins_pos[key]])/60.0
                except ValueError:
                    value = 0.0
                self.q_ins[key].append(value)
            for key in self.q_outs.keys():
                try:
                    value = float(line[self.q_outs_pos[key]])/60.0
                except ValueError:
                    value = 0.0
                self.q_outs[key].append(value)
        for key in self.q_outs.keys():
            self.q_outs[key] = numpy.array(self.q_outs[key])
            value = numpy.sum(self.q_outs[key])
            if value < 1e-8:
                self.q_outs[key] = None
        for key in self.q_ins.keys():
            self.q_ins[key] = numpy.array(self.q_ins[key])
            value = numpy.sum(self.q_ins[key])
            if value < 1e-8:
                self.q_ins[key] = None


if __name__ == '__main__':

    def test():
        """Test it.
        """
        pre = PrecalculatedGwQ('../pcg/input/qBalance.csv')
        pre.process_input()
