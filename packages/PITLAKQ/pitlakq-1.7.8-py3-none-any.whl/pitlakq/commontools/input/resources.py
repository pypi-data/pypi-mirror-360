"""Read resource data.
"""

import os
import sys

from pitlakq.commontools.tools import raise_or_show_info

SPECIE_ORDER = """tra ss col tds ldom rdom algae lpom po4 nh4 no3 dox sed tic
alkal ph co2 hco3 co3 fe cbod al so4 ca mg na ka mn cl fe3 mn3 sid ch4 feoh3
aloh3 cd pb zn ars pyrite po4precip""".split()

class Singleton(object):
    """Singleton. All instances are identical.
    """
    def __new__(cls, *args, **kwargs):
        if '_inst' not in vars(cls):
            cls._inst = super(Singleton, cls).__new__(cls)
        return cls._inst


class Resources(Singleton):
    """All data in resources.
    """
    called = False
    def __init__(self, config):
        if not self.called:
            self.config = config
            self.fixed_specie_names = SPECIE_ORDER
            self.db_keys = {}
            self.db_names = {}
            self.number_of_additional_minerals = 0
            self.config.fixed_specie_names = self.fixed_specie_names
            self.number_of_constituents = len(self.fixed_specie_names)
            self.w2_name_map = {}
            self.phreeqc_species = self._read_const(self.config.all_const_names)
            self._check_const_names()
            self.const_names = dict((specie['name'], specie['key']) for specie in
                                    self.phreeqc_species)
            self.mineral_names = self._read_const(self.config.all_mineral_names)
            self._check_mineral_names()
            self.make_additional_species()
            self.called = True

    def _read_const(self, file_name):
        """
        Reading species database.
        """
        with open(file_name) as fobj:
            header = next(fobj).split()
            species = []
            for raw_line in fobj:
                # Skip comments.
                raw_line = raw_line.split('#')[0]
                if not raw_line:
                    continue
                line = raw_line.split()
                if not line:
                    continue
                entry = dict((head, line[pos]) for pos, head in
                             enumerate(header[:len(line)]))
                for key, value in entry.items():
                    if value == 'void':
                        entry[key] = None
                if entry['molar_weight'] is not None:
                    entry['molar_weight'] = float(entry['molar_weight'])
                species.append(entry)
                key = entry['key']
                name = entry['name']
                error = False
                if key in self.db_keys:
                    args = ('Key', key)
                    error  = True
                elif name in self.db_names:
                    args = ('Name', name)
                    error = True
                if error:
                    msg = '\n{0} "{1}" defined more than once.\n'.format(*args)
                    msg += 'Please correct {0}'.format(
                                            os.path.basename(file_name))
                    print(msg)
                    sys.exit(1)
                self.db_keys[key] = name
                self.db_names[name] = key
        c_species = set(['tic', 'co2', 'co3'])
        if not self.config.c_as_c:
            for entry in species:
                if entry['key'] in c_species:
                    entry['molar_weight'] += 16 * 3 + 1 # HCO3 12 + 16 * 3
        return species

    def _check_const_names(self):
        """Check that only known species are specified.
        """
        self._check_names(self.phreeqc_species,
                          group='lake_active_const_names',
                          file_name='const_names.txt')

    def _check_mineral_names(self):
        """Check that only known minerals are specified.
        """
        self._check_names(self.mineral_names,
                          group='lake_active_minerals_names',
                          file_name='mineral_names.txt')

    def _check_names(self, species, file_name, group):
        """Check specie or mineral names.
        """
        db_names = set(specie['key'] for specie in species)
        active_species = set(getattr(self.config, group))
        not_defined = active_species - db_names
        if len(not_defined) == 1 and None in not_defined:
            not_defined = None
        if not_defined:
            msg = '\nFound undefined names for "{0}"\n'.format(group)
            msg += '=' * len(msg.strip()) + '\n\n'
            msg += 'The following names cannot be used unless defined in '
            msg += '"{0}" in "resources" and "activeconst.txt" '.format(
                file_name)
            msg += 'using the same order of names.\n\n'
            msg += '\n'.join('- {0}'.format(name) for name in not_defined)
            msg += '\n\nAllowed names are:\n\n'
            msg += '\n'.join('- {0}'.format(name) for name in sorted(db_names))
            raise_or_show_info(ValueError, msg)

    def make_additional_species(self):
        """Make additional species. These can be defined by the user.
        """
        additional_names = []
        additional_keys = []
        additional_species = {}
        nspecies = len(self.phreeqc_species)
        entries_species = [('', 'c2'), ('ssp', 'ssp'),
                           ('ssgw', 'ssgw'), ('ss', 'cssk')]
        entries_minerals = entries_species[:2] + entries_species[3:]
        for index, specie in enumerate(self.phreeqc_species +
                                       self.mineral_names):
            if specie.get('w2ssp') == 'auto':
                if index < nspecies:
                    assert specie['w2ssgw'] == 'auto'
                    entries = entries_species
                else:
                    if specie['w2ssgw'] is not None:
                        msg = 'Mineral {0} must use "void" for "w2ssgw".'
                        print(msg.format(specie['name']))
                        sys.exit(1)
                    entries = entries_minerals
                    self.number_of_additional_minerals += 1
                name = specie['name']
                key = specie['key']
                self.w2_name_map[name] = key
                for entry, target in entries:
                    additional_species[key + entry] = (target,
                                               self.number_of_constituents)
                additional_keys.append(key)
                self.number_of_constituents += 1
        self.config.additional_specie_names = additional_names
        self.config.additional_specie_keys = additional_keys
        self.config.additional_species = additional_species
        self.all_species_keys = self.fixed_specie_names + additional_keys
        self.config.all_species_keys = self.all_species_keys
        name_map = dict((specie['key'], specie['name']) for specie in
                         self.phreeqc_species + self.mineral_names)
        all_specie_names = [name_map[key] for key in self.all_species_keys]
        self.config.name_indices = dict((name, index) for index, name in
                                        enumerate(all_specie_names))
