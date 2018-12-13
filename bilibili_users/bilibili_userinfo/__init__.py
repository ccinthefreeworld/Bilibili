#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File:              __init__.py.py
@Contact:           ccinthefreeworld@gmail.com
@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2018/12/11 14:22    cc         1.0          None
'''

# 日志
import logging

logger = logging.getLogger('bilibili_userinfo')
logger.setLevel(logging.INFO)

fh = logging.FileHandler('bilibili_userinfo.log')
fh.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(filename)s - %(funcName)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)

logger.addHandler(fh)
logger.addHandler(ch)

# mysql数据库
connect = {
   'host': 'localhost',
   'port': 3306 ,
   'user': 'root',
   'passwd': '' ,
   'db': 'bilibili',
   'charset': 'utf8'
}

# 浏览器headers
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36'
                  '(KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest'
}
