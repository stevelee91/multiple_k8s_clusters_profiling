import time
import os
import sys
import subprocess
import requests
import multiprocessing
import pycurl
import urllib
import json
from collections import OrderedDict
from pprint import pprint as pp
import cluster_ip_setup


##################user input part
cluster_num = cluster_ip_setup.input_cluster_num()
worker_num = cluster_ip_setup.input_worker_num()
master_ip = cluster_ip_setup.input_master_ip()
worker_ip = list()

for i in range (0, int(worker_num)):
  append_worker_ip = cluster_ip_setup.input_worker_ip()
  worker_ip.append(append_worker_ip)

#################### computing part how many number of nodes in the cluster
request_message = 'http://%s:30000/api/v1/query?query=kubelet_running_pod_count' % master_ip
r=requests.get(request_message)
c=r.content.decode('utf-8')
json_data=json.loads(c)

Num_of_Node = len(json_data['data']["result"])

################### each nodes name store into the Node_name list

Node_name = list()


for i in range (0, Num_of_Node):
  Node_name_input = json_data["data"]["result"][i]["metric"]["instance"]
  Node_name.append(Node_name_input)
  Pod_count= json_data["data"]["result"][i]["value"][1]
  print(json.dumps(json_data, indent = 4, sort_keys=True))
  print(Node_name)
  print(Pod_count)
  print(Num_of_Node)

################### filesystem bytes in each nodes
Node_num = len(Node_name)
Node_cpu_total = list()

url = 'http://%s:30000/api/v1/query' % master_ip
 # PARAM  = 'query= 100 - (avg by (instance) (irate(node_cpu_seconds_total{job="%s", mode="idle"}[5m])) * 100)' % Node_name[i]
 # PARAM = 'query= node_filesystem_size_bytes{device="/dev/vda1", job="%s", mountpoint="/"}' % Node_name[i]
PARAM = 'query= max(((node_filesystem_size_bytes{fstype=~"ext4|vfat"} - node_filesystem_free_bytes{fstype=~"ext4|vfat"}) / node_filesystem_size_bytes{fstype=~"ext4|vfat"}) * 100) by (instance)'
r=requests.get(url, params= PARAM)
c=r.content.decode('utf-8')
json_data=json.loads(c)
print(json.dumps(json_data, indent = 4, sort_keys=True))

#  Node_cpu_input = json_data["data"]["result"][0]["value"][1]
#  Node_cpu_total.append(Node_cpu_input)
#  print(Node_cpu_total)



