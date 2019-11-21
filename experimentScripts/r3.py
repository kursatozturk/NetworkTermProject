import socket
import struct
import ntplib

# receive -> 's': '10.10.3.1'
# send    -> 'd': '10.10.7.1'
"""
emulation delay sh
experiment 1:

s=$(getent ahosts "s" | cut -d " " -f 1 | uniq)
r3=$(getent ahosts "r3" | cut -d " " -f 1 | uniq)
d=$(getent ahosts "d" | cut -d " " -f 1 | uniq)

s_adapter=$(ip route get $s | grep -Po '(?<=(dev )).*(?= src| proto)')
r3_adapter=$(ip route get $r3 | grep -Po '(?<=(dev )).*(?= src| proto)')
d_adapter=$(ip route get $d | grep -Po '(?<=(dev )).*(?= src| proto)')

s_random_delay=$(( ( RANDOM % 11 )  + 15 ))"ms"
r3_random_delay=$(( ( RANDOM % 11 )  + 15 ))"ms"
d_random_delay=$(( ( RANDOM % 11 )  + 15 ))"ms"

sudo tc qdisc change dev $s_adapter root netem delay $s_random_delay
sudo tc qdisc change dev $r3_adapter root netem delay $r3_random_delay
sudo tc qdisc change dev $d_adapter root netem delay $d_random_delay

experiment 2:

s=$(getent ahosts "s" | cut -d " " -f 1 | uniq)
r3=$(getent ahosts "r3" | cut -d " " -f 1 | uniq)
d=$(getent ahosts "d" | cut -d " " -f 1 | uniq)

s_adapter=$(ip route get $s | grep -Po '(?<=(dev )).*(?= src| proto)')
r3_adapter=$(ip route get $r3 | grep -Po '(?<=(dev )).*(?= src| proto)')
d_adapter=$(ip route get $d | grep -Po '(?<=(dev )).*(?= src| proto)')

s_random_delay=$(( ( RANDOM % 11 )  + 35 ))"ms"
r3_random_delay=$(( ( RANDOM % 11 )  + 35 ))"ms"
d_random_delay=$(( ( RANDOM % 11 )  + 35 ))"ms"

sudo tc qdisc change dev $s_adapter root netem delay $s_random_delay
sudo tc qdisc change dev $r3_adapter root netem delay $r3_random_delay
sudo tc qdisc change dev $d_adapter root netem delay $d_random_delay

experiment 3:

s=$(getent ahosts "s" | cut -d " " -f 1 | uniq)
r3=$(getent ahosts "r3" | cut -d " " -f 1 | uniq)
d=$(getent ahosts "d" | cut -d " " -f 1 | uniq)

s_adapter=$(ip route get $s | grep -Po '(?<=(dev )).*(?= src| proto)')
r3_adapter=$(ip route get $r3 | grep -Po '(?<=(dev )).*(?= src| proto)')
d_adapter=$(ip route get $d | grep -Po '(?<=(dev )).*(?= src| proto)')

s_random_delay=$(( ( RANDOM % 11 )  + 45 ))"ms"
r3_random_delay=$(( ( RANDOM % 11 )  + 45 ))"ms"
d_random_delay=$(( ( RANDOM % 11 )  + 45 ))"ms"

sudo tc qdisc change dev $s_adapter root netem delay $s_random_delay
sudo tc qdisc change dev $r3_adapter root netem delay $r3_random_delay
sudo tc qdisc change dev $d_adapter root netem delay $d_random_delay

"""

listen_s = '10.10.3.2', 20010
listen_d = '10.10.7.2', 20010

send_s = '10.10.3.1', 20010
send_d = '10.10.7.1', 20010

msg_count = 100
buffer_size = 32

# socket responsible for communication btw s
sock_s = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
sock_s.bind(listen_s)

# socket responsible for communication btw d
sock_d = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
sock_d.bind(listen_d)


for _ in range(msg_count):
    # wait till d is ready
    print('waiting d to be ready')
    sock_d.recv(1)
    print('run')
    # inform s that r3 is listening
    sock_s.sendto(b'1', send_s)
    # listen s
    ts = sock_s.recv(buffer_size)
    # forward msg to d
    sock_d.sendto(ts, send_d)
