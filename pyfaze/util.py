import re

def calc_bcc(data):
    """
        Calculates a checksum using the Block Character Check method.
    """
    bc = 0x00
    for byte in str(data):
        b = ord(byte)
        if b is 0x10:
            if last is 0x10:
                bc = bc + b
        else:
            bc = bc + b
        last = b
    bcc = (~bc & 0xff) + 1

    return chr(bcc & 0xff)


def build_packet_bcc(message):
    """
        Builds a ANA/AB packet with a BCC checksum.
    """
    bcc = calc_bcc(message)
    out = "\x10\x02%s\x10\x03%s" % (message, bcc)

    return out


def decaser(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
