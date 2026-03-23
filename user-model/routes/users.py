#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
用户管理路由
"""

from flask import Blueprint, request, jsonify, session
from models.database import db
from services.user_service import UserService
from utils.response import success, error
from routes.auth import login_required, permission_required

bp = Blueprint('users', __name__)


@bp.route('', methods=['GET'])
@login_required
def list_users():
    """获取用户列表"""
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 20, type=int)
    keyword = request.args.get('keyword', '')
    department_id = request.args.get('department_id', type=int)
    status = request.args.get('status', type=int)

    user_service = UserService()
    result = user_service.get_users(page, limit, keyword, department_id, status)

    return success(result)


@bp.route('/<int:user_id>', methods=['GET'])
@login_required
def get_user(user_id):
    """获取用户详情"""
    user_service = UserService()
    user = user_service.get_user(user_id)

    if not user:
        return error('用户不存在', 404)

    return success(user)


@bp.route('', methods=['POST'])
@login_required
@permission_required('user:create')
def create_user():
    """创建用户"""
    data = request.get_json()
    if not data:
        return error('参数不能为空', 400)

    user_service = UserService()
    result = user_service.create_user(data)

    if result['success']:
        return success({'user_id': result['user_id']}, '创建成功')
    else:
        return error(result['message'], 400)


@bp.route('/<int:user_id>', methods=['PUT'])
@login_required
@permission_required('user:update')
def update_user(user_id):
    """更新用户"""
    data = request.get_json()
    if not data:
        return error('参数不能为空', 400)

    user_service = UserService()
    result = user_service.update_user(user_id, data)

    if result['success']:
        return success(message='更新成功')
    else:
        return error(result['message'], 400)


@bp.route('/<int:user_id>', methods=['DELETE'])
@login_required
@permission_required('user:delete')
def delete_user(user_id):
    """删除用户（软删除）"""
    user_service = UserService()
    result = user_service.delete_user(user_id)

    if result['success']:
        return success(message='删除成功')
    else:
        return error(result['message'], 400)


@bp.route('/<int:user_id>/password', methods=['PUT'])
@login_required
def update_password(user_id):
    """修改密码"""
    # 只能修改自己的密码，除非有 user:update 权限
    current_user_id = session.get('user_id')
    permissions = session.get('permissions', [])

    if current_user_id != user_id and 'user:update' not in permissions:
        return error('没有权限', 403)

    data = request.get_json()
    old_password = data.get('old_password', '')
    new_password = data.get('new_password', '')

    if not new_password:
        return error('新密码不能为空', 400)

    user_service = UserService()
    result = user_service.change_password(user_id, old_password, new_password, current_user_id)

    if result['success']:
        return success(message='密码修改成功')
    else:
        return error(result['message'], 400)


@bp.route('/<int:user_id>/roles', methods=['PUT'])
@login_required
@permission_required('user:update')
def update_user_roles(user_id):
    """更新用户角色"""
    data = request.get_json()
    if not data:
        return error('参数不能为空', 400)

    role_ids = data.get('role_ids', [])

    user_service = UserService()
    result = user_service.update_user_roles(user_id, role_ids)

    if result['success']:
        return success(message='角色更新成功')
    else:
        return error(result['message'], 400)


@bp.route('/profile', methods=['GET'])
@login_required
def get_profile():
    """获取当前用户个人信息"""
    user_id = session.get('user_id')
    user_service = UserService()
    user = user_service.get_user(user_id)

    if not user:
        return error('用户不存在', 404)

    # 移除敏感字段
    user.pop('password_hash', None)
    user.pop('permissions', None)

    return success(user)


@bp.route('/profile', methods=['PUT'])
@login_required
def update_profile():
    """更新当前用户个人信息"""
    user_id = session.get('user_id')
    data = request.get_json()
    if not data:
        return error('参数不能为空', 400)

    # 只允许更新部分字段
    allowed_fields = ['nickname', 'avatar', 'gender', 'birthday', 'phone', 'email']
    update_data = {k: v for k, v in data.items() if k in allowed_fields}

    if not update_data:
        return error('没有要更新的字段', 400)

    user_service = UserService()
    result = user_service.update_user(user_id, update_data)

    if result['success']:
        # 更新 session 中的信息
        session['username'] = user_service.get_user(user_id).get('username', '')
        return success(message='个人资料更新成功')
    else:
        return error(result['message'], 400)
