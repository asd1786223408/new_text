# -*- coding: utf-8 -*-
"""
部门管理模块
"""
from flask import Blueprint, request, session
from ..models.department import Department
from ..utils.response import success, error

departments_bp = Blueprint('departments', __name__, url_prefix='/api/departments')


@departments_bp.route('/tree', methods=['GET'])
def get_department_tree():
    """
    获取部门树
    GET /api/departments/tree
    """
    tree = Department.get_tree()
    return success(tree)


@departments_bp.route('/list', methods=['GET'])
def list_departments():
    """
    获取部门列表（扁平化）
    GET /api/departments/list
    """
    departments = Department.get_all_list()
    return success(departments)


@departments_bp.route('/<int:dept_id>', methods=['GET'])
def get_department(dept_id):
    """
    获取部门详情
    GET /api/departments/<部门 ID>
    """
    dept = Department.get_by_id(dept_id)
    if not dept:
        return error('部门不存在', 404)
    return success(dept)


@departments_bp.route('', methods=['POST'])
def create_department():
    """
    创建部门
    POST /api/departments
    Content-Type: application/json

    参数:
    - name: 部门名称（必填）
    - parent_id: 父部门 ID（默认 0）
    - leader_id: 负责人 ID
    """
    data = request.get_json()
    if not data:
        return error('参数不能为空', 400)

    name = data.get('name', '').strip()
    if not name:
        return error('部门名称不能为空', 400)

    parent_id = data.get('parent_id', 0)
    leader_id = data.get('leader_id')

    dept_id = Department.create(name, parent_id, leader_id)
    return success({'dept_id': dept_id}, '部门创建成功')


@departments_bp.route('/<int:dept_id>', methods=['PUT'])
def update_department(dept_id):
    """
    更新部门
    PUT /api/departments/<部门 ID>
    Content-Type: application/json

    参数:
    - name: 部门名称
    - parent_id: 父部门 ID
    - leader_id: 负责人 ID
    - sort: 排序
    - status: 状态
    """
    data = request.get_json()
    if not data:
        return error('参数不能为空', 400)

    dept = Department.get_by_id(dept_id)
    if not dept:
        return error('部门不存在', 404)

    success_flag, message = Department.update(dept_id, **data)
    if not success_flag:
        return error(message or '更新失败', 400)

    return success(message='部门更新成功')


@departments_bp.route('/<int:dept_id>', methods=['DELETE'])
def delete_department(dept_id):
    """
    删除部门
    DELETE /api/departments/<部门 ID>
    """
    dept = Department.get_by_id(dept_id)
    if not dept:
        return error('部门不存在', 404)

    success_flag, message = Department.delete(dept_id)
    if not success_flag:
        return error(message, 400)

    return success(message='部门删除成功')
