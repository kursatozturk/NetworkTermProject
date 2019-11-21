from threading import Thread, Lock
import socket
import struct
from typing import Tuple
import time
# Node #3 , r2
# This is router

file_lock = Lock()  # file lock to rule out writing rtts to file

# node spesific variables
endpoint = 'r2'
interfaces = {
    #   node: (listen,      send)
    'r3': ('10.10.6.1', '10.10.6.2'),
    'd': ('10.10.5.1', '10.10.5.2')
}

recieved_interfaces = {
    #   node: (listen,      send)
    's': ('10.10.2.1', '10.10.2.2'),
    'r1': ('10.10.8.2', '10.10.8.1')
}

# global variables
msg = b'bulgurpilavi'
message_count = 1000

# variables for connection
port = 20010
buffer_size = 128


# helper functions
def create_packet(ts: float = None) -> bytes:
    """
        @param ts: timestamp
        @return: packet to send as bytes
    """
    _ts = struct.pack('d', ts or time.time())
    return _ts + msg


def acknowledge(ts: float) -> bytes:
    """
        @param ts: timestamp
        @return: acknowledgement packet as bytes
    """
    _ts = struct.pack('d', ts)
    return _ts + b'ack'


def parse_packet(packet: bytes) -> Tuple[float, str]:
    """
        @param packet: bytes fetched through socket.
        @return: a tuple containing timestamp and the message in the packet
    """
    _ts = struct.unpack('d', packet[:8])
    return _ts[0], packet[8:]


#   other_endpoints s, r1
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

    # if listening to s,
    # r2 should get rtt.

    if other_endpoint == 's':
        # inform other endpoint that this endpoint
        # ready to get avg rtt cost
        sock.sendto(b'1', (receiver, port))
        avg_rtt = sock.recv(buffer_size)    # receive avg_rtt values FROM S
        avg_rtt = float(avg_rtt.decode())

        file_lock.acquire()
        with open('link_costs.txt', 'a') as file:
            file.write(f'{other_endpoint}-{endpoint}={avg_rtt}\n')  # s-r2=avg_rtt
        file_lock.release()

# other_endpoints r3, d


def link_interface(other_endpoint: str, interface: Tuple[str, str]):
    """
        Sends messages to the link's outer interface and reads acknowledgement from link's inner interface.
        @param other_endpoint: node that link is connected by outer interface.
        @interface: tuple containing inner and outer ip's of link.
        @return: None
    """
    # I will be the sender
    sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    listen, receiver = interface
    sock.bind((listen, port))
    rtts = list()

    # to make sure other endpoint is active and listening
    # we will wait it to send a sign byte
    sock.recv(1)
    # recieved byte is not important
    # not necessary to read what it is
    for _ in range(message_count):
        sock.sendto(create_packet(), (receiver, port))
        recv_msg = sock.recv(buffer_size)
        ts, _ = parse_packet(recv_msg)
        rtts.append(time.time() - ts)


    tot_rtt = 0.0
    for rtt in rtts:
        tot_rtt += rtt
    avg_rtt = tot_rtt / float(message_count)
    file_lock.acquire()
    with open('link_costs.txt', 'a') as file:
        # r3-r2=avg_rtt ;  d-r2=avg_rtt
        file.write(f'{other_endpoint}-{endpoint}={avg_rtt}\n')
    file_lock.release()


if __name__ == "__main__":
    threads = list()
    for node, interface in interfaces.items():
        t = Thread(target=link_interface, args=(node, interface))
        t.start()
        threads.append(t)
    for node, interface in recieved_interfaces.items():
        t = Thread(target=listen_interface, args=(node, interface))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()
