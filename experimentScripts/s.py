import socket
import struct
import ntplib


# send ->  'r3': '10.10.3.2'
"""
emulation delay sh
experiment 1:

s=$(getent ahosts "s" | cut -d " " -f 1 | uniq)
r3=$(getent ahosts "r3" | cut -d " " -f 1 | uniq)

s_adapter=$(ip route get $s | grep -Po '(?<=(dev )).*(?= src| proto)')
r3_adapter=$(ip route get $r3 | grep -Po '(?<=(dev )).*(?= src| proto)')

s_random_delay=$(( ( RANDOM % 11 )  + 15 ))"ms"
r3_random_delay=$(( ( RANDOM % 11 )  + 15 ))"ms"

sudo tc qdisc change dev $s_adapter root netem delay $s_random_delay
sudo tc qdisc change dev $r3_adapter root netem delay $r3_random_delay

experiment 2:

s=$(getent ahosts "s" | cut -d " " -f 1 | uniq)
r3=$(getent ahosts "r3" | cut -d " " -f 1 | uniq)

s_adapter=$(ip route get $s | grep -Po '(?<=(dev )).*(?= src| proto)')
r3_adapter=$(ip route get $r3 | grep -Po '(?<=(dev )).*(?= src| proto)')

s_random_delay=$(( ( RANDOM % 11 )  + 35 ))"ms"
r3_random_delay=$(( ( RANDOM % 11 )  + 35 ))"ms"

sudo tc qdisc change dev $s_adapter root netem delay $s_random_delay
sudo tc qdisc change dev $r3_adapter root netem delay $r3_random_delay

experiment 3:

s=$(getent ahosts "s" | cut -d " " -f 1 | uniq)
r3=$(getent ahosts "r3" | cut -d " " -f 1 | uniq)

s_adapter=$(ip route get $s | grep -Po '(?<=(dev )).*(?= src| proto)')
r3_adapter=$(ip route get $r3 | grep -Po '(?<=(dev )).*(?= src| proto)')

s_random_delay=$(( ( RANDOM % 11 )  + 45 ))"ms"
r3_random_delay=$(( ( RANDOM % 11 )  + 45 ))"ms"

sudo tc qdisc change dev $s_adapter root netem delay $s_random_delay
sudo tc qdisc change dev $r3_adapter root netem delay $r3_random_delay

"""
msg = b'tinyCutieMonster'
msg_count = 100

listen_r3 = '10.10.3.1', 20010
send_r3 = '10.10.3.2', 20010

sock = socket.socket(family = socket.AF_INET, type = socket.SOCK_DGRAM)
sock.bind(listen_r3)
ntpc = ntplib.NTPClient()

for _ in range(msg_count):
    print('waiting for r3 to be ready')
    sock.recv(1)
    print('run!')
    response = ntpc.request('pc11.instageni.arc.vt.edu', version=3)
    ts = struct.pack('d', response.tx_timestamp)
    sock.sendto(ts, send_r3)
