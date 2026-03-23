# -*- coding: utf-8 -*-
"""
用户平台 - 主应用
集成用户管理、部门管理、角色权限、简历管理、岗位管理
"""
import os
import json
import logging
from flask import Flask, session
from flask_session import Session
import redis

# 导入路由蓝图
from routes.auth import auth_bp
from routes.users import users_bp
from routes.departments import departments_bp
from routes.roles import roles_bp
from routes.permissions import permissions_bp
from routes.resumes import resumes_bp
from routes.positions import positions_bp

# 创建 Flask 应用
app = Flask(__name__)

# 加载配置
def load_config():
    config_path = os.path.join(os.path.dirname(__file__), 'config', 'env.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

config = load_config()

# 配置 Session
app.secret_key = config.get('session', {}).get('secret_key', 'dev-secret-key')
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_PERMANENT'] = True
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_KEY_PREFIX'] = 'user_platform:'
app.config['PERMANENT_SESSION_LIFETIME'] = config.get('session', {}).get('timeout', 86400)

# 配置 Redis
redis_config = config.get('redis', {})
try:
    redis_client = redis.Redis(
        host=redis_config.get('host', 'localhost'),
        port=redis_config.get('port', 6379),
        password=redis_config.get('password') or None,
        decode_responses=False
    )
    redis_client.ping()
    app.config['SESSION_REDIS'] = redis_client
    Session(app)
    print("Redis Session 连接成功")
except Exception as e:
    print(f"Redis 连接失败：{e}，使用内存 Session")
    app.config['SESSION_TYPE'] = 'filesystem'
    Session(app)

# 注册蓝图
app.register_blueprint(auth_bp)
app.register_blueprint(users_bp)
app.register_blueprint(departments_bp)
app.register_blueprint(roles_bp)
app.register_blueprint(permissions_bp)
app.register_blueprint(resumes_bp)
app.register_blueprint(positions_bp)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@app.route('/health', methods=['GET'])
def health():
    """健康检查"""
    return {'status': 'ok', 'service': 'user-platform'}


@app.route('/api', methods=['GET'])
def api_index():
    """API 索引"""
    return {
        'service': 'user-platform',
        'version': '1.0.0',
        'modules': {
            'auth': '/api/auth',
            'users': '/api/users',
            'departments': '/api/departments',
            'roles': '/api/roles',
            'permissions': '/api/permissions',
            'resumes': '/api/resumes',
            'positions': '/api/positions'
        }
    }


# 错误处理
@app.errorhandler(404)
def not_found(error):
    return {'code': 1, 'message': '接口不存在'}, 404


@app.errorhandler(500)
def internal_error(error):
    return {'code': 1, 'message': '服务器内部错误'}, 500


if __name__ == '__main__':
    server_config = config.get('server', {})
    host = server_config.get('host', '0.0.0.0')
    port = server_config.get('port', 8000)

    logger.info(f"启动用户平台服务：http://{host}:{port}")
    logger.info(f"API 文档：http://{host}:{port}/api")

    app.run(host=host, port=port, debug=True)
