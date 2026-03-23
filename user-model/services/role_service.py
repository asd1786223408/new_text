#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
角色服务
"""

import json
from models.database import db


class RoleService:
    def get_all_roles(self):
        """获取所有角色"""
        sql = "SELECT * FROM roles ORDER BY id"
        roles = db.fetch_all(sql)

        # 解析权限 JSON
        for role in roles:
            if role.get('permissions'):
                if isinstance(role['permissions'], str):
                    role['permissions'] = json.loads(role['permissions'])
            else:
                role['permissions'] = []

        return roles

    def get_role(self, role_id):
        """获取角色详情"""
        sql = "SELECT * FROM roles WHERE id = %s"
        role = db.fetch_one(sql, (role_id,))

        if role:
            if role.get('permissions'):
                if isinstance(role['permissions'], str):
                    role['permissions'] = json.loads(role['permissions'])
            else:
                role['permissions'] = []

        return role

    def create_role(self, data):
        """创建角色"""
        name = data.get('name', '').strip()
        display_name = data.get('display_name', '')
        description = data.get('description', '')
        permissions = data.get('permissions', [])

        # 检查角色名是否存在
        sql = "SELECT id FROM roles WHERE name = %s"
        if db.fetch_one(sql, (name,)):
            return {'success': False, 'message': '角色名已存在'}

        # 插入角色
        sql = """INSERT INTO roles (name, display_name, description, permissions)
                 VALUES (%s, %s, %s, %s)"""
        db.execute(sql, (name, display_name, description, json.dumps(permissions)))

        result = db.fetch_one("SELECT LAST_INSERT_ID() as id")
        return {'success': True, 'role_id': result['id']}

    def update_role(self, role_id, data):
        """更新角色"""
        role = self.get_role(role_id)
        if not role:
            return {'success': False, 'message': '角色不存在'}

        fields = []
        params = []

        for key in ['display_name', 'description', 'status']:
            if key in data:
                fields.append(f"{key} = %s")
                params.append(data[key])

        if not fields:
            return {'success': False, 'message': '没有要更新的字段'}

        params.append(role_id)
        sql = f"UPDATE roles SET {', '.join(fields)} WHERE id = %s"
        db.execute(sql, tuple(params))

        return {'success': True}

    def delete_role(self, role_id):
        """删除角色"""
        role = self.get_role(role_id)
        if not role:
            return {'success': False, 'message': '角色不存在'}

        # 检查是否有用户使用该角色
        sql = "SELECT COUNT(*) as count FROM user_roles WHERE role_id = %s"
        result = db.fetch_one(sql, (role_id,))
        if result['count'] > 0:
            return {'success': False, 'message': '该角色下有用户，无法删除'}

        sql = "DELETE FROM roles WHERE id = %s"
        db.execute(sql, (role_id,))

        return {'success': True}

    def update_role_permissions(self, role_id, permission_ids):
        """更新角色权限"""
        role = self.get_role(role_id)
        if not role:
            return {'success': False, 'message': '角色不存在'}

        # 根据权限 ID 获取权限标识
        if permission_ids:
            placeholders = ','.join(['%s'] * len(permission_ids))
            sql = f"SELECT name FROM permissions WHERE id IN ({placeholders})"
            perms = db.fetch_all(sql, tuple(permission_ids))
            permissions = [p['name'] for p in perms]
        else:
            permissions = []

        sql = "UPDATE roles SET permissions = %s WHERE id = %s"
        db.execute(sql, (json.dumps(permissions), role_id))

        # 更新该角色下所有用户的权限
        self._update_user_permissions(role_id, permissions)

        return {'success': True}

    def _update_user_permissions(self, role_id, permissions):
        """更新角色下所有用户的权限"""
        # 获取角色下所有用户
        sql = "SELECT user_id FROM user_roles WHERE role_id = %s"
        user_roles = db.fetch_all(sql, (role_id,))

        for ur in user_roles:
            user_id = ur['user_id']
            # 获取用户所有角色的权限并集
            all_permissions = self._get_user_all_permissions(user_id)
            sql = "UPDATE users SET permissions = %s WHERE id = %s"
            db.execute(sql, (json.dumps(all_permissions), user_id))

    def _get_user_all_permissions(self, user_id):
        """获取用户所有角色的权限并集"""
        sql = """SELECT r.permissions FROM roles r
                 JOIN user_roles ur ON r.id = ur.role_id
                 WHERE ur.user_id = %s"""
        user_roles = db.fetch_all(sql, (user_id,))

        permissions = set()
        for ur in user_roles:
            if ur.get('permissions'):
                perms = ur['permissions']
                if isinstance(perms, str):
                    perms = json.loads(perms)
                permissions.update(perms)

        return list(permissions)
