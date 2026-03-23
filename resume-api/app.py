#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
简历附件管理服务
提供简历批量上传、下载、列表等功能，关联岗位信息
"""

import os
import json
import logging
from flask import Flask, request, send_file
from qcloud_cos import CosConfig, CosS3Client
from datetime import datetime
import io
import pymysql
from utils.response import success, error

app = Flask(__name__)

# 加载配置
def load_config():
    config_path = os.path.join(os.path.dirname(__file__), '..', 'env.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

config = load_config()
cos_config = config.get('cos', {})
mysql_config = config.get('mysql', {})
dashscope_config = config.get('dashscope', {})

# 初始化 COS 客户端
cos_client = CosS3Client(CosConfig(
    Region=cos_config.get('region', 'ap-guangzhou'),
    SecretId=cos_config.get('secret_id'),
    SecretKey=cos_config.get('secret_key')
))

BUCKET = cos_config.get('bucket')

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_db_connection():
    """获取数据库连接"""
    return pymysql.connect(
        host=mysql_config.get('host', 'localhost'),
        port=mysql_config.get('port', 3306),
        user=mysql_config.get('user', 'root'),
        password=mysql_config.get('password', ''),
        database=mysql_config.get('database', 'user_platform'),
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )


def init_database():
    """初始化数据库表"""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # 创建岗位表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS positions (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    title VARCHAR(200) NOT NULL COMMENT '岗位名称',
                    description TEXT COMMENT '岗位描述',
                    requirements TEXT COMMENT '任职要求',
                    department VARCHAR(100) COMMENT '所属部门',
                    skills_required JSON COMMENT '技能要求列表',
                    headcount INT DEFAULT 1 COMMENT '招聘人数',
                    hire_by_date DATE COMMENT '期望入职时间',
                    status TINYINT DEFAULT 1 COMMENT '1-招聘中，0-已结束',
                    created_by INT COMMENT '创建人 ID',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    INDEX idx_status (status),
                    INDEX idx_created (created_at)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='岗位表'
            """)

            # 创建简历表（如果不存在）
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS resume_attachments (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    file_name VARCHAR(255) NOT NULL COMMENT '原始文件名',
                    cos_key VARCHAR(512) NOT NULL COMMENT 'COS 存储路径',
                    file_size INT DEFAULT 0 COMMENT '文件大小 (字节)',
                    file_type VARCHAR(100) COMMENT '文件类型/MIME 类型',
                    position_id INT COMMENT '关联岗位 ID',
                    position_name VARCHAR(255) COMMENT '岗位名称',
                    candidate_name VARCHAR(100) COMMENT '候选人姓名',
                    candidate_phone VARCHAR(20) COMMENT '候选人电话',
                    candidate_email VARCHAR(100) COMMENT '候选人邮箱',
                    upload_user_id INT COMMENT '上传用户 ID',
                    upload_username VARCHAR(100) COMMENT '上传用户名',
                    status TINYINT DEFAULT 1 COMMENT '状态：1-有效，0-无效',
                    download_count INT DEFAULT 0 COMMENT '下载次数',
                    analysis_score INT COMMENT 'AI 打分 0-100',
                    analysis_report JSON COMMENT 'AI 分析报告',
                    analyzed_at TIMESTAMP COMMENT '分析时间',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    INDEX idx_position (position_id),
                    INDEX idx_status (status),
                    INDEX idx_created (created_at),
                    INDEX idx_score (analysis_score)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='简历附件表'
            """)
            conn.commit()
            logger.info('数据库表初始化成功')
    except Exception as e:
        logger.error(f'数据库初始化失败：{e}')
        conn.rollback()
        raise e
    finally:
        conn.close()


@app.route('/health', methods=['GET'])
def health():
    """健康检查"""
    return success({'status': 'ok', 'timestamp': datetime.now().isoformat()})


@app.route('/batch-upload', methods=['POST'])
def batch_upload():
    """
    批量上传简历
    POST /batch-upload
    Content-Type: multipart/form-data

    参数:
    - files[]: 文件列表（必填，支持多文件）
    - position_id: 岗位 ID（可选）
    - position_name: 岗位名称（可选）
    - upload_user_id: 上传用户 ID（可选）
    - upload_username: 上传用户名（可选）

    或者使用 JSON 格式传递岗位信息（每个文件可独立指定）:
    - files[]: 文件列表
    - items: JSON 数组，每个元素包含 {file_index, position_id, position_name, candidate_name, candidate_phone, candidate_email}
    """
    if 'files' not in request.files:
        # 尝试从 items 中获取文件
        items_json = request.form.get('items')
        if items_json:
            items = json.loads(items_json)
        else:
            return error('未找到文件', 400)
    else:
        files = request.files.getlist('files')
        if not files or len(files) == 0:
            return error('文件列表为空', 400)

    # 获取统一的岗位信息（如果提供）
    position_id = request.form.get('position_id')
    position_name = request.form.get('position_name')
    upload_user_id = request.form.get('upload_user_id')
    upload_username = request.form.get('upload_username')

    # 获取每个文件的详细信息
    items_json = request.form.get('items')
    items = json.loads(items_json) if items_json else []

    results = []
    failed = []

    conn = get_db_connection()
    try:
        for index, file in enumerate(files):
            if file.filename == '':
                failed.append({'index': index, 'error': '文件名为空'})
                continue

            # 查找是否有针对该文件的详细信息
            item_info = next((item for item in items if item.get('file_index') == index), {})

            # 使用文件级别的详细信息，如果没有则使用统一的岗位信息
            file_position_id = item_info.get('position_id') or position_id
            file_position_name = item_info.get('position_name') or position_name
            candidate_name = item_info.get('candidate_name', '')
            candidate_phone = item_info.get('candidate_phone', '')
            candidate_email = item_info.get('candidate_email', '')

            # 生成 COS 存储路径：resume/年/月/日/时间戳_文件名
            date_str = datetime.now().strftime('%Y/%m/%d')
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')
            file_extension = os.path.splitext(file.filename)[1]
            cos_key = f"resume/{date_str}/{timestamp}_{file.filename}"

            try:
                # 读取文件内容
                file_data = file.read()

                # 上传到 COS
                response = cos_client.put_object(
                    Bucket=BUCKET,
                    Body=file_data,
                    Key=cos_key
                )

                # 获取文件类型
                file_type = file.content_type or ''

                # 写入数据库
                with conn.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO resume_attachments
                        (file_name, cos_key, file_size, file_type, position_id, position_name,
                         candidate_name, candidate_phone, candidate_email, upload_user_id, upload_username)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        file.filename,
                        cos_key,
                        len(file_data),
                        file_type,
                        file_position_id or None,
                        file_position_name or None,
                        candidate_name or None,
                        candidate_phone or None,
                        candidate_email or None,
                        upload_user_id or None,
                        upload_username or None
                    ))
                    file_id = cursor.lastrowid
                    conn.commit()

                logger.info(f'文件上传成功：{file.filename} -> {cos_key}, ID: {file_id}')
                results.append({
                    'id': file_id,
                    'file_name': file.filename,
                    'cos_key': cos_key,
                    'position_id': file_position_id,
                    'position_name': file_position_name,
                    'size': len(file_data),
                    'upload_time': datetime.now().isoformat()
                })

            except Exception as e:
                logger.error(f'上传失败 {file.filename}: {e}')
                failed.append({'index': index, 'filename': file.filename, 'error': str(e)})

        return success({
            'success': len(failed) == 0,
            'count': len(results),
            'results': results,
            'failed': failed
        })

    except Exception as e:
        conn.rollback()
        logger.error(f'批量上传失败：{e}')
        return error('上传失败', 500)
    finally:
        conn.close()


@app.route('/download/<int:file_id>', methods=['GET'])
def download_file(file_id):
    """
    下载文件
    GET /download/<文件 ID>
    """
    conn = get_db_connection()
    try:
        # 查询文件信息
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT id, file_name, cos_key, status
                FROM resume_attachments
                WHERE id = %s
            """, (file_id,))
            record = cursor.fetchone()

        if not record:
            return error('文件不存在', 404)

        if record['status'] == 0:
            return error('文件已被删除', 404)

        # 从 COS 下载
        response = cos_client.get_object(Bucket=BUCKET, Key=record['cos_key'])
        file_data = response['Body'].get_raw_stream().read()

        # 增加下载次数
        with conn.cursor() as cursor:
            cursor.execute("""
                UPDATE resume_attachments
                SET download_count = download_count + 1
                WHERE id = %s
            """, (file_id,))
            conn.commit()

        return send_file(
            io.BytesIO(file_data),
            as_attachment=True,
            download_name=record['file_name']
        )

    except Exception as e:
        logger.error(f'下载失败：{e}')
        return error('下载失败', 500)
    finally:
        conn.close()


