import seaborn as sns
import matplotlib.pyplot as plt
import pymongo
import os
import subprocess
import sys
import requests
import re
import datetime
from time import localtime, strftime
from pymongo import MongoClient
import json
from bson.json_util import dumps
from bson.json_util import loads
import subprocess
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

### 변경 가능한 파라미터들
Mongo_IP = 'portal_IP' # MongoDB의 IP
Cluster_num = 3 # Resource data를 가져올 클러스터들의 개수
DB_list = ['Web_App_DB', 'IoT_Cloud', 'ML'] # MongoDB에 저장되는 data의 Collection list
Metric_list = ['Network_transmit', 'Cpu_usage', 'Mem_usage']
WorkloadType_list = ['Web_App_DB', 'IoTCloud', 'ml']
WorkloadFile_list = ['3tier', 'IoTCloud', 'ml']
Epoch_list1 = [5, 50] # Web_App_DB, ML Workload의 Epoch 수
Epoch_list2 = [5, 20] # IoTCloud Workload의 Epoch 수

### 상기 데이터들의 모든 경우를 표현한 그래프를 저장함
connection = pymongo.MongoClient(Mongo_IP, 27017)
for m in range(Cluster_num):
    for n in range(len(WorkloadType_list)):
        for k in range(len(Epoch_list1)):
            for p in range(len(Metric_list)):
                x_array = []
                y_array = []
                DB_Name = 'C' + str(m+1) + '_' + DB_list[n]
                db = connection[DB_Name]
                Metric1 = Metric_list[p]
                if (WorkloadType_list[n] == "IoTCloud"):
                    Workload = WorkloadFile_list[n] + '_' + str(Epoch_list2[k]) + '_'
                else:
                    Workload = WorkloadFile_list[n] + '_' + str(Epoch_list1[k]) + '_'

                # 반복 100 번까지
                for i in range(1, 101):
                    db_id = Workload + str(i)
                    collection = db[db_id]  # db 열기
                    # array 만들기
                    docs = collection.find()
                    count = 0
                    for result in docs:
                        bson_ = dumps(result, indent=4, sort_keys=True)
                        json_ = loads(bson_)
                        count = count + 1
                        node_list = json_["Node_list"]
                        var_total = 0
                        node_cnt = 0 # Node_list 내의 노드 수를 나타냄
                        # 노드 수 4개까지의 각 Metric값을 더한 후 평균값 계산
                        for var in node_list:
                            node_cnt = node_cnt + 1
                            if (node_cnt == 5):
                                break
                            var_metric = var[Metric1]
                            var_total = var_total + float(var_metric)
                        var = var_total / 4
                        y_array.append(var)
                        
                        # x 축 어레이 만들기
                    for j in range(1, count + 1):
                        x_array.append(j * 5)

                    # 그래프 뿌리기
                x = np.array(x_array)
                y = np.array(y_array)

                # Setup for Filename
                if (WorkloadType_list[n] == "IoTCloud"):
                    db_id_fig = 'C' + str(m+1) + '_' + WorkloadType_list[n] + '_' + str(Epoch_list2[k]) + '_' + Metric_list[p]
                else:
                    db_id_fig = 'C' + str(m+1) + '_' + WorkloadType_list[n] + '_' + str(Epoch_list1[k]) + '_' + Metric_list[p]

                # Setup for df
                if (WorkloadType_list[n] == "IoTCloud"):
                    df = pd.DataFrame({"time_5s": x, Metric_list[p] + '_' + WorkloadType_list[n] + '_' + str(Epoch_list2[k]) + '_epochs': y})
                else:
                    df = pd.DataFrame({"time_5s": x, Metric_list[p] + '_' + WorkloadType_list[n] + '_' + str(Epoch_list1[k]) + '_epochs': y})

                #Using Seaborn for 1st plot
                if (WorkloadType_list[n] == "IoTCloud"):
                    sns_plot1 = sns.pointplot(x="time_5s", y=Metric_list[p] + '_' + WorkloadType_list[n] + '_' + str(Epoch_list2[k]) + '_epochs', data=df, color="green")
                else:
                    sns_plot1 = sns.pointplot(x="time_5s", y=Metric_list[p] + '_' + WorkloadType_list[n] + '_' + str(Epoch_list1[k]) + '_epochs', data=df, color="green")

                fig1 = sns_plot1.get_figure()
                fig1.savefig(f"{db_id_fig!r}_1.png")
                # Cleaning graphical plots
                plt.clf()

                # Using matplotlib for 2nd plot
                if (WorkloadType_list[n] == "IoTCloud"):
                    sns_plot2 = sns.lmplot('time_5s', Metric_list[p] + '_' + WorkloadType_list[n] + '_' + str(
                        Epoch_list2[k]) + '_epochs', df, truncate=False, order=2, height=7, aspect=1,
                                           scatter_kws={"s": 10, "color": "b"}, line_kws={'color': 'b'})
                else:
                    sns_plot2 = sns.lmplot('time_5s', Metric_list[p] + '_' + WorkloadType_list[n] + '_' + str(
                        Epoch_list1[k]) + '_epochs', df, truncate=False, order=2, height=7, aspect=1,
                                           scatter_kws={"s": 10, "color": "b"}, line_kws={'color': 'b'})

                sns_plot2.savefig(f"{db_id_fig!r}_2.png")
                # Cleaning graphical plots
                plt.clf()
                #print("save complete")

#print("END")
