from pyfaze.registers import register_list
from pyfaze.utils import decaser, calc_bcc
from struct import pack
import serial

__all__ = ["AnafazeController"]

def make_message_header(src, dest, cmd, transaction_id):
    return "%s%s%s\x00%s" % (
            chr(dest & 0xff),
            chr(src & 0xff),
            chr(cmd & 0xff),
            transaction_id)

def make_register_property(register):
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

        print packet

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

        print packet

    return property(get_register, set_register)


def transaction_gen():
    i = 0
    while True:
        yield pack("H", i)
        i = i + 1


class AnafazeController(object):
    def __new__(cls, name, bases, dct):
        for reg in register_list:
            dct[decaser(reg.name)] = make_register_property(reg)

        return super(AnafazeController, cls).__new__(cls, name, bases, dct)

    def __init__(self, port, baud_rate, destination=0, bcc=True):
        self.destination = destination
        self._checksum = calc_bcc if bcc else lambda(x: None)
        self._transation = transaction_gen()

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