@app.route('/list', methods=['GET'])
def list_files():
    """
    列出简历文件
    GET /list?position_id=岗位 ID&status=状态&keyword=关键词&page=页码&page_size=每页数量&sort=排序字段&order=asc|desc

    参数:
    - position_id: 岗位 ID
    - status: 状态 (1-有效，0-无效)
    - keyword: 搜索关键词
    - page: 页码
    - page_size: 每页数量
    - sort: 排序字段 (created_at, analysis_score)
    - order: 排序顺序 (asc, desc)
    """
    position_id = request.args.get('position_id')
    status = request.args.get('status', '1')
    keyword = request.args.get('keyword', '')
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 20))
    sort = request.args.get('sort', 'created_at')
    order = request.args.get('order', 'desc').upper()

    # 白名单验证排序字段
    allowed_sort = ['created_at', 'analysis_score', 'download_count']
    if sort not in allowed_sort:
        sort = 'created_at'
    if order not in ['ASC', 'DESC']:
        order = 'DESC'

    offset = (page - 1) * page_size

    conn = get_db_connection()
    try:
        # 构建查询条件
        conditions = []
        params = []

        if status is not None:
            conditions.append('status = %s')
            params.append(status)

        if position_id:
            conditions.append('position_id = %s')
            params.append(position_id)

        if keyword:
            conditions.append('(file_name LIKE %s OR candidate_name LIKE %s OR candidate_phone LIKE %s)')
            keyword_pattern = f'%{keyword}%'
            params.extend([keyword_pattern, keyword_pattern, keyword_pattern])

        where_clause = ' AND '.join(conditions) if conditions else '1=1'

        # 查询总数
        with conn.cursor() as cursor:
            cursor.execute(f"SELECT COUNT(*) as total FROM resume_attachments WHERE {where_clause}", params)
            total = cursor.fetchone()['total']

        # 查询数据
        params_for_list = params.copy() + [page_size, offset]
        with conn.cursor() as cursor:
            cursor.execute(f"""
                SELECT id, file_name, file_size, file_type, position_id, position_name,
                       candidate_name, candidate_phone, candidate_email,
                       upload_username, status, download_count, analysis_score, created_at, updated_at
                FROM resume_attachments
                WHERE {where_clause}
                ORDER BY {sort} {order}
                LIMIT %s OFFSET %s
            """, params_for_list)
            files = cursor.fetchall()

        # 格式化时间字段
        for f in files:
            if f.get('created_at') and hasattr(f['created_at'], 'isoformat'):
                f['created_at'] = f['created_at'].isoformat()
            if f.get('updated_at') and hasattr(f['updated_at'], 'isoformat'):
                f['updated_at'] = f['updated_at'].isoformat()

        return success({
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': (total + page_size - 1) // page_size,
            'files': files
        })

    except Exception as e:
        logger.error(f'列出文件失败：{e}')
        return error('列出文件失败', 500)
    finally:
        conn.close()


