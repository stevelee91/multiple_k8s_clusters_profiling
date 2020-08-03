#!/bin/bash

######ml pattern
kubectl delete -f patterns/ml_pattern/keras2.yaml


######3tier pattern
kubectl delete -f patterns/kube_wordpress_3tier_pattern/mysql.yaml
kubectl delete -f patterns/kube_wordpress_3tier_pattern/mysql-service.yaml
kubectl delete -f patterns/kube_wordpress_3tier_pattern/wordpress.yaml
kubectl delete -f patterns/kube_wordpress_3tier_pattern/wordpress-service.yaml
kubectl delete secret generic mysql-password --from-literal=password=rP@ssw0rd
kubectl describe secret mysql-password
kubectl delete -f patterns/kube_wordpress_3tier_pattern/wordpress-volumeclaim.yaml
kubectl delete -f patterns/kube_wordpress_3tier_pattern/mysql-volumeclaim.yaml
kubectl delete -f patterns/kube_wordpress_3tier_pattern/pv1.yaml
kubectl delete -f patterns/kube_wordpress_3tier_pattern/pv2.yaml

######IoT-Cloud pattern
kubectl delete -f patterns/IoT-Cloud_pattern/Smart-Energy-service-yaml/zookeeper.yaml
kubectl delete -f patterns/IoT-Cloud_pattern/Smart-Energy-service-yaml/kafka.yaml
kubectl delete -f patterns/IoT-Cloud_pattern/Smart-Energy-service-yaml/influx_chro.yaml
kubectl delete -f patterns/IoT-Cloud_pattern/Smart-Energy-service-yaml/api_server.yaml
kubectl delete -f patterns/IoT-Cloud_pattern/Smart-Energy-service-yaml/consumer_device1.yaml
kubectl delete -f patterns/IoT-Cloud_pattern/Smart-Energy-service-yaml/EdgeX.yaml
