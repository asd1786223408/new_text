# -*- coding: utf-8 -*-
"""
权限管理模块
"""
from flask import Blueprint, request
from ..models.permission import Permission
from ..utils.response import success, error

permissions_bp = Blueprint('permissions', __name__, url_prefix='/api/permissions')


@permissions_bp.route('', methods=['GET'])
def list_permissions():
    """
    获取所有权限
    GET /api/permissions
    """
    permissions = Permission.get_all()
    return success(permissions)


@permissions_bp.route('/grouped', methods=['GET'])
def get_grouped_permissions():
    """
    获取按模块分组的权限
    GET /api/permissions/grouped
    """
    grouped = Permission.get_by_group()
    return success(grouped)


@permissions_bp.route('/module/<module>', methods=['GET'])
def get_module_permissions(module):
    """
    获取指定模块的权限
    GET /api/permissions/module/<模块名>
    """
    permissions = Permission.get_by_module(module)
    return success(permissions)


@permissions_bp.route('', methods=['POST'])
def create_permission():
    """
    创建权限
    POST /api/permissions
    Content-Type: application/json

    参数:
    - name: 权限标识（必填）
    - display_name: 显示名称（必填）
    - module: 所属模块（必填）
    - action: 操作类型（必填）
    - icon: 图标
    - sort: 排序
    """
    data = request.get_json()
    if not data:
        return error('参数不能为空', 400)

    name = data.get('name', '').strip()
    display_name = data.get('display_name', '').strip()
    module = data.get('module', '').strip()
    action = data.get('action', '').strip()

    if not name or not display_name or not module or not action:
        return error('权限标识、显示名称、模块、操作类型不能为空', 400)

    # 检查权限标识是否存在
    if Permission.get_by_name(name):
        return error('权限标识已存在', 400)

    perm_id = Permission.create(name, display_name, module, action, data.get('icon'), data.get('sort', 0))
    return success({'perm_id': perm_id}, '权限创建成功')


@permissions_bp.route('/<int:perm_id>', methods=['PUT'])
def update_permission(perm_id):
    """
    更新权限
    PUT /api/permissions/<权限 ID>
    Content-Type: application/json

    参数:
    - display_name: 显示名称
    - icon: 图标
    - sort: 排序
    - status: 状态
    """
    data = request.get_json()
    if not data:
        return error('参数不能为空', 400)

    perm = Permission.get_by_id(perm_id)
    if not perm:
        return error('权限不存在', 404)

    Permission.update(perm_id, **data)
    return success(message='权限更新成功')


@permissions_bp.route('/<int:perm_id>', methods=['DELETE'])
def delete_permission(perm_id):
    """
    删除权限
    DELETE /api/permissions/<权限 ID>
    """
    perm = Permission.get_by_id(perm_id)
    if not perm:
        return error('权限不存在', 404)

    Permission.delete(perm_id)
    return success(message='权限删除成功')
