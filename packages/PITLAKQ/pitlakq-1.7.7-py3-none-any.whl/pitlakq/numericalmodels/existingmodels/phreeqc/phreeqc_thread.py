"""Running a thread for PHREEQC calculations.
"""
from __future__ import print_function

import threading

import Pyro4
from Pyro4 import core
from Pyro4.errors import NamingError
from Pyro4 import naming


class PhreeqcThread(threading.Thread):
    """Phreeqc thread.
    """

    def __init__(self, node_name):
        threading.Thread.__init__(self)
        self.node_name = node_name
        if self.node_name:
            #core.initClient()
            ## locate the NS
            #locator = naming.NameServerLocator()
            #ns = locator.getNS()
            ## resolve the Pyro object
            #try:
                #uri = ns.resolve('phreeqc' + self.node_name)
                #print('connected with', uri)
            #except NamingError as err:
                #print('Couldn\'t find object, nameserver says:', err)
                #raise SystemExit
            ## create a proxy for the Pyro object, and return that
            uri = "PYRONAME:" + 'phreeqc' + self.node_name
            # self.phreeqc_remote = core.getProxyForURI(uri)
            self.phreeqc_remote = Pyro4.Proxy(uri)
        self.phreeqc_runner = None

    def run(self):
        """Start the thread.
        """
        # Attributes are set from outside.
        # pylint: disable-msg=E1101
        if self.node_name:
            self.phreeqc_remote = self.phreeqc_runner
            # self.phreeqc_remote.set_runner(self.phreeqc_runner)
        else:
            self.phreeqc_remote = self.phreeqc_runner
        if self.first:
            self.phreeqc_remote.do_first_run(self.config,
                                             self.constituents_dict,
                                             self.temperature,
                                             self.ph,
                                             self.pe,
                                             self.cell_discription,
                                             self.delta_t,
                                             self.equi_phase_amount_dict,
                                             self.header_text,
                                             self.charge,
                                             self.redox_couple,
                                             self.units)
            if self.node_name:
                self.phreeqc_runner = self.phreeqc_remote
                #self.phreeqc_runner = self.phreeqc_remote.get_runner()
            else:
                self.phreeqc_runner = self.phreeqc_remote
        else:
            self.phreeqc_remote.do_next_run(self.config,
                                            self.constituents_dict,
                                            self.temperature,
                                            self.ph,
                                            self.pe,
                                            self.run_number,
                                            self.cell_discription,
                                            self.delta_t,
                                            self.kinetics,
                                            self.equi_phase_amount_dict,
                                            self.charge,
                                            self.erosion_active,
                                            self.erosion_cec,
                                            self.erosion_porewater,
                                            self.erosion_flag,
                                            self.erosion_cec_spezies,
                                            self.erosion_cec_valences,
                                            self.porewater_moles)
            if self.node_name:
                self.phreeqc_runner = self.phreeqc_remote
                # self.phreeqc_runner = self.phreeqc_remote.get_runner()
            else:
                self.phreeqc_runner = self.phreeqc_remote
