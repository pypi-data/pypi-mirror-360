"""Calculate some error statistics.
"""

import math


def check_lenght(data1, data2):
    """Make sure data1 and data2 have the same lenghts.
    """
    if len(data1) != len(data2):
        msg = 'Data sets need to have same lenght.\n'
        msg += 'Data set 1 has lenght of: %d\n' % len(data1)
        msg += 'Data set 2 has lenght of: %d\n' % len(data2)
        raise ValueError(msg)


def least_squares(data1, data2, allow_different_lenght=False):
    """Calculate the least squares from two given data sets.

    Returns the sum of the squares of the differerenecs between both data sets.
    The lenghts of `data1` and `data2` have to be the same unless
    `allow_different_lenght` is set to `True`. In this case the
    shorter data sets determines how many values are used just like
    in the built-in function `zip`.
    """
    # shortcut if both data sets are identical
    if data1 is data2:
        return 0.0
    if not allow_different_lenght:
        check_lenght(data1, data2)
    return sum((value1 - value2) ** 2 for value1, value2 in zip(data1, data2))


def ame(data1, data2):
    """Calculate the absolute mean error (AME):

    AME = abs(data1 - data1) / n
    n = len(data1) = len(data2)
    """
    check_lenght(data1, data2)
    n = len(data1)
    return sum((value1 - value2) for value1, value2 in zip(data1, data2)) / n


def rms(data1, data2):
    """Calculate the root mean square error (RMS):

    RMS = sqrt(abs(data1 - data1) / n)
    n = len(data1) = len(data2)
    """
    return math.sqrt(least_squares(data1, data2)/ len(data1))
