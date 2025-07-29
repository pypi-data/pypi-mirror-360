"""Balance for W2.
"""


class W2Balance:
    """The balance of W2.
    """
    # Only one piblic method.
    # pylint: disable-msg=R0903
    w2_constiuent_order = ['tra', 'ss', 'col', 'tds', 'ldom', 'rdom',
                         'algae', 'lpom', 'po4', 'nh4', 'no3', 'do',
                         'sed', 'tic', 'alkal', 'ph', 'co2', 'hco3',
                         'co3', 'fe', 'cbod', 'al', 'so4', 'ca', 'mg',
                         'na', 'ka', 'mn', 'cl', 'fe3', 'mn3', 'sid',
                         'ch4', 'feoh3', 'aloh3', 'cd', 'pb', 'zn',
                         'ars', 'pyrite', 'po4precip']
    volume_description = {'voldh': 'downstream head volume',
                          'voltbr': 'total branch volume change',
                          'volibr': 'upstream branch inflow volume',
                          'volpr': 'precipitation volume',
                          'voltr': 'tributaries volume',
                          'volin': 'upstream inflow volume',
                          'volout': 'downstream outflow volume',
                          'voluh': 'upstream head volume',
                          'volwd': 'withdrawl values',
                          'volgwout': 'groundwater outflow volume',
                          'volgwin': 'groundwater inflow volume',
                          'voldt': 'distribited tributaries volume',
                          'volev': 'evaporation volume'}
    heat_description = {'tssuh': 'heat sink/source due to upstream head',
                        'tssgwin':
                        'heat sink/source due to groundwater inflow',
                        'tsswd': 'heat sink/source due to withdrawl',
                        'eibr': 'intial branch energy aggregated',
                        'tsspr': 'heat sink/source due to precipitation',
                        'tssdt':
                        'heat sink/source due to distributed tributaries',
                        'tssout': 'heat sink/source due to downstream outflow',
                        'tsss': 'heat sink/source due to surface exchange',
                        'tssev': 'heat sink/source due to evaporation',
                        'etbr': 'total branch energy aggregated by time',
                        'tssin': 'heat sink/sourcedue to upstream inflow',
                        'tssgwout':
                        'heat sink/source due to groundwater outflow',
                        'tssdh': 'heat sink/source due to downstream head',
                        'tssice':
                        'heat sink/source due to iceformation/melting',
                        'tssb': 'heat sink/source due to bottom exchange',
                        'tsstr': 'heat sink/source due to tributaries'}
    mass_description = {'csswd': 'mass sink/source due to withdrawl',
                        'csspr': 'mass sink/source due to precipitation',
                        'cssout': 'mass sink/source due to downstream outflow',
                        'cssdt':
                        'mass sink/sourcedue to distributed tributaries',
                        'cssatm':
                        'mass sink/source due to exchange with atmosphere',
                        'cssuh': 'mass sink/source due to upsteram head',
                        'cssgwout':
                        'mass sink/source due to groundwater outflow',
                        'cssin': 'mass sink/source due to upstream inflow',
                        'cssphc':
                        'mass sink/source due to reactions on phreeqc',
                        'cssdh': 'mass sink/source due to downstream head',
                        'cssw2': 'mass sink/source due to reactions in w2',
                        'csssed':
                        'mass sink/source dueto exchange with sediment',
                        'cssgwin':
                        'mass sink/source due to groundwater inflow',
                        'csstr': 'mass sink/source due to tributaries'}

    def __init__(self, config):
        self.config = config
        self.const_map = {}
        self.make_const_map()

    def make_const_map(self):
        """Create a dict stroring the index.
        """
        n = 0
        for name in self.w2_constiuent_order:
            self.const_map[name] = n
            n += 1
