#!/bin/bash

ssh="~/.ssh/id_geni_ssh_rsa"
HOST="e2171874@pc1.instageni.utdallas.edu"
s_port="25614"
r1_port="25611"
r2_port="25612"
r3_port="25613"
d_port="25610"

r1_file_name="router1.py"
r2_file_name="router2.py"
r3_file_name="router3.py"
s_file_name="source.py"
d_file_name="destination.py"

if [ "${1}" = "input" ] ; then
    eval "scp -i ${ssh} -P ${s_port} ./input.txt" "${HOST}:/users/e2171874/input.txt"
    eval "scp -i ${ssh} -P ${d_port} ./input.txt" "${HOST}:/users/e2171874/input.txt"
    exit
fi

if [ "${1}" = "all" ] ; then
    echo "Deploying all scripts..."
    eval "./deploy_scripts.sh s"
    eval "./deploy_scripts.sh r1"
    eval "./deploy_scripts.sh r2"
    eval "./deploy_scripts.sh r3"
    eval "./deploy_scripts.sh d"
    exit
fi

port_name=$(expr "${1:?}_port")
file_name=$(expr "${1:?}_file_name")
port=${!port_name}
file=${!file_name}

echo "Deploying ${file} to Node ${1}";
eval "scp -i ${ssh} -P ${port} ./${file} ${HOST}:/users/e2171874/script.py"
