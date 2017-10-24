
# -*- coding: utf-8 -*-
##
# @file fetch_bmlink.py
# @brief scrapy company info
# @author kangchch
# @version 1.0
# @date 2017-10-23

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
    name = "bmlink"

    def __init__(self, settings, *args, **kwargs):
        super(BuildingMaterialSpider, self).__init__(*args, **kwargs)
        self.settings = settings
        mongo_info = settings.get('MONGO_INFO', {})

        try:
            self.mongo_db = pymongo.MongoClient(mongo_info['host'], mongo_info['port']).bmlink_info
        except Exception, e:
            self.log('connect mongo 192.168.60.65:10010 failed! (%s)' % (str(e)), level=log.CRITICAL)
            raise scrapy.exceptions.CloseSpider('initialization mongo error (%s)' % (str(e)))

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def start_requests(self):

        try:
            records = self.mongo_db.company_url.find({'status': 0}, {'url': 1})
            for record in records:
                company_url = record['url']
                next_url = ''.join([company_url, '/company'])
                meta = {'dont_redirect': True, 'company_url': company_url, 'dont_retry': True}
                self.log('fetch new url=%s' % (next_url), level=log.INFO)
                yield scrapy.Request(url = next_url, meta = meta, callback = self.parse_introduce_page, dont_filter = True)
        except:
            self.log('start_request error! (%s)' % (str(traceback.format_exc())), level=log.INFO)

    # 解析公司介绍
    def parse_introduce_page(self, response):
        sel = Selector(response)

        ret_item = BuildingMaterialsItem()
        ret_item['update_item'] = {}
        i = ret_item['update_item']
        i['company_url'] = response.meta['company_url']

        if response.status != 200 or len(response.body) <= 0:
            self.log('fetch failed ! status = %d, url=%s' % (response.status, i['company_url']), level = log.WARNING)

        ## company_name 公司名称
        company_name = sel.xpath("//div[@class='company_jj'][1]//li[1]/p[@class='info']/text()").extract()
        i['company_name'] = '' if not company_name else company_name[0].strip()

        ## introduce 公司简介
        introduce = sel.xpath("//div[@class='detail']")
        i['introduce'] = '' if not introduce else introduce[0].xpath('string(.)').extract()[0].strip().strip('\n')
        # introduce = introduce[0].xpath('string(.)').extract() ##取带有样式的汉字
        # i['introduce'] = '' if not introduce else introduce[0].strip()

        # industry 主营行业
        industry = sel.xpath("//div[@class='company_jj'][1]//li[4]/p[@class='info']/text()").extract()
        i['industry'] = '' if not industry else industry[0].strip()

        ## 详细信息{'员工人数','年营业额'}
        xpath_handles = sel.xpath("//div[@class='company_jj'][2]/ul[@class='tableType']//text()").extract()
        xpath_handles = ''.join(xpath_handles)

        ## year_turnover 年营业额
        year_turnover = re.findall(u"年营业额：\n?\s*([^\n]+)", xpath_handles, re.S) if xpath_handles else ''
        i['year_turnover'] = '' if not year_turnover else year_turnover[0].strip()

        # 员工人数 staffs
        staffs = re.findall(u"员工人数：\n?\s*([^\n]+)", xpath_handles, re.S) if xpath_handles else ''
        i['staffs'] = '' if not year_turnover else staffs[0].strip()

        # xpath_handles = sel.xpath("//div[@class='company_jj'][2]/ul[@class='tableType']//li")
        # for handle in xpath_handles:
            # item = handle.xpath("p/text()").extract()
            # if item and item[0].strip() == u'员工人数：':
                # print item[1]

        meta = {'dont_redirect': True, 'item': ret_item, 'dont_retry': True}
        # self.log(' parse_indroduce_page . company_name:%s, turnover:%s, staffs:%s'
                                        # % (i['company_name'], i['year_turnover'], i['staffs']), level=log.INFO)
        yield scrapy.Request(url = i['company_url'] + '/certificate', meta = meta, callback = self.parse_renzheng_page, dont_filter = True)


    #解析认证信息
    def parse_renzheng_page(self, response):
        sel = Selector(response)

        ret_item = response.meta['item']
        i = ret_item['update_item']

        if sel.xpath("//p[@class='ok_rz']/text()").extract():
            ## 实名认证
            xpath_handles = sel.xpath("//div[@class='company_rz']/ul[@class='tableType']//text()").extract()
            xpath_handles = ''.join(xpath_handles)

            ## 注册号 registr
            registr = re.findall(u"注册号：\n?\s*([^\n]+)", xpath_handles, re.S) if xpath_handles else ''
            i['registr'] = '' if not registr else registr[0].strip()

            ## 法人代表 legal
            legal = re.findall(u"法人代表：\n?\s*([^\n]+)", xpath_handles, re.S) if xpath_handles else ''
            i['legal'] = '' if not legal else legal[0].strip()

            ## 登记机关 register_office 
            office = re.findall(u"登记机关：\n?\s*([^\n]+)", xpath_handles, re.S) if xpath_handles else ''
            i['register_office'] = '' if not office else office[0].strip()

            ## 成立时间 found_time
            found_time = re.findall(u"成立时间：\n?\s*([^\n]+)", xpath_handles, re.S) if xpath_handles else ''
            i['found_time'] = '' if not found_time else found_time[0].strip()

            ## 公司类型 company_type
            company_type = re.findall(u"公司类型：\n?\s*([^\n]+)", xpath_handles, re.S) if xpath_handles else ''
            i['company_type'] = '' if not company_type else company_type[0].strip()

            ## 成立日期 found_date
            found_date = re.findall(u"成立日期：\n?\s*([^\n]+)", xpath_handles, re.S) if xpath_handles else ''
            i['found_date'] = '' if not found_date else found_date[0].strip()

            ## 注册资本 registr_capital
            registr_capital = re.findall(u"注册资本：\n?\s*([^\n]+)", xpath_handles, re.S) if xpath_handles else ''
            i['registr_capital'] = '' if not registr_capital else registr_capital[0].strip()

            ## 经营期限 operate_period
            operate_period = re.findall(u"经营期限：\n?\s*([^\n]+)", xpath_handles, re.S) if xpath_handles else ''
            i['operate_period'] = '' if not operate_period else operate_period[0].strip()

            ## 经营范围 operate_range
            operate_range = re.findall(u"经营范围：\n?\s*([^\n]+)", xpath_handles, re.S) if xpath_handles else ''
            i['operate_range'] = '' if not operate_range else operate_range[0].strip()

            meta = {'dont_redirect': True, 'item': ret_item, 'dont_retry': True}
            # self.log(' parse_renzheng_page . registr_capital:%s' % (i['registr_capital']), level=log.INFO)
            yield scrapy.Request(url = i['company_url'] + '/contact', meta = meta, callback = self.parse_contact_page, dont_filter = True)
        else:
            self.log('未认证. url=%s ' % (i['company_url']), level=log.INFO)

            meta = {'dont_redirect': True, 'item': ret_item, 'dont_retry': True}
            # self.log(' parse_renzheng_page . registr_capital:%s' % (i['registr_capital']), level=log.INFO)
            yield scrapy.Request(url = i['company_url'] + '/contact', meta = meta, callback = self.parse_contact_page, dont_filter = True)


    #解析联系我们页面
    def parse_contact_page(self, response):
        sel = Selector(response)

        ret_item = response.meta['item']
        i = ret_item['update_item']

        ## 联系我们
        xpath_handles = sel.xpath("//dl[@class='cardInfo']//text()").extract()
        xpath_handles = ''.join(xpath_handles)

        ## contactor 联系人
        contactor = sel.xpath("//div[@class='cardName']/h3/text()").extract()
        i['contactor'] = '' if not contactor else contactor[0].strip()

        ## duty 部门
        duty = re.findall(u"\s*部\s{0,5}?门：\n?\s*([^\n]+)", xpath_handles, re.S) if xpath_handles else ''
        i['duty'] = '' if not duty else duty[0].strip()

        ## telephone 电话
        telephone = re.findall(u"\s*电\s{0,5}?话：\n?\s*([^\n]+)", xpath_handles, re.S) if xpath_handles else ''
        i['telephone'] = '' if not telephone else telephone[0].strip()

        ## mobilephone 手机
        mobilephone = re.findall(u"\s*手\s{0,5}?机：\n?\s*([^\n]+)", xpath_handles, re.S) if xpath_handles else ''
        i['mobilephone'] = '' if not mobilephone else mobilephone[0].strip()

        ## fax 传真
        fax = re.findall(u"\s*传\s{0,5}?真：\n?\s*([^\n]+)", xpath_handles, re.S) if xpath_handles else ''
        i['fax'] = '' if not fax else fax[0].strip()

        ## zip_code 邮编
        zip_code = re.findall(u"\s*邮\s{0,5}?编：\n?\s*([^\n]+)", xpath_handles, re.S) if xpath_handles else ''
        i['zip_code'] = '' if not zip_code else zip_code[0].strip()

        ## url 网址
        url = re.findall(u"\s*网\s{0,5}?址：\n?\s*([^\n]+)", xpath_handles, re.S) if xpath_handles else ''
        i['url'] = '' if not url else url[0].strip()

        ## address 地址
        address = re.findall(u"\s*地\s{0,5}?址：\n?\s*([^\n]+)", xpath_handles, re.S) if xpath_handles else ''
        i['address'] = '' if not address else address[0].strip()

        ## 会员下面4项
        member_ups = sel.xpath("//div[@class='leftSider']/ul//text()").extract()
        member_ups = ''.join(member_ups)

        ## company_type 企业类型
        company_type = re.findall(u"企业类型：\n?\s*([^\n]+)", member_ups, re.S) if member_ups else ''
        i['company_type'] = '' if not company_type else company_type[0].strip()

        ## operate_pattern 经营模式
        operate_pattern = re.findall(u"经营模式：\n?\s*([^\n]+)", member_ups, re.S) if member_ups else ''
        i['operate_pattern'] = '' if not operate_pattern else operate_pattern[0].strip()

        ## honor 荣誉资质
        honor = re.findall(u"荣誉资质：\n?\s*([^\n]+)", member_ups, re.S) if member_ups else ''
        i['honor'] = '' if not honor else honor[0].strip()

        ## mainpro 主营
        mainpro = re.findall(u"主.*?营：\n?\s*([^\n]+)", member_ups, re.S) if member_ups else ''
        i['mainpro'] = '' if not mainpro else mainpro[0].strip()

        ## member_year 会员年限
        member_year = sel.xpath("//div[@class='title']//text()").extract()
        member_year = ''.join(member_year)
        member_year = re.findall(u"\d+", member_year, re.S)if member_year else ''
        i['member_year'] = '' if not member_year else member_year[0].strip()

        ## member_level 会员级别
        ## 高级会员
        member_level= sel.xpath("//div[@class='title']//p/span/text()").extract()
        if member_level:
            i['member_level'] = '' if not member_level else member_level[0].strip()
        else:
            ## 普通会员
            member_level_pt = sel.xpath("//div[@class='free_vip']//text()").extract()
            i['member_level'] = '' if not member_level_pt else member_level_pt[0].strip()

        self.log(' . company_name:%s, url=%s ' % (i['company_name'], i['company_url']), level=log.INFO)

        yield ret_item
