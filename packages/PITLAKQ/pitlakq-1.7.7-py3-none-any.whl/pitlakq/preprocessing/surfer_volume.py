"""Calculate lake level-volume relationship with Surfer and pywinauto.

This program is intended to produce test data to compare with W2 volumes.
It is tested with Surfer 9.1.352 - Apr 8 2009.

The mechanism is rather brittle. Don't do anything with the keybord or the
mouse while the program is running. If the program crashes, make sure you
start with an empty temporary directory. If it complains with
"There are 2 windows that match the criteria" or claims a file that is there
is missing, increase the value for WAIT_BETWEEN_LEVELS. This value depends
on how fast the machine is.

The whole thing is really slow. It took about 45 minutes to calculate
900 levels. The calculation itself may take a second or so.
"""

from __future__ import print_function

import os
import time

from pywinauto import application

STARTUP_DELAY = 3
WAIT_BETWEEN_LEVELS = 0.5


class LevelVolumeRelation(object):
    """Calculate lake level-volume relationship with Surfer and pywinauto.
    """
    def __init__(self, app_path, grid_file_name, tmp_path):
        self.grid_file_name = grid_file_name
        self.tmp_path = tmp_path
        self.app_path = app_path
        self.app = None

    def _start_surfer(self):
        """Start the Surfer applicatio
        """
        self.app = application.Application()
        self.app.Start_(self.app_path)
        print('Waiting %d seconds until Surfer has started.' % STARTUP_DELAY)
        time.sleep(STARTUP_DELAY)

    def calculate_volume(self, level):
        """
        Use Surfer with pywinauto to compute volume and area for given level.
        """
        if not self.app:
            self._start_surfer()
        surfer = self.app.Surfer
        pause = 0.01
        surfer.TypeKeys('{F10} {RIGHT 5} {ENTER} {DOWN 12} {ENTER}',
                        pause=pause)
        open_dlg = self.app.window_(title_re='Open Grid')
        open_dlg.TypeKeys(self.grid_file_name + ' {ENTER}')
        volume_dlg = self.app.window_(title_re='Grid Volume')
        volume_dlg.TypeKeys('{DOWN} {TAB} ' + '%5.2f' % level)
        volume_dlg.TypeKeys('{TAB} {UP} {ENTER}', pause=pause)
        volume_dlg = self.app.window_(title_re='Surfer - Report*')
        volume_dlg.TypeKeys('{F10} {ENTER} {DOWN 2} {ENTER}', pause=pause)
        save_dlg = self.app.window_(title_re='Speichern unter')
        save_dlg.TypeKeys(os.path.join(self.tmp_path, '%5.2f.txt' % level))
        save_dlg.TypeKeys('{RIGHT} {TAB} {DOWN} {ENTER 2} {F10} {ENTER 2}',
                          pause=pause)
        time.sleep(WAIT_BETWEEN_LEVELS)

    def read_surfer_output(self, level):
        """Read volume and area from report file from Surfer.
        """
        fobj = open(os.path.join(self.tmp_path, ('%5.2f.txt' % level).strip()))
        for line in fobj:
            if line.startswith('Positive Volume [Cut]:'):
                volume = float(line.split()[-1])
            elif line.startswith('Positive Planar Area [Cut]:'):
                area_planar = float(line.split()[-1])
            elif line.startswith('Positive Surface Area [Cut]:'):
                area_surface = float(line.split()[-1])
        return volume, area_planar, area_surface


def main(start, end, step, grid_file_name, tmp_path='tmp', do_surfer=True,
         app_path=r'c:\Program Files (x86)\Golden Software\Surfer 9'
                  r'\Surfer.exe'):
    """Do the calculation for the levels (start, end, step) exclusive.
    """
    lvr = LevelVolumeRelation(app_path, grid_file_name, tmp_path)
    level = start
    fout = open(os.path.join(tmp_path, 'volume_area.txt'), 'w')
    fout.write('%15s %15s %15s  %15s\n' % ('level', 'volume', 'area_planar',
                                           'area_surface'))
    while level < end:
        if do_surfer:
            lvr.calculate_volume(level)
        volume, area_planar, area_surface = lvr.read_surfer_output(level)
        fout.write('%15.2f %15.2f %15.2f %15.2f\n' % (level, volume,
                                                      area_planar,
                                                      area_surface))
        level += step
    fout.close()


if __name__ == '__main__':
    main(start=110, end=200.1, step=0.1,
         grid_file_name=(r'c:\Daten\Mike\projekte\australien\daten\fuer-Modell'
                         r'\kepwari\kepwari_asci.grd'),
         tmp_path=(r'c:\Daten\Mike\projekte\australien\daten\fuer-Modell'
                   r'\kepwari\tmp'))
