#!/bin/bash
TEST=$(pwd)
echo $TEST

kubectl create -f $TEST/pv1.yaml
kubectl create -f $TEST/pv2.yaml
kubectl create -f $TEST/wordpress-volumeclaim.yaml
kubectl create -f $TEST/mysql-volumeclaim.yaml
kubectl create secret generic mysql-password --from-literal=password=rP@ssw0rd
kubectl describe secret mysql-password
kubectl apply -f $TEST/mysql.yaml
kubectl create -f $TEST/mysql-service.yaml
kubectl apply -f $TEST/wordpress.yaml
kubectl create -f $TEST/wordpress-service.yaml
