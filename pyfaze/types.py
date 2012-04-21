from struct import pack, unpack, calcsize
from functools import partial
from collections import namedtuple

__all__ = ["ANA_REG", "ANA_UI", "ANA_SI", "ANA_UC", "ANA_SC"]


def make_anafaze_type(struct_def, name):
    return type(name, (object,), 
        dict(
            to_python = partial(unpack, *[struct_def]),
            from_python = partial(pack, *[struct_def]),
            byte_size = calcsize(struct_def),
        )
    )()


ANA_REG = ANA_UI = make_anafaze_type("H", "ANA_UI") # Unsigned Integer (16-bit unsigned int)
ANA_SI = make_anafaze_type("h", "ANA_SI") # Signed Integer (16-bit signed int)
ANA_UC = make_anafaze_type("B", "ANA_UC") # Unsigned Char (8-bit unsigned char)
ANA_SC = make_anafaze_type("b", "ANA_SC") # Signed Char (8-bit signed char)
