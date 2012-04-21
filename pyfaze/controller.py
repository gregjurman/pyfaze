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
            0, self.destination,
            1, tran_id
            ) + str(register.byte_location) + str(data_len)

        check = self._checksum(message)

        msg = message.replace("\x10", "\x10\x10")
        packet = "\x10\x02%s\x10\x03%s" % (msg, check)

        self.ser.open()

        self.ser.write(packet)

        # Get the ACK/NACK
        ack = ""
        attempted = 0
        while ack not in ["\x10\x06", "\x10\x15"]:
            ack = ack + self.ser.read(1)
            if not self.ser.inWaiting() and attempted == 6:
                break
            attempted = attempted + 1

        if ack == "\x10\x15":
            raise Exception("Command failed to send")

        # Read in data
        msg_back = ""
        while '\x10\x02' not in msg_back or '\x10\x03' not in msg_back:
            msg_back= msg_back + self.ser.read()

        # don't forget our check-byte
        msg_back = msg_back + self.ser.read(1)

        # Say thank you to the nice little controller.
        #   (It's the polite thing to do)
        self.ser.write('\x10\x06')

        self.ser.close()

        returned_data = disect_packet(msg_back)
    
        # actually marshall
        return register.to_python(returned_data)

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
        self.ser = serial.Serial(
            port=port,
            baudrate=baud_rate,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=1,
        )

        self.ser.close()
        
        # Do some basic detection
        self.loop_count = 2 ** ((self.system_status[1] >> 6) + 2) + 1
