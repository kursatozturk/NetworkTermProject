from threading import Thread
import socket
import struct
import time
# Node #2 , r1
# This is router

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

port = 20010
msg = b'bulgurpilavi'


def create_packet():
    _ts = struct.pack('d', time.time())
    return _ts + msg


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


def link_interface(other_endpoint, interface):
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
        t, msg = parse_packet(recv_msg)
        assert msg == b'ack'
        rtts.append(time.time() - t)
        #print(f'recieved msg: {msg}')
    assert len(rtts) == message_count
    tot_rtt = 0
    for rtt in rtts:
        tot_rtt += rtt
    avg_rtt = tot_rtt / message_count
    print(f'{endpoint}---{other_endpoint} -> {avg_rtt}')


if __name__ == "__main__":
    threads = list()
    for node, interface in interfaces.items():
        t = Thread(target=link_interface, args=(node, interface))
        t.start()
        threads.append(t)
    for _, interface in recieved_interfaces.items():
        t = Thread(target=listen_interface, args=(interface, ))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()
