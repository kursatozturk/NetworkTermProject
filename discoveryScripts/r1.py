from threading import Thread, Lock
import socket
import struct
from typing import Tuple
import time
# Node #2 , r1
# This is router

file_lock = Lock()
endpoint = 'r1'

"""
    Represents the links that used to send messages.
    key holds the node that links connected to,
    value holds a tuple containing two ip of two endpoint of the link.
"""
interfaces = {
    #   node: (listen,      send)
    'r2': ('10.10.8.1', '10.10.8.2'),
    'd': ('10.10.4.1', '10.10.4.2')
}

"""
    Represents the links that used to receive mesesages.
    key holds the node that links connected to,
    value holds a tuple containing two ip of two endpoint of the link.
"""
recieved_interfaces = {
    #   node: (listen,      send)
    's': ('10.10.1.2', '10.10.1.1'),

}

# global variables
message_count = 1000
msg = b'bulgurpilavi'

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
        @return: acknowledgement packet as bytes7

        creates an acknowledgement packet.

    """
    _ts = struct.pack('d', ts)
    return _ts + b'ack'


def parse_packet(packet: bytes) -> Tuple[float, str]:
    """
        @param packet: bytes fetched through socket.
        @return: a tuple containing timestamp and the message in the packet

        Parses the received packet.
    """
    _ts = struct.unpack('d', packet[:8])
    return _ts[0], packet[8:]


#   other_endpoint s
def listen_interface(other_endpoint: str, interface: Tuple[str, str]):
    """
        @param other_endpoint: node that link is connected by outer interface.
        @interface: tuple containing inner and outer ip's of link.
        @return: None

        listens to the link's inner interface and sends acknowledgement to link's outer interface.
    """
    # I will be reciever
    sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM) # socket to listen other endpoint
    listen, receiver = interface


    # bind socket to listen ip to receive packets
    sock.bind((listen, port))

    # inform other endpoint that this endpoint opened
    sock.sendto(b'1', (receiver, port))

    for _ in range(message_count):
        recv_msg = sock.recv(buffer_size)
        # extract timestamp from message
        ts, _ = parse_packet(recv_msg)
        # put timestamp to acknowledgement message
        send_msg = acknowledge(ts=ts)
        # send back to receiver interface
        sock.sendto(send_msg, (receiver, port))

    # if listening to s,
    # r2 should get rtt.
    if other_endpoint == 's':
        # inform other endpoint that this endpoint
        # ready to get avg rtt cost
        sock.sendto(b'1', (receiver, port))
        avg_rtt = sock.recv(buffer_size)    # receive avg_rtt values from s
        avg_rtt = float(avg_rtt.decode())

        file_lock.acquire()
        with open('link_costs.txt', 'a') as file:
            file.write(f'{other_endpoint}-{endpoint}={avg_rtt}\n')  # s-r1=avg_rtt
        file_lock.release()


# other_endpoints r2, d
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
        # create a packet and send it to receiver
        sock.sendto(create_packet(), (receiver, port))
        # wait for acknowledgement
        recv_msg = sock.recv(buffer_size)
        # extract timestamp
        ts, _ = parse_packet(recv_msg)
        # calculate rtt and store
        rtts.append(time.time() - ts)

    tot_rtt = 0
    for rtt in rtts:
        tot_rtt += rtt
    avg_rtt = tot_rtt / message_count

    file_lock.acquire()
    with open('link_costs.txt', 'a') as file:
        # r2-r1=avg_rtt ;  d-r1=avg_rtt
        file.write(f'{other_endpoint}-{endpoint}={avg_rtt}\n')
    file_lock.release()


if __name__ == "__main__":
    threads = list()
    for node, interface in interfaces.items():
        # open a thread for each link
        t = Thread(target=link_interface, args=(node, interface))
        t.start()
        threads.append(t)
    for node, interface in recieved_interfaces.items():
        # open a thread for each link
        t = Thread(target=listen_interface, args=(node, interface))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()
