# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html
import re
from logging import exception

from fake_useragent import UserAgent
from scrapy import signals

from ScrapyWeiboRelate.get_cookies import get_cookies, delete_cookies
from ScrapyWeiboRelate.proxy_handle import get_proxy_local,delete_proxy_local
from twisted.internet.error import TimeoutError
# useful for handling different item types with a single interface


class ScrapyWeiboRelateSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class ScrapyWeiboRelateDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    def cookie_reform(self,cookie):
        cookies_dict = {}
        for data in cookie:
            key = data.split('=', 1)[0]  # (以'='切割，1为切割1次)
            value = data.split('=', 1)[1]
            cookies_dict[key] = value
        return cookies_dict

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s




    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.
        ua = UserAgent(verify_ssl=False).random
        # ua = random.choice(settings.USER_AGENT_LIST)
        request.headers['User-Agent'] = ua


        # mycookie = random.choice(settings.Cookie_list)
        # request.cookies = self.cookie_reform(mycookie.split('; '))
        cookie,origin_cookie = get_cookies()
        # print(cookie[0]["cookie"])
        request.cookies = cookie
        # print('添加Cookies : ' + mycookie.split('; ')[-1])

        # request.cookies = settings.Cookie_list

        proxy = "http://" + str(get_proxy_local().get("proxy"))
        request.meta['download_timeout'] = 10
        request.meta["proxy"] = proxy
        print('为 %s 添加代理 %s 及cookies %s' % (request.url, proxy ,cookie['SSOLoginState']))
        if re.findall(r'login.sina',request.url):
            delete_cookies(origin_cookie)
        # print('为 %s 添加代理 %s 及cookies %s' % (request.url, proxy ,mycookie.split('; ')[-1]))

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        print('状态码', response.status)
        if isinstance(exception, TimeoutError):
            print('TimeoutError')
            return request
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain

        print('代理%s，访问%s出现异常:%s' % (request.meta['proxy'], request.url, exception))
        import time
        time.sleep(5)
        delete_proxy_local(request.meta['proxy'].split("//")[-1])
        request.meta['proxy'] = 'http://' + str(get_proxy_local().get("proxy"))

        # return request
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)
