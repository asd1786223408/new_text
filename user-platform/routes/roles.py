# -*- coding: utf-8 -*-
"""
角色管理模块
"""
from flask import Blueprint, request
from ..models.role import Role, UserRole
from ..utils.response import success, error

roles_bp = Blueprint('roles', __name__, url_prefix='/api/roles')


@roles_bp.route('', methods=['GET'])
def list_roles():
    """
    获取角色列表
    GET /api/roles?keyword=关键词&page=页码&page_size=每页数量
    """
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 20))
    keyword = request.args.get('keyword', '')

    result = Role.list(page, page_size, keyword)
    return success(result)


@roles_bp.route('/all', methods=['GET'])
def get_all_roles():
    """
    获取所有角色（简化列表）
    GET /api/roles/all
    """
    roles = Role.get_all()
    return success(roles)


@roles_bp.route('/<int:role_id>', methods=['GET'])
def get_role(role_id):
    """
    获取角色详情
    GET /api/roles/<角色 ID>
    """
    role = Role.get_by_id(role_id)
    if not role:
        return error('角色不存在', 404)
    return success(role)


@roles_bp.route('', methods=['POST'])
def create_role():
    """
    创建角色
    POST /api/roles
    Content-Type: application/json

    参数:
    - name: 角色标识（必填）
    - display_name: 显示名称（必填）
    - description: 描述
    - permissions: 权限列表
    """
    data = request.get_json()
    if not data:
        return error('参数不能为空', 400)

    name = data.get('name', '').strip()
    display_name = data.get('display_name', '').strip()

    if not name or not display_name:
        return error('角色标识和显示名称不能为空', 400)

    # 检查角色标识是否存在
    existing = Role.get_by_id(Role.get_by_name(name)['id'] if Role.get_by_name(name) else 0)
    if Role.get_by_name(name):
        return error('角色标识已存在', 400)

    role_id = Role.create(name, display_name, data.get('description', ''), data.get('permissions', []))
    return success({'role_id': role_id}, '角色创建成功')


@roles_bp.route('/<int:role_id>', methods=['PUT'])
def update_role(role_id):
    """
    更新角色
    PUT /api/roles/<角色 ID>
    Content-Type: application/json

    参数:
    - display_name: 显示名称
    - description: 描述
    - permissions: 权限列表
    - status: 状态
    """
    data = request.get_json()
    if not data:
        return error('参数不能为空', 400)

    role = Role.get_by_id(role_id)
    if not role:
        return error('角色不存在', 404)

    Role.update(role_id, **data)
    return success(message='角色更新成功')


@roles_bp.route('/<int:role_id>', methods=['DELETE'])
def delete_role(role_id):
    """
    删除角色
    DELETE /api/roles/<角色 ID>
    """
    role = Role.get_by_id(role_id)
    if not role:
        return error('角色不存在', 404)

    success_flag, message = Role.delete(role_id)
    if not success_flag:
        return error(message, 400)

    return success(message='角色删除成功')


@roles_bp.route('/<int:role_id>/users', methods=['GET'])
def get_role_users(role_id):
    """
    获取角色下的用户列表
    GET /api/roles/<角色 ID>/users
    """
    users = UserRole.get_users_by_role(role_id)
    return success(users)
