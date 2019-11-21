s=$(getent ahosts "s" | cut -d " " -f 1 | uniq)
r3=$(getent ahosts "r3" | cut -d " " -f 1 | uniq)

s_adapter=$(ip route get $s | grep -Po '(?<=(dev )).*(?= src| proto)')
r3_adapter=$(ip route get $r3 | grep -Po '(?<=(dev )).*(?= src| proto)')

s_random_delay=$(( ( RANDOM % 11 )  + 45 ))"ms"
r3_random_delay=$(( ( RANDOM % 11 )  + 45 ))"ms"

sudo tc qdisc change dev $s_adapter root netem delay $s_random_delay
sudo tc qdisc change dev $r3_adapter root netem delay $r3_random_delay
