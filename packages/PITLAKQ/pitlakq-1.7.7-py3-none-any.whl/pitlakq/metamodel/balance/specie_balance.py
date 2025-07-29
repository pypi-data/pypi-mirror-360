"""Balance for all species for all sources and sinks.
"""

import os

import numpy


# PyLint still can't find numpy members.
# pylint: disable-msg=E1101

class SpecieBalance(object):
    """Balance for all species for all sozurces and sinks.

    The is one output <specie_name>.txt per specie with
    entris for:
    * change in lake concentration
    * tributary inflows and outflows for each tributary
    * gw inflow and outflow
    * change in concentration due to PHREEQC calculations
    * erosion input
    * leaching from sediment sections
    * precipitation
    * loading
    All masses are in tons.
    """

    def __init__(self, config):
        self.config = config
        self.active_sources = ['lake', 'tributaries']
        trib_names = self.config.w2.input.data['tributaries']\
                     ['tributary_names']['value']
        self.w2_specie_indices = None
        self.trib_name_order = ['trib_%s' % name for name in trib_names]
        self.active_species_names = self.make_active_species()
        self.offsets = {}
        self.masses = {}
        self.cum_masses = {}
        self.cum_masses['lake'] = {}
        self.cum_masses['lake'][''] = self._get_lake_masses()
        self.cum_masses['tributaries'] = self._get_trib_masses()
        self.masses['lake'] = {}
        self.masses['lake'][''] = self.cum_masses['lake']['']
        self.masses['tributaries'] = self.cum_masses['tributaries']
        self.inital_masses = self.cum_masses['lake'][''].copy()
        self.write_initial_masses()
        start_other_balance = 2
        if self.config.precalc_gw or self.config.gwh:
            self.active_sources.append('gw')
            self.cum_masses['gw'] = self._get_gw_masses()
            self.masses['gw'] = self.cum_masses['gw']
            start_other_balance += 1
        self.atmosphere = False
        if (self.config.w2_input.data['calculations']
            ['allow_atmospheric_exchange']['value']):
            self.atmosphere = True
        if self.atmosphere:
            self.active_sources.append('atmosphere')
            self.cum_masses['atmosphere'] = {}
            self.masses['atmosphere'] = {}
            self.cum_masses['atmosphere'][''] = self._get_atm_masses()
            self.masses['atmosphere'][''] = self.cum_masses['atmosphere']['']
            start_other_balance += 1
        if self.config.loading:
            self.active_sources.append('loading')
            self.cum_masses['loading'] = self._get_loading_masses()
            self.masses['loading'] = self.cum_masses['loading']
            start_other_balance += 1
        if self.config.phreeqc_coupling_lake:
            self.active_sources.append('phreeqc')
        if self.config.erosion:
            self.active_sources.append('erosion')
        if self.config.leaching:
            self.active_sources.append('leaching')


        for source in self.active_sources[start_other_balance:]:
            self.masses[source] = self.config.specie_balances[source]
        self.output_files, self.cum_out_files = self.open_output_files()
        self.first = True
        self.row_format = ''

    def make_active_species(self):
        """Get active species as define in w2 input.
        """
        active = self.config.w2.input.data['active_constituents']
        species_names = active['constituent_name']['value']
        active_constinuents = active['active_constituents']['value']
        active_species_names = []
        for index, name in enumerate(species_names):
            if active_constinuents[index]:
                active_species_names.append(name)
        return active_species_names

    def make_w2_specie_indices(self):
        """Make the indicies for access of w2 species
        """
        w2 = self.config.w2
        self.w2_specie_indices = []
        for index, w2_name in enumerate(self.config.all_species_keys):
            for name in self.active_species_names:
                if w2_name == w2.w2_name_map[name]:
                    self.w2_specie_indices.append(index)
                    continue

    def write_initial_masses(self):
        """Write all intial masses to file
        """
        fobj = open(os.path.join(self.config.balance_path,
                                 'initial_masses.txt'), 'w')
        fobj.write('%-25s %25s\n' %('specie', 'initial mass [t]'))
        for specie, mass in sorted(self.inital_masses.items()):
            fobj.write('%-25s %25.5g\n' % (specie, mass))
        fobj.close()

    def open_output_files(self):
        """Open all output_files
        """
        files = {}
        cum_files = {}
        base_path = self.config.balance_path
        for name in self.active_species_names:
            path = os.path.join(base_path, '%s_change.txt' % name)
            cum_path = os.path.join(base_path, '%s_cum.txt' % name)
            files[name] = open(path, 'w')
            cum_files[name] = open(cum_path, 'w')
        return files, cum_files

    def writer_headers(self):
        """Write headers for all output files.
        """
        header_names = ['date']
        for source in self.active_sources:
            for name in sorted(self.masses[source].keys()):
                if name:
                    name = '_' + name
                header_names.append(source + name)
        header_names.append('balance_error')
        header = tuple(header_names)
        cum_header = tuple([header_names[0]] + ['cum_%s' % name for name in
                                                header_names[1:]])
        cols = len(header_names) - 1
        format_ = '%10s' + ' %30s' * cols + '\n'
        self.row_format = '%02d.%02d.%4d' + ' %30.9g' * cols + '\n'
        for name in self.active_species_names:
            self.output_files[name].write(format_ % header)
            self.cum_out_files[name].write(format_ % cum_header)

    def write_balance(self, date):
        """Write balance data to all files.
        """
        if self.first:
            self.first = False
            self.writer_headers()
            for source in self.active_sources[1:]:
                self.cum_masses[source] = {}
                for section in self.masses[source]:
                    self.cum_masses[source][section] = {}
                    for name in self.masses[source][section]:
                        self.cum_masses[source][section][name] = 0.0

        def make_data(values):
            """Assemble data.
            """
            return tuple([date.day, date.month, date.year] + values)
        self.masses['lake'][''] = self._get_lake_masses()
        self.masses['tributaries'] = self._get_trib_masses()
        if self.config.precalc_gw or self.config.gwh:
            self.masses['gw'] = self._get_gw_masses()
        if self.atmosphere:
            self.masses['atmosphere'][''] = self._get_atm_masses()
        if self.config.loading:
            self.masses['loading'] = self._get_loading_masses()
        for name in self.active_species_names:
            mass = []
            cum_mass = []
            for source in self.active_sources:
                sub_names = sorted(self.cum_masses[source].keys())
                for sub_name in sub_names:
                    if name in set(self.masses[source][sub_name].keys()):
                        cum = self.cum_masses[source][sub_name][name]
                        try:
                            current_mass = (self.masses[source][sub_name][name]
                                            - cum)
                        except FloatingPointError:
                            current_mass = 0.0
                            print('Error:')
                            print(source)
                            print(sub_name)
                            print(name)
                            print(self.masses[source][sub_name][name])
                            print(cum)
                        current_cum_mass = cum + current_mass
                        mass.append(current_mass)
                        cum_mass.append(current_cum_mass)
                        self.cum_masses[source][sub_name][name] = \
                                                    current_cum_mass
                    else:
                        mass.append(0.0)
                        cum_mass.append(0.0)
            error = mass[0] - sum(mass[1:])
            cum_error = (cum_mass[0] - sum(cum_mass[1:]) -
                         self.inital_masses[name])
            mass.append(error)
            cum_mass.append(cum_error)
            self.output_files[name].write(self.row_format % make_data(mass))
            self.cum_out_files[name].write(self.row_format %
                                           make_data(cum_mass))
            self.output_files[name].flush()
            self.cum_out_files[name].flush()

    def _get_lake_masses(self):
        """Sum up masses in lake.
        """
        w2 = self.config.w2
        masses = {}
        vactive = w2.get_shared_data('vactive')[:]
        for name in self.active_species_names:
            masses[name] = numpy.sum(w2.get_shared_data(w2.w2_name_map[name])
                                     * vactive) / 1e6 # g --> t
        return masses

    def _get_trib_masses(self):
        """Sum up masses from tributaries.
        """
        w2 = self.config.w2
        if not self.w2_specie_indices:
            self.make_w2_specie_indices()
        if not 'tributaries' in self.offsets:
            self.offsets['tributaries'] = {}
            self.masses['tributaries'] = {}
            for trib_index, trib in enumerate(self.trib_name_order):
                self.offsets['tributaries'][trib] = {}
                self.masses['tributaries'][trib] = {}
                for index, name in zip(self.w2_specie_indices,
                                       self.active_species_names):
                    self.offsets['tributaries'][trib][name] = 0.0
                    self.masses['tributaries'][trib][name] = 0.0
        masses = {}
        balance = w2.get_shared_data('trib_specie_balance')[:]
        for trib_index, trib in enumerate(self.trib_name_order):
            masses[trib] = {}
            for index, name in zip(self.w2_specie_indices,
                                   self.active_species_names):
                old_cum_balance = self.masses['tributaries'][trib][name]
                masses[trib][name] = balance[trib_index, index] / 1e6 # g --> t
                offset = self.offsets['tributaries'][trib][name]
                if self.config.w2.offset_balance:
                    offset = old_cum_balance
                    self.offsets['tributaries'][trib][name] = offset
                masses[trib][name] += offset
        return masses

    def _get_gw_masses(self):
        """Sum up masses from gw in and out flows.
        """
        w2 = self.config.w2
        if not 'gw' in self.offsets:
            self.offsets['gw'] = {}
            self.masses['gw'] = {}
            for direction in ['in', 'out']:
                self.offsets['gw'][direction] = {}
                self.masses['gw'][direction] = {}
                for name in self.active_species_names:
                    self.offsets['gw'][direction][name] = 0.0
                    self.masses['gw'][direction][name] = 0.0
        gw = {}
        nsum = numpy.sum
        for direction in ['in', 'out']:
            gw[direction] = {}
            for index, name in zip(self.w2_specie_indices,
                                   self.active_species_names):
                w2_name = 'cssgw' + direction
                old_cum_balance = self.masses['gw'][direction][name]
                gw[direction][name] = (nsum(w2.get_shared_data(w2_name)
                                           [index,:]) / 1e6)
                offset = self.offsets['gw'][direction][name]
                if self.config.w2.offset_balance:
                    offset = old_cum_balance
                    self.offsets['gw'][direction][name] = offset
                gw[direction][name] += offset
        return gw

    def _get_atm_masses(self):
        """Sum up masses from exchange with the atmosphere.
        """
        w2 = self.config.w2
        if not self.w2_specie_indices:
            self.make_w2_specie_indices()
        atm = {}
        for index, name in zip(self.w2_specie_indices,
                               self.active_species_names):
            atm[name] = (numpy.sum(w2.get_shared_data('cssatm')
                                           [index,:]) / 1e6)
        return atm

    def _get_loading_masses(self):
        """Sum up masses from loading.
        """
        w2 = self.config.w2
        if not 'loading' in self.offsets:
            self.offsets['loading'] = {}
            self.masses['loading'] = {}
            self.offsets['loading'][''] = {}
            self.masses['loading'][''] = {}
            for name in self.active_species_names:
                self.offsets['loading'][''][name] = 0.0
                self.masses['loading'][''][name] = 0.0
        if not self.w2_specie_indices:
            self.make_w2_specie_indices()
        nsum = numpy.sum
        load = {}
        load[''] = {}
        for index, name in zip(self.w2_specie_indices,
                               self.active_species_names):
            old_cum_balance = self.masses['loading'][''][name]
            load[''][name] = (nsum(w2.get_shared_data('cssload')[index,:]) /
                              1e6)
            offset = self.offsets['loading'][''][name]
            if self.config.w2.offset_balance:
                offset = old_cum_balance
                self.offsets['loading'][''][name] = offset
            load[''][name] += offset
        return load
