import socket
import struct
import ntplib

# receive -> 's': '10.10.3.1'
# send    -> 'd': '10.10.7.1'


# ip of the link's interface in the r3
listen_s = '10.10.3.2', 20010
# ip of the link's interface in the s
send_s = '10.10.3.1', 20010


# ip of the link's interface in the r3
listen_d = '10.10.7.2', 20010
# ip of the link's interface in the d
send_d = '10.10.7.1', 20010

msg_count = 100
buffer_size = 32

# socket responsible for communication with s
sock_s = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
# bind socket to s link
sock_s.bind(listen_s)

# socket responsible for communication with d
sock_d = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
# bind socket to d link
sock_d.bind(listen_d)



for _ in range(msg_count):
    # wait till d is ready
    sock_d.recv(1)
    # inform s that r3 is listening
    sock_s.sendto(b'1', send_s)
    # listen s
    ts = sock_s.recv(buffer_size)
    # forward msg to d
    sock_d.sendto(ts, send_d)
