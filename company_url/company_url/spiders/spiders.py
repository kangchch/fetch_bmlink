#! coding: utf-8

import requests
import os
import pymongo
from pymongo import MongoClient
import datetime
import logging
import scrapy
import re
import time
import traceback
from scrapy import log
import sys
from scrapy.conf import settings
from company_url.items import CompanyUrlItem
from scrapy.selector import Selector
from lxml import etree
from ipdb import set_trace


reload(sys)
sys.setdefaultencoding('utf-8')

class CompanyUrlSpider(scrapy.Spider):
    name = "spider"

    def __init__(self, settings, *args, **kwargs):
        super(CompanyUrlSpider, self).__init__(*args, **kwargs)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def start_requests(self):
        try:
            for page in range(1, 1242):
                start_url = 'http://www.bmlink.com/newjoin/%d/' % (page)
                meta = {'dont_redirect': True, 'dont_retry': True}
                yield scrapy.Request(url=start_url, meta=meta, callback=self.parse, dont_filter=True)
        except:
            self.log('start_request error! (%s)' % (str(traceback.format_exc())), level=log.INFO)

    ##遍历公司解析公司网址
    def parse(self, response):
        sel = Selector(response)

        if response.status != 200:
            self.log('fetch failed! status=%d' % (response.status), level=log.WARNING)

        i = CompanyUrlItem()
        urls = sel.xpath("//ul[@class='list all']/li/a")
        for url in urls:
            i['url'] = url.xpath("@href")[0].extract()
            self.log('fetch succsed! url=%s' % (i['url']), level=log.INFO)

            yield i


