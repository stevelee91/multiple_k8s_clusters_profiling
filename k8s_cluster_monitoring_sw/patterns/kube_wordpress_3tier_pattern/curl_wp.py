import requests

def curl_wp(cnt_curl):
    for i in range(0, cnt_curl):
        response = requests.get('http://localhost:31118/wp-admin')
        print(response)


