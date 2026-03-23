# -*- coding: utf-8 -*-
"""
角色模型
"""
import json
from ..utils.db_pool import get_db_connection


class Role:
    """角色模型类"""

    @staticmethod
    def create(name, display_name, description='', permissions=None):
        """创建角色"""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO roles (name, display_name, description, permissions)
                    VALUES (%s, %s, %s, %s)
                """, (name, display_name, description, json.dumps(permissions or [])))
                role_id = cursor.lastrowid
                conn.commit()
            return role_id
        finally:
            conn.close()

    @staticmethod
    def get_by_id(role_id):
        """根据 ID 获取角色"""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM roles WHERE id = %s
                """, (role_id,))
                role = cursor.fetchone()
                if role and role.get('permissions') and isinstance(role['permissions'], str):
                    role['permissions'] = json.loads(role['permissions'])
                return role
        finally:
            conn.close()

    @staticmethod
    def get_all():
        """获取所有角色"""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT id, name, display_name, description, status, created_at
                    FROM roles
                    WHERE status = 1
                    ORDER BY id
                """)
                roles = cursor.fetchall()
            return roles
        finally:
            conn.close()

    @staticmethod
    def list(page=1, page_size=20, keyword=None):
        """获取角色列表"""
        conn = get_db_connection()
        try:
            conditions = []
            params = []

            if keyword:
                conditions.append('(name LIKE %s OR display_name LIKE %s)')
                keyword_pattern = f'%{keyword}%'
                params.extend([keyword_pattern, keyword_pattern])

            where_clause = ' AND '.join(conditions) if conditions else '1=1'
            offset = (page - 1) * page_size

            with conn.cursor() as cursor:
                # 总数
                cursor.execute(f"""
                    SELECT COUNT(*) as total FROM roles WHERE {where_clause}
                """, params)
                total = cursor.fetchone()['total']

                # 列表
                params_for_list = params.copy() + [page_size, offset]
                cursor.execute(f"""
                    SELECT id, name, display_name, description, permissions, status, created_at
                    FROM roles
                    WHERE {where_clause}
                    ORDER BY created_at DESC
                    LIMIT %s OFFSET %s
                """, params_for_list)
                roles = cursor.fetchall()

            # 解析权限 JSON
            for role in roles:
                if role.get('permissions') and isinstance(role['permissions'], str):
                    role['permissions'] = json.loads(role['permissions'])

            return {
                'total': total,
                'page': page,
                'page_size': page_size,
                'total_pages': (total + page_size - 1) // page_size,
                'roles': roles
            }
        finally:
            conn.close()

    @staticmethod
    def update(role_id, **kwargs):
        """更新角色"""
        allowed_fields = ['display_name', 'description', 'permissions', 'status']
        update_data = {k: v for k, v in kwargs.items() if k in allowed_fields}

        if not update_data:
            return False

        # 处理 permissions
        if 'permissions' in update_data and isinstance(update_data['permissions'], list):
            update_data['permissions'] = json.dumps(update_data['permissions'])

        conn = get_db_connection()
        try:
            set_clause = ', '.join([f'{k} = %s' for k in update_data.keys()])
            values = list(update_data.values()) + [role_id]

            with conn.cursor() as cursor:
                cursor.execute(f"""
                    UPDATE roles SET {set_clause}
                    WHERE id = %s
                """, values)
                conn.commit()
            return True
        finally:
            conn.close()

    @staticmethod
    def delete(role_id):
        """删除角色"""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                # 检查是否有用户关联
                cursor.execute("SELECT COUNT(*) as count FROM user_roles WHERE role_id = %s", (role_id,))
                if cursor.fetchone()['count'] > 0:
                    return False, '角色下有用户关联，无法删除'

                cursor.execute("DELETE FROM roles WHERE id = %s", (role_id,))
                conn.commit()
            return True, None
        finally:
            conn.close()


class UserRole:
    """用户角色关联模型"""

    @staticmethod
    def add(user_id, role_id):
        """添加用户角色关联"""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO user_roles (user_id, role_id)
                    VALUES (%s, %s)
                    ON DUPLICATE KEY UPDATE created_at = NOW()
                """, (user_id, role_id))
                conn.commit()
            return True
        finally:
            conn.close()

    @staticmethod
    def remove(user_id, role_id):
        """移除用户角色关联"""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    DELETE FROM user_roles
                    WHERE user_id = %s AND role_id = %s
                """, (user_id, role_id))
                conn.commit()
            return True
        finally:
            conn.close()

    @staticmethod
    def get_roles_by_user(user_id):
        """获取用户的角色列表"""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT r.id, r.name, r.display_name, r.description
                    FROM roles r
                    INNER JOIN user_roles ur ON r.id = ur.role_id
                    WHERE ur.user_id = %s AND r.status = 1
                """, (user_id,))
                return cursor.fetchall()
        finally:
            conn.close()

    @staticmethod
    def get_users_by_role(role_id):
        """获取角色的用户列表"""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT u.id, u.username, u.nickname, u.email, u.phone
                    FROM users u
                    INNER JOIN user_roles ur ON u.id = ur.user_id
                    WHERE ur.role_id = %s AND u.deleted_at IS NULL
                """, (role_id,))
                return cursor.fetchall()
        finally:
            conn.close()
