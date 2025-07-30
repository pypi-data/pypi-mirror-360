# -*- coding: utf-8 -*-
"""
@Time    : 2024/3/19 17:17

@Author  : wangchao
"""
import pymysql
from pymongo import MongoClient


def mysql_conn(mysql_config):
    """
    MySQL连接

    mysql_config(dict): 连接配置
    e.g.
    {"host":"","port":"","user":"","password":"","database":""}
    """
    conn = pymysql.connect(**mysql_config)
    cursor = conn.cursor()
    return cursor


def mongodb_conn(host, port, mongo_db, username, password, is_authorized=False):
    """
    Mongo连接

    host(str): 主机地址
    port(int): 端口号
    mongo_db(str): 数据库名称
    username(str): 用户名
    password(str): 密码
    is_authorized(bool):
    """

    client = MongoClient(host=host, port=int(port), username=username,
                         password=password, authSource="admin")
    db = client[mongo_db]
    return db


def redis_conn(host, port, password):
    """
    Redis连接

    host(str): 主机地址
    port(int): 端口号
    password(str): 密码
    """
    from rediscluster import RedisCluster
    conn = RedisCluster(host=host, port=port, password=password)
    return conn


class DBConnectFunction:
    @classmethod
    def mysql_conn(cls, mysql_config):
        return mysql_conn(mysql_config)

    @classmethod
    def mongodb_conn(cls, host, port, mongo_db, username, password, is_authorized=False):
        return mongodb_conn(host, port, mongo_db, username, password, is_authorized)

    @classmethod
    def redis_conn(cls, host, port, password):
        return redis_conn(host, port, password)


__all__ = [
    "DBConnectFunction",
    "redis_conn", "mysql_conn", "mongodb_conn"
]
