import json
import random
import re
import sys
import time
from time import sleep

import emojiswitch
import scrapy
from scrapy import signals
from scrapy.spidermiddlewares.httperror import HttpError
from snownlp import SnowNLP
from twisted.internet.error import TimeoutError, DNSLookupError
from harvesttext import HarvestText

from ScrapyWeiboRelate.items import ScrapyWeiboRelateItem

class WeiboSpider(scrapy.Spider):
    name = 'weibo'
    user_id = int('6056282307')
    follow_list = []  # 存储爬取到的所有关注微博的user_id
    follow_name_list = []  # 存储爬取到的所有关注微博的用户名
    fans_list = []  # 存储爬取到的所有粉丝微博的user_id
    fans_name_list = []  # 存储爬取到的所有粉丝微博的用户名
    user = {}           # 存储目标微博用户信息
    followpage = 'https://weibo.cn/%d/follow?page=%d'
    followurl = "https://weibo.cn/%d/follow"
    fanspage = 'https://weibo.cn/%d/fans?page=%d'
    fansurl = "https://weibo.cn/%d/fans"
    infourl = 'https://m.weibo.cn/api/container/getIndex?'
    base_url = 'https://weibo.cn/%d/info'
    further_url = "https://weibo.cn"
    relate_deep = 2
    now_deep = 0
    deepth = 1
    relate_fans_deep = 1
    now_fans_deep = 0
    deepth_fans = 2


    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(WeiboSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signals.spider_closed)
        return spider

    def start_requests(self):
        yield scrapy.Request(url=self.base_url%self.user_id, callback=self.parse_uinfo, priority=11)
        #爬取关注列表
        yield scrapy.Request(url=self.followurl % self.user_id, callback=self.parse_getpage, priority=10,
                             cb_kwargs={'deepth': self.deepth,'id': self.user_id})
        #爬取粉丝列表
        yield scrapy.Request(url=self.fansurl % self.user_id, callback=self.parse_fans_getpage, priority=10,
                             cb_kwargs={'deepth': self.deepth, 'id': self.user_id})

    def parse_getpage(self, response, **kwargs):
        """得到follow/fans的页数"""
        deepth = kwargs['deepth']
        user_id = kwargs['id']
        if response.xpath("//input[@name='mp']") == []:
            page_num = 1
        else:
            page_num = (int)(response.xpath("//input[@name='mp']")[0].attrib['value'])
        print(u'用户关注页数：' + str(page_num))
        page1 = 0
        random_pages = random.randint(1, 5)
        for page in range(1, page_num + 1):
            # get_one_page(page)
            onepageurl = self.followpage % (user_id, page)
            yield scrapy.Request(url=onepageurl,callback=self.parse_onepage, priority=9, cb_kwargs={'deepth': deepth,'uid': user_id})  #改了部分

            if page - page1 == random_pages and page < page_num:
                sleep(random.randint(1, 2))
                page1 = page
                random_pages = random.randint(1, 5)
        print('用户 %d 关注列表爬取完毕'%user_id)

    def parse_onepage(self,response, **kwargs):
        """爬取每一页的follow/fans列表"""
        table_list = response.xpath('//table')
        varuid = kwargs['uid']
        for t in table_list:
            im = t.xpath('.//a/@href')[0].extract()  # 获取uid
            name = t.xpath('.//a/text()')[0].extract()  # 获取用户名
            user_id = im[im.find('u') + 2:]  # 截取uid
            img = t.xpath('.//img/@src').extract()  # 获取图片，如果有两个图片，第二个图片是大V
            people = t.xpath('.//td/text()').extract()[0]  # 获取粉丝数
            num_people = re.search(r'\d+', people).group()

            if user_id.isdigit() and len(img) <= 1 and int(num_people) < 10000:  # 删除大V和粉丝数大于10000的用户
                deepth = kwargs['deepth']

                item = ScrapyWeiboRelateItem()
                item['userid'] = str(varuid)
                item['followuser'] = user_id
                item['deepth'] = deepth
                item['weight'] = 0
                item['crawl_time'] = '1'
                yield item

                deepth += 1
                self.follow_list.append(user_id)

                if deepth <= self.relate_deep:
                    yield scrapy.Request(url=self.followurl % int(user_id), callback=self.parse_getpage, priority=10,
                                         cb_kwargs={'deepth': deepth, 'id': int(user_id)})
                    time.sleep(random.uniform(1, 2))
                    yield scrapy.Request(url=self.fansurl % int(user_id), callback=self.parse_fans_getpage, priority=10,
                                         cb_kwargs={'deepth': self.deepth, 'id': self.user_id})
                yield scrapy.Request(url=self.base_url % int(user_id), callback=self.parse_uinfo, priority=11)
                # yield scrapy.FormRequest(self.infourl, callback=self.parse_userinfo,
                #                          formdata={'containerid': '100505' + str(user_id)} ,dont_filter=True, priority=8,
                #                          cb_kwargs={'id': int(user_id)})

    def parse_fans_getpage(self, response, **kwargs):
        """得到follow/fans的页数"""
        deepth = kwargs['deepth']
        user_id = kwargs['id']
        if response.xpath("//input[@name='mp']") == []:
            page_num = 1
        else:
            page_num = (int)(response.xpath("//input[@name='mp']")[0].attrib['value'])
        print(u'用户粉丝页数：' + str(page_num))
        page1 = 0
        random_pages = random.randint(1, 5)
        for page in range(1, page_num + 1):
            # get_one_page(page)
            onepageurl = self.fanspage % (user_id, page)
            yield scrapy.Request(url=onepageurl,callback=self.parse_fans_onepage, priority=9, cb_kwargs={'deepth': deepth,'uid': user_id})  #改了部分

            if page - page1 == random_pages and page < page_num:
                sleep(random.randint(1, 2))
                page1 = page
                random_pages = random.randint(1, 5)
        print('用户 %d 粉丝列表爬取完毕'%user_id)

    def parse_fans_onepage(self,response, **kwargs):
        """爬取每一页的follow/fans列表"""
        table_list = response.xpath('//table')
        varuid = kwargs['uid']
        for t in table_list:
            im = t.xpath('.//a/@href')[0].extract()  # 获取uid
            name = t.xpath('.//a/text()')[0].extract()  # 获取用户名
            user_id = im[im.find('u') + 2:]  # 截取uid
            img = t.xpath('.//img/@src').extract()  # 获取图片，如果有两个图片，第二个图片是大V
            people = t.xpath('.//td/text()').extract()[0]  # 获取粉丝数
            num_people = re.search(r'\d+', people).group()

            if user_id.isdigit() and len(img) <= 1 and int(num_people) < 10000:  # 删除大V和粉丝数大于10000的用户
                deepth = kwargs['deepth']

                item = ScrapyWeiboRelateItem()
                item['userid'] = user_id
                item['followuser'] = str(varuid)
                item['deepth'] = deepth
                item['weight'] = 0
                item['crawl_time'] = '1'
                yield item

                deepth += 1
                self.fans_list.append(user_id)

                if deepth <= self.relate_fans_deep:
                    yield scrapy.Request(url=self.followurl % int(user_id), callback=self.parse_fans_getpage, priority=10,
                                         cb_kwargs={'deepth': deepth, 'id': int(user_id)})
                    time.sleep(random.uniform(1, 2))
                    yield scrapy.Request(url=self.fansurl % int(user_id), callback=self.parse_getpage, priority=10,
                                         cb_kwargs={'deepth': deepth, 'id': int(user_id)})
                yield scrapy.Request(url=self.base_url % int(user_id), callback=self.parse_uinfo, priority=11)
                # yield scrapy.FormRequest(self.infourl, callback=self.parse_userinfo,
                #                          formdata={'containerid': '100505' + str(user_id)} ,dont_filter=True, priority=8,
                #                          cb_kwargs={'id': int(user_id)})

    def parse_userinfo(self, response, **kwargs):
        """爬取用户详细信息"""
        js = json.loads(response.text)
        if js['ok']:
            info = js['data']['userInfo']

            item = ScrapyWeiboRelateItem()
            item['id'] = kwargs['id']
            item['screen_name'] = info.get('screen_name', '')
            item['gender'] = info.get('gender', '')
            item['statuses_count'] = info.get('statuses_count', 0)
            item['followers_count'] = info.get('followers_count', 0)
            item['follow_count'] = info.get('follow_count', 0)
            item['description'] = info.get('description', '')
            item['profile_url'] = info.get('profile_url', '')
            item['profile_image_url'] = info.get('profile_image_url', '')
            item['avatar_hd'] = info.get('avatar_hd', '')
            item['urank'] = info.get('urank', 0)
            item['mbrank'] = info.get('mbrank', 0)
            item['verified'] = info.get('verified', False)
            item['verified_type'] = info.get('verified_type', 0)
            item['verified_reason'] = info.get('verified_reason', '')
            item['crawl_time'] = '0'

            yield item

    def standardize_info(self, weibo):
        """标准化信息，去除乱码"""
        for k, v in weibo.items():
            if 'int' not in str(type(v)) and 'long' not in str(
                    type(v)) and 'bool' not in str(type(v)):
                weibo[k] = v.replace(u"\u200b", "").encode(
                    sys.stdout.encoding, "ignore").decode(sys.stdout.encoding)
        return weibo

    def parse_uinfo(self, response):
        item  = ScrapyWeiboRelateItem()
        selector = response.xpath('/html')
        item['id'] = re.findall('(\d+)/info', response.url)[0]
        imgurl = selector.xpath('/html/body/div[4]/img/@src').extract()
        try:
            item['src_url'] = imgurl[0]
        except:
            item['src_url'] = 'https: // tvax1.sinaimg.cn / default / images / default_avatar_female_50.gif?KID = imgbed, tva & Expires = 1608232859 & ssig = kqbMa6HGNF'
        user_info_text = ";".join(selector.xpath('body/div[@class="c"]//text()').extract())
        nick_name = re.findall('昵称;?:?(.*?);', user_info_text)
        gender = re.findall('性别;?:?(.*?);', user_info_text)
        place = re.findall('地区;?:?(.*?);', user_info_text)
        brief_introduction = re.findall('简介;?:?(.*?);', user_info_text)
        birthday = re.findall('生日;?:?(.*?);', user_info_text)
        sex_orientation = re.findall('性取向;?:?(.*?);', user_info_text)
        sentiment = re.findall('感情状况;?:?(.*?);', user_info_text)
        vip_level = re.findall('会员等级;?:?(.*?);', user_info_text)
        authentication = re.findall('认证;?:?(.*?);', user_info_text)
        labels = re.findall('标签;?:?(.*?)更多>>', user_info_text)
        if nick_name and nick_name[0]:
            item["nick_name"] = nick_name[0].replace(u"\xa0", "")
        if gender and gender[0]:
            item["gender"] = gender[0].replace(u"\xa0", "")
        if place and place[0]:
            place = place[0].replace(u"\xa0", "").split(" ")
            item["province"] = place[0]
            if len(place) > 1:
                item["city"] = place[1]
        if brief_introduction and brief_introduction[0]:
            item["brief_introduction"] = brief_introduction[0].replace(u"\xa0", "")
        if birthday and birthday[0]:
            item['birthday'] = birthday[0]
        if sex_orientation and sex_orientation[0]:
            if sex_orientation[0].replace(u"\xa0", "") == gender[0]:
                item["sex_orientation"] = "同性恋"
            else:
                item["sex_orientation"] = "异性恋"
        if sentiment and sentiment[0]:
            item["sentiment"] = sentiment[0].replace(u"\xa0", "")
        if vip_level and vip_level[0]:
            item["vip_level"] = vip_level[0].replace(u"\xa0", "")
        if authentication and authentication[0]:
            item["authentication"] = authentication[0].replace(u"\xa0", "")
        if labels and labels[0]:
            item["labels"] = labels[0].replace(u"\xa0", ",").replace(';', '').strip(',')
        request_meta = response.meta
        request_meta['item'] = item
        item['crawl_time'] = '0'
        time.sleep(random.uniform(1, 2))
        yield scrapy.Request(self.further_url + '/u/{}'.format(item['id']),
                      callback=self.parse_further_information,
                      meta=request_meta, dont_filter=True, priority=12)

    def parse_further_information(self, response):

        text = response.text
        item = response.meta['item']

        try:
            user_tweets,at_user,tropic = self.tweet(response.xpath("//div[@class='c']"))
            if type(user_tweets)==list:
                clean_tweet = self.clean_text(user_tweets)
                senti = self.senti_score(clean_tweet)
                try:
                    avg_score = sum(senti) / len(senti)
                except:
                    avg_score = 0
                if at_user:
                    item['at_user'] = at_user
                if tropic:
                    item['tropic'] = tropic
                item['recent_tweet'] = user_tweets
                item['friendly_score'] = avg_score
            else:
                item['friendly_score'] = 0
        except:
            print('SnowNLP Error')

        tweets_num = re.findall('微博\[(\d+)\]', text)
        if tweets_num:
            item['tweets_num'] = int(tweets_num[0])
        follows_num = re.findall('关注\[(\d+)\]', text)
        if follows_num:
            item['follows_num'] = int(follows_num[0])
        fans_num = re.findall('粉丝\[(\d+)\]', text)
        if fans_num:
            item['fans_num'] = int(fans_num[0])
        yield item

    def tweet(self,info):
        is_exist = info[0].xpath("div/span[@class='ctt']")
        if is_exist:
            tweet = []
            at_user = []
            tropic = []
            for i in range(len(info) - 2):
                infos = info[i].xpath('div//text()').extract()
                content = ''
                if self.is_original(info[i]):
                    for i2 in infos:
                        if str(i2).strip():
                            if re.findall(r'@.', str(i2)):
                                at_user.append(str(i2))
                                continue

                            if re.findall(r'#.*#', str(i2)):
                                # print(str(i2))
                                tropic.append(str(i2))

                            content = content + str(i2)
                    content = re.findall(r'(.*)赞\[\d*\]', content)
                    content = content[0].replace('\xa0', '')
                    # content = content.replace('原图', '')
                    # content = content.replace('全文', '')
                    content = content
                else:
                    for i2 in infos[3:]:
                        if str(i2).strip():
                            if re.findall(r'@.', str(i2)):
                                at_user.append(str(i2))
                                continue

                            if re.findall(r'#.*#', str(i2)):
                                tropic.append(str(i2))

                            content = content + str(i2)
                    contentlist = []
                    content1 = re.findall(r'(.*)赞\[\d*\]', content.split('原文评论')[0])
                    content1 = content1[0].replace('\xa0', '')
                    # content1 = content1.replace('原图', '')
                    # content1 = content1.replace('全文', '')
                    content2 = re.findall(r'转发理由:(.*)赞\[\d*\]', content.split('原文评论')[1])
                    content2 = content2[0].replace('\xa0', '')
                    # content2 = content2.replace('原图', '')
                    # content2 = content2.replace('全文', '')
                    contentlist.append(content1)
                    contentlist.append(content2)
                    content = contentlist

                tweet.append(content)
            return tweet,at_user,tropic
        else:
            return 'None','None','None'

    def clean_text(self,origin):
        cltweets = []
        ht = HarvestText()
        for twcl in origin:
            if type(twcl) == list:
                cltwcl = []
                for etwcl in twcl:
                    cltwcl.append(
                        ht.clean_text(emojiswitch.demojize(etwcl, delimiters=("[", "]")), t2s=True, weibo_at=False))
                    # cltweets.append(
                    #     ht.clean_text(emojiswitch.demojize(twcl, delimiters=("[", "]")), t2s=True))
                cltweets.append(cltwcl)
            else:
                cltweets.append(
                    ht.clean_text(emojiswitch.demojize(twcl, delimiters=("[", "]")), t2s=True, weibo_at=False))
                # cltweets.append(
                #     ht.clean_text(emojiswitch.demojize(twcl, delimiters=("[", "]")), t2s=True))
        # print(cltweets)
        return cltweets

    def senti_score(self,tweet):
        sentiscore = []
        for twcl in tweet:
            if type(twcl) == list:
                varlist = []
                for etwcl in twcl:
                    try:
                        varlist.append(SnowNLP(etwcl).sentiments)
                    except:
                        varlist.append(0.5)
                    # print('%s%f' % (etwcl, SnowNLP(etwcl).sentiments))
                try:
                    if etwcl == '转发微博':
                        sentiscore.append(varlist[0])
                    else:
                        if varlist[0] < 0.5:  # 原博是负面的信息
                            if varlist[1] < 0.5:  # 转发是负面的信息    反+反=正
                                sentiscore.append(varlist[0] + varlist[1])
                            else:  # 转发是正面的信息     反+正=反
                                sentiscore.append(varlist[1] - varlist[0])
                        else:  # 原博是正面的
                            if varlist[1] < 0.5:  # 转发是负面的  正+反=反
                                sentiscore.append(varlist[0] - varlist[1])
                            else:  # 转发是正面的  正+正=正
                                sentiscore.append(max(varlist[0], varlist[1]))
                except:
                    sentiscore.append(0.5)
            else:
                sentiscore.append(SnowNLP(twcl).sentiments)
                # print('%s%f' % (twcl, SnowNLP(twcl).sentiments))

        return sentiscore



    def is_original(self, info):
        """判断微博是否为原创微博"""
        is_original = info.xpath("div/span[@class='cmt']")
        if len(is_original) > 3:
            return False
        else:
            return True



    def errback_httpbin(self, failure):
        # log all errback failures,
        # in case you want to do something special for some errors,
        # you may need the failure's type
        self.logger.error(repr(failure))

        # if isinstance(failure.value, HttpError):
        if failure.check(HttpError):
            # you can get the response
            response = failure.value.response
            self.logger.error('HttpError on %s', response.url)

        # elif isinstance(failure.value, DNSLookupError):
        elif failure.check(DNSLookupError):
            # this is the original request
            request = failure.request
            self.logger.error('DNSLookupError on %s', request.url)

        elif failure.check(TimeoutError):
            request = failure.request
            self.logger.error('TimeoutError on %s', request.url)

    def spider_closed(self):
        print(self.follow_list)
