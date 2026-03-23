# -*- coding: utf-8 -*-
"""
岗位模型
"""
import json
from ..utils.db_pool import get_db_connection


class Position:
    """岗位模型类"""

    @staticmethod
    def create(title, description='', requirements='', department=None, skills_required=None,
               headcount=1, hire_by_date=None, created_by=None):
        """创建岗位"""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO positions
                    (title, description, requirements, department, skills_required, headcount, hire_by_date, created_by)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (title, description, requirements, department,
                      json.dumps(skills_required) if skills_required else None,
                      headcount, hire_by_date, created_by))
                position_id = cursor.lastrowid
                conn.commit()
            return position_id
        finally:
            conn.close()

    @staticmethod
    def get_by_id(position_id):
        """根据 ID 获取岗位详情"""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT p.*,
                           COUNT(r.id) as resume_count,
                           COALESCE(AVG(r.analysis_score), 0) as avg_score
                    FROM positions p
                    LEFT JOIN resume_attachments r ON p.id = r.position_id AND r.status = 1
                    WHERE p.id = %s
                    GROUP BY p.id
                """, (position_id,))
                position = cursor.fetchone()

                if position:
                    # 解析 skills_required
                    if position.get('skills_required') and isinstance(position['skills_required'], str):
                        position['skills_required'] = json.loads(position['skills_required'])

            return position
        finally:
            conn.close()

    @staticmethod
    def list(page=1, page_size=20, status=None, department=None, keyword=None):
        """获取岗位列表"""
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
            offset = (page - 1) * page_size

            with conn.cursor() as cursor:
                # 总数
                cursor.execute(f"""
                    SELECT COUNT(*) as total FROM positions WHERE {where_clause}
                """, params)
                total = cursor.fetchone()['total']

                # 列表
                params_for_list = params.copy() + [page_size, offset]
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

            # 解析 skills_required
            for p in positions:
                if p.get('skills_required') and isinstance(p['skills_required'], str):
                    p['skills_required'] = json.loads(p['skills_required'])

            return {
                'total': total,
                'page': page,
                'page_size': page_size,
                'total_pages': (total + page_size - 1) // page_size,
                'positions': positions
            }
        finally:
            conn.close()

    @staticmethod
    def update(position_id, **kwargs):
        """更新岗位"""
        allowed_fields = ['title', 'description', 'requirements', 'department',
                          'skills_required', 'headcount', 'hire_by_date', 'status']
        update_data = {k: v for k, v in kwargs.items() if k in allowed_fields}

        if not update_data:
            return False

        # 处理 skills_required
        if 'skills_required' in update_data and isinstance(update_data['skills_required'], list):
            update_data['skills_required'] = json.dumps(update_data['skills_required'])

        conn = get_db_connection()
        try:
            set_clause = ', '.join([f'{k} = %s' for k in update_data.keys()])
            values = list(update_data.values()) + [position_id]

            with conn.cursor() as cursor:
                cursor.execute(f"""
                    UPDATE positions SET {set_clause}
                    WHERE id = %s
                """, values)
                conn.commit()
            return True
        finally:
            conn.close()

    @staticmethod
    def delete(position_id):
        """软删除岗位（设为已结束）"""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("UPDATE positions SET status = 0 WHERE id = %s", (position_id,))
                conn.commit()
            return True
        finally:
            conn.close()

    @staticmethod
    def get_statistics(position_id):
        """获取岗位统计数据"""
        conn = get_db_connection()
        try:
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

                # 分数分布
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

            return {
                'stats': stats,
                'distribution': distribution
            }
        finally:
            conn.close()

    @staticmethod
    def get_top_candidates(position_id, limit=10):
        """获取岗位下得分最高的候选人"""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT id, candidate_name, candidate_phone, candidate_email,
                           file_name, analysis_score, analysis_report
                    FROM resume_attachments
                    WHERE position_id = %s AND status = 1 AND analysis_score IS NOT NULL
                    ORDER BY analysis_score DESC
                    LIMIT %s
                """, (position_id, limit))
                candidates = cursor.fetchall()

            # 解析分析报告
            for c in candidates:
                if c.get('analysis_report') and isinstance(c['analysis_report'], str):
                    c['analysis_report'] = json.loads(c['analysis_report'])

            return candidates
        finally:
            conn.close()
