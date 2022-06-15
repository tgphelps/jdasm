
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


class Attribute:
    attribute_name_index: int
    attribute_length: int
    info: bytes

    def __init__(self):
        pass


class Field:
    access_flags: int
    name_index: int
    descriptor_index: int
    attributes_count: int
    attribute_info: list[Attribute]


class Method:
    access_flags: int
    name_index: int
    descriptor_index: int
    attributes_count: int
    attribute_info: list[Attribute]


class Classfile:
    data: bytes
    magic: int
    minor_version: int
    major_version: int
    constant_pool_count: int
    constant_pool: list[Cp_info]
    access_flags: int
    this_class: int
    super_class: int
    interfaces_count: int
    interfaces: list[int]
    fields_count: int
    fields: list[Field]
    methods_count: int
    methods: list[Method]
    attributes_count: int
    attributes: list[Attribute]

    offset: int  # used only while parsing

    def __init__(self, buff):
        self.data = buff

    def parse(self):
        self.parse_header()
        self.parse_constant_pool()
        self.parse_middle()
        self.parse_fields()
        self.parse_methods()
        self.parse_attributes()

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
        # print('cpool DONE. length =', len(self.constant_pool))
        self.offset = offset

    def parse_middle(self):
        offset = self.offset
        a, b, c, d = struct.unpack('>HHHH', self.data[offset: offset+8])
        self.access_flags = a
        self.this_class = b
        self.super_class = c
        self.interfaces_count = d
        # print(a, b, c, d)
        offset += 8
        if self.interfaces_count > 0:
            print('interfaces:', self.interfaces_count)
        self.interfaces = []
        for i in range(self.interfaces_count):
            a = struct.unpack(">H", self.data[offset: offset+2])
            self.interfaces.append(a[0])
            offset += 2
        self.offset = offset

    def parse_fields(self):
        a = struct.unpack('>H', self.data[self.offset: self.offset+2])
        self.fields_count = a[0]
        self.fields = []
        self.offset += 2
        for i in range(self.fields_count):
            f = Field()
            a, b, c, d = struct.unpack('>HHHH', self.data[self.offset: self.offset+8])
            self.offset += 8
            f.access_flags = a
            f.name_index = b
            f.descriptor_index = c
            f.attributes_count = d
            f.attribute_info = []
            for j in range(f.attributes_count):
                f.attribute_info.append(self.parse_one_attribute())
            self.fields.append(f)

    def parse_methods(self):
        a = struct.unpack('>H', self.data[self.offset: self.offset+2])
        self.methods_count = a[0]
        self.methods = []
        self.offset += 2
        for i in range(self.methods_count):
            m = Method()
            a, b, c, d = struct.unpack('>HHHH', self.data[self.offset: self.offset+8])
            self.offset += 8
            m.access_flags = a
            m.name_index = b
            m.descriptor_index = c
            m.attributes_count = d
            m.attribute_info = []
            for j in range(m.attributes_count):
                m.attribute_info.append(self.parse_one_attribute())
            self.methods.append(m)

    def parse_attributes(self):
        a = struct.unpack('>H', self.data[self.offset: self.offset+2])
        self.attributes_count = a[0]
        self.offset += 2
        self.attributes = []
        for a in range(self.attributes_count):
            self.attributes.append(self.parse_one_attribute())

    def parse_one_attribute(self) -> Attribute:
        offset = self.offset
        a, b = struct.unpack('>HI', self.data[offset: offset+6])
        offset += 6
        attr = Attribute()
        attr.attribute_name_index = a
        attr.attribute_length = b
        attr.info = self.data[offset: offset + b]
        self.offset += 6 + b
        return attr


# ------------------------------------------------

def parse(buff: bytes) -> Optional[Classfile]:
    # print('parsing...')
    cls = Classfile(buff)
    cls.parse()
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

        print('', file=f)
        print(f'access flags: {cls.access_flags:#04x}', file=f)
        print(f'this class: {cls.this_class}', file=f)
        print(f'super class: {cls.super_class}', file=f)
        print(f'interfaces count: {cls.interfaces_count}', file=f)
        if cls.interfaces_count > 0:
            s = ' '.join([str(i) for i in cls.interfaces])
            print('interfaces:', s, file=f)

        show_fields(cls, f)
        show_methods(cls, f)


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


def show_fields(cls: Classfile, fp: TextIO) -> None:
    print('\nFields:', file=fp)
    for f in cls.fields:
        print(f'field {f.access_flags:#04x} {f.name_index} {f.descriptor_index} ' +
              f'{f.attributes_count}', file=fp)
        if f.attributes_count > 0:
            print('   attributes:', file=fp)
            for a in f.attribute_info:
                print(f'   name {a.attribute_name_index} len: {a.attribute_length}', file=fp)


def show_methods(cls: Classfile, fp: TextIO) -> None:
    print('\nMethods:', file=fp)
    for m in cls.methods:
        print(f'method {m.access_flags:#04x} {m.name_index} {m.descriptor_index} ' +
              f'{m.attributes_count}', file=fp)
        if m.attributes_count > 0:
            print('   attributes:', file=fp)
            for a in m.attribute_info:
                print(f'   name {a.attribute_name_index} len: {a.attribute_length}', file=fp)


def show_attributes(cls: Classfile, fp: TextIO) -> None:
    print(f'\nAttribute count: {cls.attributes_count}')
    if cls.attributes_count > 0:
        for a in cls.attributes:
            print(f'   name {a.attribute_name_index} len: {a.attribute_length}', file=fp)
