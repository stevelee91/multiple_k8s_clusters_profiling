#!/bin/bash

args=("$@")
echo ${args[0]}
var_cnt=${args[0]}


SET=$(seq 1 $var_cnt)

for i in $SET

do
    curl http://localhost:31118/webapp/wp-admin
    echo "Running loop seq "$i

    # some instructions

done



