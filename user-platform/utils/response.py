# -*- coding: utf-8 -*-
"""
统一响应格式
"""
from flask import jsonify


def success(data=None, message='操作成功', status_code=200):
    """成功响应"""
    response = {
        'code': 0,
        'message': message,
        'data': data if data is not None else {}
    }
    return jsonify(response), status_code


def error(message='操作失败', status_code=400, data=None):
    """错误响应"""
    response = {
        'code': 1,
        'message': message,
        'data': data if data is not None else {}
    }
    return jsonify(response), status_code
