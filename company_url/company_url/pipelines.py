# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo
import datetime
from scrapy import log
from scrapy.conf import settings

class CompanyUrlPipeline(object):

    def __init__(self, settings):
        self.settings = settings

    @classmethod
    def from_crawler(cls, crawler):
        return cls(settings=crawler.settings)

    def open_spider(self, spider):
        mongo_info = settings.get('MONGO_INFO', {})
        self.mongo_db = pymongo.MongoClient(mongo_info['host'], mongo_info['port']).bmlink_info

    def close_spider(self, spider):
        pass

    def process_item(self, item, spider):
        #insert mongo
        url = item['url']
        try:
            self.mongo_db.company_url.insert_one(
                {
                    'url': url,
                    'status': 0,
                    'insert_time': datetime.datetime.now()
                }
            )
        except pymongo.errors.DuplicateKeyError:
            spider.log('url is exist! url=%s' % (url), level=log.ERROR)
            pass
        except Exception, e:
            spider.log('insert mongo failed! url=%s (%s)' % (url, str(e)), level=log.ERROR)

        spider.log('piplines insert mongo succed. url:%s' % (url), level=log.INFO)
