# -*- coding: utf-8 -*-
"""
部门模型
"""
from ..utils.db_pool import get_db_connection


class Department:
    """部门模型类"""

    @staticmethod
    def create(name, parent_id=0, leader_id=None):
        """创建部门"""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                # 获取父部门层级
                if parent_id == 0:
                    level = 1
                else:
                    cursor.execute("SELECT level FROM departments WHERE id = %s", (parent_id,))
                    parent = cursor.fetchone()
                    level = parent['level'] + 1 if parent else 1

                cursor.execute("""
                    INSERT INTO departments (name, parent_id, level, leader_id)
                    VALUES (%s, %s, %s, %s)
                """, (name, parent_id, level, leader_id))
                dept_id = cursor.lastrowid
                conn.commit()
            return dept_id
        finally:
            conn.close()

    @staticmethod
    def get_by_id(dept_id):
        """根据 ID 获取部门"""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT d.*, p.name as parent_name, l.nickname as leader_name
                    FROM departments d
                    LEFT JOIN departments p ON d.parent_id = p.id
                    LEFT JOIN users l ON d.leader_id = l.id
                    WHERE d.id = %s
                """, (dept_id,))
                return cursor.fetchone()
        finally:
            conn.close()

    @staticmethod
    def get_tree(parent_id=0):
        """获取部门树"""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT d.*, COUNT(u.id) as user_count
                    FROM departments d
                    LEFT JOIN users u ON d.id = u.department_id AND u.deleted_at IS NULL
                    WHERE d.parent_id = %s AND d.status = 1
                    GROUP BY d.id
                    ORDER BY d.sort, d.id
                """, (parent_id,))
                departments = cursor.fetchall()

            # 递归获取子部门
            for dept in departments:
                children = Department.get_tree(dept['id'])
                dept['children'] = children if children else []

            return departments
        finally:
            conn.close()

    @staticmethod
    def get_all_list():
        """获取所有部门列表（扁平化）"""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT id, name, parent_id, level, sort, status
                    FROM departments
                    WHERE status = 1
                    ORDER BY level, sort, id
                """)
                return cursor.fetchall()
        finally:
            conn.close()

    @staticmethod
    def update(dept_id, **kwargs):
        """更新部门信息"""
        allowed_fields = ['name', 'parent_id', 'leader_id', 'sort', 'status']
        update_data = {k: v for k, v in kwargs.items() if k in allowed_fields}

        if not update_data:
            return False

        conn = get_db_connection()
        try:
            # 如果修改了父部门，需要检查循环引用
            if 'parent_id' in update_data:
                new_parent_id = update_data['parent_id']
                if new_parent_id == dept_id:
                    return False
                # 检查新父部门是否是该部门的子部门
                children = Department._get_all_children(dept_id)
                if new_parent_id in children:
                    return False

            set_clause = ', '.join([f'{k} = %s' for k in update_data.keys()])
            values = list(update_data.values()) + [dept_id]

            with conn.cursor() as cursor:
                cursor.execute(f"""
                    UPDATE departments SET {set_clause}
                    WHERE id = %s
                """, values)
                conn.commit()
            return True
        finally:
            conn.close()

    @staticmethod
    def _get_all_children(dept_id):
        """获取部门的所有子部门 ID"""
        conn = get_db_connection()
        try:
            children = set()
            with conn.cursor() as cursor:
                cursor.execute("SELECT id FROM departments WHERE parent_id = %s", (dept_id,))
                for row in cursor.fetchall():
                    children.add(row['id'])
                    children.update(Department._get_all_children(row['id']))
            return children
        finally:
            conn.close()

    @staticmethod
    def delete(dept_id):
        """删除部门（检查是否有子部门或用户）"""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                # 检查是否有子部门
                cursor.execute("SELECT COUNT(*) as count FROM departments WHERE parent_id = %s", (dept_id,))
                if cursor.fetchone()['count'] > 0:
                    return False, '存在子部门，无法删除'

                # 检查是否有用户
                cursor.execute("SELECT COUNT(*) as count FROM users WHERE department_id = %s AND deleted_at IS NULL", (dept_id,))
                if cursor.fetchone()['count'] > 0:
                    return False, '部门下存在用户，无法删除'

                cursor.execute("DELETE FROM departments WHERE id = %s", (dept_id,))
                conn.commit()
            return True, None
        finally:
            conn.close()
