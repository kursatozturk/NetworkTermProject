from threading import Thread
import socket
import struct
import time
from typing import Tuple
# Node #5, d
# This is destination

# node spesific variables
endpoint = 'd'

"""
    Represents the links that used to receive mesesages.
    key holds the node that links connected to,
    value holds a tuple containing two ip of two endpoint of the link.
"""
recieved_interfaces = {
    #   node: (listen,      send)
    'r1': ('10.10.4.2', '10.10.4.1'),
    'r2': ('10.10.5.2', '10.10.5.1'),
    'r3': ('10.10.7.1', '10.10.7.2')
}

# global variables
message_count = 1000
"""
    We helped the poor.
"""
msg = b'bulgurpilavi'

# variables for connection
port = 20010
buffer_size = 128 # sent message is 20 bytes long, but it does no harm.

def acknowledge(ts: float = None) -> bytes:
    """
        @param ts: timestamp
        @return: acknowledgement packet as bytes

        creates an acknowledgement packet.
    """
    _ts = struct.pack('d', ts or time.time())
    return _ts + b'ack'



def parse_packet(packet: bytes) -> Tuple[float, str]:
    """
        @param packet: bytes fetched through socket.
        @return: a tuple containing timestamp and the message in the packet

        Parses the received packet.
    """
    _ts = struct.unpack('d', packet[:8])
    return _ts[0], packet[8:]


#   other_endpoints: r1, r2, r3
def listen_interface(other_endpoint: str, interface: Tuple[str, str]):
    """
        @param other_endpoint: node that link is connected by outer interface.
        @interface: tuple containing inner and outer ip's of link.
        @return: None

        listens to the link's inner interface and sends acknowledgement to link's outer interface.
    """

    sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM) # socket to listen other endpoint
    listen, receiver = interface

    # bind socket to listen ip to receive packets
    sock.bind((listen, port))

    # inform other endpoint that this endpoint opened
    sock.sendto(b'1', (receiver, port))

    for _ in range(message_count):
        # there will be exactly `message_count` messages.
        # receive message
        recv_msg = sock.recv(buffer_size)
        # extract timestamp from message
        ts, _ = parse_packet(recv_msg)
        # put timestamp to acknowledgement message
        send_msg = acknowledge(ts=ts)
        # send back to receiver interface
        sock.sendto(send_msg, (receiver, port))


if __name__ == "__main__":
    threads = list()
    for node, interface in recieved_interfaces.items():
        # open a thread for each link
        t = Thread(target=listen_interface, args=(node, interface))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()