@app.route('/<int:file_id>', methods=['GET'])
def get_file_info(file_id):
    """
    获取文件详情
    GET /<文件 ID>
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT id, file_name, file_size, file_type, cos_key,
                       position_id, position_name,
                       candidate_name, candidate_phone, candidate_email,
                       upload_user_id, upload_username, status,
                       download_count, created_at, updated_at
                FROM resume_attachments
                WHERE id = %s
            """, (file_id,))
            record = cursor.fetchone()

        if not record:
            return error('文件不存在', 404)

        # 格式化时间字段
        if record.get('created_at') and hasattr(record['created_at'], 'isoformat'):
            record['created_at'] = record['created_at'].isoformat()
        if record.get('updated_at') and hasattr(record['updated_at'], 'isoformat'):
            record['updated_at'] = record['updated_at'].isoformat()

        return success(record)

    except Exception as e:
        logger.error(f'获取文件详情失败：{e}')
        return error('获取文件详情失败', 500)
    finally:
        conn.close()


@app.route('/<int:file_id>', methods=['DELETE'])
def delete_file(file_id):
    """
    删除文件（软删除）
    DELETE /<文件 ID>
    """
    conn = get_db_connection()
    try:
        # 查询文件信息
        with conn.cursor() as cursor:
            cursor.execute("SELECT cos_key, status FROM resume_attachments WHERE id = %s", (file_id,))
            record = cursor.fetchone()

        if not record:
            return error('文件不存在', 404)

        # 软删除：仅更新状态
        with conn.cursor() as cursor:
            cursor.execute("UPDATE resume_attachments SET status = 0 WHERE id = %s", (file_id,))
            conn.commit()

        logger.info(f'文件软删除成功：ID={file_id}')
        return success({'id': file_id}, '删除成功')

    except Exception as e:
        conn.rollback()
        logger.error(f'删除失败：{e}')
        return error('删除失败', 500)
    finally:
        conn.close()


