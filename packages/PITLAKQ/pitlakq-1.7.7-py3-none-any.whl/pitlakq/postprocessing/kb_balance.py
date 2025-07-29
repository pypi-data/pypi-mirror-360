"""Calculate KB for balance terms.

Also used to check input values.
"""


import pitlakq.numericalmodels.existingmodels.phreeqc.kb_calculation as \
       kb_calculation


# TOOD: Read species names from database. See issue #4.

NAME_MAP = {'phosphorus': 'P', 'magnesium': 'Mg', 'calcium': 'Ca',
            'potassium': 'K',
            'chlorid': 'Cl', 'sulfate': 'Sulfat', 'sodium': 'Na',
            'inorganic_carbon': 'C',
            'ph': 'pH', 'aluminium': 'Al', 'iron_III': 'Fe(+3)',
            'iron_II': 'Fe(+2)', 'manganese_II': 'Mn(+2)',
            'manganese_III': 'Mn(+3)',
            'dissolved_oxygen': 'O(0)', 'nitrate_nitrite': 'N(+5)',
            'ammonium': 'Amm', 'ks43': 'ks43'}


w2_names = """ph;sulfate;mercury;silver;aluminium;arsenic;barium;beryllium;
              boron;calcium;cadmium;cobalt;chromium;copper;iron_II;potassium;
              magnesium;manganese_II;molybdenum;sodium;nickel;phosphorus;lead;
              antimony;selenium;silicon;tin;strontium;titanium;thallium;
              uranium;vanadium;zinc;chlorid;inorganic_carbon;ks43"""
phc_names = """pH;Sulfat;Hg;Ag;Al;As;Ba;Be;B;Ca;Cd;Co;Cr;Cu;Fe(+2);K;Mg;Mn(+2);
                  Mo;Na;Ni;P;Pb;Sb;Se;Si;Sn;Sr;Ti;Tl;U;V;Zn;Cl;C"""

w2_names  = [entry.strip() for entry in w2_names.split(';')]
phc_names  = [entry.strip() for entry in phc_names.split(';')]
more_names = dict(zip(w2_names,phc_names))

NAME_MAP.update(more_names)

class KbBalance(object):
    """Calculate KB for balance output.
    """
    # Name `kb` is fine.
    # pylint: disable-msg=C0103
    # Only one emthod is ok.
    # pylint: disable-msg=R0903
    def __init__(self, config, kb, constituents):
        self.config = config
        self.kb = kb
        self.constituents = constituents

    def calculate(self):
        """Calculate the balance.
        """
        calculator = kb_calculation.KbCalculator(self.config, self.kb,
                                                 self.constituents,
                                                 units='mg/l',
                                                 precipitans=[
                                                  #   'Fe(OH)3(a)',
                                                     #'Schwertmanite',
                                                     #'Al(OH)3(a)'
                                                     ])
        result = calculator.calculate()
        return result


def read_river_input(file_name):
    """Read input for river concentrations.
    """
    fobj = open(file_name)
    header = next(fobj).split()
    positions = [(NAME_MAP[name], pos) for pos, name in
                 enumerate(header) if name not in ('date', 'time', 'tracer',
                                                   'factor')]
    constituents = []
    ks43 = []
    dates = []
    for line in fobj:
        if line.strip():
            data = line.split()
            dates.append(data[0])
            const = dict([(name, float(data[pos])) for name, pos in
                                      positions])
            # force charge with pH and set NaOH as titrans
            # const['pH'] = 0.0 # 14.0
            ks43.append(const.pop('ks43'))
            constituents.append(const)
    return constituents, ks43, dates
