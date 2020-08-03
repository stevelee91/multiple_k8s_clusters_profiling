#!/bin/bash

echo -e "How many times curl? c "
read word

SET=$(seq 0 $word)

for i in $SET

do
#    curl 'http://203.237.53.233:30122/wp-admin' 
    curl 'localhost:31118/wp-admin' 

#    echo "Running loop seq "$i

    # some instructions

done






