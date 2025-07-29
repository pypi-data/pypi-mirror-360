"""Tools for reading several flavors of text files with columns
"""

import datetime
import StringIO

from pitlakq.commontools.filereader.fobj import open_file


def read_columns(fobj_or_file_name, convert='date_rest_float',
                 date_format='%d.%m.%Y', time_format='%H:%M',
                 comment_char='#'):
    """Read columns from text file.

    Convert is either pre_defined or a dict with all column headers as
    keys and convertion functions as value.

    Supported pre-defimned converters:

    * 'date_rest_float': Read colum labled `date` as date object
                         all other columns as floats.
    * 'datetime_rest_float': Read colums labled `date` and 'time' as date
                             object all other columns as floats.
    """

    def clean_line(line):
        """Ignore evertyhing after the comment char as well as empty lines.
        """
        return line.split(comment_char)[0].strip()

    fobj = open_file(fobj_or_file_name)
    # skip empty lines
    header = None
    for line in fobj:
        if clean_line(line):
            header = line.split()
            break
    if not header:
        return {}
    if isinstance(convert, dict):
        converters = convert
    else:
        converters = _make_convertes(header, convert, date_format, time_format)
    data = dict((key, []) for key in converters)
    for line in fobj:
        if clean_line(line):
            entries = dict((head, entry) for head, entry in
                           zip(header, line.split()))
            if convert == 'date_rest_float':
                entries['datetime'] = entries['date']
                del entries['date']
            elif convert == 'datetime_rest_float':
                entries['datetime'] = entries['date'] + ' ' + entries['time']
                del entries['date']
                del entries['time']
            for name, convert_func in converters.items():
                data[name].append(convert_func(entries[name]))
    return data


def _make_convertes(header, convert, date_format, time_format):
    """Make the convertes according to given option.
    """

    def datetime_converter(date_string):
        """Convert string to datetime object.
        """
        return datetime.datetime.strptime(date_string, datetime_format)

    converters = dict((head, float) for head in header)
    if convert == 'date_rest_float':
        datetime_format = date_format
        del converters['date']
    elif convert == 'datetime_rest_float':
        datetime_format = '%s %s' % (date_format, time_format)
        del converters['date']
        del converters['time']
    else:
        raise NameError('Converter %s is not supported.'
                        % (str(converters)))
    converters['datetime'] = datetime_converter
    return converters
