#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
用户管理平台 - Flask 应用
"""

from flask import Flask, session, jsonify, request
from flask_session import Session
from flask_cors import CORS
import redis
import json
import os

from models.database import db
from routes import auth, users, roles, departments, permissions, logs

def create_app():
    app = Flask(__name__)

    # 配置
    app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
    app.config['SESSION_TYPE'] = 'redis'
    app.config['SESSION_REDIS'] = redis.Redis(host='localhost', port=6379, db=0)
    app.config['SESSION_PERMANENT'] = True
    app.config['PERMANENT_SESSION_LIFETIME'] = 3600 * 24  # 24 小时

    # 初始化扩展
    Session(app)
    CORS(app, supports_credentials=True)

    # 初始化数据库
    db.init_app(app)

    # 注册蓝图
    app.register_blueprint(auth.bp, url_prefix='/api/auth')
    app.register_blueprint(users.bp, url_prefix='/api/users')
    app.register_blueprint(roles.bp, url_prefix='/api/roles')
    app.register_blueprint(departments.bp, url_prefix='/api/departments')
    app.register_blueprint(permissions.bp, url_prefix='/api/permissions')
    app.register_blueprint(logs.bp, url_prefix='/api/logs')

    # 记录操作日志的中间件
    @app.after_request
    def log_operation(response):
        try:
            # 跳过静态文件和健康检查
            if request.path.startswith('/static') or request.path == '/health':
                return response

            # 获取当前用户
            user_id = session.get('user_id')
            username = session.get('username', '')

            # 记录操作日志
            import json
            params = request.get_json(silent=True) or request.form.to_dict() if request.form else dict(request.args)

            db.execute("""
                INSERT INTO operation_logs (user_id, username, action, module, method, url, params, ip, user_agent, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                user_id,
                username,
                request.endpoint,
                request.blueprint,
                request.method,
                request.path,
                json.dumps(params) if params else None,
                request.remote_addr,
                request.headers.get('User-Agent', '')[:255],
                response.status_code
            ))
        except Exception as e:
            pass  # 日志记录失败不影响主流程

        return response

    # 健康检查
    @app.route('/health')
    def health():
        return jsonify({'status': 'ok'})

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=8000, debug=True)
