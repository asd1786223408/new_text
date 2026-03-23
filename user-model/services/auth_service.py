#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
认证服务
"""

import bcrypt
import json
from datetime import datetime
from models.database import db


class AuthService:
    def authenticate(self, account, password):
        """
        认证用户
        account 可以是邮箱或手机号
        """
        # 尝试按邮箱查询
        if '@' in account:
            sql = "SELECT * FROM users WHERE email = %s AND deleted_at IS NULL"
            user = db.fetch_one(sql, (account,))
        else:
            # 按手机号或用户名查询
            sql = """SELECT * FROM users
                     WHERE (username = %s OR phone = %s) AND deleted_at IS NULL"""
            user = db.fetch_one(sql, (account, account))

        if not user:
            return None

        # 验证密码
        if not bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
            return None

        return user

    def register(self, username, password, email=None, phone=None):
        """注册用户"""
        # 检查用户名是否存在
        sql = "SELECT id FROM users WHERE username = %s AND deleted_at IS NULL"
        if db.fetch_one(sql, (username,)):
            return {'success': False, 'message': '用户名已存在'}

        # 检查邮箱是否存在
        if email:
            sql = "SELECT id FROM users WHERE email = %s AND deleted_at IS NULL"
            if db.fetch_one(sql, (email,)):
                return {'success': False, 'message': '邮箱已被注册'}

        # 检查手机号是否存在
        if phone:
            sql = "SELECT id FROM users WHERE phone = %s AND deleted_at IS NULL"
            if db.fetch_one(sql, (phone,)):
                return {'success': False, 'message': '手机号已被注册'}

        # 加密密码
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        # 获取默认权限（普通用户）
        default_permissions = '["user:read"]'

        # 插入用户
        sql = """INSERT INTO users (username, password_hash, email, phone, permissions, status)
                 VALUES (%s, %s, %s, %s, %s, 1)"""

        db.execute(sql, (username, password_hash, email or None, phone or None, default_permissions))

        # 获取用户 ID
        result = db.fetch_one("SELECT LAST_INSERT_ID() as id")
        user_id = result['id']

        # 关联默认角色（user）
        sql = "SELECT id FROM roles WHERE name = 'user'"
        role = db.fetch_one(sql)
        if role:
            sql = "INSERT INTO user_roles (user_id, role_id) VALUES (%s, %s)"
            db.execute(sql, (user_id, role['id']))

        return {'success': True, 'user_id': user_id}

    def update_login_info(self, user_id, ip):
        """更新登录信息"""
        sql = """UPDATE users SET last_login_at = %s, last_login_ip = %s, login_failure_count = 0
                 WHERE id = %s"""
        db.execute(sql, (datetime.now(), ip, user_id))

    def get_user_info(self, user_id):
        """获取用户信息"""
        sql = """SELECT u.id, u.username, u.email, u.phone, u.avatar, u.nickname,
                        u.gender, u.birthday, u.department_id, u.position, u.status,
                        u.permissions, u.last_login_at, d.name as department_name
                 FROM users u
                 LEFT JOIN departments d ON u.department_id = d.id
                 WHERE u.id = %s AND u.deleted_at IS NULL"""
        return db.fetch_one(sql, (user_id,))
