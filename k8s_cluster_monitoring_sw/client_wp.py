import requests
import time
import subprocess

def client_wp(cnt_client):
    print(cnt_client)
    #url = 'http://203.237.53.208:31118/wp-admin'
    #headers = {'Content-Type': 'application/json; charset=utf-8'}
    cmd ="siege -c%s -t10S http://127.0.0.1:31118" % (cnt_client)
    subprocess.call([cmd], shell=True)


