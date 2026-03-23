#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
用户服务
"""

import bcrypt
import json
from datetime import datetime
from models.database import db


class UserService:
    def get_users(self, page, limit, keyword='', department_id=None, status=None):
        """获取用户列表"""
        offset = (page - 1) * limit

        # 构建查询条件
        conditions = ["u.deleted_at IS NULL"]
        params = []

        if keyword:
            conditions.append("(u.username LIKE %s OR u.nickname LIKE %s OR u.email LIKE %s OR u.phone LIKE %s)")
            keyword_param = f'%{keyword}%'
            params.extend([keyword_param, keyword_param, keyword_param, keyword_param])

        if department_id:
            conditions.append("u.department_id = %s")
            params.append(department_id)

        if status is not None:
            conditions.append("u.status = %s")
            params.append(status)

        where_sql = " AND ".join(conditions)

        # 查询总数
        count_sql = f"SELECT COUNT(*) as total FROM users u WHERE {where_sql}"
        total_result = db.fetch_one(count_sql, tuple(params))
        total = total_result['total'] if total_result else 0

        # 查询数据
        sql = f"""SELECT u.id, u.username, u.email, u.phone, u.avatar, u.nickname,
                         u.gender, u.birthday, u.department_id, u.position, u.status,
                         u.last_login_at, u.created_at, d.name as department_name
                  FROM users u
                  LEFT JOIN departments d ON u.department_id = d.id
                  WHERE {where_sql}
                  ORDER BY u.created_at DESC
                  LIMIT %s OFFSET %s"""

        params.extend([limit, offset])
        users = db.fetch_all(sql, tuple(params))

        # 获取用户角色
        for user in users:
            roles = self.get_user_roles(user['id'])
            user['roles'] = roles

        return {
            'list': users,
            'total': total,
            'page': page,
            'limit': limit
        }

    def get_user(self, user_id):
        """获取用户详情"""
        sql = """SELECT u.*, d.name as department_name
                 FROM users u
                 LEFT JOIN departments d ON u.department_id = d.id
                 WHERE u.id = %s AND u.deleted_at IS NULL"""
        user = db.fetch_one(sql, (user_id,))

        if user:
            user['roles'] = self.get_user_roles(user_id)

        return user

    def get_user_roles(self, user_id):
        """获取用户角色"""
        sql = """SELECT r.id, r.name, r.display_name
                 FROM roles r
                 JOIN user_roles ur ON r.id = ur.role_id
                 WHERE ur.user_id = %s"""
        return db.fetch_all(sql, (user_id,))

    def create_user(self, data):
        """创建用户"""
        username = data.get('username', '').strip()
        password = data.get('password', '')
        email = data.get('email', '').strip()
        phone = data.get('phone', '').strip()
        nickname = data.get('nickname', '')
        department_id = data.get('department_id')
        position = data.get('position')
        status = data.get('status', 1)
        role_ids = data.get('role_ids', [])

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

        # 获取默认权限
        permissions = self._get_permissions_by_roles(role_ids)

        # 插入用户
        sql = """INSERT INTO users (username, password_hash, email, phone, nickname,
                                    department_id, position, status, permissions)
                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        db.execute(sql, (username, password_hash, email or None, phone or None,
                        nickname or None, department_id, position or None, status,
                        json.dumps(permissions)))

        # 获取用户 ID
        result = db.fetch_one("SELECT LAST_INSERT_ID() as id")
        user_id = result['id']

        # 关联角色
        if role_ids:
            for role_id in role_ids:
                sql = "INSERT INTO user_roles (user_id, role_id) VALUES (%s, %s)"
                db.execute(sql, (user_id, role_id))

        return {'success': True, 'user_id': user_id}

    def update_user(self, user_id, data):
        """更新用户"""
        # 检查用户是否存在
        user = self.get_user(user_id)
        if not user:
            return {'success': False, 'message': '用户不存在'}

        # 构建更新字段
        fields = []
        params = []

        for key in ['email', 'phone', 'nickname', 'avatar', 'gender', 'birthday',
                    'department_id', 'position', 'status']:
            if key in data:
                fields.append(f"{key} = %s")
                params.append(data[key])

        if not fields:
            return {'success': False, 'message': '没有要更新的字段'}

        params.append(user_id)
        sql = f"UPDATE users SET {', '.join(fields)} WHERE id = %s"
        db.execute(sql, tuple(params))

        return {'success': True}

    def delete_user(self, user_id):
        """删除用户（软删除）"""
        user = self.get_user(user_id)
        if not user:
            return {'success': False, 'message': '用户不存在'}

        sql = "UPDATE users SET deleted_at = %s WHERE id = %s"
        db.execute(sql, (datetime.now(), user_id))

        return {'success': True}

    def change_password(self, user_id, old_password, new_password, current_user_id):
        """修改密码"""
        user = self.get_user(user_id)
        if not user:
            return {'success': False, 'message': '用户不存在'}

        # 如果是修改自己的密码，验证旧密码
        if current_user_id == user_id:
            if not bcrypt.checkpw(old_password.encode('utf-8'), user['password_hash'].encode('utf-8')):
                return {'success': False, 'message': '原密码错误'}

        # 加密新密码
        password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        sql = """UPDATE users SET password_hash = %s, password_changed_at = %s
                 WHERE id = %s"""
        db.execute(sql, (password_hash, datetime.now(), user_id))

        return {'success': True}

    def update_user_roles(self, user_id, role_ids):
        """更新用户角色"""
        user = self.get_user(user_id)
        if not user:
            return {'success': False, 'message': '用户不存在'}

        # 删除旧角色
        sql = "DELETE FROM user_roles WHERE user_id = %s"
        db.execute(sql, (user_id,))

        # 添加新角色
        if role_ids:
            for role_id in role_ids:
                sql = "INSERT INTO user_roles (user_id, role_id) VALUES (%s, %s)"
                db.execute(sql, (user_id, role_id))

        # 更新用户权限
        permissions = self._get_permissions_by_roles(role_ids)
        sql = "UPDATE users SET permissions = %s WHERE id = %s"
        db.execute(sql, (json.dumps(permissions), user_id))

        return {'success': True}

    def _get_permissions_by_roles(self, role_ids):
        """根据角色 ID 列表获取权限"""
        if not role_ids:
            return []

        permissions = set()
        for role_id in role_ids:
            sql = "SELECT permissions FROM roles WHERE id = %s"
            result = db.fetch_one(sql, (role_id,))
            if result and result.get('permissions'):
                perms = result['permissions']
                if isinstance(perms, str):
                    perms = json.loads(perms)
                permissions.update(perms)

        return list(permissions)
