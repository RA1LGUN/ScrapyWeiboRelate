# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ScrapyWeiboRelateItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()

    crawl_time = scrapy.Field()           #时间戳及标记

    id = scrapy.Field()  # 用户ID
    nick_name = scrapy.Field()  # 昵称
    gender = scrapy.Field()  # 性别
    province = scrapy.Field()  # 所在省
    city = scrapy.Field()  # 所在城市
    src_url = scrapy.Field()  #头像URL
    brief_introduction = scrapy.Field()  # 简介
    birthday = scrapy.Field()  # 生日
    tweets_num = scrapy.Field()  # 微博数
    follows_num = scrapy.Field()  # 关注数
    fans_num = scrapy.Field()  # 粉丝数
    sex_orientation = scrapy.Field()  # 性取向
    sentiment = scrapy.Field()  # 感情状况
    vip_level = scrapy.Field()  # 会员等级
    authentication = scrapy.Field()  # 认证
    person_url = scrapy.Field()  # 首页链接
    at_user = scrapy.Field()    #@到的用户
    tropic = scrapy.Field()     #微博话题
    friendly_score = scrapy.Field() #友善度
    recent_tweet = scrapy.Field() #近期微博
    labels = scrapy.Field()  # 标签


    userid = scrapy.Field()
    followuser = scrapy.Field()
    deepth = scrapy.Field()
    weight = scrapy.Field()

    # pass

class WeiboContentItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()

    user_id = scrapy.Field()           #时间戳及标记
    screen_name = scrapy.Field()
    id = scrapy.Field()
    bid = scrapy.Field()
    text = scrapy.Field()
    location = scrapy.Field()
    created_at = scrapy.Field()
    source = scrapy.Field()
    attitudes_count = scrapy.Field()
    comments_count = scrapy.Field()
    reposts_count = scrapy.Field()
    topics = scrapy.Field()
    at_users = scrapy.Field()

