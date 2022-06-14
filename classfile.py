
import struct
from typing import Optional, TextIO

# from Globals import g

CONSTANT_Invalid = 0
CONSTANT_Utf8 = 1
CONSTANT_Integer = 3
CONSTANT_Float = 4
CONSTANT_Long = 5
CONSTANT_Double = 6
CONSTANT_Class = 7
CONSTANT_String = 8
CONSTANT_Fieldref = 9
CONSTANT_Methodref = 10
CONSTANT_InterfaceMethodref = 11
CONSTANT_NameAndType = 12
CONSTANT_MethodHandle = 15
CONSTANT_MethodType = 16
CONSTANT_InvokeDynamic = 18
CONSTANT_Module = 19
CONSTANT_Package = 20

CP_OFFSET = 10  # Offset of constant pool in classfile


cp_names = [
    'Invalid',
    'Utf8',
    'Invalid-2',
    'Integer',
    'Float',
    'Long',
    'Double',
    'Class',
    'String',
    'Fieldref',
    'Methodref',
    'InterfaceMethodref',
    'NameAndType',
    'Invalid-13',
    'Invalid-14',
    'MethodHandle',
    'MethodType',
    'Invalid-17',
    'InvokeDynamic',
    'Module',
    'Package'
    ]


class Cp_info:
    tag: int

    # NOTE: Only a few of these will be populated for a given tag.
    class_index: int
    name_and_type_index: int
    string_index: int
    name_index: int
    descriptor_index: int

    bytes_num: bytes

    length: int
    bytes_utf: bytes
    reference_kind: int
    reference_index: int

    bootstrap_method_attr_index: int

    def __init__(self, tag):
        self.tag = tag


class Classfile:
    data: bytes
    magic: int
    minor_version: int
    major_version: int
    constant_pool_count: int
    constant_pool: list[Cp_info]

    def __init__(self, buff):
        self.data = buff

    def parse_header(self):
        a, b, c, d = struct.unpack('>IHHH', self.data[0:10])
        assert a == 0xcafebabe
        self.magic = a
        self.minor_version = b
        self.major_version = c
        self.constant_pool_count = d
        # print('cp count:', d)

    def parse_constant_pool(self):
        self.constant_pool = []
        self.constant_pool.append(Cp_info(0))  # dummy entry
        i = 1  # The CP number is one more than the list index.
        offset = CP_OFFSET
        while i < self.constant_pool_count:
            need_extra_cp_entry = False
            tag = self.data[offset]
            cp = Cp_info(tag)
            if tag in (CONSTANT_Fieldref, CONSTANT_Methodref, CONSTANT_InterfaceMethodref):
                a, b = struct.unpack(">HH", self.data[offset+1: offset + 5])
                cp.class_index = a
                cp.name_and_type_index = b
                offset += 5
            elif tag == CONSTANT_String:
                a = struct.unpack(">H", self.data[offset+1: offset+3])
                cp.string_index = a[0]
                offset += 3
            elif tag in (CONSTANT_Class, CONSTANT_Module, CONSTANT_Package):
                a = struct.unpack(">H", self.data[offset+1: offset+3])
                cp.name_index = a[0]
                offset += 3
            elif tag == CONSTANT_Utf8:
                a = struct.unpack('>H', self.data[offset+1: offset+3])
                length = a[0]
                cp.bytes_utf = self.data[offset+3: offset+3+length]
                offset += 3 + length
            elif tag == CONSTANT_NameAndType:
                a, b = struct.unpack('>HH', self.data[offset+1: offset + 5])
                cp.name_index = a
                cp.descriptor_index = b
                offset += 5
            elif tag in (CONSTANT_Integer, CONSTANT_Float):
                cp.bytes_num = self.data[offset+1: offset+5]
                offset += 5
            elif tag in (CONSTANT_Long, CONSTANT_Double):
                cp.bytes_num = self.data[offset+1: offset+9]
                offset += 9
                i += 1  # Adjust index of next entry
                need_extra_cp_entry = True
            elif tag == CONSTANT_MethodHandle:
                a, b = struct.unpack('>BH', self.data[offset+1: offset+4])
                cp.reference_kind = a
                cp.reference_index = b
                offset += 4
            elif tag == CONSTANT_MethodType:
                a = struct.unpack('>H', self.data[offset+1: offset+3])
                cp.descriptor_index = a[0]
                offset += 3
            elif tag == CONSTANT_InvokeDynamic:
                a, b = struct.unpack('>HH', self.data[offset+1: offset+5])
                cp.bootstrap_method_attr_index = a
                cp. name_and_type_index = b
                offset += 5
            else:
                print('invalid tag:', tag)
                assert False
            # print('storing cp info:', i, 'tag:', tag)
            self.constant_pool.append(cp)
            if need_extra_cp_entry:
                cp = Cp_info(CONSTANT_Invalid)
                self.constant_pool.append(cp)
            i += 1
        print('cpool DONE. length =', len(self.constant_pool))


