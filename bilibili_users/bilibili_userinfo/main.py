#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File:              main.py
@Contact:           ccinthefreeworld@gmail.com
@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2018/12/11 14:23    cc         1.0          None
'''
import requests
import pymysql
import time

from bilibili_userinfo import logger, connect, headers

# 连接mysql数据库
conn = pymysql.connect(**connect)
cur = conn.cursor()

# 记录爬取数据的条目
total = 0

def run(user_id):
    """
    开始爬取用户个人信息
    :param user_id:
    :return:
    """
    enter_space(user_id)

def enter_space(user_id):
    """
    进入用户主页
    :param user_id:
    :return:
    """
    try:
        url = 'https://space.bilibili.com/' + str(user_id)
        response = requests.get(url, headers = headers, timeout = 6)
        if response.status_code == 200:
            # logger.info('进入主页成功, user_id = {}'.format(user_id))
            get_basic_userinfo(user_id)
        else:
            logger.info('进入主页失败, use_id = {}, code = {}'.format(user_id, response.status_code))
    except ConnectionError as e:
        logger.error('网络连接异常，e = {}',format(e))

def get_basic_userinfo(user_id):
    """
    获取基础用户个人信息
    :param user_id:
    :return:
    """
    global total

    url = 'https://space.bilibili.com/ajax/member/GetInfo'
    payload = {
         'mid' : user_id
    }
    head = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36'
                  '(KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
            'Referer': 'https://space.bilibili.com/' + str(user_id)
        }
    try:
        response =  requests.post(url, headers = head, data = payload, timeout = 6)
        if response.status_code == 200:
            content = response.json()
            if content.get('data'):
                data = content['data']
                regtime = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(data['regtime']))
                result =  (
                    data['mid'],
                    data['name'],
                    data['sex'],
                    data['rank'],
                    data['face'],
                    regtime,
                    data['spacesta'],
                    data['birthday'],
                    data['sign'],
                    data['level_info']['current_level'],
                    data['official_verify']['desc'],
                    data['vip']['vipType'],
                    data['vip']['vipStatus'],
                    data['toutu'],
                    data['toutuId'],
                    data['theme'],
                    data['theme_preview'],
                    data['coins'],
                    data['im9_sign'],
                    data['fans_badge']
                )
                # logger.info('获取用户个人信息成功 use_id = {}'.format(user_id))
                result += get_add_userfollow(user_id)
                result += get_add_usercount(user_id)
                result += get_add_userview(user_id)
                logger.info(result)
                save_userinfo_mysql(result)
                total += 1
                if total%100 == 0:
                    logger.info('目前共计爬取到{}条数据'.format(total))
            else :
                logger.info('获取用户个人信息失败, use_id = {}'.format(user_id))
        else :
            logger.info('获取用户个人信息失败, use_id = {}, code = {}'.format(user_id, response.status_code))
    except ConnectionError as e:
        logger.error('网络连接异常，e = {}',format(e))

def get_add_userfollow(user_id):
    """
    获取用户粉丝数follower和关注数following
    :param user_id:
    :return: result
    """
    try:
        url = 'https://api.bilibili.com/x/relation/stat?vmid=' + str(user_id)
        response =  requests.get(url, headers = headers, timeout = 6)
        if response.status_code == 200:
            content = response.json()
            if content.get('data'):
                data = content['data']
                result = (
                    data['following'],
                    data['follower']
                )
                return result
            else :
                logger.info('获取用户粉丝数和关注数失败, use_id = {}'.format(user_id))
        else :
            logger.info('获取用户粉丝数和关注数失败, use_id = {}, code = {}'.format(user_id, response.status_code))
    except ConnectionError as e:
        logger.error('网络连接异常，e = {}',format(e))

def get_add_usercount(user_id):
    """
    获取用户投稿视频数archive_count和文章数article_count
    :param user_id:
    :return: result
    """
    try:
        url = 'https://api.bilibili.com/x/space/navnum?mid=' + str(user_id)
        response =  requests.get(url, headers = headers, timeout = 6)
        if response.status_code == 200:
            content = response.json()
            if content.get('data'):
                data = content['data']
                result = (
                    data['video'],
                    data['article']
                )
                return result
            else :
                logger.info('获取用户投稿视频数和文章数失败, use_id = {}'.format(user_id))
        else :
            logger.info('获取用户投稿视频数和文章数失败, use_id = {}, code = {}'.format(user_id, response.status_code))
    except ConnectionError as e:
        logger.error('网络连接异常，e = {}',format(e))

def get_add_userview(user_id):
    """
    获取用户播放数archive_view和阅读数article_view
    :param user_id:
    :return: result
    """
    try:
        url = 'https://api.bilibili.com/x/space/upstat?mid=' + str(user_id)
        response =  requests.get(url, headers = headers, timeout = 6)
        if response.status_code == 200:
            content = response.json()
            if content.get('data'):
                data = content['data']
                result = (
                    data['archive']['view'],
                    data['article']['view']
                )
                return result
            else :
                logger.info('获取用户播放数和阅读数失败, use_id = {}'.format(user_id))
        else :
            logger.info('获取用户播放数和阅读数失败, use_id = {}, code = {}'.format(user_id, response.status_code))
    except ConnectionError as e:
        logger.error('网络连接异常，e = {}',format(e))

def save_userinfo_mysql(result):
    """
    将用户个人信息保存到mysql数据库中
    相关:数据库bilibili 数据表bilibili_userinfo
    :param result:
    :return:
    """
    global conn, cur

    sql_select = 'select mid from bilibili_userinfo where not exists (select * from bilibili_upinfo where mid = {});'.format(result[0])
    # logger.info(cur.execute(sql_select))
    if 0 == cur.execute(sql_select) & 0 != cur.execute('select * from bilibili_userinfo'):
        logger.info('用户个人信息在数据库中已存在， user_id = {}'.format(result[0]))
    else :
        sql_insert = 'insert into bilibili_userinfo values(NULL, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,' \
                     ' %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);'
        try :
            cur.execute(sql_insert, result)
            # logger.info('用户个人信息保存到数据库中成功， user_id = {}'.format(result[0]))
        except:
            conn.rollback()
            logger.info('用户个人信息保存到数据库中失败， user_id = {}'.format(result[0]))
    conn.commit()

if __name__ == '__main__':
    logger.info('开始爬取B站用户个人信息数据')

    user_id = 1
    run(user_id)

    logger.info('运行结束，共计爬取到{}条数据'.format(total))
    conn.close()
