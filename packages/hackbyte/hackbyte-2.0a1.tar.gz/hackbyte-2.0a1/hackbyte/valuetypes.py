import struct

class ValueType:
    def __init__(self, fmt, size):
        self.fmt = fmt
        self.size = size

    def pack(self, value):
        return struct.pack(self.fmt, value)

    def unpack(self, data):
        return struct.unpack(self.fmt, data)[0]

# Tabel jenis type yang didukung
VALUE_TYPES = {
    'dword': ValueType('<i', 4),
    'qword': ValueType('<q', 8),
    'float': ValueType('<f', 4),
    'double': ValueType('<d', 8),
    'byte': ValueType('B', 1),  # unsigned char
    'string': None  # khusus, ditangani terpisah
}

def parse_value_type(type_):
    if type_ in VALUE_TYPES and VALUE_TYPES[type_]:
        return VALUE_TYPES[type_]
    raise ValueError(f"Unsupported type: {type_}")

def parse_value(type_, value):
    if type_ == 'string':
        return value.encode()
    elif type_ in VALUE_TYPES:
        return VALUE_TYPES[type_].pack(int(value) if type_ != 'float' and type_ != 'double' else float(value))
    else:
        raise ValueError(f"Unsupported type: {type_}")