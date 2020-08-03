import sys
import subprocess
import os 
import pandas as pd
import time 
from flask import Flask
import socket_client
import client_wp
import temphumid
import requests 

master_ip = '203.237.53.203'

app = Flask(__name__)

def kube_state(container_name):
    while True:
        f = open('output.txt','wb')
        cmd ="kubectl get po -o wide --all-namespaces"
        out = subprocess.check_output([cmd], shell=True)
        print ('have %d bytes ' % len(out))
        #print(out)
        f.write(out)
        f.close()
        time.sleep(1)  ##delay time 100 seconds
        df = pd.read_csv('output.txt', delimiter= '\s+', index_col=False)
        #print(df)
        #print(df['NAME'])
        #container_ns_row = df[(df.NAMESPACE.str.contains(default))]
        #container_namespace = container_ns_row['NAMESPACE']
        
        #container_row = df[(df.NAME.str.contains(container_name))]
        container_row = df[(df.NAME.str.contains(container_name)) & (df.NAMESPACE.str.contains('default'))]

        container_state = container_row['STATUS']
        if container_state.item() == 'Running':
            time.sleep(10)
            print('finish')
            break 
    return container_state.item()


@app.route('/ml/<cnt_epoch>')
def ml(cnt_epoch):
    cmd = "kubectl apply -f patterns/ml_pattern/keras2.yaml "
    out = subprocess.check_output([cmd], shell=True)
    f = open('output.txt','wb')
    cmd ="kubectl get po -o wide --all-namespaces"
    out = subprocess.check_output([cmd], shell=True)
    print ('have %d bytes ' % len(out))
    #print(out)
    f.write(out)
    f.close()
    time.sleep(5)  ##delay time 100 seconds
    df = pd.read_csv('output.txt', delimiter= '\s+', index_col=False)
    #print(df)
    #print(df['NAME'])
    kube_state('ml-pattern')
    socket_client.ml_test(cnt_epoch)
    return str(cnt_epoch)  

@app.route('/webapp/<cnt_client>')
def webapp(cnt_client):
    locate=os.getcwd()
    #print(locate)
    os.chdir("%s/patterns/kube_wordpress_3tier_pattern" % locate)
    ch_locate=os.getcwd()
    #print(ch_locate)
    subprocess.call("./deployment.sh")
    os.chdir("%s" % locate)
    #cmd = "./kube_wordpress_3tier_pattern/deployment.sh"
    #out = subprocess.check_output([cmd], shell=True)
    kube_state('mysql')
    kube_state('wordpress')
    print('ok')
    client_wp.client_wp(int(cnt_client))

    return str(cnt_client)

@app.route('/IoTCloud/<cnt_iot>')
def IoTCloud(cnt_iot):
    locate=os.getcwd()
    #print(locate)
    os.chdir("%s/patterns/IoT-Cloud_pattern/Smart-Energy-service-yaml" % locate)
    ch_locate=os.getcwd()
    #print(ch_locate)
    subprocess.call("./Smart_Energy.sh")
    os.chdir("%s" % locate)
    kube_state('kafka-broker-1')
    kube_state('kafka-broker-2')
    kube_state('kafka-broker-3')
    kube_state('zookeeper')
    kube_state('edgex-mongo')
    kube_state('edgex-core-consul')
    kube_state('edgex-core-command')
    kube_state('edgex-support-logging')
    kube_state('edgex-core-data')
    kube_state('edgex-core-metadata')
    kube_state('consumer-device1')
    temphumid.temphum(int(cnt_iot))

@app.route('/Delete')
def Delete():
    locate=os.getcwd()
    print(locate)
    os.chdir("%s" % locate)

    subprocess.call("./stop_all.sh")




   
if __name__ == "__main__":
    app.run(host="0.0.0.0")
   
