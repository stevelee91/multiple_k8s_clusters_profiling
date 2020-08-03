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
  def __init__ (self):
    self.Cluster_number = ""
    self.Num_of_node = ""
    self.Node_name = []
    self.Master_ip = ""
    self.Worker_ip = []


class Node(Cluster):
  def __init__(self):
    super().__init__()
    self.Node_names = ""
    self.Cpu_usage = ""
    self.Mem_usage = ""
    self.Filesystem_usage = ""
    self.Network_receive = ""
    self.Network_transmit = ""


class Pod(Node):
  def __init__(self):
    super().__init__()
    self.Pod_name = ""
    self.Cpu_usage = ""
    self.Mem_usage = ""
    self.Filesystem_usage = ""
    self.Network_receive = ""
    self.Network_transmit = ""

#Node_1 = Node()
#Node_1.Node_name.append('master1')
#print(Node_1.Node_name)

Pod1 = Pod()
Pod1.Node_name.append('master1')
print(Pod1.Node_name)
