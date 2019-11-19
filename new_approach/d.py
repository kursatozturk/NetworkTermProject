from threading import Thread
import socket
import struct
import time
# Node #2 , r1
# This is router

endpoint = 'd'

recieved_interfaces = {
    #   node: (listen,      send)
    'r1': ('10.10.4.2', '10.10.4.1'),
    'r2': ('10.10.5.2', '10.10.5.1'),
    'r3': ('10.10.7.1', '10.10.7.2')
}

port = 20010


def acknowledge(ts):
    _ts = struct.pack('d', ts)
    return _ts + b'ack'


def parse_packet(packet):
    _ts = struct.unpack('d', packet[:8])
    return _ts[0], packet[8:]


buffer_size = 128
message_count = 1000


def listen_interface(interface):
    # I will be reciever
    sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    listen, receiver = interface
    sock.bind((listen, port))
    sock.settimeout(5)
    # inform other endpoint that this endpoint opened
    sock.sendto(b'1', (receiver, port))
    while True:
        try:
            recv_msg = sock.recv(buffer_size)
            t, _ = parse_packet(recv_msg)
            send_msg = acknowledge(ts=t)
            sock.sendto(send_msg, (receiver, port))
        except Exception as e:
            print(e)
            break


if __name__ == "__main__":
    threads = list()
    for _, interface in recieved_interfaces.items():
        t = Thread(target=listen_interface, args=(interface, ))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()
