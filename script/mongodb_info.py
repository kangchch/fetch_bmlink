# -*- coding: utf-8 -*-

import pymongo
from pymongo import MongoClient
import datetime

mongo_db_Conn = pymongo.MongoClient('192.168.60.65', 10010).bmlink_info

db_bmlink = mongo_db_Conn.bmlink_tbl

db_bmlink.insert({'company_name': '',                   #公司名称
                    'company_url': '',                  #公司url地址
                    'introduce': '',                    #公司介绍
                    'industry': '',                      #主营行业
                    'year_turnover': '',                #年营业额
                    'staffs': '',                       #员工人数
                    'registr': '',                      #注册号
                    'legal': '',                        #法人
                    'register_office': '',              #登记机关
                    'found_time': '',                   #成立时间
                    'company_type': '',                 #公司类型
                    'found_date': '',                   #成立日期
                    'registr_capital': '',              #注册资本
                    'operate_period': '',              #经营期限
                    'operate_range': '',               #经营范围
                    'member_level': '',                 #会员级别
                    'member_year': '',                  #会员年限
                    'honor': '',                        #荣誉资质
                    'company_type': '',                 #企业类型
                    'operate_pattern': '',             #经营模式
                    'mainpro': '',                      #主营
                    'contactor': '',                    #联系人
                    'duty': '',                         #联系人部门
                    'telephone': '',                    #电话
                    'mobilephone': '',                  #手机
                    'fax': '',                          #传真
                    'zip_code': '',                     #邮编
                    'url': '',                          #网址
                    'address': '',                      #地址
                    'status': 0,                        #抓取状态 0 未抓取 1 以抓取 2 抓取失败
                    'insert_time': datetime.datetime.now(),
                })
