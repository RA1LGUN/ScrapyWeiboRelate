import datetime
import re
import sys

import pymongo
import requests
from fake_useragent import UserAgent

infopage = 'https://weibo.cn/%s/info'

DEFAULT_REQUEST_HEADERS = {
'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
'accept-encoding': 'gzip, deflate, br',
'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-US;q=0.7',
'cache-control': 'max-age=0',
'upgrade-insecure-requests': '1',
'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36 Edg/87.0.664.41'}

class CheckCookies():
    def __init__(self,dbname,cookiesdbname = "cookie",cookiescollection = "cookie"):
        self.dbname = dbname
        self.cookiesdbname = cookiesdbname
        self.cookiescollection = cookiescollection

    def testurl(self):
        myclient = pymongo.MongoClient("mongodb://localhost:27017/")
        db = myclient[self.dbname]["user"]
        user_data = list(db.aggregate([{ '$sample': { 'size': 1 } }]))
        uid = user_data[0]['id']
        testurl = infopage % uid
        return testurl

    def get_proxy_local(self):
        x = requests.get("http://127.0.0.1:5010/get/").json()
        proxies = {
            'http': x['proxy']
        }
        return proxies

    def main(self):
        myclient = pymongo.MongoClient("mongodb://localhost:27017/")
        db = myclient.cookies
        db2 = myclient["cookies"]["fail"]
        collection = db.weibo
        for item in collection.find():
            cookiedict = {}
            for items in item["cookie"]["cookie"]:
                y = items.split('=')
                cookiedict[y[0]] = y[1]

            testurl = self.testurl()
            proxies = self.get_proxy_local()
            DEFAULT_REQUEST_HEADERS['user-agent'] = UserAgent(verify_ssl=False).random
            r = requests.get(testurl, headers=DEFAULT_REQUEST_HEADERS, proxies=proxies, cookies=cookiedict)
            print(r.status_code)
            print(item['cookie']['uinfo']['uid'])
            content = r.content.decode(sys.stdout.encoding,"ignore")
            if re.findall('昵称;?:?(.*?);', content):
                print(re.findall('昵称;?:?(.*?);', content))
            else:
                item['cookie']['uinfo']['check_count'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                item['cookie']['uinfo']['fail_count'] = item['cookie']['uinfo']['fail_count'] +1
                db2.insert_one(item)
                db.weibo.delete_one({'cookie.uinfo.uid': item['cookie']['uinfo']['uid']})
                print('delete %s'%item['cookie']['uinfo']['uid'])

if __name__ == '__main__':
    check = CheckCookies('weibo4')
    check.main()