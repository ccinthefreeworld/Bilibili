#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File:              bilibili_userrelationinfo.py
@Contact:           ccinthefreeworld@gmail.com
@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2018/12/13 13:53    cc         1.0          None
'''

import requests
import pymysql
import time
import datetime

from bilibili_userinfo import logger, connect, headers

# 连接mysql数据库
conn = pymysql.connect(**connect)
cur = conn.cursor()

# 记录爬取数据的条目
total = 0

# 记录已经爬取过关注列表的用户
complete = []

def run(user_id, user_name):
    """
    开始爬取用户关系信息
    :param user_id:
    :param user_name:
    :return:
    """
    time.sleep(0.5)
    enter_space(user_id, user_name)

def enter_space(user_id, user_name):
    """
    进入用户主页
    :param user_id:
    :param user_name:
    :return:
    """
    try:
        url = 'https://space.bilibili.com/' + str(user_id)
        response = requests.get(url, headers = headers, timeout = 6)
        if response.status_code == 200:
            # logger.info('进入主页成功, user_id = {}'.format(user_id))
            get_userfollowing_list(user_id, user_name)
        else:
            logger.info('进入主页失败, use_id = {}, code = {}'.format(user_id, response.status_code))
    except ConnectionError as e:
        logger.error('网络连接异常，e = {}',format(e))

def get_userfollowing_list(user_id, user_name) :
    """
    获取用户关注列表
    :param user_id:
    :param user_name:
    :return:
    """
    global complete
    try:
        url = 'https://api.bilibili.com/x/relation/followings?vmid=' + str(user_id)
        response = requests.get(url, headers = headers, timeout = 6)
        if response.status_code == 200:
            # logger.info('获取用户关注列表成功, user_id = {}'.format(user_id))
            content = response.json()
            if content.get('data'):
                data = content['data']
                followings = []

                totals = data['total']
                followings.append(totals)

                # 由于系统限制 只能获取前50的关注
                if totals > 50 :
                    # logger.info('该用户关注列表数多于50, user_id = {}'.format(user_id))
                    totals = 50
                for i in range(0, totals):
                    try :
                        following = (
                            data['list'][i]['mid'],
                            data['list'][i]['uname']
                        )
                        followings.append(following)
                    except :
                        break
                # 保存用户关系表到mysql数据库上
                # logger.info(followings)
                save_userinfo_mysql(followings, user_id, user_name)

                complete.append(user_id)
                logger.info(complete)

                get_userfollowing_list_repeat(followings)
            else :
                logger.info('获取用户关注列表失败, use_id = {}, user_name = {}'.format(user_id, user_name))
        else:
            logger.info('获取用户关注列表失败, use_id = {}, code = {}'.format(user_id, response.status_code))
    except ConnectionError as e:
        logger.error('网络连接异常，e = {}',format(e))

def get_userfollowing_list_repeat(followings):
    """
    根据用户关注列表循环执行,需要剔除已经执行过的
    :param followings:关注列表
    :return:
    """
    global complete
    # logger.info(complete)
    try :
        totals = followings[0]
        # logger.info(totals)
        for i in range(1, totals + 1):
            try:
                flag = 0
                for j in range(len(complete)):
                    # logger.info(complete[j])
                    # logger.info(followings[i][0])
                    if followings[i][0] == complete[j]:
                        flag = 1
                        break
                # logger.info('flag = {}'.format(flag))
                if 1 != flag:
                    # logger.info(followings[i])
                    run(followings[i][0],followings[i][1])
            except:
                # logger.info('该用户关注列表数多于50, user_id = {}'.format(user_id))
                break
    except ConnectionError as e:
        logger.error('网络连接异常，e = {}',format(e))

def save_userinfo_mysql(followings, user_id, user_name):
    """
    存储用户关系信息到mysql数据库
    相关：数据库bilibili 数据表bilibili_userrelation
    :param followings:
    :param user_id:
    :param user_name:
    :return:
    """
    try:
        totals = followings[0]
        if totals > 50 :
            totals = 50

        # 单向 A关注B
        sql_A2B = 'insert into bilibili_userrelation(user1_mid, user1_name, user2_mid, user2_name, status) ' \
                     'values(%s, %s, %s, %s, 0);'
        # 单向 B关注A
        sql_B2A = 'insert into bilibili_userrelation(user1_mid, user1_name, user2_mid, user2_name, status) ' \
                     'values(%s, %s, %s, %s, 1);'
        # 双向 AB互相关注
        sql_AB = 'update bilibili_userrelation set status=2 where user1_mid = %s AND user2_mid = %s;'
        # 检查记录是否存在
        sql_selectAB = 'select count(*) from bilibili_userrelation where user1_mid = %s AND user2_mid = %s;'
        sql_selectABstatus = 'select status from bilibili_userrelation where user1_mid = %s AND user2_mid = %s;'

        for row in followings[1:totals + 1]:
            # logger.info('mid = {}'.format(row[0]))
            if user_id < row[0]:
                cur.execute(sql_selectAB,(user_id, row[0]))
                count = cur.fetchall()[0][0]
                # logger.info('count = {}'.format(count))
                if 0 == count:
                    result = (user_id, user_name) + row
                    try:
                        cur.execute(sql_A2B , result)
                    except:
                        conn.rollback()
                        logger.info('用户关系信息保存到数据库中失败,A2BB,mid分别是{}和{}'.format(user_id,row[0]))
                elif 1 == count:
                    try:
                        cur.execute(sql_selectABstatus, (user_id, row[0]))
                        status = cur.fetchone()[0]
                        # logger.info(status)
                        if 1 == status :
                            try:
                                cur.execute(sql_AB, (user_id, row[0]))
                            except:
                                 conn.rollback()
                                 logger.info('用户关系信息保存到数据库中失败,A2B,mid分别是{}和{}'.format(user_id,row[0]))
                        else:
                            logger.info('用户关系信息在数据库中,A2B已经执行过,mid分别是{}和{}'.format(user_id,row[0]))
                    except:
                        conn.rollback()
                        logger.info('用户关系信息保存到数据库中失败,A2B,mid分别是{}和{}'.format(user_id,row[0]))
                else :
                    logger.info('用户关系信息在数据库中重复有多条,A2B,mid分别是{}和{}'.format(user_id,row[0]))
            elif user_id > row[0]:
                result = row + (user_id, user_name)
                cur.execute(sql_selectAB,(row[0], user_id))
                count = cur.fetchall()[0][0]
                if 0 == count:
                    try:
                        cur.execute(sql_B2A, result)
                    except:
                        conn.rollback()
                        logger.info('用户关系信息保存到数据库中失败,B2AA,mid分别是{}和{}'.format(row[0], user_id))
                elif 1 == count :
                    try:
                        cur.execute(sql_selectABstatus, (row[0], user_id))
                        status = cur.fetchone()[0]
                    except:
                        logger.info('用户关系信息查询状态出错，B2A,mid分别是{}和{}'.format(row[0], user_id))
                    if 0 == status:
                        try:
                            cur.execute(sql_AB,  (row[0], user_id))
                        except:
                            conn.rollback()
                            logger.info('用户关系信息保存到数据库中失败,B2A,mid分别是{}和{}'.format(row[0], user_id))
                    else:
                        logger.info('用户关系信息在数据库中,B2A已经执行过,mid分别是{}和{}'.format(row[0], user_id))
                else :
                    logger.info('用户关系信息在数据库中重复有多条,B2A,mid分别是{}和{}'.format(row[0], user_id))
            else:
                logger.info('用户关系信息出错,自关,mid是{}',format(user_id))
    except ConnectionError as e:
        logger.error('网络连接异常，e = {}',format(e))

if __name__ == '__main__':
    logger.info('运行开始，开始爬取B站用户的用户关系')

    time_start = datetime.datetime.now()

    # user_id = 546195
    user_id = 2
    user_name = '碧诗'
    run(user_id, user_name)

    # user_id = 1
    # user_name = 'test'
    # followings = [1,(2,'a')]
    # save_userinfo_mysql(followings,user_id,user_name)

    time_end = datetime.datetime.now()
    time =  (time_end - time_start).seconds

    logger.info('运行结束，运行时间是{}秒'.format(time))
    conn.close()
