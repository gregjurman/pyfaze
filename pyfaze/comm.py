def get_resp_code(port):
    back = None
    for i in range(3): # Sent DLE ENQ three times?
        back = port.read(2) # Wait for DLE ACK or DLE NAK
        if back in ['\x10\x06', '\x10\x15']:
            break
        else: # Timed out
            back = None
            port.write('\x10\x05') # Send DLE ENQ

    return back


def send_command_packet(port, message):
    resp = None
    for i in range(3): # sent command three times?
        port.write(message) # Send command packet
        #sleep(0.2) # Wait 200ms

        resp = get_resp_code(port)

        if resp == '\x10\x06':
            break # Packet sent successfully
        else:
            resp = None

    return (resp == '\x10\x06')


def recv_response_packet(port):
    # Read in data
    msg = None
    for i in range(3):
        back = None
        while (back is None and port.inWaiting() == 0) or port.inWaiting():
            out = port.read(256)
            if out:
                back = back if back else '' + out


        if not back:
            # timed out
            port.write('\x10\x15') # send DLE NAK
            msg = None
        else:
            if '\x10\x02' in back and '\x10\x03' in back: # Packet valid
                port.write('\x10\x06')
                msg = back
                break

    return msg

def do_command(port, command):
    msg = None
    for i in range(3):
        if not send_command_packet(port, command): # send command three times
            msg = None
            break

        msg = recv_response_packet(port) # Try recieving 3 times,
        if msg:
            break

    return msg