@app.route('/url/<int:file_id>', methods=['GET'])
def get_presigned_url(file_id):
    """
    生成预签名 URL（临时访问链接）
    GET /url/<文件 ID>?expired=过期时间 (秒)
    """
    expired = int(request.args.get('expired', 3600))

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT cos_key, file_name FROM resume_attachments WHERE id = %s", (file_id,))
            record = cursor.fetchone()

        if not record:
            return error('文件不存在', 404)

        url = cos_client.get_presigned_download_url(
            Bucket=BUCKET,
            Key=record['cos_key'],
            Expired=expired
        )

        return success({
            'id': file_id,
            'file_name': record['file_name'],
            'url': url,
            'expired': expired
        })

    except Exception as e:
        logger.error(f'生成 URL 失败：{e}')
        return error('生成 URL 失败', 500)
    finally:
        conn.close()


# ==================== 岗位管理接口 ====================

@app.route('/positions', methods=['POST'])
def create_position():
    """
    创建岗位
    POST /positions
    Content-Type: application/json

    参数:
    - title: 岗位名称（必填）
    - description: 岗位描述
    - requirements: 任职要求
    - department: 所属部门
    - skills_required: 技能要求列表 (JSON 数组)
    - headcount: 招聘人数
    - hire_by_date: 期望入职时间 (YYYY-MM-DD)
    - created_by: 创建人 ID
    """
    data = request.get_json()
    if not data or not data.get('title'):
        return error('岗位名称不能为空', 400)

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO positions
                (title, description, requirements, department, skills_required,
                 headcount, hire_by_date, created_by)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                data.get('title'),
                data.get('description', ''),
                data.get('requirements', ''),
                data.get('department', ''),
                json.dumps(data.get('skills_required', [])) if data.get('skills_required') else None,
                data.get('headcount', 1),
                data.get('hire_by_date'),
                data.get('created_by')
            ))
            position_id = cursor.lastrowid
            conn.commit()

        return success({'id': position_id}, '岗位创建成功')

    except Exception as e:
        conn.rollback()
        logger.error(f'创建岗位失败：{e}')
        return error('创建岗位失败', 500)
    finally:
        conn.close()


