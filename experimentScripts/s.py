import socket
import struct
import ntplib


# send ->  'r3': '10.10.3.2'

msg = b'tinyCutieMonster'
msg_count = 100

# ip of the link's interface in the s
listen_r3 = '10.10.3.1', 20010
# ip of the link's interface in the r3
send_r3 = '10.10.3.2', 20010


sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# bind socket to link
sock.bind(listen_r3)

# create a ntp client to get synced time
ntpc = ntplib.NTPClient()

for _ in range(msg_count):
    # wait till r3 is ready
    sock.recv(1)
    # get synced time
    response = ntpc.request('pc11.instageni.arc.vt.edu', version=3)
    # put time into packet
    ts = struct.pack('d', response.tx_timestamp)
    # send it to r3
    sock.sendto(ts, send_r3)
