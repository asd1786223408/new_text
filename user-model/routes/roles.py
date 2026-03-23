#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
角色管理路由
"""

from flask import Blueprint, request, jsonify
from models.database import db
from services.role_service import RoleService
from utils.response import success, error
from routes.auth import login_required, permission_required

bp = Blueprint('roles', __name__)


@bp.route('', methods=['GET'])
@login_required
def list_roles():
    """获取角色列表"""
    role_service = RoleService()
    roles = role_service.get_all_roles()
    return success(roles)


@bp.route('/<int:role_id>', methods=['GET'])
@login_required
def get_role(role_id):
    """获取角色详情"""
    role_service = RoleService()
    role = role_service.get_role(role_id)

    if not role:
        return error('角色不存在', 404)

    return success(role)


@bp.route('', methods=['POST'])
@login_required
@permission_required('role:create')
def create_role():
    """创建角色"""
    data = request.get_json()
    if not data:
        return error('参数不能为空', 400)

    role_service = RoleService()
    result = role_service.create_role(data)

    if result['success']:
        return success({'role_id': result['role_id']}, '创建成功')
    else:
        return error(result['message'], 400)


@bp.route('/<int:role_id>', methods=['PUT'])
@login_required
@permission_required('role:update')
def update_role(role_id):
    """更新角色"""
    data = request.get_json()
    if not data:
        return error('参数不能为空', 400)

    role_service = RoleService()
    result = role_service.update_role(role_id, data)

    if result['success']:
        return success(message='更新成功')
    else:
        return error(result['message'], 400)


@bp.route('/<int:role_id>', methods=['DELETE'])
@login_required
@permission_required('role:delete')
def delete_role(role_id):
    """删除角色"""
    role_service = RoleService()
    result = role_service.delete_role(role_id)

    if result['success']:
        return success(message='删除成功')
    else:
        return error(result['message'], 400)


@bp.route('/<int:role_id>/permissions', methods=['PUT'])
@login_required
@permission_required('role:update')
def update_role_permissions(role_id):
    """更新角色权限"""
    data = request.get_json()
    if not data:
        return error('参数不能为空', 400)

    permission_ids = data.get('permission_ids', [])

    role_service = RoleService()
    result = role_service.update_role_permissions(role_id, permission_ids)

    if result['success']:
        return success(message='权限更新成功')
    else:
        return error(result['message'], 400)
