"""
pyro server for phreeqc
"""

from __future__ import print_function

import os
import sys, socket
import Pyro.naming
import Pyro
import Pyro.core
from Pyro.errors import PyroError, NamingError

class PhreeqcRemote(Pyro.core.ObjBase):
    def __init__(self):
        Pyro.core.ObjBase.__init__(self)
    def set_runner(self, runner):
        self.runner = runner
    def copy_exe(self):
        self.runner.copy_exe()
    def do_first_run(self, *args):
        self.runner.do_first_run(*args)
    def do_next_run(self, *args):
        self.runner.do_next_run(*args)
    def get_runner(self):
        return self.runner


def main():
    object_name = 'phreeqc' + sys.argv[1]
    #Pyro.config.PYRO_NS_HOSTNAME = 'cluster'
    Pyro.core.initServer()
    daemon = Pyro.core.Daemon()
    # locate the NS
    locator = Pyro.naming.NameServerLocator()
    print('searching for Name Server...')
    ns = locator.getNS()
    daemon.useNameServer(ns)

    # connect a new object implementation (first unregister previous one)
    try:
        ns.unregister(object_name)  # this is the name by which our object will be known to the outside world
        print('unregister', object_name)
    except NamingError:
        print('nothing to unregister')

    # connect new object implementation
    daemon.connect(PhreeqcRemote(), object_name)

    # enter the server loop.
    print('Server object %s ready.' %object_name)
    daemon.requestLoop()

if __name__=="__main__":
    main()
