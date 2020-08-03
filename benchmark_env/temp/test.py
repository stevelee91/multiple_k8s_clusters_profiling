import os
import sys
import subprocess
import requests
import multiprocessing
import urllib
import json
from json import JSONEncoder
from collections import OrderedDict
from pprint import pprint as pp
import cluster_ip_setup
import cluster_node_info3
import pymongo
from pymongo import MongoClient
import time
import pickle
import jsonpickle

##################user input part

cluster_num = '1'
Cluster_object = list()
Cluster = cluster_node_info3.Cluster()
Cluster_object.append(Cluster)
worker_num = '3'
Cluster_object[0].Num_of_node = worker_num
Cluster_object[0].Master_ip = '203.237.53.208'
Cluster_object[0].Worker_ip.append('203.237.53.204')
Cluster_object[0].Worker_ip.append('203.237.53.207')


while True:

    time.sleep(2)
#################### computing part how many number of nodes in the cluster
    for i in range(0, int(cluster_num)):
        request_message = 'http://%s:30000/api/v1/query?query=kubelet_running_pod_count' % Cluster_object[i].Master_ip
        r = requests.get(request_message)
        c = r.content.decode('utf-8')
        json_data = json.loads(c)

        Num_of_Node = len(json_data['data']["result"])
        Cluster_object[i].Num_of_node = Num_of_Node
        Cluster_object[i].Cluster_number = int(i) + 1

        ################### each nodes name store into the Node_name list

        Node_list = list()
        for j in range(0, int(Cluster_object[i].Num_of_node)):
            Node = cluster_node_info3.Node()
            Node_name_input = json_data["data"]["result"][j]["metric"]["instance"]
            Node.Node_name = Node_name_input
            # Pod_count = json_data["data"]["result"][j]["value"][1]
            Node_list.append(Node)

        Cluster_object[i].Node_list = Node_list



    # print(Cluster_object[0].Node_list[2].Node_name)


    ################### compute cpu usage percent in each nodes

    for i in range(0, int(cluster_num)):
        for j in range(0, int(Cluster_object[i].Num_of_node)):
            url = 'http://%s:30000/api/v1/query' % Cluster_object[i].Master_ip
            PARAM  = 'query= 100 - (avg by (instance) (irate(node_cpu_seconds_total{job="%s", mode="idle"}[5m])) * 100)' % Cluster_object[i].Node_list[j].Node_name
            r=requests.get(url, params= PARAM)
            c=r.content.decode('utf-8')
            json_data=json.loads(c)
            # print(json.dumps(json_data, indent = 4, sort_keys=True))

            Node_cpu_input = json_data["data"]["result"][0]["value"][1]
            Cluster_object[i].Node_list[j].Cpu_usage = Node_cpu_input
           # print(Node_cpu_total)



    ################### compute memory usage in each nodes

    for i in range(0, int(cluster_num)):
        url = 'http://%s:30000/api/v1/query' % Cluster_object[i].Master_ip
        PARAM = 'query= ((node_memory_MemTotal_bytes - node_memory_MemFree_bytes) / node_memory_MemTotal_bytes) * 100'
        r = requests.get(url, params=PARAM)
        c = r.content.decode('utf-8')
        json_data = json.loads(c)
        # print(json.dumps(json_data, indent = 4, sort_keys=True))

        for j in range(0, int(Cluster_object[i].Num_of_node)):
            Node_memory_input = json_data["data"]["result"][j]["value"][1]
            Cluster_object[i].Node_list[j].Mem_usage = Node_memory_input



    ################### network receive bytes in each nodes

    for i in range(0, int(cluster_num)):
        url = 'http://%s:30000/api/v1/query' % Cluster_object[i].Master_ip
        PARAM = 'query= rate(node_network_receive_bytes_total{device=~"^en.*"}[5m])'
        r = requests.get(url, params=PARAM)
        c = r.content.decode('utf-8')
        json_data = json.loads(c)
        #print(json.dumps(json_data, indent=4, sort_keys=True))

        for j in range(0, int(Cluster_object[i].Num_of_node)):
            Node_network_receive_input = json_data["data"]["result"][j]["value"][1]
            Cluster_object[i].Node_list[j].Network_receive = Node_network_receive_input



    ################### network transmit bytes in each nodes

    for i in range(0, int(cluster_num)):
        url = 'http://%s:30000/api/v1/query' % Cluster_object[i].Master_ip
        PARAM = 'query= rate(node_network_transmit_bytes_total{device=~"^en.*"}[5m])'
        r=requests.get(url, params= PARAM)
        c=r.content.decode('utf-8')
        json_data=json.loads(c)
        # print(json.dumps(json_data, indent = 4, sort_keys=True))

        for j in range(0, int(Cluster_object[i].Num_of_node)):
            Node_network_transmit_input = json_data["data"]["result"][j]["value"][1]
            Cluster_object[i].Node_list[j].Network_transmit = Node_network_transmit_input



    ################### filesystem bytes in each nodes

    for i in range(0, int(cluster_num)):
        url = 'http://%s:30000/api/v1/query' % Cluster_object[i].Master_ip
        PARAM = 'query= max(((node_filesystem_size_bytes{fstype=~"ext4|vfat"} - node_filesystem_free_bytes{fstype=~"ext4|vfat"}) / node_filesystem_size_bytes{fstype=~"ext4|vfat"}) * 100) by (instance)'
        r=requests.get(url, params= PARAM)
        c=r.content.decode('utf-8')
        json_data=json.loads(c)
        #print(json.dumps(json_data, indent = 4, sort_keys=True))

        for j in range(0, int(Cluster_object[i].Num_of_node)):
            Node_filesystem_usage_input =  json_data["data"]["result"][j]["value"][1]
            Cluster_object[i].Node_list[j].Filesystem_usage = Node_filesystem_usage_input



        ################### compute cpu seconds in each pods

    for i in range(0, int(cluster_num)):
        url = 'http://%s:30000/api/v1/query' % Cluster_object[i].Master_ip
        PARAM = 'query=  container_cpu_usage_seconds_total'
        # PARAM = 'query= sum(rate(container_cpu_usage_seconds_total[5m])) by (container_name)'
        r = requests.get(url, params=PARAM)
        c = r.content.decode('utf-8')
        json_data = json.loads(c)

        Num_of_pod = len(json_data['data']["result"])
        #print(json.dumps(json_data, indent=4, sort_keys=True))

        cnt_node = len(Cluster_object[i].Node_list)

        Pod_list = list()
        for j in range(0, int(Num_of_pod)):
            Pod = cluster_node_info3.Pod()
            if (len(json_data["data"]["result"][j]["metric"]) == 13):
                Pod_name_input = json_data["data"]["result"][j]["metric"]["pod_name"]
                # cnt_metric = len(json_data["data"]["result"][j]["metric"])
                What_node = json_data["data"]["result"][j]["metric"]["instance"]
                Pod.Pod_name = Pod_name_input
                Pod.What_node = What_node
                Pod.Cpu_seconds = json_data["data"]["result"][j]["value"][1]

                for k in range(0, cnt_node):
                    if Cluster_object[i].Node_list[k].Node_name == Pod.What_node:
                        #Pod_list.append(Pod)
                        #Cluster_object[i].Node_list[k].Pod_list.extend(Pod_list)

                        Cluster_object[i].Node_list[k].Pod_list.append(Pod)

            if (len(json_data["data"]["result"][j]["metric"]) != 13):
                print(1)

        ################### compute cpu usage in each pods

    for i in range(0, int(cluster_num)):
        url = 'http://%s:30000/api/v1/query' % Cluster_object[i].Master_ip
        PARAM = 'query=  rate(container_cpu_usage_seconds_total[5m])'
        # PARAM = 'query= sum(rate(container_cpu_usage_seconds_total[5m])) by (container_name)'
        r = requests.get(url, params=PARAM)
        c = r.content.decode('utf-8')
        json_data = json.loads(c)

        #Num_of_pod = len(json_data['data']["result"])
        #print(json.dumps(json_data, indent=4, sort_keys=True))
        Num_of_pod = len(json_data['data']["result"])
        cnt_node = len(Cluster_object[i].Node_list)

        for j in range(0, int(Num_of_pod)):
            if (len(json_data["data"]["result"][j]["metric"]) == 12):
                Pod_name_input = json_data["data"]["result"][j]["metric"]["pod_name"]
                What_node = json_data["data"]["result"][j]["metric"]["instance"]
                Pod.Pod_name = Pod_name_input
                Pod.What_node = What_node
                Pod.Cpu_usage = json_data["data"]["result"][j]["value"][1]

                for k in range(0, cnt_node):
                    if Cluster_object[i].Node_list[k].Node_name == Pod.What_node:
                        # Pod_list.append(Pod)
                        # Cluster_object[i].Node_list[k].Pod_list.extend(Pod_list)
                        cnt_pod = len(Cluster_object[i].Node_list[k].Pod_list)
                        Cluster_object[i].Node_list[k].Num_of_pod = cnt_pod
                        for z in range(0, cnt_pod):
                            if Cluster_object[i].Node_list[k].Pod_list[z].Pod_name == Pod.Pod_name:
                                Cluster_object[i].Node_list[k].Pod_list[z].Cpu_usage = Pod.Cpu_usage

        ################### compute memory bytes in each pods


    for i in range(0, int(cluster_num)):
        url = 'http://%s:30000/api/v1/query' % Cluster_object[i].Master_ip
        PARAM = 'query=  (container_memory_usage_bytes{container_name!="POD",container_name!=""})'
        r = requests.get(url, params=PARAM)
        c = r.content.decode('utf-8')
        json_data = json.loads(c)

        #print(json.dumps(json_data, indent=4, sort_keys=True))
        Num_of_pod = len(json_data['data']["result"])
        cnt_node = len(Cluster_object[i].Node_list)

        for j in range(0, int(Num_of_pod)):
            if (len(json_data["data"]["result"][j]["metric"]) == 16):
                Pod_name_input = json_data["data"]["result"][j]["metric"]["pod_name"]
                What_node = json_data["data"]["result"][j]["metric"]["instance"]
                Pod.Pod_name = Pod_name_input
                Pod.What_node = What_node
                Pod.Mem_bytes = json_data["data"]["result"][j]["value"][1]

                for k in range(0, cnt_node):
                    if Cluster_object[i].Node_list[k].Node_name == Pod.What_node:
                        # Pod_list.append(Pod)
                        # Cluster_object[i].Node_list[k].Pod_list.extend(Pod_list)
                        cnt_pod = len(Cluster_object[i].Node_list[k].Pod_list)
                        for z in range(0, cnt_pod):
                            if Cluster_object[i].Node_list[k].Pod_list[z].Pod_name == Pod.Pod_name:
                                Cluster_object[i].Node_list[k].Pod_list[z].Mem_bytes = Pod.Mem_bytes

        ################### compute memory usage in each pods


    for i in range(0, int(cluster_num)):
        url = 'http://%s:30000/api/v1/query' % Cluster_object[i].Master_ip
        #PARAM = 'query= rate(container_memory_usage_bytes[5m]) by (pod_name)'
        PARAM = 'query= (container_memory_usage_bytes) / (container_memory_max_usage_bytes) * 100'
        r = requests.get(url, params=PARAM)
        c = r.content.decode('utf-8')
        json_data = json.loads(c)

        #print(json.dumps(json_data, indent=4, sort_keys=True))
        Num_of_pod = len(json_data['data']["result"])
        cnt_node = len(Cluster_object[i].Node_list)

        for j in range(0, int(Num_of_pod)):
            if (len(json_data["data"]["result"][j]["metric"]) == 11):
                Pod_name_input = json_data["data"]["result"][j]["metric"]["pod_name"]
                What_node = json_data["data"]["result"][j]["metric"]["instance"]
                Pod.Pod_name = Pod_name_input
                Pod.What_node = What_node
                Pod.Mem_usage = json_data["data"]["result"][j]["value"][1]

                for k in range(0, cnt_node):
                    if Cluster_object[i].Node_list[k].Node_name == Pod.What_node:
                        # Pod_list.append(Pod)
                        # Cluster_object[i].Node_list[k].Pod_list.extend(Pod_list)
                        cnt_pod = len(Cluster_object[i].Node_list[k].Pod_list)
                        for z in range(0, cnt_pod):
                            if Cluster_object[i].Node_list[k].Pod_list[z].Pod_name == Pod.Pod_name:
                                Cluster_object[i].Node_list[k].Pod_list[z].Mem_usage = Pod.Mem_usage

        ################### compute network receive bytes in each pods

    for i in range(0, int(cluster_num)):
        url = 'http://%s:30000/api/v1/query' % Cluster_object[i].Master_ip
        # PARAM = 'query= rate(container_memory_usage_bytes[5m]) by (pod_name)'
        PARAM = 'query= (rate(container_network_receive_bytes_total[5m]))'
        r = requests.get(url, params=PARAM)
        c = r.content.decode('utf-8')
        json_data = json.loads(c)

        print(json.dumps(json_data, indent=4, sort_keys=True))
        Num_of_pod = len(json_data['data']["result"])
        cnt_node = len(Cluster_object[i].Node_list)

        for j in range(0, int(Num_of_pod)):
            if (len(json_data["data"]["result"][j]["metric"]) == 16):
                Pod_name_input = json_data["data"]["result"][j]["metric"]["pod_name"]
                What_node = json_data["data"]["result"][j]["metric"]["instance"]
                Pod.Pod_name = Pod_name_input
                Pod.What_node = What_node
                Pod.Network_receive = json_data["data"]["result"][j]["value"][1]

                for k in range(0, cnt_node):
                    if Cluster_object[i].Node_list[k].Node_name == Pod.What_node:
                        # Pod_list.append(Pod)
                        # Cluster_object[i].Node_list[k].Pod_list.extend(Pod_list)
                        cnt_pod = len(Cluster_object[i].Node_list[k].Pod_list)
                        for z in range(0, cnt_pod):
                            if Cluster_object[i].Node_list[k].Pod_list[z].Pod_name == Pod.Pod_name:
                                Cluster_object[i].Node_list[k].Pod_list[z].Network_receive = Pod.Network_receive

        ################### compute network transmit bytes in each pods

    for i in range(0, int(cluster_num)):
        url = 'http://%s:30000/api/v1/query' % Cluster_object[i].Master_ip
        # PARAM = 'query= rate(container_memory_usage_bytes[5m]) by (pod_name)'
        PARAM = 'query= rate(container_network_transmit_bytes_total[5m])'
        r = requests.get(url, params=PARAM)
        c = r.content.decode('utf-8')
        json_data = json.loads(c)

        print(json.dumps(json_data, indent=4, sort_keys=True))
        Num_of_pod = len(json_data['data']["result"])
        cnt_node = len(Cluster_object[i].Node_list)

        for j in range(0, int(Num_of_pod)):
            if (len(json_data["data"]["result"][j]["metric"]) == 16):
                Pod_name_input = json_data["data"]["result"][j]["metric"]["pod_name"]
                What_node = json_data["data"]["result"][j]["metric"]["instance"]
                Pod.Pod_name = Pod_name_input
                Pod.What_node = What_node
                Pod.Network_transmit = json_data["data"]["result"][j]["value"][1]

                for k in range(0, cnt_node):
                    if Cluster_object[i].Node_list[k].Node_name == Pod.What_node:
                        # Pod_list.append(Pod)
                        # Cluster_object[i].Node_list[k].Pod_list.extend(Pod_list)
                        cnt_pod = len(Cluster_object[i].Node_list[k].Pod_list)
                        for z in range(0, cnt_pod):
                            if Cluster_object[i].Node_list[k].Pod_list[z].Pod_name == Pod.Pod_name:
                                Cluster_object[i].Node_list[k].Pod_list[z].Network_transmit = Pod.Network_transmit


        ################### compute filesystem usage bytes in each pods

    for i in range(0, int(cluster_num)):
        url = 'http://%s:30000/api/v1/query' % Cluster_object[i].Master_ip
        # PARAM = 'query= rate(container_memory_usage_bytes[5m]) by (pod_name)'
        PARAM = 'query= (container_fs_usage_bytes)'
        r = requests.get(url, params=PARAM)
        c = r.content.decode('utf-8')
        json_data = json.loads(c)

        print(json.dumps(json_data, indent=4, sort_keys=True))
        Num_of_pod = len(json_data['data']["result"])
        cnt_node = len(Cluster_object[i].Node_list)

        for j in range(0, int(Num_of_pod)):
            if (len(json_data["data"]["result"][j]["metric"]) == 17):
                Pod_name_input = json_data["data"]["result"][j]["metric"]["pod_name"]
                What_node = json_data["data"]["result"][j]["metric"]["instance"]
                Pod.Pod_name = Pod_name_input
                Pod.What_node = What_node
                Pod.Filesystem_usage_bytes = json_data["data"]["result"][j]["value"][1]

                for k in range(0, cnt_node):
                    if Cluster_object[i].Node_list[k].Node_name == Pod.What_node:
                        # Pod_list.append(Pod)
                        # Cluster_object[i].Node_list[k].Pod_list.extend(Pod_list)
                        cnt_pod = len(Cluster_object[i].Node_list[k].Pod_list)
                        for z in range(0, cnt_pod):
                            if Cluster_object[i].Node_list[k].Pod_list[z].Pod_name == Pod.Pod_name:
                                Cluster_object[i].Node_list[k].Pod_list[z].Filesystem_usage_bytes = Pod.Filesystem_usage_bytes

        ################### compute filesystem usage in each pods

    for i in range(0, int(cluster_num)):
        url = 'http://%s:30000/api/v1/query' % Cluster_object[i].Master_ip
        # PARAM = 'query= rate(container_memory_usage_bytes[5m]) by (pod_name)'
        PARAM = 'query= (container_fs_usage_bytes) / (container_fs_limit_bytes) * 100'
        r = requests.get(url, params=PARAM)
        c = r.content.decode('utf-8')
        json_data = json.loads(c)

        print(json.dumps(json_data, indent=4, sort_keys=True))
        Num_of_pod = len(json_data['data']["result"])
        cnt_node = len(Cluster_object[i].Node_list)

        for j in range(0, int(Num_of_pod)):
            if (len(json_data["data"]["result"][j]["metric"]) == 16):
                Pod_name_input = json_data["data"]["result"][j]["metric"]["pod_name"]
                What_node = json_data["data"]["result"][j]["metric"]["instance"]
                Pod.Pod_name = Pod_name_input
                Pod.What_node = What_node
                Pod.Filesystem_usage = json_data["data"]["result"][j]["value"][1]

                for k in range(0, cnt_node):
                    if Cluster_object[i].Node_list[k].Node_name == Pod.What_node:
                        # Pod_list.append(Pod)
                        # Cluster_object[i].Node_list[k].Pod_list.extend(Pod_list)
                        cnt_pod = len(Cluster_object[i].Node_list[k].Pod_list)
                        for z in range(0, cnt_pod):
                            if Cluster_object[i].Node_list[k].Pod_list[z].Pod_name == Pod.Pod_name:
                                Cluster_object[i].Node_list[k].Pod_list[z].Filesystem_usage = Pod.Filesystem_usage



    ##################### input all resource data into the mongodb
    conn = MongoClient('127.0.0.1')
    db = conn.test_db
    test_collect = db.collections_test

    frozen = jsonpickle.encode(Cluster_object)
    value = json.loads(frozen)
    test_collect.insert(value)




