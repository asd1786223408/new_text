# -*- coding: utf-8 -*-
"""
权限模型
"""
from ..utils.db_pool import get_db_connection


class Permission:
    """权限模型类"""

    @staticmethod
    def create(name, display_name, module, action, icon=None, sort=0):
        """创建权限"""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO permissions (name, display_name, module, action, icon, sort)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (name, display_name, module, action, icon, sort))
                perm_id = cursor.lastrowid
                conn.commit()
            return perm_id
        finally:
            conn.close()

    @staticmethod
    def get_by_id(perm_id):
        """根据 ID 获取权限"""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM permissions WHERE id = %s
                """, (perm_id,))
                return cursor.fetchone()
        finally:
            conn.close()

    @staticmethod
    def get_by_name(name):
        """根据名称获取权限"""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM permissions WHERE name = %s
                """, (name,))
                return cursor.fetchone()
        finally:
            conn.close()

    @staticmethod
    def get_all():
        """获取所有权限"""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM permissions
                    WHERE status = 1
                    ORDER BY module, sort, id
                """)
                return cursor.fetchall()
        finally:
            conn.close()

    @staticmethod
    def get_by_module(module):
        """根据模块获取权限"""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM permissions
                    WHERE module = %s AND status = 1
                    ORDER BY sort, id
                """, (module,))
                return cursor.fetchall()
        finally:
            conn.close()

    @staticmethod
    def get_by_group():
        """按模块分组获取权限"""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT module, GROUP_CONCAT(name ORDER BY sort) as permissions
                    FROM permissions
                    WHERE status = 1
                    GROUP BY module
                """)
                result = cursor.fetchall()
                return {row['module']: row['permissions'].split(',') for row in result}
        finally:
            conn.close()

    @staticmethod
    def update(perm_id, **kwargs):
        """更新权限"""
        allowed_fields = ['display_name', 'icon', 'sort', 'status']
        update_data = {k: v for k, v in kwargs.items() if k in allowed_fields}

        if not update_data:
            return False

        conn = get_db_connection()
        try:
            set_clause = ', '.join([f'{k} = %s' for k in update_data.keys()])
            values = list(update_data.values()) + [perm_id]

            with conn.cursor() as cursor:
                cursor.execute(f"""
                    UPDATE permissions SET {set_clause}
                    WHERE id = %s
                """, values)
                conn.commit()
            return True
        finally:
            conn.close()

    @staticmethod
    def delete(perm_id):
        """删除权限"""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("UPDATE permissions SET status = 0 WHERE id = %s", (perm_id,))
                conn.commit()
            return True
        finally:
            conn.close()
