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
import cluster_node_info_for_test
import pymongo
from pymongo import MongoClient
import time
import pickle
import jsonpickle
import multiprocessing as mp
from datetime import datetime

def deploy_pattern(Type_of_pattern, cnt_input, cluster_num, Cluster_object):
    if Type_of_pattern == '1':
        pattern = 'ml'
        #print('please input how many epochs do you want?')
        epoch_cnt = cnt_input
        for i in range(0, int(cluster_num)):
            cmd = "curl http://%s:5000/%s/%s" % (Cluster_object[i].Master_ip, pattern, epoch_cnt)
            out = subprocess.check_output([cmd], shell=True)

    elif Type_of_pattern == '2':
        pattern = 'webapp'
        print('please input how many curl request do you want?')
        curl_cnt = cnt_input
        for i in range(0, int(cluster_num)):
            cmd = "curl http://%s:5000/%s/%s" % (Cluster_object[i].Master_ip, pattern, curl_cnt)
            out = subprocess.check_output([cmd], shell=True)
            break
    elif Type_of_pattern == '3':
        pattern = 'IoTCloud'
        print('please input how many devices do you want to use?')
        device_cnt = cnt_input
        for i in range(0, int(cluster_num)):
            cmd = "curl http://%s:5000/%s/%s" % (Cluster_object[i].Master_ip, pattern, device_cnt)
            out = subprocess.check_output([cmd], shell=True)
            break

