"""dBase file reader and writer.

This version uses code generation and `exce` to
speed up things.
"""

from __future__ import print_function

import struct
import shutil

# We expcitly use `exec` here.
# pylint: disable-msg=W0122
# Lots of attributes defined outside __init__.
# pylint: disable-msg=W0201

class Dbf(object):
    """dBase file reade and writer.
    """
    # Many instance attributes.
    # pylint: disable-msg=R0902
    def __init__(self, file_name, as_padded_strings=False):
        self.file_name = file_name
        self.as_padded_strings = as_padded_strings
        self.version_map = {"\x03": "dBASE III",
                            "\x83": "dBASE III+ with memo",
                            "\x8B": "dBASE IV with memo",
                            "\xF5": "FoxPro with memo"}
        self.fobj = open(self.file_name, 'rb')
        self.read_header()
        self.read_field_descriptor()
        self.read_lines()
        if as_padded_strings:
            self.make_string_code()
        else:
            self.make_code()
        self.compile_converter()
        self.fobj.close()

    def read_header(self):
        """Read and interpret the file header.
        """
        self.header_raw = self.fobj.read(32)
        self.version = self.version_map[self.header_raw[0]]
        self.last_update = [ord(value) for value in self.header_raw[1:4]]
        self.last_update[0] += 1900
        self.number_of_records = struct.unpack('i', self.header_raw[4:8])[0]
        self.number_of_bytes_in_header = struct.unpack('h',
                                                    self.header_raw[8:10])[0]
        self.number_of_bytes_in_record = struct.unpack('h',
                                                    self.header_raw[10:12])[0]

    def read_field_descriptor(self):
        """Read the informtion for the fields.
        """
        self.fobj.seek(32)
        self.field_descripter_raw = self.fobj.read(
            self.number_of_bytes_in_header - 32)
        self.number_of_fields = (self.number_of_bytes_in_header - 32) / 32
        self.fields = []
        self.field_name_pos = {}
        start = 0
        n = 0
        for n in range(self.number_of_fields):
            field = {}
            name = self.field_descripter_raw[start:start + 11].split(
                                                                  '\000')[0]
            self.field_name_pos[name] = n
            field['name'] = name
            field['type'] = self.field_descripter_raw[start + 11]
            field['length'] = ord(self.field_descripter_raw[start + 16])
            field['decimal'] = ord(self.field_descripter_raw[start + 17])
            start += 32
            self.fields.append(field)
            n += 1

    def read_lines(self):
        """Read the lines with the data.
        """
        self.fobj.seek(self.number_of_bytes_in_header + 1)
        data = self.fobj.read(self.number_of_bytes_in_record *
                              self.number_of_records)
        self.data = data
        self.lines = []
        start = 0
        end = self.number_of_bytes_in_record
        for _ in range(self.number_of_records):
            self.lines.append(data[start:start+end])
            start += end

    def compile_converter(self):
        """Bytcompile the generated code.
        """
        code = compile(self.code, '<string>', 'exec')
        exec(code)
        try:
            # `compiled_conv` is defined in `exec`.
            # pylint: disable-msg=E0602
            self.list = [compiled_conv(value) for value in self.lines]
        except:
            print(self.code)
            raise

    def make_code(self):
        """Generate the code
        """
        self.code = 'def compiled_conv(line):\n'
        self.code += '    record = [" "] * %d\n' % self.number_of_fields
        start = 0
        n = 0
        for field in self.fields:
            self.code += '    raw = line[%d:%d]\n' % (start,
                                                      start+field['length'])
            if field['type'] == 'N':
                if field['decimal'] > 0:
                    self.code += '    if raw.strip():\n'
                    self.code += '        try:\n'
                    self.code += '            record[%d] = float(raw)\n' % n
                    self.code += '        except ValueError:\n'
                    self.code += '            pass\n'
                    self.code += '    else:\n'
                    self.code += '        record[%d] = 0.0\n' % n
                else:
                    self.code += '    if raw.strip():\n'
                    self.code += '        record[%d] = int(raw)\n' % n
                    self.code += '    else:\n'
                    self.code += '        record[%d] = 0\n' % n
            elif field['type'] == 'D':
                self.code += '    if raw.strip():\n'
                self.code += '        record[%d] = int(raw)\n' % n
            else:
                self.code += '    record[%d] = raw.strip()\n' % n
            start += field['length']
            n += 1
        self.code += '    return record\n'

    def make_string_code(self):
        """Generate code for a string.
        """
        self.code = 'def compiled_conv(line):\n'
        self.code += '    record = [" "] * %d\n' % self.number_of_fields
        start = 0
        n = 0
        for field in self.fields:
            self.code += '    raw = line[%d:%d]\n' % (start,
                                                      start+field['length'])
            self.code += '    record[%d] = raw\n' % n
            start += field['length']
            n += 1
        self.code += '    return record\n'

    def make_back_code(self):
        """Generate code for writing the file back.
        """
        self.back_code = 'def compiled_back_conv(line):\n    back_line = \'\''
        n = 0
        for field in self.fields:
            field_len = field['length']
            if field['type'] == 'C' or field['type'] == 'D':
                self.back_code += ' + '
                self.back_code += 'str(line[%d]).ljust(%d)' % (n, field_len)
            elif field['type'] == 'N':
                if field['decimal'] > 0:
                    self.back_code += (' + ' + '(\'%.' + str(field['decimal'])
                                       + 'f\''+ ' %line[' + str(n) + ']'
                                       + ').rjust(' + str(field_len)
                                       + ')')
                else:
                    self.back_code += (' + ' + '(\'%d\'' + ' %line['
                                       + str(n) + ']' + ').rjust('
                                       + str(field_len)+ ')')
            else:
                print('not definded', field['type'])
            n += 1
        self.back_code += '\n'
        self.back_code += '    return back_line\n'

    def compile_back_converter(self):
        """Compile bytecode to write data back to dBase file.
        """
        code = compile(self.back_code, '<string>', 'exec')
        exec(code)
        # `compiled_back_conv` is defined in `exec`.
        # pylint: disable-msg=E0602
        self.back_list = [compiled_back_conv(value) for value in self.list]

    def convert_back_as_padded_strings1(self):
        """Writing file as padde strings. Version 1.
        """
        for line in self.list[:-1]:
            for item in line:
                self.traget_file.write(item)
            self.traget_file.write(' ')
        for item in self.list[-1]:
            self.traget_file.write(item)
        self.traget_file.write('\012')

    def convert_back_as_padded_strings2(self):
        """Writing file as padded strings. Version 2.
        """
        for line in self.back_list[:-1]:
            for item in line:
                self.traget_file.write(item)
            self.traget_file.write(' ')
        for item in self.back_list[-1]:
            self.traget_file.write(item)
        self.traget_file.write('\032')

    def write(self):
        """Write the file.
        """
        number_of_new_records = len(self.list)
        shutil.copy(self.file_name, self.file_name + '.bak')
        self.traget_file = open(self.file_name, 'wb')
        self.new_header = self.header_raw[:4]
        self.new_header += struct.pack('i', number_of_new_records)
        self.new_header += self.header_raw[8:]
        self.new_header += self.field_descripter_raw
        self.new_header += ' '
        self.traget_file.write(self.new_header)
        if self.as_padded_strings:
            self.back_list = self.list
            self.convert_back_as_padded_strings1()
        else:
            self.make_back_code()
            self.compile_back_converter()
            self.convert_back_as_padded_strings1()
        self.traget_file.flush()
        self.traget_file.close()