# ------------------------------------------------

def parse(buff: bytes) -> Optional[Classfile]:
    # print('parsing...')
    cls = Classfile(buff)

    cls.parse_header()
    cls.parse_constant_pool()

    return cls

# ------------------------------------------------


def disassemble(cls: Classfile, fname: str) -> None:
    # print('disassembling into:', fname)
    with open(fname, 'wt') as f:
        print(f'magic: {cls.magic:#8x}', file=f)
        print(f'major version: {cls.major_version}', file=f)
        print(f'minor version: {cls.minor_version}', file=f)
        print(f'constant pool count: {cls.constant_pool_count}', file=f)

        show_constant_pool(cls, f)


def show_constant_pool(cls: Classfile, f: TextIO) -> None:
    print('\nConstant pool:', file=f)
    for i, cp in enumerate(cls.constant_pool):
        # print('showing. tag =', cp.tag, len(cp_names))
        name = cp_names[cp.tag]
        if cp.tag in (CONSTANT_Methodref, CONSTANT_Fieldref, CONSTANT_InterfaceMethodref):
            print(f'{i}: {name} {cp.class_index} {cp.name_and_type_index}', file=f)
        elif cp.tag == CONSTANT_String:
            print(f'{i}: {name} {cp.string_index}', file=f)
        elif cp.tag in (CONSTANT_Class, CONSTANT_Module, CONSTANT_Package):
            print(f'{i}: {name} {cp.name_index}', file=f)
        elif cp.tag == CONSTANT_NameAndType:
            print(f'{i}: {name} {cp.name_index} {cp.descriptor_index}', file=f)
        elif cp.tag == CONSTANT_Integer:
            a = struct.unpack('>i', cp.bytes_num)
            num = a[0]
            print(f'{i}: {name} {num}', file=f)
        elif cp.tag == CONSTANT_Float:
            a = struct.unpack('>f', cp.bytes_num)
            num = a[0]
            print(f'{i}: {name} {num} raw: {bytes.hex(cp.bytes_num)}', file=f)
        elif cp.tag == CONSTANT_Long:
            a = struct.unpack('>q', cp.bytes_num)
            num = a[0]
            print(f'{i}: {name} {num}', file=f)
        elif cp.tag == CONSTANT_Double:
            a = struct.unpack('>d', cp.bytes_num)
            num = a[0]
            print(f'{i}: {name} {num} raw: {bytes.hex(cp.bytes_num)}', file=f)
        elif cp.tag == CONSTANT_Utf8:
            print(f'{i}: {name} {cp.bytes_utf!r}', file=f)
        elif cp.tag == CONSTANT_MethodHandle:
            print(f'{i}: {name} {cp.reference_kind} {cp.reference_index}', file=f)
        elif cp.tag == CONSTANT_MethodType:
            print(f'{i}: {name} {cp.descriptor_index}', file=f)
        elif cp.tag == CONSTANT_InvokeDynamic:
            print(f'{i}: {name} {cp.bootstrap_method_attr_index} {cp.name_and_type_index}', file=f)
        else:
            print(f'{i}: {name}', file=f)
