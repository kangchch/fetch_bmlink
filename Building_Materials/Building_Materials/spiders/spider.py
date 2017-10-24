# -*- coding: utf-8 -*-
from scrapy.http import Request
import xml.etree.ElementTree
from scrapy.selector import Selector

import scrapy
import re
from pymongo import MongoClient
from copy import copy
import traceback
import pymongo
import cx_Oracle
from scrapy import log
from Building_Materials.items import BuildingMaterialsItem
import time
import datetime
import sys
import logging
import random
import binascii
from scrapy.conf import settings
import json

reload(sys)
sys.setdefaultencoding('utf-8')


class BuildingMaterialSpider(scrapy.Spider):
    name = ""

    def __init__(self, settings, *args, **kwargs):
        super(BuildingMaterialSpider, self).__init__(*args, **kwargs)
        self.settings = settings

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def start_requests(self):
        try:
            item = BuildingMaterialsItem()
            item['status'] = 0
            start_url = 'http://www.bmlink.com/company/'
            meta = {'dont_redirect': True, 'item': item, 'dont_retry': True}
            yield scrapy.Request(
                    url = start_url,
                    meta = meta,
                    callback = self.parse,
                    dont_filter = True)

        except:
            self.log('start_request error! (%s)' % (str(traceback.format_exc())), level=log.INFO)

    #解析页面的三个类目(陶瓷,橡胶塑料,精细化工)
    def parse(self, response):
        i = response.meta['item']
        i['status'] = response.status
        sel = Selector(response)

        if i['status'] != 200:
            self.log('fetch failed ! status = %d' % (i['status']), level = log.WARNING)

        classify_xpaths = sel.xpath('//div[@class="itemcell"]/h2/a/@href').extract()
        for url in classify_xpaths:
            next_url = ''.join(['http://www.bmlink.com', url])
            meta = {'dont_redirect': True, 'item': i, 'dont_retry': True}
            self.log('next_url=%s' % (next_url), level=log.INFO)
            yield scrapy.Request(
                    url = next_url,
                    meta = meta,
                    callback = self.parse_list_page,
                    dont_filter = True)

    '''
        u'公司名称': 'company_name'
        u'主营产品': 'mainpro'
        u'所在地区': 'area'
        u'经营方式': 'tYpe'
    '''
    #解析分页
    def parse_list_page(self, response):
        sel = Selector(response)

        info_xpaths = sel.xpath('//li/div[@class="info"]')
        for each in info_xpaths:
            company_name = each.xpath("p[@class='company']/a/text()").extract()[0]
            mainpro = each.xpath("div[@class='mainPro']/p/text()").extract()[0]
            area = each.xpath("div[@class='area']/p/text()").extract()[0]
            tYpe = each.xpath("div[@class='type']/p/text()").extract()[0]
            company_url_xpaths = each.xpath("p[@class='company']/a")
            for url in company_url_xpaths:
                company_url = url.xpath("@href").extract()[0]
                meta = {'dont_redirect':True, 'dont_retry': True, 'company_name': company_name,
                        'mainpro': mainpro, 'area': area, 'tYpe': tYpe}
                self.log('company=%s, mainpro=%s, area=%s, tYpe=%s, url=%s' %
                        (company_name, mainpro, area, tYpe), level=log.INFO)
                yield scrapy.Request(
                        url = (company_url + 'contact'),
                        meta = meta,
                        callback = self.parse_company_page,
                        dont_filter = True
                        )

    '''
        u'联系人': 'contacter'
        u'手机': 'mp'
        u'电话': 'telephone'
        u'传真': 'fax'
        u'邮编': 'zipcode'
        u'地址': 'address'
        u'网址': 'url_from'
        u'部门': 'duty'
    '''
    #解析公司联系我们页面
    def parse_company_page(self, response):
        sel = Selector(response)

        address = sel.xpath("//dt[@class='area']/text()").extract()
        if address:
            address = re.findall(u'(?<=地址:).*')



























