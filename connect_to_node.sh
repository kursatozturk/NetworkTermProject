#!/bin/bash

ssh="~/.ssh/id_geni_ssh_rsa"
HOST="e2171874@pc1.instageni.utdallas.edu"
s_port="25614"
r1_port="25611"
r2_port="25612"
r3_port="25613"
d_port="25610"


port_name=$(expr "${1:?}_port")

port=${!port_name}

eval "ssh -i ${ssh} -p ${port} ${HOST}"