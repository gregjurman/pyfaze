from pyfaze.registers import register_list
from pyfaze.util import decaser, calc_bcc
from pyfaze.comm import do_command
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


def disect_packet(packet):
    data = packet[2:len(packet)-3]
    out_data = packet[8:-3]
    bcc_check = packet[-1]

    check = calc_bcc(data)

    if bcc_check != check:
        raise Exception("Expected %s, got %s for checksum" % (ord(check), ord(bcc_check)))

    return out_data

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

        tran_id = self._transaction.next()
        message = make_message_header(
            self.source, self.destination,
            1, tran_id
            ) + str(register.byte_location) + str(data_len)

        check = self._checksum(message)

        msg = message.replace("\x10", "\x10\x10")
        packet = "\x10\x02%s\x10\x03%s" % (msg, check)

        msg_back = None
        with self.ser as port:
            if not port.isOpen():
                port.open()
            msg_back = do_command(port, packet)

        if not msg_back:
            raise AttributeError("Cannot read attribute from controller")

        returned_data = disect_packet(msg_back)

        clean_data = returned_data.replace("\x10\x10", "\x10")

        # actually marshall
        return register.to_python(clean_data)

    def set_register(self, value):
        # XXX: Needs testing
        data = register.from_python(value)

        message = make_message_header(
            self.source, self.destination,
            8, self._transaction.next()
            ) + register.byte_location + data

        check = self._checksum(message)

        msg = message.replace("\x10", "\x10\x10")
        packet = "\x10\x02%s\x10\x03%s" % (msg, check)

        msg_back = None
        with self.ser as port:
            if not port.isOpen():
                port.open()
            msg_back = do_command(port, packet)

        if not msg_back:
            raise AttributeError("Cannot write attribute to controller.")

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

    def __init__(self, port, baud_rate, source=0, destination=1, bcc=True):
        """
            Create a new connection to a controller via RS232.
        """
        self.destination = destination
        self.source = source
        self._checksum = calc_bcc if bcc else (lambda x: None)
        self._transaction = transaction_gen()

        # Set 0 until we detect the loop count
        self.loop_count = 0

        # Open the serial port
        self.ser = serial.Serial(
            port=port,
            baudrate=baud_rate,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=0.5,
            interCharTimeout=0.2
        )

        self.ser.nonblocking()

        # Do some basic detection
        self.loop_count = 2 ** ((self.system_status[1] >> 6) + 2) + 1
