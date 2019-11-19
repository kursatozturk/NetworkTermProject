from threading import Thread, Lock
import socket
import struct
import time
# Node #2 , r1
# This is router
file_lock = Lock()
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


# other_endpoints s, r1
def listen_interface(other_endpoint, interface):
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
            ts, _ = parse_packet(recv_msg)
            send_msg = acknowledge(ts=ts)
            sock.sendto(send_msg, (receiver, port))
        except Exception as e:
            print(e)
            break
    if other_endpoint is 's':
        avg_rtt = sock.recv(buffer_size)    # receive avg_rtt values from s and r1
        avg_rtt = float(avg_rtt.decode())
        file_lock.acquire()
        with open('link_costs.txt', 'a') as file:
            file.write(other_endpoint + "-" + endpoint + "=" + avg_rtt)  # s-r2=avg_rtt
        file_lock.release()


#   other_endpoints r3, d
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
        ts, _ = parse_packet(recv_msg)
        rtts.append(time.time() - ts)

    tot_rtt = 0
    for rtt in rtts:
        tot_rtt += rtt
    avg_rtt = tot_rtt / message_count
    file_lock.acquire()
    with open('link_costs.txt', 'a') as file:
        file.write(other_endpoint + "-" + endpoint + "=" + avg_rtt)  # r3-r2=avg_rtt ;  d-r2=avg_rtt
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
