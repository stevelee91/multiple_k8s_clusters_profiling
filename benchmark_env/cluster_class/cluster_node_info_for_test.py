import time
import os
import sys
import subprocess
import requests
import multiprocessing
import urllib
import json
from collections import OrderedDict
from pprint import pprint as pp
import cluster_ip_setup

##################class definition part


class Cluster:
  def __init__(self):
    self.Cluster_number = ""
    self.Num_of_node = ""
    self.Node_list = []
    self.Master_ip = ""
    self.Worker_ip = []
    self.Pattern_type = int
    self.Pattern_execute_cnt = int
    self.Monitoring_time = str
    self.Deployment_cnt = int
    self.Circulation_cnt = int
    self.Cpu_usage = float
    self.Network_transmit = float
class Node:
  def __init__(self):
    self.Node_name = str
    self.Num_of_cpu_core = int
    self.Cpu_usage = float
    self.Cpu_seconds = float
    self.Mem_usage = float
    self.Mem_bytes = float
    self.Filesystem_usage = float
    self.Filesystem_bytes = float
    self.Network_receive = float
    self.Network_transmit = float
    self.Read_latency = float
    self.Write_latency = float
    self.Disk_Overall_IO = float
    self.Num_of_pod = ""
    self.Pod_list = []


class Pod:
  def __init__(self):
    self.Pod_name = str
    #self.Namespace = str
    self.What_node = str
    self.Cpu_usage = float
    self.Cpu_seconds = float
    self.Mem_usage = float
    self.Mem_bytes = float
    self.Filesystem_usage = float
    self.Filesystem_usage_bytes = float
    self.Network_receive = float
    self.Network_transmit = float

