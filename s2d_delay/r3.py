import socket
import struct
import ntplib

# receive -> 's': '10.10.3.1'
# send    -> 'd': '10.10.7.1'

sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
sock.bind(('10.10.3.1', 20010))
ts = sock.recv(8)
sock.sendto(ts, ('10.10.7.1', 20010))