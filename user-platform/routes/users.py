# -*- coding: utf-8 -*-
"""
用户管理模块
"""
from flask import Blueprint, request, session
from ..models.user import User
from ..models.role import UserRole
from ..utils.response import success, error

users_bp = Blueprint('users', __name__, url_prefix='/api/users')


def check_permission(permission):
    """权限检查装饰器"""
    def decorator(f):
        def wrapper(*args, **kwargs):
            user_id = session.get('user_id')
            if not user_id:
                return error('未登录', 401)
            permissions = session.get('permissions', [])
            if 'super_admin' not in str(permissions) and permission not in permissions:
                return error('无权限', 403)
            return f(*args, **kwargs)
        wrapper.__name__ = f.__name__
        return wrapper
    return decorator


@users_bp.route('', methods=['GET'])
def list_users():
    """
    获取用户列表
    GET /api/users?department_id=部门 ID&status=状态&keyword=关键词&page=页码&page_size=每页数量
    """
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 20))
    department_id = request.args.get('department_id')
    status = request.args.get('status')
    keyword = request.args.get('keyword', '')

    result = User.list(page, page_size, department_id, status, keyword)
    return success(result)


@users_bp.route('/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """
    获取用户详情
    GET /api/users/<用户 ID>
    """
    user = User.get_by_id(user_id)
    if not user:
        return error('用户不存在', 404)

    # 获取用户角色
    roles = UserRole.get_roles_by_user(user_id)
    user['roles'] = roles

    return success(user)


@users_bp.route('', methods=['POST'])
def create_user():
    """
    创建用户
    POST /api/users
    Content-Type: application/json

    参数:
    - username: 用户名（必填）
    - password: 密码（必填）
    - email: 邮箱
    - phone: 手机号
    - nickname: 昵称
    - department_id: 部门 ID
    - position: 职位
    - role_ids: 角色 ID 列表
    """
    data = request.get_json()
    if not data:
        return error('参数不能为空', 400)

    username = data.get('username', '').strip()
    password = data.get('password', '')

    if not username or not password:
        return error('用户名和密码不能为空', 400)

    # 检查用户名是否存在
    if User.get_by_username(username):
        return error('用户名已存在', 400)

    # 检查邮箱
    email = data.get('email', '').strip()
    if email and User.get_by_email(email):
        return error('邮箱已被使用', 400)

    # 检查手机号
    phone = data.get('phone', '').strip()
    if phone and User.get_by_phone(phone):
        return error('手机号已被使用', 400)

    # 创建用户
    user_id = User.create(
        username=username,
        password=password,
        email=email or None,
        phone=phone or None,
        nickname=data.get('nickname'),
        department_id=data.get('department_id'),
        position=data.get('position')
    )

    # 关联角色
    role_ids = data.get('role_ids', [])
    for role_id in role_ids:
        UserRole.add(user_id, role_id)

    # 同步权限到用户
    if role_ids:
        permissions = set()
        for role_id in role_ids:
            role = UserRole.get_roles_by_user(user_id)
            for r in role:
                if r.get('permissions'):
                    permissions.update(r['permissions'])
        User.update_permissions(user_id, list(permissions))

    return success({'user_id': user_id}, '用户创建成功')


@users_bp.route('/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """
    更新用户
    PUT /api/users/<用户 ID>
    Content-Type: application/json

    参数:
    - email: 邮箱
    - phone: 手机号
    - nickname: 昵称
    - avatar: 头像 URL
    - gender: 性别
    - birthday: 生日
    - department_id: 部门 ID
    - position: 职位
    - status: 状态
    - role_ids: 角色 ID 列表
    """
    data = request.get_json()
    if not data:
        return error('参数不能为空', 400)

    user = User.get_by_id(user_id)
    if not user:
        return error('用户不存在', 404)

    # 检查邮箱是否重复
    email = data.get('email', '').strip()
    if email and email != user.get('email'):
        existing = User.get_by_email(email)
        if existing and existing['id'] != user_id:
            return error('邮箱已被使用', 400)

    # 检查手机号是否重复
    phone = data.get('phone', '').strip()
    if phone and phone != user.get('phone'):
        existing = User.get_by_phone(phone)
        if existing and existing['id'] != user_id:
            return error('手机号已被使用', 400)

    # 更新基本信息
    update_data = {k: v for k, v in data.items() if k in [
        'email', 'phone', 'nickname', 'avatar', 'gender', 'birthday',
        'department_id', 'position', 'status'
    ]}

    if update_data:
        User.update(user_id, **update_data)

    # 更新角色
    role_ids = data.get('role_ids')
    if role_ids is not None:
        # 删除现有角色
        existing_roles = UserRole.get_roles_by_user(user_id)
        for role in existing_roles:
            UserRole.remove(user_id, role['id'])
        # 添加新角色
        for role_id in role_ids:
            UserRole.add(user_id, role_id)

        # 同步权限
        permissions = set()
        for role_id in role_ids:
            role = UserRole.get_roles_by_user(user_id)
            for r in role:
                if r.get('permissions'):
                    permissions.update(r['permissions'])
        User.update_permissions(user_id, list(permissions))

    return success(message='用户更新成功')


@users_bp.route('/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """
    删除用户（软删除）
    DELETE /api/users/<用户 ID>
    """
    user = User.get_by_id(user_id)
    if not user:
        return error('用户不存在', 404)

    User.delete(user_id)
    return success(message='用户删除成功')
