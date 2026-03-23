#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
部门管理路由
"""

from flask import Blueprint, request, jsonify
from models.database import db
from services.department_service import DepartmentService
from utils.response import success, error
from routes.auth import login_required, permission_required

bp = Blueprint('departments', __name__)


@bp.route('', methods=['GET'])
@login_required
def list_departments():
    """获取部门列表（树形结构）"""
    dept_service = DepartmentService()
    departments = dept_service.get_all_departments()
    return success(departments)


@bp.route('/tree', methods=['GET'])
@login_required
def get_department_tree():
    """获取部门树形结构"""
    dept_service = DepartmentService()
    tree = dept_service.get_department_tree()
    return success(tree)


@bp.route('/<int:dept_id>', methods=['GET'])
@login_required
def get_department(dept_id):
    """获取部门详情"""
    dept_service = DepartmentService()
    dept = dept_service.get_department(dept_id)

    if not dept:
        return error('部门不存在', 404)

    return success(dept)


@bp.route('', methods=['POST'])
@login_required
@permission_required('dept:manage')
def create_department():
    """创建部门"""
    data = request.get_json()
    if not data:
        return error('参数不能为空', 400)

    dept_service = DepartmentService()
    result = dept_service.create_department(data)

    if result['success']:
        return success({'dept_id': result['dept_id']}, '创建成功')
    else:
        return error(result['message'], 400)


@bp.route('/<int:dept_id>', methods=['PUT'])
@login_required
@permission_required('dept:manage')
def update_department(dept_id):
    """更新部门"""
    data = request.get_json()
    if not data:
        return error('参数不能为空', 400)

    dept_service = DepartmentService()
    result = dept_service.update_department(dept_id, data)

    if result['success']:
        return success(message='更新成功')
    else:
        return error(result['message'], 400)


@bp.route('/<int:dept_id>', methods=['DELETE'])
@login_required
@permission_required('dept:manage')
def delete_department(dept_id):
    """删除部门"""
    dept_service = DepartmentService()
    result = dept_service.delete_department(dept_id)

    if result['success']:
        return success(message='删除成功')
    else:
        return error(result['message'], 400)
