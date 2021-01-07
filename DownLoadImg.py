import os
import re

import pymongo
import requests
from fake_useragent import UserAgent

DEFAULT_REQUEST_HEADERS = {
'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
'accept-encoding': 'gzip, deflate, br',
'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-US;q=0.7',
'cache-control': 'max-age=0',
'upgrade-insecure-requests': '1',
'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36 Edg/87.0.664.41'}
# dic_path = r'Test/Test/img/%s.%s'

DEFAULT_URL = 'https://tvax1.sinaimg.cn/default/images/default_avatar_female_50.gif?KID=imgbed,tva&Expires=1608232859&ssig=kqbMa6HGNF'

class downloadimg():

    def __init__(self,dbname,dic_path):
        self.myclient = pymongo.MongoClient("mongodb://localhost:27017/")
        self.db = self.myclient[dbname]['user']
        self.img_path = dic_path + '/%s.%s'
        self.dic_path = dic_path

    def get_proxy_local(self):
        x = requests.get("http://127.0.0.1:5010/get/").json()
        proxies = {
            'http': x['proxy']
        }
        return proxies

    def run(self):
        for item in self.db.find():
            # print(item['src_url'])
            proxies = self.get_proxy_local()
            DEFAULT_REQUEST_HEADERS['user-agent'] = UserAgent(verify_ssl=False).random
            if bool(re.findall(r'[0-9]{3}/(.+.jpg)',item['src_url'])):
                jpg_path = self.img_path %(item['src_url'][-10:].replace('%','PC'),'jpg')
                r = requests.get(item['src_url'], headers=DEFAULT_REQUEST_HEADERS, proxies=proxies)
                print(jpg_path)
                with open(jpg_path, 'wb') as f:
                    f.write(r.content)
            elif bool(re.findall(r'/images/(.+.gif)',item['src_url'])):
                gif_path = self.img_path %(item['src_url'][-10:].replace('%','PC'),'gif')
                r = requests.get(item['src_url'], headers=DEFAULT_REQUEST_HEADERS, proxies=proxies)
                with open(gif_path, 'wb') as f:
                    f.write(r.content)

        proxies = self.get_proxy_local()
        DEFAULT_REQUEST_HEADERS['user-agent'] = UserAgent(verify_ssl=False).random
        DEFAULT_PATH = self.img_path %(DEFAULT_URL[-10:].replace('%','PC'),'gif')
        r = requests.get(DEFAULT_URL, headers=DEFAULT_REQUEST_HEADERS, proxies=proxies)
        with open(DEFAULT_PATH, 'wb') as f:
            f.write(r.content)

    def replace_img(self):
        fileList = os.listdir(self.dic_path)
        for i in fileList:
            oldname = self.dic_path + os.sep + i
            newname = self.dic_path + os.sep + i.replace('%','PC')
            os.rename(oldname, newname)
            print(oldname, '======>', newname)


# if __name__ == '__main__':
#     di = downloadimg('weibo9',dic_path = r'Test/Test/img')
#     di.run()
#     di.replace_img()