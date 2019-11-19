from threading import Thread
import socket
import struct
import time
# Node #1 , s
# This is source

endpoint = 's'
interfaces = {
    # node : (listen,    send)
    'r1': ('10.10.1.1', '10.10.1.2'),
    'r2': ('10.10.2.2', '10.10.2.1'),
    'r3': ('10.10.3.1', '10.10.3.2')
}

port = 20010
msg = b'bulgurpilavi'


def create_packet(ts=None):
    _ts = struct.pack('d', ts or time.time())
    return _ts + msg


def parse_packet(packet):
    _ts = struct.unpack('d', packet[:8])
    return _ts[0], packet[8:]


buffer_size = 128
message_count = 1000


# other_endpoints r1, r2, r3
def link_interface(other_endpoint, interface):
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

    tot_rtt = 0
    for rtt in rtts:
        tot_rtt += rtt
    avg_rtt = tot_rtt / message_count
    sock.sendto(str(avg_rtt).encode('utf-8'), (receiver, port))  # sends avg_rtt values -> r1, r2, r3


if __name__ == "__main__":
    threads = list()
    for node, interface in interfaces.items():
        t = Thread(target=link_interface, args=(node, interface))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()
