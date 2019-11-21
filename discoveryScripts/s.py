from threading import Thread
import socket
import struct
from typing import Tuple
import time
# Node #1 , s
# This is source

# node spesific settings
endpoint = 's'
interfaces = {
    # node : (listen,    send)
    'r1': ('10.10.1.1', '10.10.1.2'),
    'r2': ('10.10.2.2', '10.10.2.1'),
    'r3': ('10.10.3.1', '10.10.3.2')
}

# global variables
msg = b'bulgurpilavi'
message_count = 1000

# variables for connection
buffer_size = 128
port = 20010

# helper functions


def create_packet(ts: float = None) -> bytes:
    """
        @param ts: timestamp
        @return: packet to send as bytes
    """
    _ts = struct.pack('d', ts or time.time())
    return _ts + msg


def parse_packet(packet: bytes) -> Tuple[float, str]:
    """
        @param packet: bytes fetched through socket.
        @return: a tuple containing timestamp and the message in the packet
    """
    _ts = struct.unpack('d', packet[:8])
    return _ts[0], packet[8:]


# other_endpoints r1, r2, r3
def link_interface(other_endpoint: str, interface: Tuple[str, str]):
    """
        Sends messages to the link's outer interface and reads acknowledgement from link's inner interface.
        @param other_endpoint: node that link is connected by outer interface.
        @interface: tuple containing inner and outer ip's of link.
        @return: None
    """
    #  I will be the sender
    sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    listen, receiver = interface
    sock.bind((listen, port))
    rtts = list()

    # to make sure other endpoint is active and listening
    # we will wait it to send a sign byte
    sock.recv(1)
    # received byte is not important
    # not necessary to read what it is
    for _ in range(message_count):
        sock.sendto(create_packet(), (receiver, port))
        recv_msg = sock.recv(buffer_size)
        ts, _ = parse_packet(recv_msg)
        rtts.append(time.time() - ts)

    sock.recv(1)  # wait till other endpoint is ready to receive rtt

    tot_rtt = 0
    for rtt in rtts:
        tot_rtt += rtt
    avg_rtt = tot_rtt / message_count
    avg_rtt = str(avg_rtt).encode('utf-8')
    # sends avg_rtt values -> r1, r2, r3
    sock.sendto(avg_rtt, (receiver, port))


if __name__ == "__main__":
    threads = list()
    for node, interface in interfaces.items():
        t = Thread(target=link_interface, args=(node, interface))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()
