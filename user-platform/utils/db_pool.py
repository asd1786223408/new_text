# -*- coding: utf-8 -*-
"""
数据库连接池
"""
import pymysql
from dbutils.pooled_db import PooledDB
import os
import json

# 全局连接池
_db_pool = None


def load_config():
    """加载配置文件"""
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'env.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


class DatabasePool:
    """数据库连接池类"""

    def __init__(self):
        global _db_pool
        config = load_config()
        mysql_config = config.get('mysql', {})

        _db_pool = PooledDB(
            creator=pymysql,
            maxconnections=20,
            mincached=2,
            maxcached=5,
            blocking=True,
            refresh=5 * 60,
            host=mysql_config.get('host', 'localhost'),
            port=mysql_config.get('port', 3306),
            user=mysql_config.get('user', 'root'),
            password=mysql_config.get('password', ''),
            database=mysql_config.get('database', 'user_platform'),
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )

    def get_connection(self):
        """获取数据库连接"""
        return _db_pool.connection()


def get_db_connection():
    """获取数据库连接（便捷函数）"""
    global _db_pool
    if _db_pool is None:
        config = load_config()
        mysql_config = config.get('mysql', {})
        return pymysql.connect(
            host=mysql_config.get('host', 'localhost'),
            port=mysql_config.get('port', 3306),
            user=mysql_config.get('user', 'root'),
            password=mysql_config.get('password', ''),
            database=mysql_config.get('database', 'user_platform'),
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
    return _db_pool.connection()


# 初始化连接池
try:
    db_pool = DatabasePool()
except Exception as e:
    print(f"数据库连接池初始化失败：{e}")
    db_pool = None
