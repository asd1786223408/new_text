#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
统一响应格式
"""

from flask import jsonify


def success(data=None, message='操作成功'):
    """成功响应"""
    return jsonify({
        'code': 0,
        'message': message,
        'data': data
    })


def error(message='操作失败', code=400, data=None):
    """错误响应"""
    return jsonify({
        'code': code,
        'message': message,
        'data': data
    }), code