@app.route('/positions', methods=['GET'])
def list_positions():
    """
    获取岗位列表
    GET /positions?status=状态&department=部门&keyword=关键词&page=页码&page_size=每页数量

    参数:
    - status: 状态 (1-招聘中，0-已结束)
    - department: 部门
    - keyword: 搜索关键词 (岗位名称)
    - page: 页码
    - page_size: 每页数量
    """
    status = request.args.get('status')
    department = request.args.get('department', '')
    keyword = request.args.get('keyword', '')
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 20))

    offset = (page - 1) * page_size

    conn = get_db_connection()
    try:
        conditions = []
        params = []

        if status is not None:
            conditions.append('status = %s')
            params.append(status)

        if department:
            conditions.append('department = %s')
            params.append(department)

        if keyword:
            conditions.append('title LIKE %s')
            params.append(f'%{keyword}%')

        where_clause = ' AND '.join(conditions) if conditions else '1=1'

        # 查询总数
        with conn.cursor() as cursor:
            cursor.execute(f"SELECT COUNT(*) as total FROM positions WHERE {where_clause}", params)
            total = cursor.fetchone()['total']

        # 查询数据，关联统计简历数
        params_for_list = params.copy() + [page_size, offset]
        with conn.cursor() as cursor:
            cursor.execute(f"""
                SELECT p.*,
                       COUNT(r.id) as resume_count,
                       COALESCE(AVG(r.analysis_score), 0) as avg_score
                FROM positions p
                LEFT JOIN resume_attachments r ON p.id = r.position_id AND r.status = 1
                WHERE {where_clause}
                GROUP BY p.id
                ORDER BY p.created_at DESC
                LIMIT %s OFFSET %s
            """, params_for_list)
            positions = cursor.fetchall()

        # 格式化时间字段
        for p in positions:
            if p.get('created_at') and hasattr(p['created_at'], 'isoformat'):
                p['created_at'] = p['created_at'].isoformat()
            if p.get('hire_by_date') and hasattr(p['hire_by_date'], 'isoformat'):
                p['hire_by_date'] = p['hire_by_date'].isoformat()
            # 解析 skills_required JSON
            if p.get('skills_required') and isinstance(p['skills_required'], str):
                p['skills_required'] = json.loads(p['skills_required'])

        return success({
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': (total + page_size - 1) // page_size,
            'positions': positions
        })

    except Exception as e:
        logger.error(f'获取岗位列表失败：{e}')
        return error('获取岗位列表失败', 500)
    finally:
        conn.close()


@app.route('/positions/<int:position_id>', methods=['GET'])
def get_position(position_id):
    """
    获取岗位详情
    GET /positions/<岗位 ID>
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT p.*,
                       COUNT(r.id) as resume_count,
                       COALESCE(AVG(r.analysis_score), 0) as avg_score,
                       MAX(CASE WHEN r.analysis_score IS NOT NULL THEN r.analysis_score ELSE 0 END) as max_score
                FROM positions p
                LEFT JOIN resume_attachments r ON p.id = r.position_id AND r.status = 1
                WHERE p.id = %s
                GROUP BY p.id
            """, (position_id,))
            position = cursor.fetchone()

        if not position:
            return error('岗位不存在', 404)

        # 格式化时间字段
        if position.get('created_at') and hasattr(position['created_at'], 'isoformat'):
            position['created_at'] = position['created_at'].isoformat()
        if position.get('hire_by_date') and hasattr(position['hire_by_date'], 'isoformat'):
            position['hire_by_date'] = position['hire_by_date'].isoformat()
        # 解析 skills_required JSON
        if position.get('skills_required') and isinstance(position['skills_required'], str):
            position['skills_required'] = json.loads(position['skills_required'])

        return success(position)

    except Exception as e:
        logger.error(f'获取岗位详情失败：{e}')
        return error('获取岗位详情失败', 500)
    finally:
        conn.close()


