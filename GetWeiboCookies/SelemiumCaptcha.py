import base64
import datetime
import json
import os
import random
import re

import requests
from pymongo.errors import DuplicateKeyError
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from fake_useragent import UserAgent
import sys
import time
sys.path.append(os.getcwd())
from CAPTCHA import weibo

class weibo():
    def __init__(self, username, password,proxy):
        self.username = username
        self.password = password
        self.url = 'https://gongyi.sina.com.cn/'
        self.wburl = 'https://weibo.com/'
        self.codeurl = 'https://api.weibo.com/chat/#/chat'
        opt = webdriver.ChromeOptions()
        opt.add_argument("–proxy-server=http://%s" % proxy)
        self.browser = webdriver.Chrome(
            executable_path='C:\\Program Files (x86)\\Google\\Chrome\\Application\\chromedriver.exe',
            chrome_options=opt)
        self.wait = WebDriverWait(self.browser, 20)
        self.browser.maximize_window()
        self.browser.get(self.url)

    def run(self):
        self.CAPTCHA()
        while not self.isLogin():
            self.CAPTCHA()
            print('登陆失败')
            time.sleep(random.uniform(2, 2.5))
        self.browser.get(self.wburl)  # 已登录weibo.com
        time.sleep(random.uniform(2, 3))
        self.browser.get(self.codeurl)
        time.sleep(random.uniform(5, 7))
        return_code = self.return_unicode()
        return return_code



    def CAPTCHA(self):
        time.sleep(random.uniform(2, 2.5))
        self.browser.find_element_by_xpath('//*[@id="SI_User"]/div[2]/div/a').click()
        time.sleep(random.uniform(0.5, 1.2))

        username = self.browser.find_element_by_xpath('//*[@id="SI_User"]/div[3]/div[2]/ul/li[2]/input')
        password = self.browser.find_element_by_xpath('//*[@id="SI_User"]/div[3]/div[2]/ul/li[3]/input')
        username.send_keys(self.username)
        password.send_keys(self.password)
        time.sleep(random.uniform(2, 2.5))

        try:
            word = self.get_code()
            code = self.browser.find_element_by_xpath('//*[@id="SI_User"]/div[3]/div[2]/ul/li[4]/input')
            code.send_keys(word)
            time.sleep(random.uniform(2, 2.5))
            self.browser.find_element_by_xpath('//*[@id="SI_User"]/div[3]/div[2]/ul/li[6]/span/a').click()
            time.sleep(random.uniform(3, 3.5))

            try:
                x = str(self.browser.find_element_by_xpath('//*[@id="SI_User"]/div[3]/div[2]/p').text)
                while len(x):
                    word = self.get_code()
                    code.send_keys(word)
                    time.sleep(random.uniform(2, 2.5))
                    self.browser.find_element_by_xpath('//*[@id="SI_User"]/div[3]/div[2]/ul/li[6]/span/a').click()
                    time.sleep(random.uniform(5, 5.5))
                    x = str(self.browser.find_element_by_xpath('//*[@id="SI_User"]/div[3]/div[2]/p').text)
            except:
                print('Done')
                pass
        except:
            self.browser.find_element_by_xpath('//*[@id="SI_User"]/div[3]/div[2]/ul/li[6]/span/a').click()
            time.sleep(random.uniform(5, 5.5))


    def isLogin(self):
        try:
            ActionChains(self.browser).move_to_element(
                self.browser.find_element_by_xpath('//*[@id="SI_User"]/div[2]/div/a')).perform()
            print('登陆成功')
            return True

        except:
            return False

    def get_code(self):
        nodes = self.browser.find_element_by_xpath('//*[@id="SI_User"]/div[3]/div[2]/ul/li[4]/img')
        nodes.screenshot('test.png')
        return self.get_ai_words(uname='RA1LGUN', pwd='cjc123456', img='test.png')

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

    def return_unicode(self):
        self.browser.get(self.codeurl)
        time.sleep(random.uniform(5, 5.5))
        items = self.browser.find_element_by_xpath('//*[@id="app"]/div/div/div[1]/div[3]/div/div[1]/div/div/ul')
        li = items.find_elements_by_tag_name("li")
        for i in range(len(li)):
            try:
                if re.findall('微博安全中心', li[i].text):
                    print('ok')
                    time.sleep(random.uniform(4, 5.5))
                    li[i].click()
                    time.sleep(random.uniform(4, 5.5))
                    infos = self.browser.find_element_by_xpath('//*[@id="drag-area"]/div/div[1]/div[2]/div[2]/div[1]/div/ul')
                    oneinfo = infos.find_elements_by_tag_name("li")
                    try:
                        for y in range(1,5):
                            LoginCode = re.findall('验证码：([0-9]{6})', oneinfo[-y].text)
                            print(LoginCode)
                            if LoginCode:
                                return LoginCode
                    except:
                        print('Read Done')
                        return ''
            except:
                print('None Centre')
                return ''

    def return_code(self):
        print('return_code')
        self.browser.get(self.codeurl)
        time.sleep(random.uniform(5, 5.5))
        try:
            items = self.browser.find_element_by_xpath('//*[@id="app"]/div/div/div[1]/div[3]/div/div[1]/div/div/ul')
            LoginCode = re.findall('验证码：([0-9]{6})', items.text)
            if LoginCode:
                return LoginCode[0]
            else:
                return ''
        except:
            return ''

    def closebrowser(self):
        self.browser.quit()



if __name__ == '__main__':
    username = '16563377754'
    password = 'zxc123456'
    proxy_url = requests.get("http://127.0.0.1:5010/get/").json().get("proxy")
    x = weibo(username,password,proxy_url)
    code = x.run()
    time.sleep(random.uniform(2, 4.5))
    x.closebrowser()
    print(code)
