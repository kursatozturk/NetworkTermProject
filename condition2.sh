sudo tc qdisc change dev eth1 root netem loss 15% delay 3ms
sudo tc qdisc change dev eth2 root netem loss 15% delay 3ms
sudo tc qdisc change dev eth3 root netem loss 15% delay 3ms
sudo tc qdisc change dev eth4 root netem loss 15% delay 3ms