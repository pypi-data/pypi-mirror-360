"""
Wrapper class for W2 extension module.

This a proxy and can be either started as a seperated
process communicating with pyro with the main program
or be imported as a normal module.
"""
import os

# NumPy, dynamic members.
# pylint: disable-msg=E1101

import numpy
from Pyro4 import core

from libpitlakq import w2_fortran

from . import pointers


DUMMY_W2_CODE_NAME = 'dummy'


class W2Proxy(object):
    """Proxy for W2.
    """

    def __init__(self, config, temp_path):
        self.config = config
        self.temp_path = temp_path
        self.w2_fortran = w2_fortran
        self.reps = 0

    def set_shared_data(self, name, value, is_ssload=False):
        """Set shared data.
        """
        if name == DUMMY_W2_CODE_NAME:
            return
        if is_ssload:
            position = self.config.name_indices[name]
            real_value = getattr(self.w2_fortran.shared_data, 'ssload')
            real_value[:, :, position] = value
            setattr(self.w2_fortran.shared_data, 'ssload', real_value)
            return
        if name in self.config.additional_species:
            real_name, position = self.config.additional_species[name]
            real_value = getattr(self.w2_fortran.shared_data, real_name)
            real_value[:, :, position] = value
            setattr(self.w2_fortran.shared_data, real_name, real_value)
            return
        try:
            # use getattr to prevent memory leak
            # if only setattr is used memory consumptions grows
            # slowly over time
            try:
                getattr(self.w2_fortran.shared_data, name)
            except AttributeError:
                pass
            try:
                setattr(self.w2_fortran.shared_data, name, value)
            except ValueError as err:
                msg = 'too many axes: 1 (effrank=1), expected rank=0'
                if str(err).strip() == msg:
                    print('string')
                    if value.dtype == '<U1':
                        setattr(self.w2_fortran.shared_data, name, ''.join(value))
                    else:
                        print(self.w2_fortran.shared_data, name, value)
                        raise
        except SystemError:
            real_name, position = pointers.pointers[name]
            position = int(position)
            real_value = getattr(self.w2_fortran.shared_data, real_name)
            real_value[:, :, position] = value
            setattr(self.w2_fortran.shared_data, real_name, real_value)
        try:
            # special treatment for strings
            if (len(self.get_shared_data(name).shape) != 0 and
                value != self.get_shared_data(name)):
                    raise ValueError()
        except ValueError:
            try:
                assert value.all() == self.get_shared_data(name).all()
            except TypeError:
                print('str', name)
                assert (str(value).strip() ==
                        str(self.get_shared_data(name)).strip())

    def get_shared_data(self, name, is_ssload=False):
        """Get shared data.
        """
        if is_ssload:
            position = self.config.name_indices[name]
            real_value = getattr(self.w2_fortran.shared_data, 'ssload')
            return real_value[:, :, position]
        if name in self.config.additional_species:
            real_name, position = self.config.additional_species[name]
            real_value = getattr(self.w2_fortran.shared_data, real_name)
            return real_value[:, :, position]
        try:
            value = getattr(self.w2_fortran.shared_data, name)
            return value
        except SystemError:
            real_name, position = pointers.pointers[name]
            position = int(position)
            real_value = getattr(self.w2_fortran.shared_data, real_name)
            return real_value[:, :, position]



    def readinput(self):
        """Proxy method for `w2_fortran.readinput`.
        """
        old_path = os.getcwd()
        os.chdir(self.temp_path)
        self.w2_fortran.readinput()
        os.chdir(old_path)

    def cleanup(self):
        """Proxy method for `w2_fortran.cleanup`.
        """
        self.w2_fortran.cleanup()

    def close_files(self):
        """Proxy method for `w2_fortran.close_files`.
        """
        self.w2_fortran.close_files()

    def hydrodynamics(self):
        """Proxy method for `w2_fortran.hydrodynamics`.
        """
        self.w2_fortran.hydrodynamics()

    def allocate_main(self):
        """Proxy method for `w2_fortran.allocate_main`.
        """
        self.w2_fortran.allocate_main()

    def deallocate_main(self):
        """Proxy method for `w2_fortran.deallocate_main`.
        """
        self.w2_fortran.deallocate_main()

    def set_pointers(self):
        """Proxy method for `w2_fortran.set_pointers`.
        """
        self.w2_fortran.set_pointers()

    def deallocate_pointers(self):
        """Proxy method for `w2_fortran.deallocate_pointers`.
        """
        self.w2_fortran.deallocate_pointers()

    def initvariables(self):
        """Proxy method for `w2_fortran.initvariables`.
        """
        self.w2_fortran.initvariables()

    def constituentcalculations(self, kinetics, add_ssp, add_ssgw, add_ssload):
        """Proxy method for `w2_fortran.constituentcalculations`.
        """
        self.w2_fortran.constituentcalculations(kinetics, add_ssp, add_ssgw,
                                                add_ssload)

    def misccalculations(self):
        """Proxy method for `w2_fortran.misccalculations`.
        """
        self.w2_fortran.misccalculations()

    @property
    def active_volume(self):
        """Calculate active volume of lake.
        """
        return numpy.sum(self.get_shared_data('vactive')[:])

    @property
    def geometry(self):
        """Retrun geometry values.
        """
        geometry = {}
        for name in ['dlx', 'b', 'h']:
            geometry[name] = self.get_shared_data(name)
        return geometry


class W2PyroProxy(W2Proxy):
    """Proxy for W2 using pyro.
    """

    #def __init__(self, temp_path, daemon):
        #core.ObjBase.__init__(self)
        #W2Proxy.__init__(self, temp_path)
        #self.daemon = daemon

    #def stop(self):
        #"""Stopping server.
        #"""
        #print('Pyro server stopped.')
        #self.daemon.shutdown()


if __name__ == '__main__':

    def test():
        """Test it.
        """
        core.initServer()
        daemon = core.Daemon()
        temp_path = r'e:\daten\projects\pitlakq\RAM\zwenkau_BV2f\temp'
        uri = daemon.connect(W2PyroProxy(temp_path, daemon), "w2_proxy")

        print("The daemon runs on port:", daemon.port)
        print("The object's uri is:", uri)
        daemon.requestLoop()

    test()
