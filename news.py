from threading import Thread
import socket
import struct
import time
# Node #1 , s
# This is server listens to

whoami = 's'
listen = {
    '10.10.1.1': 'r1',  # r1 for ack
    '10.10.2.2': 'r2',  # r2 for ack
    '10.10.3.1': 'r3'  # r3 for ack
}
# Will send messages to
receivers = {
    '10.10.1.2',  # r1
    '10.10.2.1',  # r2
    '10.10.3.2'  # r3
}


msg_to_be_send = b"ejderiya"
buffer_size = 1024
port = 20001


class ThisShouldNotHappen(Exception):
    pass


def create_header(ack=False, ts=None):
    ack = b'0' if not ack else b'1'
    _ts = struct.pack('d', ts or time.time())
    return ack + _ts


def create_msg(msg):
    return create_header() + msg


def parse_msg(msg):
    ack = int(msg[0])
    ts = struct.unpack('d', msg[1:9])
    return ack, ts[0], msg[9:]


def listen_to(ip_addr):
    whom = listen.get(ip_addr)
    sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    sock.settimeout(5)  # close after 10 seconds of inactivity
    sock.bind((ip_addr, port))
    rtts = list()
    while True:
        try:
            recv_msg = sock.recv(buffer_size)
            ack, ts, msg = parse_msg(recv_msg)
            _t = time.time() - ts
            if ack == ord('1'):
                # calculate rtt
                rtts.append(_t)

            else:
                raise(ThisShouldNotHappen('not ack msg received'))
        except TimeoutError:
            break
        except Exception as e:
            print(e)
            break
    if rtts:
        tot_rtt = 0
        for rtt in rtts:
            tot_rtt += rtt
        tot_rtt /= len(rtts)
        print("count rtt ;", len(rtts))
        print(f'{whoami}->{whom}|{tot_rtt}')
    else:
        print(f'there is no room for {whom} in {whoami}')


def send_to(ip_addrs):
    send_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

    for _ in range(10000):
        for ip in ip_addrs:
            msg = create_msg(msg_to_be_send)
            send_socket.sendto(msg, (ip, port))


if __name__ == '__main__':
    listeners = []
    for ip in listen.keys():
        t = Thread(target=listen_to, args=(ip,))
        t.start()
        listeners.append(t)

    send_to(receivers)

    for listener in listeners:
        listener.join()
