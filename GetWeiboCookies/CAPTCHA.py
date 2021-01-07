# -*- coding: utf-8 -*-
# coding by Mutu
# -*- 2020-11-23 20:19:12.928097 -*-
import json
import sys

import requests,re
import rsa,time,base64
from fake_useragent import UserAgent
from binascii import b2a_hex

class weibo():
    def __init__(self, username, password,proxy):
        self.session = requests.Session()
        headers = {
            # 'Host': 'login.sina.com.cn',
            'Referer': 'http://my.sina.com.cn/',
            'User-Agent': UserAgent(verify_ssl=False).random
        }
        self.session.headers.update(headers)
        # proxy = self.get_proxy()
        self.session.proxies = proxy
        self.username = username
        self.password = password

    def get_proxy(self):
        proxy_url = requests.get("http://127.0.0.1:5010/get/").json().get("proxy")
        proxy_dict = {"http":proxy_url}
        return proxy_dict


    def get_sp(self, pubkey, servertime, nonce):
        '''
        获取sp值
        :param pubkey:
        :param servertime:
        :param nonce:
        :return:
        '''
        publickey = rsa.PublicKey(int(pubkey, 16), int('10001', 16))
        message = str(servertime) + '\t' + str(nonce) + '\n' + str(self.password)
        sp = b2a_hex(rsa.encrypt(message.encode(), publickey))
        return sp

    def login(self):
        '''
        登录请求
        :return:
        '''
        pre_login = 'https://login.sina.com.cn/sso/prelogin.php'
        su = base64.b64encode(self.username.encode()).decode()
        params = {
            'entry': 'account',
            'su': su,
            'rsakt': 'mod',
            'checkpin': 1,
            'client': 'ssologin.js(v1.4.19)',
            '_': str(int(time.time()) * 1000),
        }
        data = self.session.get(pre_login, params=params).json()
        # print(data)
        # input("==")
        nonce = data.get('nonce', '')
        pubkey = data.get('pubkey', '')
        rsakv = data.get('rsakv', '')
        servertime = data.get('servertime', '')

        # 验证码参数
        showpin = data.get("showpin", "")
        pcid = data.get("pcid", "")

        #获取加密后的密码
        sp = self.get_sp(pubkey, servertime, nonce)

        url = f"https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.19)&_={int(time.time() * 1000)}"
        data_post = {
            "entry": "account",
            "gateway": 1,
            "from": "",
            "savestate": 0,# 30
            "qrcode_flag": True,
            "useticket": 0,
            "pagerefer": "http://my.sina.com.cn/profile/logined",#
            "vsnf": 1,
            "su": base64.b64encode(self.username.encode("UTF-8")).decode("UTF-8"),
            "service": "sso",
            "servertime": servertime,
            "nonce": nonce,
            "pwencode": "rsa2",
            "rsakv": rsakv,
            "sp": sp,
            "sr": "1920*1080",
            "encoding": "UTF-8",
            "cdult": 3,
            "domain": "sina.com.cn",
            "prelt": 44,
            "returntype": "TEXT",
            "pcid":pcid,
        }
        # print(showpin)
        if showpin:#   1：有验证码
            captcha = self.dealwith(url,pcid,data_post)
            return captcha

        else:#         0：没有验证码
            res = self.session.post(url, data=data_post)
            if res.json()["retcode"]=="0":
                ticket_url = res.json()['crossDomainUrlList'][0]
                print("已登录用户：{}".format(res.json().get("nick")))
                captcha = self.login_cn()
                return captcha
            else:
                msg = res.json()["reason"]
                return "无验证码："+msg,res.json()["retcode"],res.json().get("nick")

    def dealwith(self,url,pcid,data_post):
        '''
        需要验证码账户处理函数
        :param url:
        :param pcid:
        :param data_post:
        :return:
        '''
        door = self.get_pic(pcid)
        data_post["pcid"] = pcid
        data_post["door"] = door.strip()  ## door的准确性

        res = self.session.post(url, data=data_post)
        print(res.json())
        print(res.json()['retcode'])
        if res.json()['retcode'] == "0":  # <retcode=0>表示登录成功
            print("已登录用户：{}".format(res.json().get("nick")))
            captcha = self.login_cn()
            return captcha
        elif res.json()['retcode'] == "2070":
            print(res.json()["reason"])
            print("重新输入")
            time.sleep(1)
            return self.dealwith(url, pcid, data_post)
        else:
            msg = res.json()["reason"]
            print("未知错误:",msg)
            return msg,res.json()["retcode"],""

    def get_pic(self,pcid):
        '''
        获取验证码图片
        :param pcid:
        :return:
        '''
        pic_url = "https://login.sina.com.cn/cgi/pin.php"#?r=21611665&s=0&p=yf-d45933a1b0467026f90bf3f9543cd8c86807
        params = {
            'r': 21611665,
            's': 0,
            'p': pcid

        }
        resp = self.session.get(pic_url,params=params).content
        with open("pic.png", "wb") as f:
            f.write(resp)
        words=self.get_ai_words(uname='RA1LGUN', pwd='cjc123456', img='pic.png')
        return words

    def get_ai_words(self,uname, pwd,  img):

        with open(img, 'rb') as f:
            base64_data = base64.b64encode(f.read())
            b64 = base64_data.decode()
        data = {"username": uname, "password": pwd, "image": b64}
        result = json.loads(requests.post("http://api.ttshitu.com/base64", json=data).text)
        if result['success']:
            return result["data"]["result"]
        else:
            return result["message"]
        return ""

    def get_words(self,pic):
        '''
        调用百度云ocr识别验证码
        :param pic:图片文件
        :return:
        '''
        url = "https://cloud.baidu.com/aidemo"
        with open(pic, 'rb') as f:
            base64_data = base64.b64encode(f.read())
            s = base64_data.decode()
            print(s)
        params = {
            'image': 'data:image/png;base64,' + s,
            'type': 'https://aip.baidubce.com/rest/2.0/ocr/v1/accurate_basic',
            'detect_direction': 'false',
        }

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36",
            # "Content-Type": "application/x-www-form-urlencoded",
        }
        resp = requests.post(url, data=params, headers=headers)
        print(resp.json())
        if resp.json()["data"]["words_result"]:
            if resp.json()['errno']:
                print("ocr识别请求错误")
            else:
                words = resp.json()["data"]["words_result"][0]["words"]
                # input("==")
                return words
        else:
            return "get_words have something problem"

    def cookie_to_mongodb(self,cookie_dic):
        """将爬取的信息写入MongoDB数据库"""
        try:
            import pymongo
        except ImportError:
            sys.exit(u'系统中可能没有安装pymongo库，请先运行 pip install pymongo ，再运行程序')
        try:
            from pymongo import MongoClient

            client = MongoClient("mongodb://localhost:27017/")
            db = client['cookies']
            collection = db['weibo']

            insert_info = {'cookie': cookie_dic}
            collection.insert_one(insert_info)
        except pymongo.errors.ServerSelectionTimeoutError:
            sys.exit(u'系统中可能没有安装或启动MongoDB数据库，请先根据系统环境安装或启动MongoDB，再运行程序')

    def login_cn(self):
        params = {
            'checkpin': 1,
            'entry': 'mweibo',
            'su': base64.b64encode(self.username.encode()).decode(),
            # 'callback': 'jsonpcallback1606628658879',
        }
        pre_url = "https://login.sina.com.cn/sso/prelogin.php"
        pre_resp = self.session.get(pre_url,params=params)

        pre_data = pre_resp.json()
        showpin = pre_data.get('showpin', '')
        # 登录提交表单
        login_url = "https://passport.weibo.cn/sso/login"
        data = {
            'username': self.username,
            'password': self.password,
            'savestate': 1,
            'r': 'https://weibo.cn/',
            'ec': 0,
            'pagerefer': 'https://weibo.cn/',
            'entry': 'mweibo',
            'wentry': '',
            'loginfrom': '',
            'client_id': '',
            'code': '',
            'qq': '',
            'mainpageflag': 1,
            'hff': '',
            'hfp': ''

        }
        self.session.post(login_url,data=data)
        # print("showpin:",showpin)
        # 发送验证码
        msg_url = "https://passport.weibo.cn/signin/secondverify/ajsend?msg_type=private_msg"
        self.session.get(msg_url)
        time.sleep(3)
        # 获取验证码weibo.com

        com_msg_url2 = "https://api.weibo.com/webim/2/direct_messages/conversation.json"
        params2 = {
            'convert_emoji': 1,
            'count': 15,
            'max_id': 0,
            'uid': 2735327001,#音数p越社文
            'is_include_group': 0,
            'source': 209678993,
            't': str(time.time() * 1000),
        }
        cookie_list = []
        for item in self.session.cookies.items():
            one = item[0] + "=" + item[1]
            cookie_list.append(one)
        cookie = ";".join(cookie_list)
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Host': 'api.weibo.com',
            # 'Pragma': 'no-cache',
            'Referer': 'https://api.weibo.com/chat/',
            'cookie': cookie,
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36',
            'special_source': '3',
            'add_virtual_user': '3,4',
            'is_include_group': '0',
            'need_back': '0,0',
            'count': '80',
            'source': '209678993',
            't': str(time.time() * 1000),
        }
        self.session.headers.update(headers)
        res_msg = self.session.get(com_msg_url2, params=params2)
        res_msg.encoding = "utf-8"
        # print(res_msg.json())
        # print(res_msg.text)
        msg_id_ = re.findall("验证码：(.*?)，仅用于登录你的微博帐号，30分钟内有效。",res_msg.text)
        print(msg_id_)
        msg_id = msg_id_[0]
        return msg_id
