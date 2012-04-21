from struct import pack, unpack, calcsize
from functools import partial

__all__ = [ 'make_anafaze_type',
    "ANA_REG","ANA_BYTE", 
    "ANA_DIGOUT", "ANA_DIGIN", 
    "ANA_UI", "ANA_SI", 
    "ANA_UC", "ANA_SC"
]


def make_anafaze_type(struct_def, name):
    """
    Creates an object that helps marshall data to and from python and the anafaze
    """
    return type(name, (object,), 
        dict(
            to_python = partial(unpack, *[struct_def]),
            from_python = partial(pack, *[struct_def]),
            byte_size = calcsize(struct_def),
        )
    )()


ANA_REG = ANA_UI = make_anafaze_type("H", "ANA_UI") # Unsigned Integer (16-bit unsigned int)
ANA_SI = make_anafaze_type("h", "ANA_SI") # Signed Integer (16-bit signed int)
ANA_BYTE = ANA_DIGIN = ANA_UC = make_anafaze_type("B", "ANA_UC") # Unsigned Char (8-bit unsigned char)
ANA_SC = make_anafaze_type("b", "ANA_SC") # Signed Char (8-bit signed char)
ANA_DIGOUT = make_anafaze_type("BBBBBBBB", "ANA_DIGOUT")


