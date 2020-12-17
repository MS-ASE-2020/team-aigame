#!/bin/bash
# $1: server port
ip=$(hostname -i)
./env $1 &
./client 0 $ip $1
./client 1 $ip $1
./client 2 $ip $1
./client 3 $ip $1
