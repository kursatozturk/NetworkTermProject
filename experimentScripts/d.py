import socket
import struct
import ntplib
from math import sqrt

# send ->  'r3': '10.10.3.2'


# global variables
msg_count = 100

# connection variables
listen = '10.10.7.1', 20010
send = '10.10.7.2', 20010
buffer_size = 32


# ntplib client to sync time
ntpc = ntplib.NTPClient()

# open and bind socket
sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
sock.bind(listen)

# container of delays
e2e_delays = list()

for _ in range(msg_count):
    # inform r3 that d is listening
    sock.sendto(b'1', send)
    # listen r3
    ts = sock.recv(buffer_size)
    # get synced time
    response = ntpc.request('pc11.instageni.arc.vt.edu', version=3)
    # extract timestamp received from r3 (coming from s)
    ts = struct.unpack('d', ts)[0]
    # calculate and store end to end delay
    e2e_delays.append(response.tx_timestamp - ts)


tot = 0
for e2e_delay in e2e_delays:
    tot += e2e_delay

# find mean of end to end delays
mean = tot / msg_count

# calculate 95% confidence interval
tmp = 0

for e2e_delay in e2e_delays:
    d = e2e_delay - mean
    tmp += d * d
# finds std_dev
std_dev = sqrt(tmp / (msg_count - 1))

# constant to find 95% confidence interval
Z = 1.960


error = Z * std_dev / sqrt(msg_count)

confidence_interval = mean - error, mean + error

# print the interval to terminal
print(confidence_interval)
