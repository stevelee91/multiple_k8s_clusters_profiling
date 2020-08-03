#coding:utf-8  ##한글 처리

import requests, json
import time
import requests, json
import time
import os
import sys
import subprocess
from time import localtime, strftime
import threading

class EdgeX:
    def __init__(self, ip='localhost'):
        self.ip = ip
        self.port = 31091
        self.metaIp = ip
        self.metaPort = 32007
        self.headers = {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*','Access-Control-Allow-Headers': '*', 'Access-Control-Allow-Methods' : 'POST, GET, OPTIONS'}

    def DataTemplate(self):
        deviceTemplate = '{"name":"device","formatting":"%s"}'
        tempTemplate = '{"name":"temperature","min":"-40","max":"140","type":"F","uomLabel":"degree cel","defaultValue":"0","formatting":"%s","labels":["temp","hvac"]}'
        humidTemplate = '{"name":"humidity","min":"0","max":"100","type":"F","uomLabel":"per","defaultValue":"0","formatting":"%s","labels":["humidity","hvac"]}'
        dateTemplate = '{"name":"time","formatting":"%s","labels":["time","YYYYMMDD HHMMSS"]}'
        url = 'http://%s:%d/api/v1/valuedescriptor' % (self.ip, self.port)
        response = requests.post(url, data=deviceTemplate, headers=self.headers)
        response = requests.post(url, data=tempTemplate, headers=self.headers)
        response = requests.post(url, data=humidTemplate, headers=self.headers)
        response = requests.post(url, data=dateTemplate, headers=self.headers)


    def createDevice(self, deviceName):
        print('Creating addressable for ', deviceName)
        addresableData = '{"origin":1471806386919,"name":"%s","protocol":"HTTP","address":"","port":"161","path":"","publisher":"none","user":"none","password":"none","topic":"none"}' % (
        deviceName,)
        url = 'http://%s:%d/api/v1/addressable' % (self.metaIp, self.metaPort)
        response = requests.post(url, data=addresableData, headers=self.headers)
        if response.status_code != 200:
            print(response.status_code)
            print(response.content)
        else:
            print('OK')

        print('Creating addressable for service')
        serviceAddresableData = '{"origin":1471806386919,"name":"%s-address","protocol":"HTTP","address":"","port":"49989","path":"","publisher":"none","user":"none","password":"none","topic":"none"}'%(deviceName,)
        url = 'http://%s:%d/api/v1/addressable' % (self.metaIp, self.metaPort)
        response = requests.post(url, data=serviceAddresableData, headers=self.headers)
        if response.status_code != 200:
            print(response.status_code)
            print(response.content)
        else:
            print('OK')

        print('Creating service')
        serviceData = '{"origin":1471806386919,"name":"edgex-%s","description":"temperature service for rooms","lastConnected":0,"lastReported":0,"labels":["snmp","rtu","io"],"adminState":"unlocked","operatingState":"enabled","addressable":{"name":"%s-address"}}'%(deviceName, deviceName,)
        url = 'http://%s:%d/api/v1/deviceservice' % (self.metaIp, self.metaPort)
        response = requests.post(url, data=serviceData, headers=self.headers)
        if response.status_code != 200:
            print(response.status_code)
            print(response.content)
        else:
            print('OK')


    def execute(number):
        print(number)
        date = strftime("%y.%m.%d-%H:%M:%S", localtime())
        #h, t = dht.read_retry(dht.DHT22, 4)
        h = 60
        t = 32
        if t <= 35:
            print 'Temp={0:0.1f}*C Humidity={1:0.1f}%'.format(t, h)

            url = "http://localhost:31091/api/v1/event"

            payload = {"origin": 1471806386919, "device": "Device"+str(number),
                       "readings": [{"origin": 1471806386919, "name": "device", "value": 'Device'+str(number)},
                                    {"origin": 1471806386919, "name": "time", "value": date},
                                    {"origin": 1471806386919, "name": "temperature", "value": t},
                                    {"origin": 1471806386919, "name": "humidity", "value": h}]}

            headers = {"Accept": "application/json", "Content-Type": "application/json"}

            response = requests.post(url, data=json.dumps(payload), headers=headers)
            time.sleep(10)  ##delay time 100 seconds

            print(response.text)
            print(response.headers)


            url = "http://localhost:32014" ##flask에 api 요청
            response = requests.get(url, headers=headers)

if __name__ == '__main__':
    print("how many devices?")
    device_cnt = input()
    edgex_list = list()
    for i in range(0, int(device_cnt)):
        edgex = EdgeX()
        edgex.DataTemplate()
        edgex.createDevice('Device'+str(i))
        edgex_list.append(edgex)

    for i in range(0, int(device_cnt)):
#        my_thread = threading.Thread(target=edgex_list[i].execute(), args=(i,))
        my_thread = threading.Thread(target=edgex.execute, args=(i,))
        my_thread.start()

