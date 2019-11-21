from threading import Thread
import socket
import struct
import time
from typing import Tuple
# Node #5, d
# This is destination

# node spesific variables
endpoint = 'd'

recieved_interfaces = {
    #   node: (listen,      send)
    'r1': ('10.10.4.2', '10.10.4.1'),
    'r2': ('10.10.5.2', '10.10.5.1'),
    'r3': ('10.10.7.1', '10.10.7.2')
}

# global variables
message_count = 1000
msg = b'bulgurpilavi'

# variables for connection
port = 20010
buffer_size = 128

def acknowledge(ts: float = None) -> bytes:
    """
        @param ts: timestamp
        @return: acknowledgement packet as bytes
    """
    _ts = struct.pack('d', ts or time.time())
    return _ts + b'ack'



def parse_packet(packet: bytes) -> Tuple[float, str]:
    """
        @param packet: bytes fetched through socket.
        @return: a tuple containing timestamp and the message in the packet
    """
    _ts = struct.unpack('d', packet[:8])
    return _ts[0], packet[8:]


#   other_endpoints r1, r2, r3
def listen_interface(other_endpoint: str, interface: Tuple[str, str]):
    """
        listens to the link's inner interface and sends acknowledgement to link's outer interface.
        @param other_endpoint: node that link is connected by outer interface.
        @interface: tuple containing inner and outer ip's of link.
        @return: None
    """
    # I will be reciever
    sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    listen, receiver = interface
    sock.bind((listen, port))
    sock.settimeout(5)
    # inform other endpoint that this endpoint opened
    sock.sendto(b'1', (receiver, port))

    for _ in range(message_count):
        recv_msg = sock.recv(buffer_size)
        ts, _ = parse_packet(recv_msg)
        send_msg = acknowledge(ts=ts)
        sock.sendto(send_msg, (receiver, port))


if __name__ == "__main__":
    threads = list()
    for node, interface in recieved_interfaces.items():
        t = Thread(target=listen_interface, args=(node, interface))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()
