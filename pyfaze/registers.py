from pyfaze.types import *
from collections import namedtuple

register_list = []

def slicer(iterable, width):
    """
        Slices iterables into chunks. How does itertools not have this function.
    """
    if len(iterable) % width is not 0:
        raise Exception("Iterable length must be divisable by the width")

    for start in range(0, len(iterable), width):
        yield iterable[start:start+width]


class AnafazeRegister(object):
    """{0}{4}:
    {1}

    Data Type: {2}
    Size: {3}
    """
    pass


def make_anafaze_register(cls_name, name, register_location, _type, iterated=True, read_only=False, long_description=None):
    """
    Generates a register class that is used to marshall data to and from the Anafaze controller.

    - cls_name - (str) Class name of the register
    - name - (str) Human readable name of the register
    - register_location - (int) Memory location on the Anafaze (ie. 0x0020, 0x0F60)
    - _type - (AnafazeType or int) Either a marshalling helper or a integer symbolizing a fixed byte-size
    - read_only - If the register is read only
    - long_description - Documentation on what the register does.
    """

    def from_python(cls, value):
        """
            Convert value(or values) from Python into something the Anafaze understands
        """
        out_list = []
        for v in value:
            out_list.append(_type.from_python(v))

        return "".join(out_list)

    def to_python(cls, value):
        """
            Convert value(or values) from the Anafaze into something Python understands 
        """
        in_list = []
        for v in slicer(str(value), _type.byte_size):
            data = "".join(v)
            m = _type.to_python(data)
            if len(m) == 1:
                in_list.append(m[0])
            else:
                in_list.append(m)

        if len(in_list) == 1:
            return in_list[0]

        return in_list

    if isinstance(_type, int):
        # If we got a set number rather than a marshall type its a fixed byte-size and
        #   non-iterable.
        _type = make_anafaze_type('B'*_type, cls_name+"Type")
        iterated = False

    reg = type(cls_name, (AnafazeRegister,), 
        dict(
            __doc__ = AnafazeRegister.__doc__.format(
                name, str(long_description), 
                _type.__class__.__name__, _type.byte_size,
                " (Read Only)" if read_only else ""),
            to_python = classmethod(to_python),
            from_python = classmethod(from_python) if not read_only else classmethod(lambda x,v=None: None),
            byte_size = _type.byte_size,
            name = name,
            type = _type,
            location = register_location,
            iterated = iterated,
            byte_location = ANA_REG.from_python(register_location),
        )
    )

    register_list.append(reg)

    return reg


PropBandGain = make_anafaze_register("PropBandGain", "Proportional Band/Gain",
    0x0020, ANA_UC)

DerivativeTerm = make_anafaze_register("DerivativeTerm", "Derivative Term",
    0x0060, ANA_UC)

IntegralTerm = make_anafaze_register("IntegralTerm", "Integral Term", 
    0x00A0, ANA_UI)

EEPROMVersion = make_anafaze_register("EEPROMVersion", "EEPROM Version Code", 
    0x0BF0, 3, iterated=False, read_only=True)

AmbientSensorReadings = make_anafaze_register("AmbientSensorReadings", 
    "Ambient Sensor Readings", 
    0x0720, ANA_SI, iterated=False, read_only=True)

ProcessVariable = make_anafaze_register("ProcessVariable", "Process Variable",
    0x0280, ANA_SI, iterated=True, read_only=True)

ControllerType = make_anafaze_register("ControllerType", "Controller Type", 
    0x47F0, ANA_BYTE, iterated=False, read_only=True)

SystemStatus = make_anafaze_register("SystemStatus", "System Status", 
    0x0AC8, 4, iterated=False, read_only=True)
