import socket
import struct
import ntplib


# send ->  'r3': '10.10.3.2'

sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
ntpc=ntplib.NTPClient()
response = ntpc.request('ops.instageni.clemson.edu', version=3)
ts = response.tx_timestamp
ts = struct.pack('d', ts)
sock.sendto(ts, ('10.10.3.2', 20010))
