from threading import Thread
import socket
import struct
import time

# Node #3 , r2
# This is router
whoami = 'r2'
listen = {
    '10.10.2.1': 's',  # s receive messages
    '10.10.8.2': 'r1',  # r1 receive messages
    '10.10.6.1': 'r3', # r3  for ack
    '10.10.5.1': 'd'  # d  for ack

}
# Will send messages to
recievers = {
    '10.10.6.2',  # r3
    '10.10.5.2',  # d
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


def acknowledge(ts):
    return create_header(ack=True, ts=ts) + b'ack'


def parse_msg(msg):
    ack = int(msg[0])
    ts = struct.unpack('d', msg[1:9])
    return ack, ts[0], msg[9:]



def listen_to(ip_addr):
    whom = listen[ip_addr]
    sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    sock.settimeout(5)  # close after 10 seconds of inactivity
    sock.bind((ip_addr, port))
    rtts = list()
    while True:
        try:
            recv_msg, (addr, _) = sock.recvfrom(buffer_size)
            ack, ts, msg = parse_msg(recv_msg)
            _t = time.time() - ts
            if ack == ord('1'):
                # calculate rtt
                rtts.append(_t)

            else:
                # msg recieved
                # send acknowledgement
                print(f'"{msg}" recieved in {_t} seconds. Sender is {whom}')
                ack_msg = acknowledge(ts)
                sock.sendto(ack_msg, (addr, port))

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

    send_to(recievers)

    for listener in listeners:
        listener.join()
