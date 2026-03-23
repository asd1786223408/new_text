# -*- coding: utf-8 -*-
"""
认证登录模块
"""
import uuid
from flask import Blueprint, request, session
from ..models.user import User
from ..utils.response import success, error

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    用户登录
    POST /api/auth/login

    参数:
    - account: 用户名/邮箱/手机号
    - password: 密码
    """
    data = request.get_json()
    if not data:
        return error('参数不能为空', 400)

    account = data.get('account', '').strip()
    password = data.get('password', '')

    if not account or not password:
        return error('账号和密码不能为空', 400)

    # 查找用户
    user = User.get_by_username(account)
    if not user:
        user = User.get_by_email(account)
    if not user:
        user = User.get_by_phone(account)

    if not user:
        User.record_login_log(None, 'password', 0, request.remote_addr, request.user_agent.string, '用户不存在')
        return error('用户不存在', 404)

    # 检查用户状态
    if user['status'] == 0:
        return error('账号已被禁用', 403)
    if user['status'] == 2:
        return error('账号已被锁定', 403)

    # 验证密码
    if not User.verify_password(password, user['password_hash']):
        User.record_login_log(user['id'], 'password', 0, request.remote_addr, request.user_agent.string, '密码错误')
        return error('密码错误', 400)

    # 更新登录信息
    User.update_login_info(user['id'], request.remote_addr)
    User.record_login_log(user['id'], 'password', 1, request.remote_addr, request.user_agent.string)

    # 生成 Session
    session_id = str(uuid.uuid4())
    session['user_id'] = user['id']
    session['username'] = user['username']
    session['permissions'] = user.get('permissions', [])

    return success({
        'user_id': user['id'],
        'username': user['username'],
        'nickname': user.get('nickname', ''),
        'avatar': user.get('avatar', ''),
        'permissions': user.get('permissions', [])
    }, '登录成功')


@auth_bp.route('/logout', methods=['POST'])
def logout():
    """
    用户登出
    POST /api/auth/logout
    """
    session.clear()
    return success(message='登出成功')


@auth_bp.route('/info', methods=['GET'])
def get_info():
    """
    获取当前用户信息
    GET /api/auth/info
    """
    user_id = session.get('user_id')
    if not user_id:
        return error('未登录', 401)

    user = User.get_by_id(user_id)
    if not user:
        session.clear()
        return error('用户不存在', 404)

    return success({
        'id': user['id'],
        'username': user['username'],
        'nickname': user.get('nickname', ''),
        'avatar': user.get('avatar', ''),
        'email': user.get('email', ''),
        'phone': user.get('phone', ''),
        'department_id': user.get('department_id'),
        'position': user.get('position'),
        'permissions': user.get('permissions', [])
    })


@auth_bp.route('/change-password', methods=['POST'])
def change_password():
    """
    修改密码
    POST /api/auth/change-password

    参数:
    - old_password: 原密码
    - new_password: 新密码
    """
    user_id = session.get('user_id')
    if not user_id:
        return error('未登录', 401)

    data = request.get_json()
    if not data:
        return error('参数不能为空', 400)

    old_password = data.get('old_password', '')
    new_password = data.get('new_password', '')

    if not old_password or not new_password:
        return error('密码不能为空', 400)

    if len(new_password) < 6:
        return error('密码长度不能少于 6 位', 400)

    user = User.get_by_id(user_id)
    if not User.verify_password(old_password, user['password_hash']):
        return error('原密码错误', 400)

    # 更新密码
    from ..models.user import User as UserModel
    import bcrypt
    new_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    UserModel.update(user_id, password_hash=new_hash)

    return success(message='密码修改成功')
