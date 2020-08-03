#!/bin/bash
args=("$@")
echo ${args[0]}
var_cnt=${args[0]}

for i in $var_cnt; do
    curl -I 'http://localhost:31118/wp-admin'
    echo '3'
done

