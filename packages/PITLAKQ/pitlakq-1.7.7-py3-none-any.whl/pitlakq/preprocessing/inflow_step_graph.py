"""Show inflow input data as step graph.

Usually we use the w2 input in step-mode, that is a
value will be used until the next comes.

Example:

01.01.2000   1
01.01.2001   2
01.01.2002   1
01.01.2003   3

means:

3 +
  |
2 +         ---------
  |         |       |
1 +---------        ---------
  |
  +--------+--------+-------+
 2000    2001     2002    2003
"""

import datetime


import matplotlib as mpl
import matplotlib.pyplot as plt

from pitlakq.commontools.filereader.read_columns_txt import read_columns

mpl.rcParams['mathtext.fontset'] = 'custom'
mpl.rcParams['mathtext.it'] = 'sans'


class StepGraph(object):
    """Show the step graph.
    """

    def __init__(self, data_file_names, plot_properties=None,
                 figure_file_name=None, fill_to_zero=False):
        try:
            data_file_names[0][0]
        except KeyError:
            data_file_names = [data_file_names]
        self.data_file_names = data_file_names
        if not plot_properties:
            plot_properties = {}
        self.fill_to_zero = fill_to_zero
        self.plot_properties = plot_properties
        self.figure_file_name = figure_file_name

    @staticmethod
    def read_input(fobj):
        """Read w2 inflow input.
        """
        data = read_columns(fobj, convert='datetime_rest_float')
        data['inflow'] = data['tributaryInflow']
        del data['tributaryInflow']
        return data

    @staticmethod
    def add_data(data_list):
        """Add data from two files.
        """
        dates = data_list[0]['datetime']
        values = data_list[0]['inflow']
        for entry in data_list[1:]:
            assert dates == entry['datetime']
            values = [old_value + new_value for old_value, new_value
                      in zip(values, entry['inflow'])]
        return {'datetime': dates, 'inflow': values}

    @staticmethod
    def double_dates(old_data):
        """Add dates to get step function.
        """
        new_dates = []
        new_values = []
        delta_t = datetime.timedelta(seconds=1)
        old_dates = old_data['datetime']
        old_values = old_data['inflow']
        for (date1, date2), value in  zip(zip(old_dates[:-1], old_dates[1:]),
                                          old_values):
            new_dates.append(date1)
            new_dates.append(date2 - delta_t)
            new_values.append(value)
            new_values.append(value)
        new_dates.append(old_dates[-1])
        new_values.append(old_values[-1])
        return {'datetime': new_dates, 'inflow': new_values}

    def show(self, data_groups=None, show=True):
        """Show inflows.
        """
        if not data_groups:
            data_groups = []
            for file_name_group in self.data_file_names:
                data_list = []
                for file_name in file_name_group:
                    data_list.append(self.read_input(open(file_name)))
                data = self.add_data(data_list)
                data = self.double_dates(data)
                data_groups.append(data)
        if len(data_groups) == 1:
            plt.plot(data_groups[0]['datetime'], data_groups[0]['inflow'])
            if self.fill_to_zero:
                ax = plt.gca()
                ax.fill_between(data_groups[0]['datetime'], 0,
                                data_groups[0]['inflow'])
                ax.set_ylim([0.0, None])
        elif len(data_groups) == 2:
            plt.plot(data_groups[0]['datetime'], data_groups[0]['inflow'],
                     'b',
                     data_groups[1]['datetime'], data_groups[1]['inflow'],
                     'g:', linewidth=2)
        else:
            raise IndexError('Only two data_groups are allowed. %d found'
                             % len(data_groups))
        plt.xlabel('Date')
        plt.ylabel('Inflow in $m^3/s$')
        for attr in ['title', 'legend', 'xlim', 'ylim']:
            if attr in self.plot_properties:
                func = getattr(plt, attr)
                args, kwargs = self.plot_properties[attr]
                # Magic is good here.
                # pylint: disable-msg=W0142
                func(*args, **kwargs)
        if show:
            plt.show()
        if self.figure_file_name:
            plt.savefig(self.figure_file_name)


def show_graph(data_file_names, show=False, plot_properties=None,
               figure_file_name=None, fill_to_zero=False):
    """
    Show graph with inflows.
    """
    graph = StepGraph(data_file_names, plot_properties, figure_file_name,
                      fill_to_zero)
    graph.show(show=show)
