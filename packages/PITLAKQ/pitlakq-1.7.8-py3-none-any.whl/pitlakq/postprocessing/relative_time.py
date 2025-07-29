"""Convert date into relative time to an offset.
"""

from __future__ import print_function

from contextlib import nested
import datetime
import glob
import os
import shutil


def convert_file(in_file_name, out_file_name, start_date):
    """Convert one file replacing the date with relative time in days.
    """
    # Python >= 2.7
    # with open(in_file_name) as fobj_in, open(out_file_name, 'w') as fobj_out:
    # Python 2.6 still needs nested
    with nested(open(in_file_name), open(out_file_name, 'w')) as (
        fobj_in, fobj_out):
        fobj_out.write(next(fobj_in))
        for line in fobj_in:
            date = datetime.datetime.strptime(line[:10], '%d.%m.%Y')
            diff = (date - start_date).days
            new_line = '{0:10d}'.format(diff) + line[10:]
            fobj_out.write(new_line)


def convert_all(in_dir, out_dir, start_date):
    """Convert all txt files.
    """
    for in_file_name in glob.glob(os.path.join(in_dir, '*.txt')):
        out_file_name = os.path.join(out_dir, os.path.basename(in_file_name))
        try:
            convert_file(in_file_name, out_file_name, start_date)
        except ValueError:
            print('No conversion for:', in_file_name)
            shutil.copy(in_file_name, out_file_name)
