from pyfaze.registers import register_list
from pyfaze.util import decaser, calc_bcc
from struct import pack
import serial

from binascii import hexlify


__all__ = ["AnafazeController"]

def make_message_header(src, dest, cmd, transaction_id):
    """
        Make the message header. Helper function
    """
    return "%s%s%s\x00%s" % (
            chr((dest+7) & 0xff),
            chr(src & 0xff),
            chr(cmd & 0xff),
            transaction_id)

def make_register_property(register):
    """
    Generates a property for accessing the register.

    This will cause the controller to be polled when getting, and
    new data uploaded when setting.
    """
    def get_register(self):
        if register.iterated:
            data_len = chr((register.byte_size * self.loop_count) & 0xff)
        else:
            data_len = chr(register.byte_size & 0xff)

        message = make_message_header(
            0, self.destination,
            1, self._transaction.next()
            ) + register.byte_location + data_len

        check = self._checksum(message)

        msg = message.replace("\x10", "\x10\x10")
        packet = "\x10\x02%s\x10\x03%s" % (msg, check)

        print hexlify(packet)

        return None

    def set_register(self, value):
        data = register.from_python(value)
    
        message = make_message_header(
            0, self.destination, 
            8, self._transaction.next()
            ) + register.byte_location + data

        check = self._checksum(message)

        msg = message.replace("\x10", "\x10\x10")
        packet = "\x10\x02%s\x10\x03%s" % (msg, check)

        print hexlify(packet)

    return property(get_register, set_register, register.__doc__)


def transaction_gen():
    """
    Little generator for transaction IDs
    """
    i = 0
    while True:
        yield pack("H", i)
        i = i + 1

class AnafazeControllerMeta(type):
    """
        Append all registers to the controller class as properties
    """
    def __new__(mcs, name, bases, dct):
        for reg in register_list:
            dct[decaser(reg.__name__)] = make_register_property(reg)

        return type.__new__(mcs, name, bases, dct)

class AnafazeController(object):
    __metaclass__ = AnafazeControllerMeta

    def __init__(self, port, baud_rate, destination=1, bcc=True):
        """
            Create a new connection to a controller via RS232.
        """
        self.destination = destination
        self._checksum = calc_bcc if bcc else (lambda x: None)
        self._transaction = transaction_gen()

        # Set 0 until we detect the loop count
        self.loop_count = 0

        # Open the serial port
        #self.ser = serial.Serial(
        #    port=port,
        #    baudrate=baud_rate,
        #    parity=serial.PARITY_NONE,
        #    stopbits=serial.STOPBITS_ONE,
        #    bytesize=serial.EIGHTBITS
        #)
