"""Split path in all of its parts.

We have two different implementations-
parse_path should be faster because it avoids the anti-pattern
`insert(0, my_list)`.
"""

import os
import sys


def splitall(path):
    """Split path in all its parts.
    
    Python Cookbook First Edition, 2002
    4.16 Trent Mick
    """
    allparts = []
    while True:
        parts = os.path.split(path)
        if parts[0] == path:  # sentinel for absolute paths
            allparts.insert(0, parts[0])
            break
        elif parts[1] == path: # sentinel for relative paths
            allparts.insert(0, parts[1])
            break
        else:
            path = parts[0]
            allparts.insert(0, parts[1])
    return allparts


def parse_path(path):
    """Parses a path to its components.

    Example:
        parse_path("C:\\Python25\\lib\\site-packages\\zipextimporter.py")
    Returns:
       ['C:\\', 'Python25', 'lib', 'site-packages', 'zipextimporter.py'] 
    Scott David Daniels
    http://mail.python.org/pipermail/python-list/2008-June/1148321.html

    This avoids the anti-pattern `insert(0, my_list)`."""
    head, tail = os.path.split(path)
    result = []
    if not tail:
        if head == path:
            return [head]
        # Perhaps result = [''] here to an indicate ends-in-sep
        head, tail = os.path.split(head)
    while head and tail:
        result.append(tail)
        head, tail = os.path.split(head)
    result.append(head or tail)
    result.reverse()
    return result
