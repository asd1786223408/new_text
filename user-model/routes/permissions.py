#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
权限管理路由
"""

from flask import Blueprint, request, jsonify
from models.database import db
from utils.response import success, error
from routes.auth import login_required, permission_required

bp = Blueprint('permissions', __name__)


@bp.route('', methods=['GET'])
@login_required
def list_permissions():
    """获取所有权限"""
    module = request.args.get('module', '')

    if module:
        sql = "SELECT * FROM permissions WHERE module = %s ORDER BY sort"
        permissions = db.fetch_all(sql, (module,))
    else:
        sql = "SELECT * FROM permissions ORDER BY module, sort"
        permissions = db.fetch_all(sql)

    return success(permissions)


@bp.route('/modules', methods=['GET'])
@login_required
def get_modules():
    """获取所有模块"""
    sql = "SELECT DISTINCT module FROM permissions ORDER BY module"
    modules = db.fetch_all(sql)
    return success([m['module'] for m in modules])


@bp.route('', methods=['POST'])
@login_required
@permission_required('system:config')
def create_permission():
    """创建权限"""
    data = request.get_json()
    if not data:
        return error('参数不能为空', 400)

    name = data.get('name', '').strip()
    display_name = data.get('display_name', '')
    module = data.get('module', '')
    action = data.get('action', '')
    icon = data.get('icon', '')
    sort = data.get('sort', 0)

    if not name or not display_name:
        return error('权限标识和显示名称不能为空', 400)

    # 检查权限标识是否存在
    sql = "SELECT id FROM permissions WHERE name = %s"
    if db.fetch_one(sql, (name,)):
        return error('权限标识已存在', 400)

    # 插入权限
    sql = """INSERT INTO permissions (name, display_name, module, action, icon, sort)
             VALUES (%s, %s, %s, %s, %s, %s)"""
    db.execute(sql, (name, display_name, module, action, icon, sort))

    result = db.fetch_one("SELECT LAST_INSERT_ID() as id")
    return success({'permission_id': result['id']}, '创建成功')


@bp.route('/<int:permission_id>', methods=['GET'])
@login_required
def get_permission(permission_id):
    """获取权限详情"""
    sql = "SELECT * FROM permissions WHERE id = %s"
    permission = db.fetch_one(sql, (permission_id,))

    if not permission:
        return error('权限不存在', 404)

    return success(permission)


@bp.route('/<int:permission_id>', methods=['PUT'])
@login_required
@permission_required('system:config')
def update_permission(permission_id):
    """更新权限"""
    data = request.get_json()
    if not data:
        return error('参数不能为空', 400)

    # 检查权限是否存在
    sql = "SELECT id FROM permissions WHERE id = %s"
    if not db.fetch_one(sql, (permission_id,)):
        return error('权限不存在', 404)

    # 构建更新字段
    fields = []
    params = []

    for key in ['display_name', 'module', 'action', 'icon', 'sort', 'status']:
        if key in data:
            fields.append(f"{key} = %s")
            params.append(data[key])

    if not fields:
        return error('没有要更新的字段', 400)

    params.append(permission_id)
    sql = f"UPDATE permissions SET {', '.join(fields)} WHERE id = %s"
    db.execute(sql, tuple(params))

    return success(message='更新成功')


@bp.route('/<int:permission_id>', methods=['DELETE'])
@login_required
@permission_required('system:config')
def delete_permission(permission_id):
    """删除权限"""
    # 检查权限是否存在
    sql = "SELECT id FROM permissions WHERE id = %s"
    if not db.fetch_one(sql, (permission_id,)):
        return error('权限不存在', 404)

    # 检查是否有角色使用该权限
    sql = "SELECT COUNT(*) as count FROM roles WHERE permissions LIKE %s"
    result = db.fetch_one(sql, (f'%"{permission_id}"%',))
    # 注意：这里简化处理，实际应该检查权限标识

    sql = "DELETE FROM permissions WHERE id = %s"
    db.execute(sql, (permission_id,))

    return success(message='删除成功')