@app.route('/positions/<int:position_id>', methods=['PUT'])
def update_position(position_id):
    """
    更新岗位
    PUT /positions/<岗位 ID>
    Content-Type: application/json

    参数:
    - title: 岗位名称
    - description: 岗位描述
    - requirements: 任职要求
    - department: 所属部门
    - skills_required: 技能要求列表
    - headcount: 招聘人数
    - hire_by_date: 期望入职时间
    - status: 状态 (1-招聘中，0-已结束)
    """
    data = request.get_json()
    if not data:
        return error('参数不能为空', 400)

    conn = get_db_connection()
    try:
        # 检查岗位是否存在
        with conn.cursor() as cursor:
            cursor.execute("SELECT id FROM positions WHERE id = %s", (position_id,))
            if not cursor.fetchone():
                return error('岗位不存在', 404)

        # 构建更新字段
        update_fields = []
        update_values = []

        allowed_fields = ['title', 'description', 'requirements', 'department',
                          'skills_required', 'headcount', 'hire_by_date', 'status']
        for field in allowed_fields:
            if field in data:
                update_fields.append(f'{field} = %s')
                if field == 'skills_required' and isinstance(data[field], list):
                    update_values.append(json.dumps(data[field]))
                else:
                    update_values.append(data[field])

        if not update_fields:
            return error('没有要更新的字段', 400)

        update_values.append(position_id)

        with conn.cursor() as cursor:
            cursor.execute(f"""
                UPDATE positions
                SET {', '.join(update_fields)}
                WHERE id = %s
            """, update_values)
            conn.commit()

        return success(message='岗位更新成功')

    except Exception as e:
        conn.rollback()
        logger.error(f'更新岗位失败：{e}')
        return error('更新岗位失败', 500)
    finally:
        conn.close()


@app.route('/positions/<int:position_id>', methods=['DELETE'])
def delete_position(position_id):
    """
    删除/结束岗位
    DELETE /positions/<岗位 ID>
    """
    conn = get_db_connection()
    try:
        # 检查岗位是否存在
        with conn.cursor() as cursor:
            cursor.execute("SELECT id FROM positions WHERE id = %s", (position_id,))
            if not cursor.fetchone():
                return error('岗位不存在', 404)

        # 软删除：将状态设为已结束
        with conn.cursor() as cursor:
            cursor.execute("UPDATE positions SET status = 0 WHERE id = %s", (position_id,))
            conn.commit()

        return success(message='岗位已结束')

    except Exception as e:
        conn.rollback()
        logger.error(f'删除岗位失败：{e}')
        return error('删除岗位失败', 500)
    finally:
        conn.close()


# ==================== 简历分析接口 ====================

def parse_resume_text(file_data, file_type, file_name=''):
    """
    解析简历文件，提取文本内容
    """
    try:
        if 'pdf' in file_type or file_name.lower().endswith('.pdf'):
            return f"PDF 文件，大小：{len(file_data)} 字节"
        elif 'image' in file_type:
            return "图片文件，需要 OCR 识别"
        else:
            try:
                return file_data.decode('utf-8', errors='ignore')[:5000]
            except:
                return file_data.decode('gbk', errors='ignore')[:5000]
    except Exception as e:
        logger.error(f'解析简历失败：{e}')
        return ""


def analyze_resume_by_qwen(resume_text, position_info):
    """
    调用千问 API 分析简历
    """
    try:
        import http.client
        import json as json_lib
        import re

        api_key = dashscope_config.get('api_key', '')
        if not api_key:
            return None, "未配置千问 API Key"

        prompt = f"""你是一位专业的 HR 招聘专家，请分析这份简历与岗位的匹配度。

岗位信息：
{position_info}

简历内容：
{resume_text}

请按照以下 JSON 格式输出分析结果（不要输出其他内容）：
{{
    "match_score": 85,
    "skills_match": ["技能 1", "技能 2"],
    "skills_missing": ["缺失技能"],
    "experience_years": 5,
    "highlights": ["亮点 1", "亮点 2"],
    "concerns": ["顾虑 1"],
    "recommendation": "A",
    "summary": "200 字以内的综合评估"
}}

评分标准：
- match_score: 0-100 分，综合匹配度
- recommendation: S(90+), A(80-89), B(70-79), C(60-69), D(<60)
"""

        connection = http.client.HTTPSConnection("dashscope.aliyuncs.com")
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = json_lib.dumps({
            "model": dashscope_config.get('model', 'qwen-plus'),
            "input": {
                "messages": [
                    {"role": "system", "content": "你是一位专业的 HR 招聘专家，负责分析简历与岗位的匹配度。"},
                    {"role": "user", "content": prompt}
                ]
            },
            "parameters": {
                "temperature": 0.3,
                "max_tokens": 1000
            }
        })

        connection.request("POST", "/api/v1/services/aigc/text-generation/generation", payload, headers)
        response = connection.getresponse()
        result = response.read().decode('utf-8')
        connection.close()

        result_json = json_lib.loads(result)

        if 'output' in result_json and 'choices' in result_json['output']:
            content = result_json['output']['choices'][0]['message']['content']
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                analysis = json_lib.loads(json_match.group())
                return analysis, None
            else:
                return None, "解析 AI 返回结果失败"
        else:
            return None, result_json.get('message', 'API 调用失败')

    except Exception as e:
        logger.error(f'千问 API 调用失败：{e}')
        return None, str(e)


