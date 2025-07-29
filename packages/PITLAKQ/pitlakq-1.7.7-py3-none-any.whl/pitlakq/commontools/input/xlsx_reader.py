"""Tools for working xlsx files.
"""

from pitlakq.commontools.datastructures.dicts import OrderedDefaultdict


try:
  basestring
except NameError:
  basestring = str

def read_xslx_table(worksheet, xlsx_file_name, comment_sign='#'):
    """Read a worksheet assumimg dense columns and rows.

    Only columns that have a header in the first line will be read.
    Missing values will cause errors. Fully empty lines and columns
    as well as comments starting with `comment_sign`  will be ignored.
    Result is a dictionary of columns with the column name as the key.
    """
    header = [(head.value, pos) for pos, head in
              enumerate(list(worksheet.rows)[0])  if head.value is not None]
    header_names = [head[0] for head in header]
    data = OrderedDefaultdict(list)
    for lineno, row in enumerate(list(worksheet.rows)[1:], 2):
        data_row = []
        for head, pos in header:
            value = row[pos].value
            if (isinstance(value, basestring) and
                value.strip().startswith(comment_sign)):
                value = None
            if value is not None:
                data_row.append(value)
        if not data_row:
            continue
        if len(data_row) != len(header):
            msg = 'Missing values in line {0}.\n'.format(lineno)
            msg += 'In worksheet {0}.\n'.format(worksheet.title)
            msg += 'All cells that have column names must have values.\n'
            msg += 'Please correct file {0}.'.format(xlsx_file_name)
            raise ValueError(msg)
        for value, head in zip(data_row, header_names):
            data[head].append(value)
    return data