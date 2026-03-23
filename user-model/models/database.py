#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据库连接模块
"""

import pymysql
import json
import os

# 加载配置
def get_db_config():
    config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'env.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    return config.get('mysql', {})


class Database:
    def __init__(self):
        self.config = None
        self.connection = None

    def init_app(self, app):
        self.config = get_db_config()

    def get_connection(self):
        if self.connection is None or not self.connection.open:
            self.connection = pymysql.connect(
                host=self.config.get('host', 'localhost'),
                port=self.config.get('port', 3306),
                user=self.config.get('user', 'root'),
                password=self.config.get('password', ''),
                database=self.config.get('database', 'user_platform'),
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor
            )
        return self.connection

    def execute(self, sql, params=None):
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(sql, params)
                conn.commit()
                return cursor
        except Exception as e:
            conn.rollback()
            raise e

    def fetch_one(self, sql, params=None):
        conn = self.get_connection()
        with conn.cursor() as cursor:
            cursor.execute(sql, params)
            return cursor.fetchone()

    def fetch_all(self, sql, params=None):
        conn = self.get_connection()
        with conn.cursor() as cursor:
            cursor.execute(sql, params)
            return cursor.fetchall()

    def close(self):
        if self.connection and self.connection.open:
            self.connection.close()


# 全局数据库实例
db = Database()