@app.route('/resume/<int:resume_id>/analyze', methods=['POST'])
def analyze_resume(resume_id):
    """
    分析单份简历
    POST /resume/<简历 ID>/analyze
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT r.*, p.description as position_description, p.requirements as position_requirements
                FROM resume_attachments r
                LEFT JOIN positions p ON r.position_id = p.id
                WHERE r.id = %s
            """, (resume_id,))
            resume = cursor.fetchone()

        if not resume:
            return error('简历不存在', 404)

        response = cos_client.get_object(Bucket=BUCKET, Key=resume['cos_key'])
        file_data = response['Body'].get_raw_stream().read()

        resume_text = parse_resume_text(file_data, resume.get('file_type', ''), resume.get('file_name', ''))

        position_info = f"岗位：{resume.get('position_name', '未指定')}\n"
        if resume.get('position_description'):
            position_info += f"岗位描述：{resume['position_description']}\n"
        if resume.get('position_requirements'):
            position_info += f"任职要求：{resume['position_requirements']}"

        analysis, err = analyze_resume_by_qwen(resume_text, position_info)

        if err:
            return error(f'AI 分析失败：{err}', 500)

        with conn.cursor() as cursor:
            cursor.execute("""
                UPDATE resume_attachments
                SET analysis_score = %s, analysis_report = %s, analyzed_at = NOW()
                WHERE id = %s
            """, (
                analysis.get('match_score', 0),
                json.dumps(analysis),
                resume_id
            ))
            conn.commit()

        return success({
            'id': resume_id,
            'score': analysis.get('match_score', 0),
            'analysis': analysis
        }, '分析完成')

    except Exception as e:
        conn.rollback()
        logger.error(f'分析简历失败：{e}')
        return error(f'分析失败：{str(e)}', 500)
    finally:
        conn.close()


@app.route('/positions/<int:position_id>/analyze', methods=['POST'])
def batch_analyze_position(position_id):
    """
    批量分析某个岗位下的所有简历
    POST /positions/<岗位 ID>/analyze

    参数:
    - unanalyzed_only: 是否只分析未分析过的简历 (默认 true)
    """
    data = request.get_json() or {}
    unanalyzed_only = data.get('unanalyzed_only', True)

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, title, description, requirements FROM positions WHERE id = %s", (position_id,))
            position = cursor.fetchone()
            if not position:
                return error('岗位不存在', 404)

        with conn.cursor() as cursor:
            if unanalyzed_only:
                cursor.execute("""
                    SELECT id, file_name, cos_key, file_type, candidate_name
                    FROM resume_attachments
                    WHERE position_id = %s AND status = 1 AND analysis_score IS NULL
                    ORDER BY created_at ASC
                """, (position_id,))
            else:
                cursor.execute("""
                    SELECT id, file_name, cos_key, file_type, candidate_name
                    FROM resume_attachments
                    WHERE position_id = %s AND status = 1
                    ORDER BY created_at ASC
                """, (position_id,))
            resumes = cursor.fetchall()

        if not resumes:
            return success({'count': 0, 'message': '没有需要分析的简历'}, None)

        position_info = f"岗位：{position['title']}\n"
        if position.get('description'):
            position_info += f"岗位描述：{position['description']}\n"
        if position.get('requirements'):
            position_info += f"任职要求：{position['requirements']}"

        results = []
        failed = []

        for resume in resumes:
            try:
                response = cos_client.get_object(Bucket=BUCKET, Key=resume['cos_key'])
                file_data = response['Body'].get_raw_stream().read()

                resume_text = parse_resume_text(file_data, resume.get('file_type', ''), resume.get('file_name', ''))

                analysis, err = analyze_resume_by_qwen(resume_text, position_info)

                if err:
                    failed.append({'id': resume['id'], 'error': err})
                    continue

                with conn.cursor() as cursor:
                    cursor.execute("""
                        UPDATE resume_attachments
                        SET analysis_score = %s, analysis_report = %s, analyzed_at = NOW()
                        WHERE id = %s
                    """, (
                        analysis.get('match_score', 0),
                        json.dumps(analysis),
                        resume['id']
                    ))
                    conn.commit()

                results.append({
                    'id': resume['id'],
                    'candidate': resume['candidate_name'] or resume['file_name'],
                    'score': analysis.get('match_score', 0)
                })

            except Exception as e:
                logger.error(f'分析简历 {resume["id"]} 失败：{e}')
                failed.append({'id': resume['id'], 'error': str(e)})

        return success({
            'total': len(resumes),
            'success': len(results),
            'failed': len(failed),
            'results': results,
            'failed_details': failed
        }, f'分析完成，成功{len(results)}份，失败{len(failed)}份')

    except Exception as e:
        conn.rollback()
        logger.error(f'批量分析失败：{e}')
        return error(f'批量分析失败：{str(e)}', 500)
    finally:
        conn.close()


