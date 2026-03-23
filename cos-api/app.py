#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
COS 对象存储接口服务
提供文件上传、下载、删除、列表等功能
"""

import os
import json
import logging
from flask import Flask, request, jsonify, send_file
from qcloud_cos import CosConfig, CosS3Client
from datetime import datetime
import io

app = Flask(__name__)

# 加载配置
def load_config():
    config_path = os.path.join(os.path.dirname(__file__), '..', 'env.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

config = load_config()
cos_config = config.get('cos', {})

# 初始化 COS 客户端
cos_client = CosS3Client(CosConfig(
    Region=cos_config.get('region', 'ap-shanghai'),
    SecretId=cos_config.get('secret_id'),
    SecretKey=cos_config.get('secret_key')
))

BUCKET = cos_config.get('bucket')

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.route('/health', methods=['GET'])
def health():
    """健康检查"""
    return jsonify({'status': 'ok', 'timestamp': datetime.now().isoformat()})


@app.route('/upload', methods=['POST'])
def upload_file():
    """
    上传文件
    POST /upload
    Form-data: file (文件), key (可选，存储路径)
    """
    if 'file' not in request.files:
        return jsonify({'error': '未找到文件'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '文件名为空'}), 400

    # 获取存储路径，默认为文件名
    key = request.form.get('key', file.filename)
    if not key:
        return jsonify({'error': '无法确定存储路径'}), 400

    try:
        # 读取文件内容
        file_data = file.read()

        # 上传到 COS
        response = cos_client.put_object(
            Bucket=BUCKET,
            Body=file_data,
            Key=key
        )

        logger.info(f'文件上传成功：{key}')
        return jsonify({
            'success': True,
            'key': key,
            'etag': response.get('ETag', '')
        })
    except Exception as e:
        logger.error(f'上传失败：{e}')
        return jsonify({'error': str(e)}), 500


@app.route('/download/<path:key>', methods=['GET'])
def download_file(key):
    """
    下载文件
    GET /download/<文件路径>
    """
    try:
        response = cos_client.get_object(Bucket=BUCKET, Key=key)
        return send_file(
            io.BytesIO(response['Body'].get_raw_stream().read()),
            as_attachment=True,
            download_name=os.path.basename(key)
        )
    except Exception as e:
        logger.error(f'下载失败：{e}')
        return jsonify({'error': str(e)}), 404


@app.route('/delete/<path:key>', methods=['DELETE'])
def delete_file(key):
    """
    删除文件
    DELETE /delete/<文件路径>
    """
    try:
        cos_client.delete_object(Bucket=BUCKET, Key=key)
        logger.info(f'文件删除成功：{key}')
        return jsonify({'success': True, 'key': key})
    except Exception as e:
        logger.error(f'删除失败：{e}')
        return jsonify({'error': str(e)}), 500


@app.route('/list', methods=['GET'])
def list_files():
    """
    列出文件
    GET /list?prefix=目录前缀&limit=数量
    """
    prefix = request.args.get('prefix', '')
    limit = int(request.args.get('limit', 100))

    try:
        response = cos_client.list_objects(
            Bucket=BUCKET,
            Prefix=prefix,
            MaxKeys=limit
        )

        files = []
        for content in response.get('Contents', []):
            last_modified = content.get('LastModified')
            if last_modified and hasattr(last_modified, 'isoformat'):
                last_modified = last_modified.isoformat()
            files.append({
                'key': content['Key'],
                'size': content['Size'],
                'last_modified': last_modified
            })

        return jsonify({'files': files, 'count': len(files)})
    except Exception as e:
        logger.error(f'列出文件失败：{e}')
        return jsonify({'error': str(e)}), 500


@app.route('/url/<path:key>', methods=['GET'])
def get_presigned_url(key):
    """
    生成预签名 URL（临时访问链接）
    GET /url/<文件路径>?expired=过期时间 (秒)
    """
    expired = int(request.args.get('expired', 3600))

    try:
        url = cos_client.get_presigned_download_url(
            Bucket=BUCKET,
            Key=key,
            Expired=expired
        )
        return jsonify({'url': url, 'expired': expired})
    except Exception as e:
        logger.error(f'生成 URL 失败：{e}')
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    server_config = config.get('server', {})
    host = server_config.get('host', '0.0.0.0')
    port = server_config.get('port', 5000)

    logger.info(f'启动 COS API 服务：http://{host}:{port}')
    app.run(host=host, port=port, debug=True)
