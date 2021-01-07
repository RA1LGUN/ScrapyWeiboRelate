import json
import requests
import random

ip_pool = []

def get_proxy_local():
    return requests.get("http://127.0.0.1:5010/get/").json()

def get_proxy():
    ip_list = get_ip_pool()
    result = random.choice(ip_list)
    # print(result, type(result))
    return result

def get_ip_pool():
    response = requests.get(
        'http://webapi.http.zhimacangku.com/getip?num=10&type=2&pro=&city=0&yys=0&port=1&time=1&ts=0&ys=0&cs=0&lb=1&sb=0&pb=4&mr=1&regions='
        # 'http://127.0.0.1:5010/get/'
    ).content
    user_dic = json.loads(response)
    for i in user_dic['data']:
        ip_pool.append(str(i['ip']) + ':' + str(i['port']))
    return ip_pool

def delete_proxy(proxy):
    ip_pool.remove(proxy)
    # print(ip_pool)
    # requests.get("http://127.0.0.1:5010/delete/?proxy={}".format(proxy))

def delete_proxy_local(proxy):
    requests.get("http://127.0.0.1:5010/delete/?proxy={}".format(proxy))