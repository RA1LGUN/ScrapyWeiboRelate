# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import datetime

import pymongo
from itemadapter import ItemAdapter
from .items import ScrapyWeiboRelateItem,WeiboContentItem


class ScrapyWeiboRelatePipeline():

    collection_name = 'scrapy_items'

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'items')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def process_item(self, item, spider):
        if type(item)==ScrapyWeiboRelateItem:
            if item['crawl_time'] == '0':               #再加一层判断  UID都为10位数
                if len(item['id']) == 10:
                    if not self.db['user'].count_documents({'id': item['id']}):
                        item['crawl_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        self.db['user'].insert_one(ItemAdapter(item).asdict())
                        print('已插入%s的数据'%str(item['id']))
                    else:
                        print("%s 已存在表中" % str(item['id']))
                else:
                    print(item['id'])

            elif item['crawl_time'] == '1':
                if len(item['userid']) == len(item['followuser']) == 10:
                    if not self.db['relate'].count_documents({'userid': item['userid'], 'followuser': item['followuser']}):     #如果不在数据库中就添加
                        item['crawl_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        self.db['relate'].insert_one(ItemAdapter(item).asdict())
                        print('已插入%s的数据'%str(item['userid']))
                    elif self.db['relate'].find_one({'userid': item['userid'], 'followuser': item['followuser']})['deepth'] > item['deepth']:   #如果在数据库中，切数据库中的深度大于现在的深度，则替换为较小深度
                        findrelatedic,updaterelatedic = {}
                        findrelatedic = {'userid': item['userid'], 'followuser': item['followuser']}
                        updaterelatedic = {"$set":{'deepth':item['deepth']}}
                        self.db['relate'].update(findrelatedic,updaterelatedic)
                        print('更新了他俩的关系')
                    else:
                        print("%d 与 %d 已有更亲密关系" % (int(item['userid']),int(item['followuser']),))
                else:
                    print(item['userid'],item['followuser'])

        return item

    def close_spider(self, spider):
        self.client.close()