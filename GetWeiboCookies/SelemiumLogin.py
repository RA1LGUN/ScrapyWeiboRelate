import datetime
import os
import random

import requests
from pymongo.errors import DuplicateKeyError
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver import ActionChains
from selenium.webdriver.support import expected_conditions as EC
import sys
import time
import eventlet
sys.path.append(os.getcwd())
from SelemiumCaptcha import weibo

TEMPLATES_FOLDER = os.getcwd() + '/templates/'

class WeiboLogin():
    def __init__(self, username, password):
        # os.system('pkill -f phantom')
        self.url = 'https://passport.weibo.cn/signin/login?entry=mweibo'
        # self.browser = webdriver.PhantomJS()
        opt = webdriver.ChromeOptions()
        self.proxy = self.get_proxy()
        opt.add_argument("–proxy-server=http://%s" % self.proxy)
        self.browser = webdriver.Chrome(executable_path = 'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chromedriver.exe',chrome_options = opt)
        # self.browser = webdriver.Chrome(
        #     executable_path='C:\\Program Files (x86)\\Google\\Chrome\\Application\\chromedriver.exe')
        # self.browser.set_window_size(1050, 840)
        # self.browser.maximize_window()
        eventlet.monkey_patch()
        self.wait = WebDriverWait(self.browser, 20)
        self.username = username
        self.password = password

    def get_proxy(self):
        proxy_url = requests.get("http://127.0.0.1:5010/get/").json().get("proxy")
        return proxy_url

    def open(self):
        """
        打开网页输入用户名密码并点击
        :return: None
        """
        self.browser.get(self.url)

        time.sleep(random.uniform(2,2.5))
        username = self.wait.until(EC.presence_of_element_located((By.ID, 'loginName')))
        password = self.wait.until(EC.presence_of_element_located((By.ID, 'loginPassword')))
        username.send_keys(self.username)
        password.send_keys(self.password)
        submit = self.browser.find_element_by_xpath('//*[@id="loginAction"]')
        submit.click()
        time.sleep(random.uniform(3,3.5))
        try:
            self.browser.find_element_by_xpath('//*[@id="vdVerify"]/div[1]/div/div/div[4]/span/a').click()
            time.sleep(3)
            self.browser.find_element_by_xpath('//*[@id="vdVerify"]/div[3]/div[2]/div[1]/div/div[2]/div/a').click()
            time.sleep(1)
            captcha = self.browser.find_element_by_xpath('//*[@id="verifyCode"]/div[1]/div/div/div[2]/div/div/div/span[1]/input')
            try:
                try:
                    captcha_submit = self.browser.find_element_by_xpath('//*[@id="verifyCode"]/div[1]/div/div/div[3]/a')
                    wb1 = weibo(self.username, self.password, self.proxy)
                    captcha_code = wb1.run()
                    while not captcha_code:
                        with eventlet.Timeout(80, False):
                            while self.browser.find_element_by_xpath(
                                    '//*[@id="verifyCode"]/div[1]/div/div/div[2]/div/div/div/span[2]').text == '重新发送':
                                time.sleep(random.uniform(1, 2.5))
                                print('retry return code')
                                self.browser.find_element_by_xpath(
                                    '//*[@id="verifyCode"]/div[1]/div/div/div[2]/div/div/div/span[2]/a').click()
                                time.sleep(random.uniform(10, 12.5))
                                captcha_code = wb1.return_unicode()
                            break

                    wb1.closebrowser()
                    captcha.send_keys(captcha_code)
                    captcha_submit.click()
                except:
                    print('weibo.com CAPTCHA bad return')
                time.sleep(random.uniform(4,4.5))
                self.browser.get('https://weibo.cn/pub/')
                time.sleep(random.uniform(2, 2.5))
                cookies = self.browser.get_cookies()
                cookie = [item["name"] + "=" + item["value"] for item in cookies]
                submit_dict = {}
                if len(cookie) > 2.5:
                    submit_dict['cookie'] = cookie
                    submit_dict['uinfo'] = {'uid':self.username,'time':str(datetime.datetime.now()),'check_count':int('0'),'fail_count':int('0')}
                    # cookie['uid'] = self.username
                    # cookie['time'] = datetime.date(2020,3,13).isoformat()
                    self.cookie_to_mongodb(submit_dict)
                    cookie_str = '; '.join(item for item in cookie)
                    print(cookie_str)
                else:
                    print('这个用户未登录成功 ')
                    print(self.username,self.password)
            except:
                print('验证码获取次数已超限，请使用其他方式验证')
                time.sleep(1)

        except:
            print('无法通过私信验证')
            time.sleep(random.uniform(1,1.5))

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
            print('获取cookie成功')
        except pymongo.errors.ServerSelectionTimeoutError:
            sys.exit(u'系统中可能没有安装或启动MongoDB数据库，请先根据系统环境安装或启动MongoDB，再运行程序')



    def run(self):
        """
        破解入口
        :return:
        """
        try:
            self.open()
            self.browser.quit()
        except:
            self.browser.quit()

def get_proxy():
    proxy_url = requests.get("http://127.0.0.1:5010/get/").json().get("proxy")
    return proxy_url

if __name__ == '__main__':
    # 在目录中新建一个account.txt文件，格式需要与account_sample.txt相同
    # 其实就是把www.xiaohao.shop买的账号复制到新建的account.txt文件中

    # username = '18579547823'
    # password = 'cxz123456'
    # proxy = get_proxy()
    # captcha_code = weibo(username,password,proxy).login()
    # print(captcha_code)

    # cookie_str = WeiboLogin(username, password).run()
    # print(cookie_str)


    file_path = os.getcwd() + '\\account.txt'
    with open(file_path, 'r') as f:
        lines = f.readlines()
    # mongo_client = pymongo.MongoClient(LOCAL_MONGO_HOST, LOCAL_MONGO_PORT)
    # collection = mongo_client[DB_NAME]["account"]
    for line in lines:
        line = line.strip()
        username = line.split('----')[0]
        password = line.split('----')[1]
        print('=' * 10 + username + '=' * 10)
        try:
            WeiboLogin(username, password).run()
        except Exception as e:
            print(e)
            continue
        # try:
        #     collection.insert(
        #         {"_id": username, "password": password, "cookie": cookie_str, "status": "success"})
        # except DuplicateKeyError as e:
        #     collection.find_one_and_update({'_id': username}, {'$set': {'cookie': cookie_str, "status": "success"}})

