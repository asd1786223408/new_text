#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
认证路由 - 登录、登出、注册
"""

from flask import Blueprint, request, jsonify, session
from models.database import db
from services.auth_service import AuthService
from utils.response import success, error
from functools import wraps

bp = Blueprint('auth', __name__)


@bp.route('/login', methods=['POST'])
def login():
    """
    用户登录
    POST /api/auth/login

    参数:
    - account: 邮箱或手机号
    - password: 密码
    """
    data = request.get_json()
    if not data:
        return error('参数不能为空', 400)

    account = data.get('account', '').strip()
    password = data.get('password', '')

    if not account or not password:
        return error('账号和密码不能为空', 400)

    auth_service = AuthService()
    user = auth_service.authenticate(account, password)

    if not user:
        return error('账号或密码错误', 401)

    if user['status'] == 0:
        return error('账号已被禁用', 403)

    if user['status'] == 2 and user.get('locked_until'):
        return error('账号已被锁定', 403)

    # 设置 session
    session['user_id'] = user['id']
    session['username'] = user['username']
    session['permissions'] = user.get('permissions', [])

    # 更新登录信息
    auth_service.update_login_info(user['id'], request.remote_addr)

    return success({
        'user_id': user['id'],
        'username': user['username'],
        'nickname': user.get('nickname', ''),
        'permissions': user.get('permissions', [])
    }, '登录成功')


@bp.route('/logout', methods=['POST'])
def logout():
    """用户登出"""
    session.clear()
    return success(message='登出成功')


@bp.route('/register', methods=['POST'])
def register():
    """
    用户注册
    POST /api/auth/register

    参数:
    - username: 用户名
    - password: 密码
    - email: 邮箱（可选）
    - phone: 手机号（可选）
    """
    data = request.get_json()
    if not data:
        return error('参数不能为空', 400)

    username = data.get('username', '').strip()
    password = data.get('password', '')
    email = data.get('email', '').strip()
    phone = data.get('phone', '').strip()

    if not username or not password:
        return error('用户名和密码不能为空', 400)

    if not email and not phone:
        return error('邮箱和手机号至少填写一项', 400)

    auth_service = AuthService()
    result = auth_service.register(username, password, email, phone)

    if result['success']:
        return success({'user_id': result['user_id']}, '注册成功')
    else:
        return error(result['message'], 400)


@bp.route('/current', methods=['GET'])
def get_current_user():
    """获取当前登录用户信息"""
    user_id = session.get('user_id')
    if not user_id:
        return error('未登录', 401)

    auth_service = AuthService()
    user = auth_service.get_user_info(user_id)

    if not user:
        session.clear()
        return error('用户不存在', 404)

    return success(user)


def login_required(f):
    """登录检查装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_id'):
            return error('请先登录', 401)
        return f(*args, **kwargs)
    return decorated_function


def permission_required(permission):
    """权限检查装饰器"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not session.get('user_id'):
                return error('请先登录', 401)

            permissions = session.get('permissions', [])
            if permission not in permissions:
                return error('没有权限', 403)

            return f(*args, **kwargs)
        return decorated_function
    return decorator
