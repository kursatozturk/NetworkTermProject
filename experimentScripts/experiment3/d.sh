r3=$(getent ahosts "r3" | cut -d " " -f 1 | uniq)
d=$(getent ahosts "d" | cut -d " " -f 1 | uniq)

r3_adapter=$(ip route get $r3 | grep -Po '(?<=(dev )).*(?= src| proto)')
d_adapter=$(ip route get $d | grep -Po '(?<=(dev )).*(?= src| proto)')

r3_random_delay=$(( ( RANDOM % 11 )  + 45 ))"ms"
d_random_delay=$(( ( RANDOM % 11 )  + 45 ))"ms"

sudo tc qdisc change dev $r3_adapter root netem delay $r3_random_delay
sudo tc qdisc change dev $d_adapter root netem delay $d_random_delay
