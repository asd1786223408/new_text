#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
部门服务
"""

from models.database import db


class DepartmentService:
    def get_all_departments(self):
        """获取所有部门"""
        sql = "SELECT * FROM departments ORDER BY level, sort"
        return db.fetch_all(sql)

    def get_department_tree(self):
        """获取部门树形结构"""
        departments = self.get_all_departments()

        # 构建树形结构
        tree = []
        dept_map = {dept['id']: {**dept, 'children': []} for dept in departments}

        for dept in departments:
            if dept['parent_id'] == 0:
                tree.append(dept_map[dept['id']])
            else:
                parent = dept_map.get(dept['parent_id'])
                if parent:
                    parent['children'].append(dept_map[dept['id']])

        return tree

    def get_department(self, dept_id):
        """获取部门详情"""
        sql = "SELECT * FROM departments WHERE id = %s"
        return db.fetch_one(sql, (dept_id,))

    def create_department(self, data):
        """创建部门"""
        name = data.get('name', '').strip()
        parent_id = data.get('parent_id', 0)
        sort = data.get('sort', 0)
        leader_id = data.get('leader_id')

        if not name:
            return {'success': False, 'message': '部门名称不能为空'}

        # 计算层级
        if parent_id == 0:
            level = 1
        else:
            parent = self.get_department(parent_id)
            if not parent:
                return {'success': False, 'message': '父部门不存在'}
            level = parent['level'] + 1

        # 插入部门
        sql = """INSERT INTO departments (name, parent_id, level, sort, leader_id)
                 VALUES (%s, %s, %s, %s, %s)"""
        db.execute(sql, (name, parent_id, level, sort, leader_id))

        result = db.fetch_one("SELECT LAST_INSERT_ID() as id")
        return {'success': True, 'dept_id': result['id']}

    def update_department(self, dept_id, data):
        """更新部门"""
        dept = self.get_department(dept_id)
        if not dept:
            return {'success': False, 'message': '部门不存在'}

        fields = []
        params = []

        for key in ['name', 'parent_id', 'sort', 'leader_id', 'status']:
            if key in data:
                fields.append(f"{key} = %s")
                params.append(data[key])

        if not fields:
            return {'success': False, 'message': '没有要更新的字段'}

        # 检查父部门变更后的层级
        if 'parent_id' in data and data['parent_id'] != dept['parent_id']:
            new_parent_id = data['parent_id']
            if new_parent_id == dept_id:
                return {'success': False, 'message': '不能将自己设为父部门'}

            # 检查是否将子部门设为父部门（会导致循环）
            children = self._get_all_children(dept_id)
            if new_parent_id in children:
                return {'success': False, 'message': '不能将子部门设为父部门'}

        params.append(dept_id)
        sql = f"UPDATE departments SET {', '.join(fields)} WHERE id = %s"
        db.execute(sql, tuple(params))

        return {'success': True}

    def delete_department(self, dept_id):
        """删除部门"""
        dept = self.get_department(dept_id)
        if not dept:
            return {'success': False, 'message': '部门不存在'}

        # 检查是否有子部门
        children = self._get_all_children(dept_id)
        if children:
            return {'success': False, 'message': '该部门下有子部门，无法删除'}

        # 检查是否有用户
        sql = "SELECT COUNT(*) as count FROM users WHERE department_id = %s"
        result = db.fetch_one(sql, (dept_id,))
        if result['count'] > 0:
            return {'success': False, 'message': '该部门下有用户，无法删除'}

        sql = "DELETE FROM departments WHERE id = %s"
        db.execute(sql, (dept_id,))

        return {'success': True}

    def _get_all_children(self, dept_id):
        """获取所有子部门 ID"""
        sql = "SELECT id FROM departments WHERE parent_id = %s"
        children = db.fetch_all(sql, (dept_id,))
        result = [c['id'] for c in children]

        for child in children:
            result.extend(self._get_all_children(child['id']))

        return result
