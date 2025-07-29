"""Save the volume balance (flows) for sources and sinks.

Currently, we do this with a monthly time step.
"""

from __future__ import print_function

import os

import numpy

W2_BALANCE_NAMES = [('volume_change', 'voltbr'),
                    ('evaporation', 'volev'),
                    ('precipitation', 'volpr'),
                    ('tributaries', 'voltr'),
                    ('gw_in', 'volgwin'),
                    ('gw_out', 'volgwout'),
                    ('initial_volume', 'volibr'),
                    ('surface_area', 'surfacearea')]


class TotalBalance:
    """Volume balance for all sources and sinks.
    """

    def __init__(self, config):
        self.config = config
        self.balance_file = None
        self.surface_area = None
        self.w2_intial_volume = None
        self.balance_check = None
        self.water_level = None
        self.balance_cum_file = None
        self.cum_balance = None
        self.active_volume = None
        self.w2_gw_in = None
        self.w2_gw_out = None
        self.balance_error = None
        self.balance = None
        self.w2_balance_names = W2_BALANCE_NAMES
        if self.config.loading:
            self.w2_balance_names.append(('loading', 'volload'))
        self.no_cum = set(('initial_volume', 'surface_area'))
        self.w2_names = {}
        self.make_w2_name_mapping()
        self.balance_name_order = []
        self.make_balance_name_order()
        self.balances = {}
        self.w2_balances = {}
        self.w2_cum_balances = {}.fromkeys(self.balance_name_order, 0.0)
        self.w2_balances_offsets = {}.fromkeys(self.balance_name_order, 0.0)
        self.first = True
        self.cum_volume = 0.0
        self.cum_balance_error = 0.0 # balance error in w2 time vs. space
        self.cum_balance_check = 0.0 # check with summation of balances
                                     # vs. volume_change
        self.open_files()
        self.write_headers()

    def make_balance_name_order(self):
        """Order the names of all balances.

        This order will be used in the header of the files.
        """
        self.balance_name_order = [entry[0] for entry in self.w2_balance_names
                                   if entry[0] not in self.no_cum]
        trib_names = self.config.w2.input.data['tributaries']\
                     ['tributary_names']['value']
        self.balance_name_order += ['trib_%s' % name for name in trib_names]

    def make_w2_name_mapping(self):
        """Create a dictionary from the list of tuples.
        """
        self.w2_names = dict(self.w2_balance_names)

    def open_files(self):
        """Open all output files.
        """
        if not os.path.exists(self.config.balance_path):
            os.mkdir(self.config.balance_path)
        self.balance_file = open(os.path.join(self.config.balance_path,
                                             'balance.txt'), 'w')
        self.balance_cum_file = open(os.path.join(self.config.balance_path,
                                             'balance_cumulative.txt'), 'w')

    def write_headers(self):
        """Write the header lines.
        """
        col = len(self.balance_name_order) + 4
        header_format = '%10s' + ' %20s' * col + '\n'
        header = ['date', 'water_level', 'total_volume'] + \
                 self.balance_name_order + ['balance_error', 'balance_check']
        cum_header = header[:3] + [head + '_cum' for head in header[3:]]
        self.balance_file.write(header_format % tuple(header))
        self.balance_cum_file.write(header_format % tuple(cum_header))

    def set_balance(self, name, balance):
        """Add a balance to the balance dict.
        """
        self.balances[name] = balance

    def check_w2_balance(self, date):
        """Get the balance values from w2 and print them to the screen.
        """
        get_sd = self.config.w2.get_shared_data
        trib_number = 0
        for name in self.balance_name_order:
            old_cum_balance = self.w2_cum_balances[name]
            if name.startswith('trib_'):
                cum_balance = get_sd('vol_trib_single')[trib_number]
                trib_number += 1
            else:
                cum_balance = sum(get_sd(self.w2_names[name])[:])
            offset = self.w2_balances_offsets[name]
            if self.config.w2.offset_balance:
                offset = old_cum_balance
            cum_balance += offset
            self.w2_balances[name] = cum_balance - old_cum_balance
            self.w2_cum_balances[name] = cum_balance
            self.w2_balances_offsets[name] = offset
        if self.first:
            self.first = False
            self.w2_intial_volume = sum(get_sd(
                                        self.w2_names['initial_volume'])[:])
            self.cum_volume = self.w2_intial_volume
        self.surface_area = get_sd('surfacearea')
        self.active_volume = self.config.w2.active_volume
        elws = get_sd('elws')
        self.water_level = elws[len(elws) // 2]
        voluh = get_sd('voluh')
        voldh = get_sd('voldh')
        check_names = ['evaporation', 'precipitation',  'tributaries', 'gw_in',
                       'gw_out']
        if self.config.loading:
            check_names.append('loading')
        self.balance_check = (self.w2_balances['volume_change'] -
                              sum(self.w2_balances[name] for name in
                                  check_names))
        self.cum_balance_check += self.balance_check
        self.balance = sum([self.w2_balances[name] for name in
                            self.balance_name_order if name not in
                            ['volume_change']])
        self.cum_balance = sum([self.w2_cum_balances[name] for name in
                                self.balance_name_order if name not in
                                ['volume_change']])
        print('volsbr', get_sd('volsbr'))
        print('voltbr', get_sd('voltbr'))
        print('diff', get_sd('volsbr') - get_sd('voltbr'))
        # PyLint still can't find numpy members.
        # pylint: disable-msg=E1101
        self.balance_error = numpy.sum(get_sd('volsbr') - get_sd('voltbr'))
        self.cum_balance_error += self.balance_error
        self.cum_volume += self.w2_balances['volume_change']
        print()
        self.show_balances()
        print('voluh', voluh)
        print('voldh', voldh)
        self.write_balance(date)

    def show_balances(self):
        """Print balance values to the screen.
        """
        print('initial volume:      %15.2f' % self.w2_intial_volume)
        print('current volume:      %15.2f' % self.active_volume)
        print('cumulative volume:   %15.2f' % self.cum_volume)
        print('surface area:        %15.2f' % self.surface_area)
        print('water level:         %15.2f' % self.water_level)
        print('balance error in w2: %15.2f' % self.balance_error)
        print('evaporation:         %15.2f' % self.w2_balances['evaporation'])
        print('precipitation:       %15.2f' % self.w2_balances['precipitation'])
        print('tributaries:         %15.2f' % self.w2_balances['tributaries'])
        print('gw_in:               %15.2f' % self.w2_balances['gw_in'])
        print('gw_out:              %15.2f' % self.w2_balances['gw_out'])
        print('total volume change: %15.2f' % self.w2_balances['volume_change'])

    def check_gw_exchange(self):
        """Get gw exchange values and print them to the screen.
        """
        if self.config.gw_model != 'modmst':
            msg = 'gw check only implemented for MODMST not for %s' \
                  % self.config.gw_model
            raise TypeError(msg)
        self.w2_gw_in = self.config.w2.get_shared_data('volgwin')[0]
        self.w2_gw_out = self.config.w2.get_shared_data('volgwout')[0]
        modmst_lake_in = self.balances['modmst'].get_value('lake', 'in',
                                                           'flow', 'rate')
        modmst_lake_out = self.balances['modmst'].getValue('lake', 'out',
                                                           'flow', 'rate')
        print('flow lake into gw:')
        try:
            error = (1 - abs(self.w2_gw_out / modmst_lake_in)) * 100
        except (ZeroDivisionError, OverflowError):
            if self.w2_gw_out == 0.0:
                error = 0.0
            else:
                error = 'N/A'
        if error == 'N/A':
            print('w2: %15.2f modmst: %15.2f error in %%: %6s' % (
                self.w2_gw_out, modmst_lake_in, error))
        else:
            print('w2: %15.2f modmst: %15.2f error in %%: %6.2f' % (
                                   self.w2_gw_out, modmst_lake_in, error))
        print('flow gw into lake:')
        try:
            error = (1 - abs(self.w2_gw_in/modmst_lake_out)) * 100
        except ZeroDivisionError:
            if self.w2_gw_in == modmst_lake_out:
                error = 0.0
            else:
                error = 'N/A'
        if error == 'N/A':
            print('w2: %15.2f modmst: %15.2f error in %%: %6s' % (
                self.w2_gw_in, modmst_lake_out, error))
        else:
            print('w2: %15.2f modmst: %15.2f error in %%: %6.2f' % (
                self.w2_gw_in, modmst_lake_out, error))

    def write_balance(self, date):
        """Write a balance line to the each balance file.
        """

        def make_data(balances, balance_error, balance_check):
            """Pack data into a tuple.
            """
            return tuple([date.day, date.month, date.year, self.water_level] +
                         [self.cum_volume] +
                         [balances[name] for name in self.balance_name_order]
                         + [balance_error, balance_check])
        col = len(self.balance_name_order) + 4
        format_ = '%02d.%02d.%4d' + ' %20.2f' * col + '\n'
        self.balance_file.write(format_ % make_data(self.w2_balances,
                                                    self.balance_error,
                                                    self.balance_check))
        self.balance_cum_file.write(format_ %
                                    make_data(self.w2_cum_balances,
                                              self.cum_balance_error,
                                              self.cum_balance_check))
        self.balance_file.flush()
        self.balance_cum_file.flush()
