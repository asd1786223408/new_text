# -*- coding: utf-8 -*-
"""
简历模型
"""
import json
import os
from datetime import datetime
from qcloud_cos import CosConfig, CosS3Client
from ..utils.db_pool import get_db_connection


def load_config():
    """加载配置"""
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'env.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_cos_client():
    """获取 COS 客户端"""
    config = load_config()
    cos_config = config.get('cos', {})
    cos_conf = CosConfig(
        Region=cos_config.get('region', 'ap-guangzhou'),
        SecretId=cos_config.get('secret_id'),
        SecretKey=cos_config.get('secret_key')
    )
    return CosS3Client(cos_conf), cos_config.get('bucket')


class Resume:
    """简历模型类"""

    @staticmethod
    def upload_to_cos(file_data, file_name):
        """上传文件到 COS"""
        cos_client, bucket = get_cos_client()

        # 生成存储路径
        date_str = datetime.now().strftime('%Y/%m/%d')
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')
        cos_key = f"resume/{date_str}/{timestamp}_{file_name}"

        # 上传
        cos_client.put_object(Bucket=bucket, Body=file_data, Key=cos_key)
        return cos_key

    @staticmethod
    def download_from_cos(cos_key):
        """从 COS 下载文件"""
        cos_client, bucket = get_cos_client()
        response = cos_client.get_object(Bucket=bucket, Key=cos_key)
        return response['Body'].get_raw_stream().read()

    @staticmethod
    def get_presigned_url(cos_key, expired=3600):
        """生成预签名 URL"""
        cos_client, bucket = get_cos_client()
        return cos_client.get_presigned_download_url(Bucket=bucket, Key=cos_key, Expired=expired)

    @staticmethod
    def create(file_name, cos_key, file_size, file_type, position_id=None, position_name=None,
               candidate_name=None, candidate_phone=None, candidate_email=None,
               upload_user_id=None, upload_username=None):
        """创建简历记录"""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO resume_attachments
                    (file_name, cos_key, file_size, file_type, position_id, position_name,
                     candidate_name, candidate_phone, candidate_email, upload_user_id, upload_username)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (file_name, cos_key, file_size, file_type, position_id, position_name,
                      candidate_name, candidate_phone, candidate_email, upload_user_id, upload_username))
                resume_id = cursor.lastrowid
                conn.commit()
            return resume_id
        finally:
            conn.close()

    @staticmethod
    def get_by_id(resume_id):
        """根据 ID 获取简历"""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM resume_attachments WHERE id = %s
                """, (resume_id,))
                return cursor.fetchone()
        finally:
            conn.close()

    @staticmethod
    def update(resume_id, **kwargs):
        """更新简历"""
        allowed_fields = ['position_id', 'position_name', 'candidate_name', 'candidate_phone',
                          'candidate_email', 'status', 'analysis_score', 'analysis_report', 'analyzed_at']
        update_data = {k: v for k, v in kwargs.items() if k in allowed_fields}

        if not update_data:
            return False

        conn = get_db_connection()
        try:
            set_clause = ', '.join([f'{k} = %s' for k in update_data.keys()])
            values = list(update_data.values()) + [resume_id]

            with conn.cursor() as cursor:
                cursor.execute(f"""
                    UPDATE resume_attachments SET {set_clause}
                    WHERE id = %s
                """, values)
                conn.commit()
            return True
        finally:
            conn.close()

    @staticmethod
    def delete(resume_id):
        """软删除简历"""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("UPDATE resume_attachments SET status = 0 WHERE id = %s", (resume_id,))
                conn.commit()
            return True
        finally:
            conn.close()

    @staticmethod
    def list(page=1, page_size=20, position_id=None, status=None, keyword=None, sort='created_at', order='desc'):
        """获取简历列表"""
        conn = get_db_connection()
        try:
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
                params.extend([keyword_pattern] * 3)

            # 排序字段白名单
            allowed_sort = ['created_at', 'analysis_score', 'download_count']
            if sort not in allowed_sort:
                sort = 'created_at'
            if order.upper() not in ['ASC', 'DESC']:
                order = 'DESC'

            where_clause = ' AND '.join(conditions) if conditions else '1=1'
            offset = (page - 1) * page_size

            with conn.cursor() as cursor:
                # 总数
                cursor.execute(f"""
                    SELECT COUNT(*) as total FROM resume_attachments WHERE {where_clause}
                """, params)
                total = cursor.fetchone()['total']

                # 列表
                params_for_list = params.copy() + [page_size, offset]
                cursor.execute(f"""
                    SELECT id, file_name, file_size, file_type, position_id, position_name,
                           candidate_name, candidate_phone, candidate_email,
                           upload_username, status, download_count, analysis_score, created_at, updated_at
                    FROM resume_attachments
                    WHERE {where_clause}
                    ORDER BY {sort} {order.upper()}
                    LIMIT %s OFFSET %s
                """, params_for_list)
                resumes = cursor.fetchall()

            return {
                'total': total,
                'page': page,
                'page_size': page_size,
                'total_pages': (total + page_size - 1) // page_size,
                'resumes': resumes
            }
        finally:
            conn.close()

    @staticmethod
    def increment_download_count(resume_id):
        """增加下载次数"""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("UPDATE resume_attachments SET download_count = download_count + 1 WHERE id = %s", (resume_id,))
                conn.commit()
        finally:
            conn.close()
