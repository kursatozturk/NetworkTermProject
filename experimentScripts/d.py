import socket
import struct
import ntplib
from math import sqrt

# send ->  'r3': '10.10.3.2'
"""
emulation delay sh


experiment 1:

r3=$(getent ahosts "r3" | cut -d " " -f 1 | uniq)
d=$(getent ahosts "d" | cut -d " " -f 1 | uniq)

r3_adapter=$(ip route get $r3 | grep -Po '(?<=(dev )).*(?= src| proto)')
d_adapter=$(ip route get $d | grep -Po '(?<=(dev )).*(?= src| proto)')

r3_random_delay=$(( ( RANDOM % 11 )  + 15 ))"ms"
d_random_delay=$(( ( RANDOM % 11 )  + 15 ))"ms"

sudo tc qdisc change dev $r3_adapter root netem delay $r3_random_delay
sudo tc qdisc change dev $d_adapter root netem delay $d_random_delay

experiment 2:

r3=$(getent ahosts "r3" | cut -d " " -f 1 | uniq)
d=$(getent ahosts "d" | cut -d " " -f 1 | uniq)

r3_adapter=$(ip route get $r3 | grep -Po '(?<=(dev )).*(?= src| proto)')
d_adapter=$(ip route get $d | grep -Po '(?<=(dev )).*(?= src| proto)')

r3_random_delay=$(( ( RANDOM % 11 )  + 35 ))"ms"
d_random_delay=$(( ( RANDOM % 11 )  + 35 ))"ms"

sudo tc qdisc change dev $r3_adapter root netem delay $r3_random_delay
sudo tc qdisc change dev $d_adapter root netem delay $d_random_delay

experiment 3:

r3=$(getent ahosts "r3" | cut -d " " -f 1 | uniq)
d=$(getent ahosts "d" | cut -d " " -f 1 | uniq)

r3_adapter=$(ip route get $r3 | grep -Po '(?<=(dev )).*(?= src| proto)')
d_adapter=$(ip route get $d | grep -Po '(?<=(dev )).*(?= src| proto)')

r3_random_delay=$(( ( RANDOM % 11 )  + 45 ))"ms"
d_random_delay=$(( ( RANDOM % 11 )  + 45 ))"ms"

sudo tc qdisc change dev $r3_adapter root netem delay $r3_random_delay
sudo tc qdisc change dev $d_adapter root netem delay $d_random_delay

"""

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

e2e_delays = list()

for _ in range(msg_count):
    # inform r3 that d is listening
    print('inform r3 and listen')
    sock.sendto(b'1', send)
    # listen r3
    ts = sock.recv(buffer_size)
    response = ntpc.request('pc11.instageni.arc.vt.edu', version=3)
    ts = struct.unpack('d', ts)[0]
    e2e_delays.append(response.tx_timestamp - ts)


tot = 0
for e2e_delay in e2e_delays:
    tot += e2e_delay


mean = tot / msg_count
print(f'len: {len(e2e_delays)}, msg_count: {msg_count}')
tmp = 0
for e2e_delay in e2e_delays:
    d = e2e_delay - mean
    tmp += d * d
print(f'tmp: {tmp}')
std_dev = sqrt(tmp / (msg_count - 1))
print(f'std dev: {std_dev}')
Z = 1.960

error = Z * std_dev / sqrt(msg_count)
print(f'error: {error}')
confidence_interval = mean - error, mean + error

print(confidence_interval)