@app.route('/positions/<int:position_id>/analysis', methods=['GET'])
def get_position_analysis(position_id):
    """
    获取岗位的分析报告
    GET /positions/<岗位 ID>/analysis
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, title FROM positions WHERE id = %s", (position_id,))
            if not cursor.fetchone():
                return error('岗位不存在', 404)

        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT
                    COUNT(*) as total,
                    COUNT(analysis_score) as analyzed_count,
                    COALESCE(AVG(analysis_score), 0) as avg_score,
                    MAX(analysis_score) as max_score,
                    MIN(analysis_score) as min_score
                FROM resume_attachments
                WHERE position_id = %s AND status = 1
            """, (position_id,))
            stats = cursor.fetchone()

            cursor.execute("""
                SELECT
                    SUM(CASE WHEN analysis_score >= 90 THEN 1 ELSE 0 END) as s_count,
                    SUM(CASE WHEN analysis_score >= 80 AND analysis_score < 90 THEN 1 ELSE 0 END) as a_count,
                    SUM(CASE WHEN analysis_score >= 70 AND analysis_score < 80 THEN 1 ELSE 0 END) as b_count,
                    SUM(CASE WHEN analysis_score >= 60 AND analysis_score < 70 THEN 1 ELSE 0 END) as c_count,
                    SUM(CASE WHEN analysis_score < 60 AND analysis_score IS NOT NULL THEN 1 ELSE 0 END) as d_count
                FROM resume_attachments
                WHERE position_id = %s AND status = 1 AND analysis_score IS NOT NULL
            """, (position_id,))
            distribution = cursor.fetchone()

            cursor.execute("""
                SELECT id, candidate_name, candidate_phone, candidate_email,
                       file_name, analysis_score, analysis_report
                FROM resume_attachments
                WHERE position_id = %s AND status = 1 AND analysis_score IS NOT NULL
                ORDER BY analysis_score DESC
                LIMIT 10
            """, (position_id,))
            top_candidates = cursor.fetchall()

            for c in top_candidates:
                if c.get('analysis_report') and isinstance(c['analysis_report'], str):
                    c['analysis_report'] = json.loads(c['analysis_report'])

        return success({
            'position_id': position_id,
            'stats': stats,
            'distribution': distribution,
            'top_candidates': top_candidates
        })

    except Exception as e:
        logger.error(f'获取分析报告失败：{e}')
        return error('获取分析报告失败', 500)
    finally:
        conn.close()


if __name__ == '__main__':
    host = server_config.get('host', '0.0.0.0')
    port = 8001  # 简历服务使用独立端口

    logger.info(f'启动简历附件管理服务：http://{host}:{port}')

    # 初始化数据库表
    init_database()

    app.run(host=host, port=port, debug=True)
