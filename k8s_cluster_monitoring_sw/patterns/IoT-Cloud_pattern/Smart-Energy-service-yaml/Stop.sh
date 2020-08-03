#!/bin/bash


kubectl delete -f zookeeper.yaml
kubectl delete -f kafka.yaml
kubectl delete -f influx_chro.yaml
kubectl delete -f api_server.yaml
kubectl delete -f consumer_device1.yaml
kubectl delete -f EdgeX.yaml



