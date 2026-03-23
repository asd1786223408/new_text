#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
操作日志路由
"""

from flask import Blueprint, request, jsonify
from models.database import db
from utils.response import success, error
from routes.auth import login_required, permission_required

bp = Blueprint('logs', __name__)


@bp.route('', methods=['GET'])
@login_required
@permission_required('system:logs')
def list_logs():
    """
    获取操作日志列表
    GET /api/logs?page=1&limit=20&user_id=&action=&module=
    """
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 20, type=int)
    user_id = request.args.get('user_id', type=int)
    action = request.args.get('action', '')
    module = request.args.get('module', '')

    offset = (page - 1) * limit
    conditions = ["1=1"]
    params = []

    if user_id:
        conditions.append("ol.user_id = %s")
        params.append(user_id)

    if action:
        conditions.append("ol.action LIKE %s")
        params.append(f'%{action}%')

    if module:
        conditions.append("ol.module LIKE %s")
        params.append(f'%{module}%')

    where_sql = " AND ".join(conditions)

    # 查询总数
    count_sql = f"SELECT COUNT(*) as total FROM operation_logs ol WHERE {where_sql}"
    total_result = db.fetch_one(count_sql, tuple(params))
    total = total_result['total'] if total_result else 0

    # 查询数据
    sql = f"""
        SELECT ol.*, u.username, u.nickname
        FROM operation_logs ol
        LEFT JOIN users u ON ol.user_id = u.id
        WHERE {where_sql}
        ORDER BY ol.created_at DESC
        LIMIT %s OFFSET %s
    """
    params.extend([limit, offset])
    logs = db.fetch_all(sql, tuple(params))

    # 转换数据类型
    for log in logs:
        if log.get('params') and isinstance(log['params'], str):
            import json
            try:
                log['params'] = json.loads(log['params'])
            except:
                pass

    return success({
        'list': logs,
        'total': total,
        'page': page,
        'limit': limit
    })


@bp.route('/stats', methods=['GET'])
@login_required
def get_stats():
    """获取统计数据"""
    # 总操作数
    count_result = db.fetch_one("SELECT COUNT(*) as total FROM operation_logs")

    # 各模块操作数
    module_result = db.fetch_all("""
        SELECT module, COUNT(*) as count
        FROM operation_logs
        WHERE created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
        GROUP BY module
        ORDER BY count DESC
        LIMIT 5
    """)

    # 最近活跃用户
    user_result = db.fetch_all("""
        SELECT ol.user_id, u.username, u.nickname, COUNT(*) as count
        FROM operation_logs ol
        LEFT JOIN users u ON ol.user_id = u.id
        WHERE ol.user_id > 0 AND ol.created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
        GROUP BY ol.user_id, u.username, u.nickname
        ORDER BY count DESC
        LIMIT 5
    """)

    return success({
        'total': count_result['total'] if count_result else 0,
        'modules': module_result,
        'active_users': user_result
    })
