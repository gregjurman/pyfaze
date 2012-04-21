from pyfaze.types import *
from collections import namedtuple

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


def make_anafaze_register(cls_name, name, register_location, _type, read_only=False, long_description=None):
    def from_python(cls, value):
        out_list = []
        for v in value:
            out_list.append(_type.from_python(v))

        return "".join(out_list)

    def to_python(cls, value):
        in_list = []
        for v in slicer(str(value), _type.byte_size):
            data = "".join(v)
            in_list.append(_type.to_python(data)[0])

        if len(in_list) == 1:
            return in_list[0]

        return in_list

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
            byte_location = ANA_REG.from_python(register_location),
        )
    )

    return reg


PropBandGain = make_anafaze_register("PropBandGain", "Proportional Band/Gain", 0x0020, ANA_UC)
DerivativeTerm = make_anafaze_register("DerivativeTerm", "Derivative Term", 0x0060, ANA_UC)
IntegralTerm = make_anafaze_register("IntegralTerm", "Integral Term", 0x00A0, ANA_UI)
EEPROMVersion = make_anafaze_register("EEPROMVersion", "EEPROM Version Code", 0x0BF0, ANA_UC, True)
AmbientSensorReadings = make_anafaze_register("AmbientSensorReadings", "Ambient Sensor Readings", 0x0720, ANA_SI, True)
ControllerType = make_anafaze_register("ControllerType", "Controller Type", 0x47F0, ANA_UC, True)