if __name__ == '__main__':
    flag = 0
    cluster_num = '1'
    Cluster_object = list()
    Cluster = cluster_node_info_for_test.Cluster()
    Cluster_object.append(Cluster)
    worker_num = '1'
    Cluster_object[0].Num_of_node = worker_num
    Cluster_object[0].Master_ip = '210.125.84.121'
    #Cluster_object[0].Master_ip = ''
    #Cluster_object[0].Worker_ip.append('')
    Cluster_object[0].Worker_ip.append('210.125.84.20')

    Cluster_object[0].Circulation_cnt = 0
    Cluster_object[0].Deployment_cnt = 1
    Type_of_pattern = 2
    cnt_input = 40
    #################### store initial value
    Init_value_cluster_object = list()
    Init_value_cluster = cluster_node_info_for_test.Cluster()
    #Init_value_cluster_object.append(Init_value_cluster)
    #worker_num = '1'
    #Init_value_cluster_object[0].Num_of_node = worker_num
    #Init_value_cluster_object[0].Master_ip = '210.125.84.77'
    # Cluster_object[0].Master_ip = '203.237.53.233'
    # Cluster_object[0].Worker_ip.append('203.237.53.209')
    #Init_value_cluster_object[0].Worker_ip.append('210.125.84.23')
    #Init_value_cluster_object[0].Worker_ip.append('210.125.84.24')
    #Init_value_cluster_object[0].Worker_ip.append('210.125.84.25')
    #Init_value_cluster_object[0].Worker_ip.append('210.125.84.26')
    #Init_value_cluster_object[0].Circulation_cnt = 0

    ##################user input part

    '''cluster_num = cluster_ip_setup.input_cluster_num()
    Cluster_object = list()
    
    for i in range(0, int(cluster_num)):
        Cluster = cluster_node_info_for_test.Cluster()
        Cluster_object.append(Cluster)
        worker_num = cluster_ip_setup.input_worker_num()
        Cluster_object[i].Num_of_node = worker_num
        master_ip = cluster_ip_setup.input_master_ip()
        Cluster_object[i].Master_ip = master_ip

        for j in range(0, int(Cluster_object[i].Num_of_node)):
            append_worker_ip = cluster_ip_setup.input_worker_ip()
            Cluster_object[i].Worker_ip.append(append_worker_ip)'''

    print('please input Type of pattern ex)1: ML pattern    2: Web-App-DB 3tier pattern     3: IoT-Cloud pattern')
    Type_of_pattern = input()
    if Type_of_pattern == '1':
        print('please input how many epochs do you want?')
        cnt_input = input()
    elif Type_of_pattern == '2':
        pattern = 'webapp'
        print('please input how many curl request do you want?')
        cnt_input = input()
    elif Type_of_pattern == '3':
        print('please input how many devices do you want to use?')
        cnt_input = input()

    print('how many Deployments?')
    Deployment_cnt = input()

    Cluster_object[0].Pattern_execute_cnt = cnt_input



    mp.set_start_method('spawn')

    for i in range(1, int(Deployment_cnt)+1):

        q = mp.Queue()
        p = mp.Process(target=deploy_pattern, args=(Type_of_pattern, cnt_input, cluster_num, Cluster_object,))
        p.start()



        while True:

            time.sleep(5)
            now = datetime.now()


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
                    Node = cluster_node_info_for_test.Node()
                    Node_name_input = json_data["data"]["result"][j]["metric"]["instance"]
                    Node.Node_name = Node_name_input
                    # Pod_count = json_data["data"]["result"][j]["value"][1]
                    Node_list.append(Node)

                Cluster_object[i].Node_list = Node_list
                Cluster_object[i].Pattern_type = Type_of_pattern
                Cluster_object[i].Monitoring_time = str(now)
                Cluster_object[i].Circulation_cnt = Cluster_object[i].Circulation_cnt + 1

            # print(Cluster_object[0].Node_list[2].Node_name)


            ################### compute cpu usage percent in each nodes

            for i in range(0, int(cluster_num)):
                for j in range(0, int(Cluster_object[i].Num_of_node)):
                    url = 'http://%s:30000/api/v1/query' % Cluster_object[i].Master_ip
                    #PARAM = 'query= 100 * (1 - avg by(instance)(irate(node_cpu{job="%s", mode="idle"}[5m])))' % Cluster_object[i].Node_list[j].Node_name
                    PARAM  = 'query= 100 - (avg by (instance, job) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)'
                    #PARAM  = 'query= 100 - (avg by (instance) (irate(node_cpu_seconds_total{job="%s", mode="idle"}[5m])) * 100)' % Cluster_object[i].Node_list[j].Node_name
                    #PARAM  = '100 * (1 - avg by(instance, job)(irate(node_cpu_seconds_total{mode='idle'}[5m])))'
                    r=requests.get(url, params= PARAM)
                    c=r.content.decode('utf-8')
                    json_data=json.loads(c)
                    print(json.dumps(json_data, indent = 4, sort_keys=True))
                    Num_of_result = len(json_data["data"]["result"])
                    for k in range(0, Num_of_result):
                        if "instance" in json_data["data"]["result"][k]["metric"]:
                            Node_cpu_input = json_data["data"]["result"][0]["value"][1]
                            Cluster_object[i].Node_list[j].Cpu_usage = Node_cpu_input
                       # print(Node_cpu_total)

            ################### compute cpu seconds in each nodes


            for i in range(0, int(cluster_num)):
                for j in range(0, int(Cluster_object[i].Num_of_node)):
                    url = 'http://%s:30000/api/v1/query' % Cluster_object[i].Master_ip
                    # PARAM = 'query= avg by (instance) (node_cpu_seconds_total{job="%s", mode="idle"})' % Cluster_object[i].Node_list[j].Node_name
                    PARAM = 'query= sum(rate(node_cpu_seconds_total{job="%s"}[5m])) by (instance)' % Cluster_object[i].Node_list[j].Node_name
                    #PARAM = 'query= avg by (instance) (node_cpu_seconds_total{job="%s", mode="idle"}[5m])' % Cluster_object[i].Node_list[j].Node_name
                    #PARAM = 'query= rate(node_cpu_seconds_total{mode="idle"}[5m])'
                    r = requests.get(url, params=PARAM)
                    c = r.content.decode('utf-8')
                    json_data = json.loads(c)
                    #print(json.dumps(json_data, indent = 4, sort_keys=True))
                    Num_of_result = len(json_data["data"]["result"])
                    for k in range(0, Num_of_result):
                            Node_cpu_seconds_input = json_data["data"]["result"][0]["value"][1]
                            Cluster_object[i].Node_list[j].Cpu_seconds = Node_cpu_seconds_input



            ################### compute memory usage in each nodes

            for i in range(0, int(cluster_num)):
                url = 'http://%s:30000/api/v1/query' % Cluster_object[i].Master_ip
                PARAM = 'query= ((node_memory_MemTotal_bytes - node_memory_MemFree_bytes) / node_memory_MemTotal_bytes) * 100'
                r = requests.get(url, params=PARAM)
                c = r.content.decode('utf-8')
                json_data = json.loads(c)
                #print(json.dumps(json_data, indent = 4, sort_keys=True))
                Num_of_result = len(json_data["data"]["result"])
                for j in range(0, int(Cluster_object[i].Num_of_node)):
                    what_node_input = json_data["data"]["result"][j]["metric"]["job"]
                    Node_memory_input = json_data["data"]["result"][j]["value"][1]
                    for k in range(0, int(Cluster_object[i].Num_of_node)):
                        if Cluster_object[i].Node_list[k].Node_name == what_node_input:
                            Cluster_object[i].Node_list[k].Mem_usage = Node_memory_input

            ################### compute memory bytes in each nodes

            for i in range(0, int(cluster_num)):
                url = 'http://%s:30000/api/v1/query' % Cluster_object[i].Master_ip
                PARAM = 'query= node_memory_Active_bytes'
                r = requests.get(url, params=PARAM)
                c = r.content.decode('utf-8')
                json_data = json.loads(c)
                #print(json.dumps(json_data, indent=4, sort_keys=True))


                for j in range(0, int(Cluster_object[i].Num_of_node)):
                    what_node_input = json_data["data"]["result"][j]["metric"]["job"]
                    Node_memory_bytes_input = json_data["data"]["result"][j]["value"][1]
                    for k in range(0, int(Cluster_object[i].Num_of_node)):
                        if Cluster_object[i].Node_list[k].Node_name == what_node_input:
                            Cluster_object[i].Node_list[k].Mem_bytes = Node_memory_bytes_input


            ################### network receive bytes in each nodes

            for i in range(0, int(cluster_num)):
                url = 'http://%s:30000/api/v1/query' % Cluster_object[i].Master_ip
                PARAM = 'query= sum(rate(node_network_receive_bytes_total{device=~"^en.*"}[5m])) by (instance, job)'
                r = requests.get(url, params=PARAM)
                c = r.content.decode('utf-8')
                json_data = json.loads(c)
                #print(json.dumps(json_data, indent=4, sort_keys=True))


                for j in range(0, int(Cluster_object[i].Num_of_node)):
                    what_node_input = json_data["data"]["result"][j]["metric"]["job"]
                    Node_network_receive_input = json_data["data"]["result"][j]["value"][1]
                    for k in range(0, int(Cluster_object[i].Num_of_node)):
                        if Cluster_object[i].Node_list[k].Node_name == what_node_input:
                            Cluster_object[i].Node_list[k].Network_receive = Node_network_receive_input



            ################### network transmit bytes in each nodes

            for i in range(0, int(cluster_num)):
                url = 'http://%s:30000/api/v1/query' % Cluster_object[i].Master_ip
                PARAM = 'query= sum(rate(node_network_transmit_bytes_total{device=~"^en.*"}[5m])) by (instance, job)'
                r=requests.get(url, params= PARAM)
                c=r.content.decode('utf-8')
                json_data=json.loads(c)
                #print(json.dumps(json_data, indent = 4, sort_keys=True))

                for j in range(0, int(Cluster_object[i].Num_of_node)):
                    what_node_input = json_data["data"]["result"][j]["metric"]["job"]
                    Node_network_transmit_input = json_data["data"]["result"][j]["value"][1]
                    for k in range(0, int(Cluster_object[i].Num_of_node)):
                        if Cluster_object[i].Node_list[k].Node_name == what_node_input:
                            Cluster_object[i].Node_list[k].Network_transmit = Node_network_transmit_input

            ################### filesystem usage in each nodes

            for i in range(0, int(cluster_num)):
                url = 'http://%s:30000/api/v1/query' % Cluster_object[i].Master_ip
                PARAM = 'query= max(((node_filesystem_size_bytes{fstype=~"ext4|vfat"} - node_filesystem_free_bytes{fstype=~"ext4|vfat"}) / node_filesystem_size_bytes{fstype=~"ext4|vfat"}) * 100) by (instance, job)'
                r=requests.get(url, params= PARAM)
                c=r.content.decode('utf-8')
                json_data=json.loads(c)
                #print(json.dumps(json_data, indent = 4, sort_keys=True))

                for j in range(0, int(Cluster_object[i].Num_of_node)):
                    what_node_input = json_data["data"]["result"][j]["metric"]["job"]
                    Node_filesystem_usage_input = json_data["data"]["result"][j]["value"][1]
                    for k in range(0, int(Cluster_object[i].Num_of_node)):
                        if Cluster_object[i].Node_list[k].Node_name == what_node_input:
                            Cluster_object[i].Node_list[k].Filesystem_usage = Node_filesystem_usage_input




            ################### filesystem usage bytes in each nodes

            for i in range(0, int(cluster_num)):
                url = 'http://%s:30000/api/v1/query' % Cluster_object[i].Master_ip
                PARAM = 'query= avg by (instance, job) (node_filesystem_size_bytes - node_filesystem_free_bytes)'
                r = requests.get(url, params=PARAM)
                c = r.content.decode('utf-8')
                json_data = json.loads(c)
                #print(json.dumps(json_data, indent = 4, sort_keys=True))

                for j in range(0, int(Cluster_object[i].Num_of_node)):
                    what_node_input = json_data["data"]["result"][j]["metric"]["job"]
                    Node_filesystem_bytes_input = json_data["data"]["result"][j]["value"][1]
                    for k in range(0, int(Cluster_object[i].Num_of_node)):
                        if Cluster_object[i].Node_list[k].Node_name == what_node_input:
                            Cluster_object[i].Node_list[k].Filesystem_bytes = Node_filesystem_bytes_input

            ################### Read latency seconds in each nodes

            for i in range(0, int(cluster_num)):
                url = 'http://%s:30000/api/v1/query' % Cluster_object[i].Master_ip
                PARAM = 'query= sum(node_disk_read_time_seconds_total) by (instance, job)'
                r = requests.get(url, params=PARAM)
                c = r.content.decode('utf-8')
                json_data = json.loads(c)
                #print(json.dumps(json_data, indent = 4, sort_keys=True))
                Num_of_result = len(json_data["data"]["result"])

                for j in range(0, int(Cluster_object[i].Num_of_node)):
                    what_node_input = json_data["data"]["result"][j]["metric"]["job"]
                    Read_latency_input = json_data["data"]["result"][j]["value"][1]
                    for k in range(0, int(Cluster_object[i].Num_of_node)):
                        if Cluster_object[i].Node_list[k].Node_name == what_node_input:
                            Cluster_object[i].Node_list[k].Read_latency = Read_latency_input


            ################### Write latency seconds in each nodes

            for i in range(0, int(cluster_num)):
                url = 'http://%s:30000/api/v1/query' % Cluster_object[i].Master_ip
                PARAM = 'query= sum(node_disk_write_time_seconds_total) by (instance, job)'
                r = requests.get(url, params=PARAM)
                c = r.content.decode('utf-8')
                json_data = json.loads(c)
                #print(json.dumps(json_data, indent = 4, sort_keys=True))
                Num_of_result = len(json_data["data"]["result"])

                for j in range(0, int(Cluster_object[i].Num_of_node)):
                    what_node_input = json_data["data"]["result"][j]["metric"]["job"]
                    Write_latency_input = json_data["data"]["result"][j]["value"][1]
                    for k in range(0, int(Cluster_object[i].Num_of_node)):
                        if Cluster_object[i].Node_list[k].Node_name == what_node_input:
                            Cluster_object[i].Node_list[k].Write_latency = Write_latency_input


            ################### Overall I/O load on my instance

            for i in range(0, int(cluster_num)):
                url = 'http://%s:30000/api/v1/query' % Cluster_object[i].Master_ip
                PARAM = 'query= sum(rate(node_disk_io_now[5m])) by (instance, job)'
                r = requests.get(url, params=PARAM)
                c = r.content.decode('utf-8')
                json_data = json.loads(c)
                #print(json.dumps(json_data, indent = 4, sort_keys=True))
                Num_of_result = len(json_data["data"]["result"])

                for j in range(0, int(Cluster_object[i].Num_of_node)):
                    what_node_input = json_data["data"]["result"][j]["metric"]["job"]
                    Disk_Overall_IO_input = json_data["data"]["result"][j]["value"][1]
                    for k in range(0, int(Cluster_object[i].Num_of_node)):
                        if Cluster_object[i].Node_list[k].Node_name == what_node_input:
                            Cluster_object[i].Node_list[k].Disk_Overall_IO = Disk_Overall_IO_input

            ################### Number of CPUs in each nodes

            for i in range(0, int(cluster_num)):
                url = 'http://%s:30000/api/v1/query' % Cluster_object[i].Master_ip
                PARAM = 'query= count without(cpu, mode) (node_cpu_seconds_total{mode="idle"})'
                r = requests.get(url, params=PARAM)
                c = r.content.decode('utf-8')
                json_data = json.loads(c)
                print(json.dumps(json_data, indent = 4, sort_keys=True))
                Num_of_result = len(json_data["data"]["result"])

                for j in range(0, int(Num_of_result)):
                    Num_of_cpu_core_input = json_data["data"]["result"][j]["value"][1]
                    what_node_input = json_data["data"]["result"][j]["metric"]["job"]

                    for k in range(0, Num_of_Node):
                        if what_node_input == Cluster_object[i].Node_list[k].Node_name:
                            Cluster_object[i].Node_list[k].Num_of_cpu_core = Num_of_cpu_core_input

            ################### compute cpu seconds in each pods
            for i in range(0, int(cluster_num)):
                url = 'http://%s:30000/api/v1/query' % Cluster_object[i].Master_ip
                PARAM = 'query= sum(rate(container_cpu_usage_seconds_total[5m])) by (instance, pod)'

                r = requests.get(url, params=PARAM)
                c = r.content.decode('utf-8')
                json_data = json.loads(c)
                #print(json.dumps(json_data, indent = 4, sort_keys=True))
                Pod_list = list()

                Num_of_result = len(json_data["data"]["result"])
                for k in range(0, Num_of_result):
                    if "pod" in json_data["data"]["result"][k]["metric"]:
                        Pod_name_input = json_data["data"]["result"][k]["metric"]["pod"]
                        What_node_input = json_data["data"]["result"][k]["metric"]["instance"]
                        Cpu_seconds_input = json_data["data"]["result"][k]["value"][1]

                        Pod = cluster_node_info_for_test.Pod()
                        Pod.Pod_name = Pod_name_input
                        Pod.What_node = What_node_input
                        Pod.Cpu_seconds = Cpu_seconds_input
                        Pod_list.append(Pod)

            Num_of_pod_in_cluster = len(Pod_list)
            for k in range(0, Num_of_pod_in_cluster):
                for j in range(0, Num_of_Node):
                    if Pod_list[k].What_node == Cluster_object[i].Node_list[j].Node_name:
                        Cluster_object[i].Node_list[j].Pod_list.append(Pod_list[k])

            for j in range(0, Num_of_Node):
                Cluster_object[i].Node_list[j].Num_of_pod = len(Cluster_object[i].Node_list[j].Pod_list)

            ################### compute cpu usage in each pods
            for i in range(0, int(cluster_num)):
                url = 'http://%s:30000/api/v1/query' % Cluster_object[i].Master_ip
                PARAM = 'query=  sum by(instance, pod)(rate(container_cpu_usage_seconds_total{}[5m])*100)'
                # PARAM = 'query=  100- (avg by (instance, pod) (irate(container_cpu_usage_seconds_total[5m]))*100)'
                # 'query= 100 - (avg by (instance) (irate(node_cpu_seconds_total{job="%s", mode="idle"}[5m])) * 100)'
                # PARAM = 'query=  rate(container_cpu_usage_seconds_total[5m])'
                # PARAM = 'query= sum(rate(container_cpu_usage_seconds_total[5m])) by (container_name)'
                r = requests.get(url, params=PARAM)
                c = r.content.decode('utf-8')
                json_data = json.loads(c)

                # Num_of_pod = len(json_data['data']["result"])
                #print(json.dumps(json_data, indent=4, sort_keys=True))

                Num_of_result = len(json_data["data"]["result"])
                for k in range(0, Num_of_result):
                    if "pod" in json_data["data"]["result"][k]["metric"]:
                        Pod_name_input = json_data["data"]["result"][k]["metric"]["pod"]
                        What_node_input = json_data["data"]["result"][k]["metric"]["instance"]
                        Cpu_usage_input = json_data["data"]["result"][k]["value"][1]

                        for j in range(0, Num_of_Node):
                            if What_node_input == Cluster_object[i].Node_list[j].Node_name:
                                for l in range(0, len(Cluster_object[i].Node_list[j].Pod_list)):
                                    if Pod_name_input == Cluster_object[i].Node_list[j].Pod_list[l].Pod_name:
                                        Cluster_object[i].Node_list[j].Pod_list[l].Cpu_usage = Cpu_usage_input

            ################### compute memory bytes in each pods
            for i in range(0, int(cluster_num)):
                url = 'http://%s:30000/api/v1/query' % Cluster_object[i].Master_ip
                PARAM = 'query=  sum by(instance, pod) (container_memory_usage_bytes)'
                # PARAM = 'query=  100- (avg by (instance, pod) (irate(container_cpu_usage_seconds_total[5m]))*100)'
                # 'query= 100 - (avg by (instance) (irate(node_cpu_seconds_total{job="%s", mode="idle"}[5m])) * 100)'
                # PARAM = 'query=  rate(container_cpu_usage_seconds_total[5m])'
                # PARAM = 'query= sum(rate(container_cpu_usage_seconds_total[5m])) by (container_name)'
                r = requests.get(url, params=PARAM)
                c = r.content.decode('utf-8')
                json_data = json.loads(c)

                # Num_of_pod = len(json_data['data']["result"])
                #print(json.dumps(json_data, indent=4, sort_keys=True))

                Num_of_result = len(json_data["data"]["result"])
                for k in range(0, Num_of_result):
                    if "pod" in json_data["data"]["result"][k]["metric"]:
                        Pod_name_input = json_data["data"]["result"][k]["metric"]["pod"]
                        What_node_input = json_data["data"]["result"][k]["metric"]["instance"]
                        Memory_bytes_input = json_data["data"]["result"][k]["value"][1]

                        for j in range(0, Num_of_Node):
                            if What_node_input == Cluster_object[i].Node_list[j].Node_name:
                                for l in range(0, len(Cluster_object[i].Node_list[j].Pod_list)):
                                    if Pod_name_input == Cluster_object[i].Node_list[j].Pod_list[l].Pod_name:
                                        Cluster_object[i].Node_list[j].Pod_list[l].Mem_bytes = Memory_bytes_input

            ################### compute memory usage in each pods
            for i in range(0, int(cluster_num)):
                url = 'http://%s:30000/api/v1/query' % Cluster_object[i].Master_ip
                #PARAM = 'query=  sum(rate(container_memory_usage_bytes) / (container_memory_max_usage_bytes)  '
                PARAM = 'query=  (container_memory_usage_bytes) / (container_memory_max_usage_bytes) * 100'
                #PARAN = 'query= (sum(rate (container_memory_usage_bytes) / container_memory_max_usage_bytes) by(pod))  * 100 '
                # PARAM = 'query=  100- (avg by (instance, pod) (irate(container_cpu_usage_seconds_total[5m]))*100)'
                # 'query= 100 - (avg by (instance) (irate(node_cpu_seconds_total{job="%s", mode="idle"}[5m])) * 100)'
                # PARAM = 'query=  rate(container_cpu_usage_seconds_total[5m])'
                # PARAM = 'query= sum(rate(container_cpu_usage_seconds_total[5m])) by (container_name)'
                r = requests.get(url, params=PARAM)
                c = r.content.decode('utf-8')
                json_data = json.loads(c)

                # Num_of_pod = len(json_data['data']["result"])
                #print(json.dumps(json_data, indent=4, sort_keys=True))

                Num_of_result = len(json_data["data"]["result"])
                for k in range(0, Num_of_result):
                    if "pod" in json_data["data"]["result"][k]["metric"]:
                        Pod_name_input = json_data["data"]["result"][k]["metric"]["pod"]
                        What_node_input = json_data["data"]["result"][k]["metric"]["instance"]
                        Memory_usage_input = json_data["data"]["result"][k]["value"][1]

                        for j in range(0, Num_of_Node):
                            if What_node_input == Cluster_object[i].Node_list[j].Node_name:
                                for l in range(0, len(Cluster_object[i].Node_list[j].Pod_list)):
                                    if Pod_name_input == Cluster_object[i].Node_list[j].Pod_list[l].Pod_name:
                                        Cluster_object[i].Node_list[j].Pod_list[l].Mem_usage = Memory_usage_input

            ################### compute network receive bytes in each pods
            for i in range(0, int(cluster_num)):
                url = 'http://%s:30000/api/v1/query' % Cluster_object[i].Master_ip
                #PARAM = 'query=  sum(rate(container_memory_usage_bytes) / (container_memory_max_usage_bytes)  '
                PARAM = 'query= (rate(container_network_receive_bytes_total[5m]))'
                #PARAN = 'query= (sum(rate (container_memory_usage_bytes) / container_memory_max_usage_bytes) by(pod))  * 100 '
                # PARAM = 'query=  100- (avg by (instance, pod) (irate(container_cpu_usage_seconds_total[5m]))*100)'
                # 'query= 100 - (avg by (instance) (irate(node_cpu_seconds_total{job="%s", mode="idle"}[5m])) * 100)'
                # PARAM = 'query=  rate(container_cpu_usage_seconds_total[5m])'
                # PARAM = 'query= sum(rate(container_cpu_usage_seconds_total[5m])) by (container_name)'
                r = requests.get(url, params=PARAM)
                c = r.content.decode('utf-8')
                json_data = json.loads(c)

                # Num_of_pod = len(json_data['data']["result"])
                #print(json.dumps(json_data, indent=4, sort_keys=True))

                Num_of_result = len(json_data["data"]["result"])
                for k in range(0, Num_of_result):
                    if "pod" in json_data["data"]["result"][k]["metric"]:
                        Pod_name_input = json_data["data"]["result"][k]["metric"]["pod"]
                        What_node_input = json_data["data"]["result"][k]["metric"]["instance"]
                        Network_receive_input = json_data["data"]["result"][k]["value"][1]

                        for j in range(0, Num_of_Node):
                            if What_node_input == Cluster_object[i].Node_list[j].Node_name:
                                for l in range(0, len(Cluster_object[i].Node_list[j].Pod_list)):
                                    if Pod_name_input == Cluster_object[i].Node_list[j].Pod_list[l].Pod_name:
                                        Cluster_object[i].Node_list[j].Pod_list[l].Network_receive = Network_receive_input

            ################### compute network transmit bytes in each pods
            for i in range(0, int(cluster_num)):
                url = 'http://%s:30000/api/v1/query' % Cluster_object[i].Master_ip
                #PARAM = 'query=  sum(rate(container_memory_usage_bytes) / (container_memory_max_usage_bytes)  '
                PARAM = 'query= rate(container_network_transmit_bytes_total[5m])'
                #PARAN = 'query= (sum(rate (container_memory_usage_bytes) / container_memory_max_usage_bytes) by(pod))  * 100 '
                # PARAM = 'query=  100- (avg by (instance, pod) (irate(container_cpu_usage_seconds_total[5m]))*100)'
                # 'query= 100 - (avg by (instance) (irate(node_cpu_seconds_total{job="%s", mode="idle"}[5m])) * 100)'
                # PARAM = 'query=  rate(container_cpu_usage_seconds_total[5m])'
                # PARAM = 'query= sum(rate(container_cpu_usage_seconds_total[5m])) by (container_name)'
                r = requests.get(url, params=PARAM)
                c = r.content.decode('utf-8')
                json_data = json.loads(c)

                # Num_of_pod = len(json_data['data']["result"])
                #print(json.dumps(json_data, indent=4, sort_keys=True))

                Num_of_result = len(json_data["data"]["result"])
                for k in range(0, Num_of_result):
                    if "pod" in json_data["data"]["result"][k]["metric"]:
                        Pod_name_input = json_data["data"]["result"][k]["metric"]["pod"]
                        What_node_input = json_data["data"]["result"][k]["metric"]["instance"]
                        Network_transmit_input = json_data["data"]["result"][k]["value"][1]

                        for j in range(0, Num_of_Node):
                            if What_node_input == Cluster_object[i].Node_list[j].Node_name:
                                for l in range(0, len(Cluster_object[i].Node_list[j].Pod_list)):
                                    if Pod_name_input == Cluster_object[i].Node_list[j].Pod_list[l].Pod_name:
                                        Cluster_object[i].Node_list[j].Pod_list[l].Network_transmit = Network_transmit_input

            ################### compute filesystem usage bytes in each pods
            for i in range(0, int(cluster_num)):
                url = 'http://%s:30000/api/v1/query' % Cluster_object[i].Master_ip
                # PARAM = 'query=  sum(rate(container_memory_usage_bytes) / (container_memory_max_usage_bytes)  '
                PARAM = 'query= (container_fs_usage_bytes)'
                # PARAN = 'query= (sum(rate (container_memory_usage_bytes) / container_memory_max_usage_bytes) by(pod))  * 100 '
                # PARAM = 'query=  100- (avg by (instance, pod) (irate(container_cpu_usage_seconds_total[5m]))*100)'
                # 'query= 100 - (avg by (instance) (irate(node_cpu_seconds_total{job="%s", mode="idle"}[5m])) * 100)'
                # PARAM = 'query=  rate(container_cpu_usage_seconds_total[5m])'
                # PARAM = 'query= sum(rate(container_cpu_usage_seconds_total[5m])) by (container_name)'
                r = requests.get(url, params=PARAM)
                c = r.content.decode('utf-8')
                json_data = json.loads(c)

                # Num_of_pod = len(json_data['data']["result"])
                print(json.dumps(json_data, indent=4, sort_keys=True))

                Num_of_result = len(json_data["data"]["result"])
                for k in range(0, Num_of_result):
                    if "pod" in json_data["data"]["result"][k]["metric"]:
                        Pod_name_input = json_data["data"]["result"][k]["metric"]["pod"]
                        What_node_input = json_data["data"]["result"][k]["metric"]["instance"]
                        Filesystem_usage_bytes_input = json_data["data"]["result"][k]["value"][1]

                        for j in range(0, Num_of_Node):
                            if What_node_input == Cluster_object[i].Node_list[j].Node_name:
                                for l in range(0, len(Cluster_object[i].Node_list[j].Pod_list)):
                                    if Pod_name_input == Cluster_object[i].Node_list[j].Pod_list[l].Pod_name:
                                        Cluster_object[i].Node_list[j].Pod_list[l].Filesystem_usage_bytes = Filesystem_usage_bytes_input

            ################### compute filesystem usage in each pods
            for i in range(0, int(cluster_num)):
                url = 'http://%s:30000/api/v1/query' % Cluster_object[i].Master_ip
                # PARAM = 'query=  sum(rate(container_memory_usage_bytes) / (container_memory_max_usage_bytes)  '
                PARAM = 'query= (container_fs_usage_bytes) / (container_fs_limit_bytes) * 100'
                # PARAN = 'query= (sum(rate (container_memory_usage_bytes) / container_memory_max_usage_bytes) by(pod))  * 100 '
                # PARAM = 'query=  100- (avg by (instance, pod) (irate(container_cpu_usage_seconds_total[5m]))*100)'
                # 'query= 100 - (avg by (instance) (irate(node_cpu_seconds_total{job="%s", mode="idle"}[5m])) * 100)'
                # PARAM = 'query=  rate(container_cpu_usage_seconds_total[5m])'
                # PARAM = 'query= sum(rate(container_cpu_usage_seconds_total[5m])) by (container_name)'
                r = requests.get(url, params=PARAM)
                c = r.content.decode('utf-8')
                json_data = json.loads(c)

                # Num_of_pod = len(json_data['data']["result"])
                #print(json.dumps(json_data, indent=4, sort_keys=True))

                Num_of_result = len(json_data["data"]["result"])
                for k in range(0, Num_of_result):
                    if "pod" in json_data["data"]["result"][k]["metric"]:
                        Pod_name_input = json_data["data"]["result"][k]["metric"]["pod"]
                        What_node_input = json_data["data"]["result"][k]["metric"]["instance"]
                        Filesystem_usage_input = json_data["data"]["result"][k]["value"][1]

                        for j in range(0, Num_of_Node):
                            if What_node_input == Cluster_object[i].Node_list[j].Node_name:
                                for l in range(0, len(Cluster_object[i].Node_list[j].Pod_list)):
                                    if Pod_name_input == Cluster_object[i].Node_list[j].Pod_list[l].Pod_name:
                                        Cluster_object[i].Node_list[j].Pod_list[l].Filesystem_usage = Filesystem_usage_input


            #storing initial cpu value for cluster
            for i in range(0, int(cluster_num)):
                if Cluster_object[i].Circulation_cnt == 1:
                    #Init_value_cluster_object.append(Cluster)
                    #Init_value_cluster_object = Cluster
                    #Init_value_cluster_object = Cluster_object
                    #Init_value_cluster_object = Cluster_object
                    Initial_sum_cpu_usage = 0
                    Initial_avg_cpu_usage = 0
                    Initial_monitoring_time = 0
                    Initial_monitoring_time = Cluster_object[i].Monitoring_time
                    for j in range(0, Cluster_object[i].Num_of_node):
                        Initial_sum_cpu_usage = float(Cluster_object[i].Node_list[j].Cpu_usage) + float(Initial_sum_cpu_usage)
                        Initial_avg_cpu_usage = Initial_sum_cpu_usage / Cluster_object[i].Num_of_node

            #storing initial network value for cluster
            for i in range(0, int(cluster_num)):
                if Cluster_object[i].Circulation_cnt == 1:
                    #Init_value_cluster_object.append(Cluster)
                    #Init_value_cluster_object = Cluster
                    #Init_value_cluster_object = Cluster_object
                    #Init_value_cluster_object = Cluster_object
                    Initial_sum_Network_transmit = 0
                    Initial_avg_Network_transmit = 0
                    Initial_monitoring_time = Cluster_object[i].Monitoring_time
                    for j in range(0, Cluster_object[i].Num_of_node):
                        Initial_sum_Network_transmit = float(Cluster_object[i].Node_list[j].Network_transmit) + float(Initial_sum_Network_transmit)
                        Initial_avg_Network_transmit = Initial_sum_Network_transmit / Cluster_object[i].Num_of_node


            ### now resource information
            Now_sum_cpu_usage = 0
            Now_avg_cpu_usage = 0
            Now_sum_Network_transmit = 0
            Now_avg_Network_transmit = 0
            for i in range(0, int(cluster_num)):
                for j in range(0, Cluster_object[i].Num_of_node):
                    Now_sum_cpu_usage = float(Cluster_object[i].Node_list[j].Cpu_usage) + float(Now_sum_cpu_usage)
                    Now_avg_cpu_usage = Now_sum_cpu_usage / Cluster_object[i].Num_of_node
                    print(Now_avg_cpu_usage)
                Cluster_object[i].Cpu_usage = Now_avg_cpu_usage

                for j in range(0, Cluster_object[i].Num_of_node):
                    Now_sum_Network_transmit = float(Cluster_object[i].Node_list[j].Network_transmit) + float(Now_sum_Network_transmit)
                    Now_avg_Network_transmit = Now_sum_Network_transmit / Cluster_object[i].Num_of_node
                Cluster_object[i].Network_transmit = Now_avg_Network_transmit

                    ##################### input all resource data into the mongodb


            conn = MongoClient('127.0.0.1')
            #db = conn.test_db
            db_name = ''
            pattern_type = ''

            if Type_of_pattern == '1':
                pattern_type = 'ml_%s_' % cnt_input
                db = conn.C3_ML
            elif Type_of_pattern == '2':
                pattern_type = '3tier_%s_' % cnt_input
                db = conn.C3_Web_App_DB
            elif Type_of_pattern == '3':
                pattern_type = 'IoTCloud_%s_' % cnt_input
                db = conn.C3_IoT_Cloud


            Collection_name = pattern_type + str(Cluster_object[0].Deployment_cnt)
            if Cluster_object[0].Circulation_cnt == 1:
                test_collect = db.create_collection(Collection_name)
            Cluster_pickle = jsonpickle.encode(Cluster_object)
            value = json.loads(Cluster_pickle)
            test_collect.insert(value)

    ########################################################################################################################
            #compare resource information with now resource information for stop monitoring.



            ### compare initial resource and now resource information
            for i in range(0, int(cluster_num)):
                if Cluster_object[i].Circulation_cnt > 1:
                    if float(Now_avg_Network_transmit) - (float(Initial_avg_Network_transmit) * 0.2) <= Initial_avg_Network_transmit:
                        today = datetime.today()
                        if int(today.hour) == int(Initial_monitoring_time[11:13]):
                            if int(today.minute) - int(Initial_monitoring_time[14:16]) >= 2:
                                #print(Cluster_object[i].Monitoring_time)
                                #print(Cluster_object[i].Monitoring_time[14:16])
                                #print(today.minute)
                                ################################ circulation initialization
                                Cluster_object[i].Network_transmit = Now_avg_Network_transmit
                                Cluster_object[i].Deployment_cnt = Cluster_object[i].Deployment_cnt + 1
                                Cluster_object[i].Circulation_cnt = 0
                                flag = 1
                                print('end')
                                break
                        if int(today.hour) > int(Initial_monitoring_time[11:13]):
                            if int(today.minute)+60 - int(Initial_monitoring_time[14:16]) >= 2:
                                # print(Cluster_object[i].Monitoring_time)
                                # print(Cluster_object[i].Monitoring_time[14:16])
                                # print(today.minute)
                                ################################ circulation initialization
                                Cluster_object[i].Network_transmit = Now_avg_Network_transmit
                                Cluster_object[i].Deployment_cnt = Cluster_object[i].Deployment_cnt + 1
                                Cluster_object[i].Circulation_cnt = 0
                                flag = 1
                                print('end')
                                break

            if flag ==1:
                master_ip = '210.125.84.121'
                cmd = "curl http://%s:5000/Delete" % (master_ip)
                out = subprocess.check_output([cmd], shell=True)
                print('finished')
                time.sleep(50)
                flag = 0
                break




