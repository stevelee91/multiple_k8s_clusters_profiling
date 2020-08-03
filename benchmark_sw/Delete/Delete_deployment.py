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
import cluster_node_info
import pymongo
from pymongo import MongoClient
import time
import pickle
import jsonpickle
import multiprocessing as mp


print('please input your master ip')
master_ip = input()
cmd = "curl http://%s:5000/Delete" % (master_ip)
out = subprocess.check_output([cmd], shell=True)


