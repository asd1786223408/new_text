# -*- coding: utf-8 -*-
"""
用户模型
"""
import bcrypt
from datetime import datetime
from ..utils.db_pool import get_db_connection


class User:
    """用户模型类"""

    @staticmethod
    def hash_password(password):
        """密码加密"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    @staticmethod
    def verify_password(password, password_hash):
        """验证密码"""
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))

    @staticmethod
    def create(username, password, email=None, phone=None, nickname=None, department_id=None, position=None):
        """创建用户"""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO users (username, password_hash, email, phone, nickname, department_id, position, permissions)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, '[]')
                """, (username, User.hash_password(password), email, phone, nickname, department_id, position))
                user_id = cursor.lastrowid
                conn.commit()
            return user_id
        finally:
            conn.close()

    @staticmethod
    def get_by_id(user_id):
        """根据 ID 获取用户"""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT id, username, email, phone, avatar, nickname, gender, birthday,
                           department_id, position, status, permissions, last_login_at,
                           last_login_ip, created_at, updated_at
                    FROM users
                    WHERE id = %s AND deleted_at IS NULL
                """, (user_id,))
                return cursor.fetchone()
        finally:
            conn.close()

    @staticmethod
    def get_by_username(username):
        """根据用户名获取用户（包含密码）"""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM users
                    WHERE username = %s AND deleted_at IS NULL
                """, (username,))
                return cursor.fetchone()
        finally:
            conn.close()

    @staticmethod
    def get_by_email(email):
        """根据邮箱获取用户"""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT id, username, email, phone, avatar, nickname, gender, birthday,
                           department_id, position, status, permissions, last_login_at, created_at
                    FROM users
                    WHERE email = %s AND deleted_at IS NULL
                """, (email,))
                return cursor.fetchone()
        finally:
            conn.close()

    @staticmethod
    def get_by_phone(phone):
        """根据手机号获取用户"""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT id, username, email, phone, avatar, nickname, gender, birthday,
                           department_id, position, status, permissions, last_login_at, created_at
                    FROM users
                    WHERE phone = %s AND deleted_at IS NULL
                """, (phone,))
                return cursor.fetchone()
        finally:
            conn.close()

    @staticmethod
    def update(user_id, **kwargs):
        """更新用户信息"""
        allowed_fields = ['email', 'phone', 'avatar', 'nickname', 'gender', 'birthday', 'department_id', 'position', 'status']
        update_data = {k: v for k, v in kwargs.items() if k in allowed_fields}

        if not update_data:
            return False

        conn = get_db_connection()
        try:
            set_clause = ', '.join([f'{k} = %s' for k in update_data.keys()])
            values = list(update_data.values()) + [user_id]

            with conn.cursor() as cursor:
                cursor.execute(f"""
                    UPDATE users SET {set_clause}
                    WHERE id = %s AND deleted_at IS NULL
                """, values)
                conn.commit()
            return True
        finally:
            conn.close()

    @staticmethod
    def update_permissions(user_id, permissions):
        """更新用户权限"""
        import json
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE users SET permissions = %s
                    WHERE id = %s AND deleted_at IS NULL
                """, (json.dumps(permissions), user_id))
                conn.commit()
            return True
        finally:
            conn.close()

    @staticmethod
    def delete(user_id):
        """软删除用户"""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE users SET deleted_at = NOW()
                    WHERE id = %s
                """, (user_id,))
                conn.commit()
            return True
        finally:
            conn.close()

    @staticmethod
    def list(page=1, page_size=20, department_id=None, status=None, keyword=None):
        """获取用户列表"""
        conn = get_db_connection()
        try:
            conditions = ['u.deleted_at IS NULL']
            params = []

            if department_id:
                conditions.append('u.department_id = %s')
                params.append(department_id)
            if status is not None:
                conditions.append('u.status = %s')
                params.append(status)
            if keyword:
                conditions.append('(u.username LIKE %s OR u.nickname LIKE %s OR u.email LIKE %s OR u.phone LIKE %s)')
                keyword_pattern = f'%{keyword}%'
                params.extend([keyword_pattern] * 4)

            where_clause = ' AND '.join(conditions)
            offset = (page - 1) * page_size

            with conn.cursor() as cursor:
                # 总数
                cursor.execute(f"""
                    SELECT COUNT(*) as total FROM users u WHERE {where_clause}
                """, params)
                total = cursor.fetchone()['total']

                # 列表
                params_for_list = params.copy() + [page_size, offset]
                cursor.execute(f"""
                    SELECT u.*, d.name as department_name
                    FROM users u
                    LEFT JOIN departments d ON u.department_id = d.id
                    WHERE {where_clause}
                    ORDER BY u.created_at DESC
                    LIMIT %s OFFSET %s
                """, params_for_list)
                users = cursor.fetchall()

            return {
                'total': total,
                'page': page,
                'page_size': page_size,
                'total_pages': (total + page_size - 1) // page_size,
                'users': users
            }
        finally:
            conn.close()

    @staticmethod
    def update_login_info(user_id, ip):
        """更新登录信息"""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE users
                    SET last_login_at = NOW(), last_login_ip = %s, login_failure_count = 0
                    WHERE id = %s
                """, (ip, user_id))
                conn.commit()
        finally:
            conn.close()

    @staticmethod
    def record_login_log(user_id, login_type, status, ip, user_agent, fail_reason=None):
        """记录登录日志"""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO login_logs (user_id, login_type, status, ip, user_agent, fail_reason)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (user_id, login_type, status, ip, user_agent, fail_reason))
                conn.commit()
        finally:
            conn.close()
