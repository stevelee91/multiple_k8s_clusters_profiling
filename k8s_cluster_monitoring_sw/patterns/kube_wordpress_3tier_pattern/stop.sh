#!/bin/bash

kubectl delete -f mysql.yaml
kubectl delete -f mysql-service.yaml
kubectl delete -f wordpress.yaml
kubectl delete -f wordpress-service.yaml
kubectl delete secret generic mysql-password --from-literal=password=rP@ssw0rd
kubectl describe secret mysql-password
kubectl delete -f wordpress-volumeclaim.yaml
kubectl delete -f mysql-volumeclaim.yaml
kubectl delete -f pv1.yaml
kubectl delete -f pv2.yaml

