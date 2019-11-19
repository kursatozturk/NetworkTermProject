import socket
import struct
import ntplib

# send ->  'r3': '10.10.3.2'

ntpc = ntplib.NTPClient()
sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

sock.bind(('10.10.7.2', 20010))
ts = sock.recv(8)
ts = struct.unpack('d', ts)
response = ntpc.request('ops.instageni.clemson.edu', version=3)

print(response.tx_timestamp - ts)
