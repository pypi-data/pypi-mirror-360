"""Work with file objects.
"""

import StringIO

def open_file(fobj_or_file_name):
    """Open file from path name or return fobj.
    """
    if isinstance(fobj_or_file_name, basestring):
        fobj = open(fobj_or_file_name)
    elif isinstance(fobj_or_file_name, file) or isinstance(fobj_or_file_name,
                                                           StringIO.StringIO):
        fobj = fobj_or_file_name
    else:
        raise TypeError(
            'First argument needs to either a file name or a file object.'
            'Found: %s' % str(fobj_or_file_name))
    return fobj