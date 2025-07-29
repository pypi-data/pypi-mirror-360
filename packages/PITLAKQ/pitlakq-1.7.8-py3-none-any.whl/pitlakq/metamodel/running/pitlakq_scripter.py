#!/usr/local/bin/python
# coding: utf-8

###############################################################################
# PITLAKQ
# The Pit Lake Hydrodynamic and Water Quality Model
# http://www.pitlakq.com/
# Author: Mike Mueller
# mmueller@hydrocomputing.com
#
# Copyright (c) 2012, Mike Mueller
# All rights reserved.
#
# This software is BSD-licensed.
# See the file license.txt for license.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
###############################################################################

"""Utility to start any script against the PITLAKQ API.


This allows to run scripts without installation of neither
Python nor PITLAKQ. Uses py2exe and copies the script
that is given as command line argument into a file
called script_runner.py that will be aded to library.zip
and executed.
"""

import os
import shutil
import subprocess
import sys
import zipfile


class PitlakqScripter(object):
    """Run scripts against the PITLAKQ API.
    """
    def __init__(self, script, out_file_name):
        self.file_name = script
        self.out_file_name = out_file_name
        self.module_name = self.out_file_name.split('.')[0]
        self.mod_text = ''

    def modify_file(self):
        """
        Replace __name__ with name of script.
        """
        fobj = open(self.file_name)
        text = fobj.readlines()
        fobj.close()
        new_text = []
        for line in text:
            split_line = line.split()
            if ' '.join(split_line) == "if __name__ == '__main__':":
                line = "if __name__ == '%s':\n" % self.module_name
            new_text.append(line)
        self.mod_text = ''.join(new_text)
                                
    def add_to_zip(self):
        """Add modified file to zip archive.
        """
        # need absoltute path
        # there is no `__file__` so we use sys.argv
        path = os.path.dirname(sys.argv[0])
        lib_name = 'library.zip'
        if os.path.isabs(path):
            zip_file_name = os.path.join(path, lib_name)
        else:
            # get absolute path by searching the
            # environmental variable PATH
            for path in os.environ['PATH'].split(os.pathsep):
                possible_file_name = os.path.join(path, lib_name)
                if os.path.exists(possible_file_name):
                    zip_file_name = possible_file_name
                    # take first one and break out
                    break
        zip_file_name_old = os.path.splitext(zip_file_name)[0] + '_old.zip'
        shutil.move(zip_file_name, zip_file_name_old)
        zin = zipfile.ZipFile(zip_file_name_old, 'r')
        zout = zipfile.ZipFile(zip_file_name, 'w')
        zout.debug = 3
        # avoid duplicate names and copy whole file except
        # the script to be executed
        found = False
        for item in zin.infolist():
            item_buffer = zin.read(item.filename)
            if item.filename == self.out_file_name:
                found = True
                zout.writestr(self.out_file_name, self.mod_text)
            else:
                zout.writestr(item, item_buffer)
        # script was not in old file --> add it without creating a duplicate
        if not found:
            zout.writestr(self.out_file_name, self.mod_text)
        zout.close()
        zin.close()

    def copy_to_exe(self):
        """Copy script to be run into compile path.
        """
        path_name = os.path.dirname(sys.argv[0])
        sys.path.append(path_name)
        file_name = os.path.join(path_name, self.out_file_name)
        shutil.copy(os.path.abspath(self.file_name), file_name)

    def import_script(self):
        """Import script, i.e. run it.
        """
        try:
            __import__(self.module_name)
        # For some reason the very first run does NOT work
        # because the script is only partially written into
        # the zip file. Seems like there is some buffering
        # going on. Therefore, we just call ourselves again
        # when this happens.
        except SyntaxError:
            subprocess.call([sys.argv[0], sys.argv[1]])
            

def main(script):
    """Run the script
    """
    scripter = PitlakqScripter(script, 'script_runner.py')
    scripter.modify_file()
    #scripter.add_to_zip()
    scripter.copy_to_exe()
    scripter.import_script()
    try:
        os.remove('script_runner.py')
        os.remove('script_runner.pyc')
    except:
        pass
    
if __name__ == '__main__':
    main(script)