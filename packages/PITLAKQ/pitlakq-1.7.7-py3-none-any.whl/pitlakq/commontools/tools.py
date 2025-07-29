"""Miscanellous tools.
"""

from __future__ import print_function

import cmath
import os
import shutil
import sys



def flatten(seq):
    """Flatten a sequence.
    """
    res = []
    for item in seq:
        if type(item) in (tuple, list):
            res.extend(flatten(item))
        else:
            res.append(item)
    return res


def kf_split_old(kf_wert):
    """Splitting kf in mantisse and exponent."""
    # pylint: disable-msg=C0103
    ke = int((cmath.log10(kf_wert).real) - 1)
    kf = 10 ** (abs((ke) + abs(cmath.log10(kf_wert))))
    if kf == 10.0:
        kf = kf // 10
        ke = ke + 1
    return kf, ke


def kfSplit(origKf):
    """Splitting kf in mantisse and exponent."""
    # pylint: disable-msg=C0103
    kf, ke = ('%e' % origKf).split('e')
    kf = float(kf)
    ke = int(ke)
    return kf, ke


def keep_old_files(file_name, nold):
    """Keep old files around by copying file to file_name + .n.

    Example:
    File is a.txt.n is a positive integer, n > 0.
    If no file a.txt exists, nothing happens.
    If a.txt exists it will be copied to a.txt.1.
    If a.txt.1 exits it will be copied to a.txt.2 and a.txt to a.txt.1.
    etc.
    """
    working_dir, base_name = os.path.split(file_name)
    ext_numbers = [int(os.path.splitext(name)[1][1:]) for name in
                   os.listdir(working_dir) if name.startswith(base_name + '.')]
    ext_numbers.sort()
    for number in ext_numbers:
        if number > nold:
            os.remove(os.path.join(working_dir, base_name + '.%d' % number))
    ext_numbers = [number for number in ext_numbers if number <= nold]
    if ext_numbers and ext_numbers[-1] < nold:
        ext_numbers.append(ext_numbers[-1] + 1)
    for old_number, new_number in reversed(list(zip(ext_numbers[:-1],
                                               ext_numbers[1:]))):
        src = os.path.join(working_dir, base_name + '.%d' % old_number)
        dst = os.path.join(working_dir, base_name + '.%d' % new_number)
        shutil.copy(src, dst)
    if os.path.exists(file_name):
        shutil.copy(file_name,
                    os.path.join(working_dir, base_name + '.%d' % 1))


def duration_display(seconds):
    """Make human readable string from seconds.
    """
    if seconds < 0:
        raise ValueError('negative durations are not allowed')
    minutes, sec = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    result = ''
    if days:
        if days == 1:
            result = '%d day ' % days
        else:
            result = '%d days ' % days
    result += '%02d:%02d:%02d (hh:mm:ss)' % (hours, minutes, sec)
    return result

def make_debug_string(names):
    """Generate a nice looking string for the given variable names.
    The names are evaluated to get their vales:

    >>> v_1 = 1
    >>> v_2 = 2
    >>> v_3 = 3
    >>> print(make_debug_string(['v_1', 'v_2', 'v_2']))
    v_1: 1
    v_2: 2
    v_2: 2
    """
    return '\n'.join(': '.join([entry, str(eval(entry))]) for entry in names)


def raise_or_show_info(exception, msg='An error has occured.'):
    """Throw exception if in sourc mode or show message if compiled.

    User that use the compiled version often do not like exceptions.
    Use for warnings about inconsistent input and the like.
    """
    if hasattr(sys,"frozen") and sys.frozen in ("windows_exe", "console_exe"):
        print(msg)
        sys.exit(1)
    else:
        raise exception(msg)


def interpolate(x_0, x_1, y_0, y_1, x_value):
    """Linear interpolation of a value.

    Given are four tabulated data points x_0, x_1, y_0, y_1.
    Find the valuy y_value for a given x_value using linear
    interpolation.

    x_0         y_0
    x_value     y_value
    x_1         y_1
    """
    return y_0 + ((y_1 - y_0) / (x_1 - x_0)) * (x_value - x_0)


if __name__ == '__main__':

    def test():
        """Test run times of old and new function for kf splitting.
        """
        import time

        loops = range(1000000)
        start1 = time.clock()
        for _ in loops:
            kfSplit(11)
        end1 = time.clock()

        start2 = time.clock()
        for _ in loops:
            kf_split_old(11)
        end2 = time.clock()
        print('new:', end1 - start1)
        print('old:', end2 - start2)
        print('new-old', (end1 - start1) - (end2 - start2))

    test()
