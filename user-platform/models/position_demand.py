# -*- coding: utf-8 -*-
"""
岗位需求模型
"""
import json
from ..utils.db_pool import get_db_connection


class PositionDemand:
    """岗位需求模型类"""

    @staticmethod
    def create(title, description='', requirements='', custom_field=None,
               salary_min=None, salary_max=None, work_location=None,
               experience_years=None, education_required=None, skills_required=None,
               department=None, headcount=1, job_type='full_time',
               contact_info=None, user_id=None, username=None):
        """创建岗位需求"""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO position_demands
                    (title, description, requirements, custom_field,
                     salary_min, salary_max, work_location, experience_years, education_required,
                     skills_required, department, headcount, job_type,
                     contact_info, user_id, username, status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 0)
                """, (title, description, requirements, custom_field,
                      salary_min, salary_max, work_location, experience_years, education_required,
                      json.dumps(skills_required) if skills_required else None,
                      department, headcount, job_type, contact_info, user_id, username))
                demand_id = cursor.lastrowid
                conn.commit()
            return demand_id
        finally:
            conn.close()

    @staticmethod
    def get_by_id(demand_id):
        """根据 ID 获取岗位需求"""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM position_demands WHERE id = %s
                """, (demand_id,))
                demand = cursor.fetchone()
                if demand:
                    # 解析 JSON 字段
                    if demand.get('skills_required') and isinstance(demand['skills_required'], str):
                        demand['skills_required'] = json.loads(demand['skills_required'])
                    if demand.get('ai_analysis') and isinstance(demand['ai_analysis'], str):
                        demand['ai_analysis'] = json.loads(demand['ai_analysis'])
                    if demand.get('ai_suggestions') and isinstance(demand['ai_suggestions'], str):
                        demand['ai_suggestions'] = json.loads(demand['ai_suggestions'])
            return demand
        finally:
            conn.close()

    @staticmethod
    def list(page=1, page_size=20, status=None, user_id=None, keyword=None, job_type=None):
        """获取岗位需求列表"""
        conn = get_db_connection()
        try:
            conditions = []
            params = []

            if status is not None:
                conditions.append('status = %s')
                params.append(status)
            if user_id:
                conditions.append('user_id = %s')
                params.append(user_id)
            if job_type:
                conditions.append('job_type = %s')
                params.append(job_type)
            if keyword:
                conditions.append('(title LIKE %s OR description LIKE %s OR requirements LIKE %s)')
                keyword_pattern = f'%{keyword}%'
                params.extend([keyword_pattern] * 3)

            where_clause = ' AND '.join(conditions) if conditions else '1=1'
            offset = (page - 1) * page_size

            with conn.cursor() as cursor:
                # 总数
                cursor.execute(f"""
                    SELECT COUNT(*) as total FROM position_demands WHERE {where_clause}
                """, params)
                total = cursor.fetchone()['total']

                # 列表
                params_for_list = params.copy() + [page_size, offset]
                cursor.execute(f"""
                    SELECT id, title, description, requirements, custom_field,
                           salary_min, salary_max, work_location, experience_years, education_required,
                           department, headcount, job_type, contact_info,
                           status, ai_score, user_id, username,
                           published_at, created_at, updated_at
                    FROM position_demands
                    WHERE {where_clause}
                    ORDER BY created_at DESC
                    LIMIT %s OFFSET %s
                """, params_for_list)
                demands = cursor.fetchall()

            # 解析 JSON 字段
            for d in demands:
                if d.get('custom_field') and isinstance(d['custom_field'], str):
                    try:
                        d['custom_field'] = json.loads(d['custom_field'])
                    except:
                        pass

            return {
                'total': total,
                'page': page,
                'page_size': page_size,
                'total_pages': (total + page_size - 1) // page_size,
                'demands': demands
            }
        finally:
            conn.close()

    @staticmethod
    def update(demand_id, **kwargs):
        """更新岗位需求"""
        allowed_fields = ['title', 'description', 'requirements', 'custom_field',
                          'salary_min', 'salary_max', 'work_location', 'experience_years',
                          'education_required', 'skills_required', 'department',
                          'headcount', 'job_type', 'contact_info', 'status']
        update_data = {k: v for k, v in kwargs.items() if k in allowed_fields}

        if not update_data:
            return False

        # 处理 skills_required
        if 'skills_required' in update_data and isinstance(update_data['skills_required'], list):
            update_data['skills_required'] = json.dumps(update_data['skills_required'])
        # 处理 custom_field
        if 'custom_field' in update_data and isinstance(update_data['custom_field'], (dict, list)):
            update_data['custom_field'] = json.dumps(update_data['custom_field'])

        conn = get_db_connection()
        try:
            set_clause = ', '.join([f'{k} = %s' for k in update_data.keys()])
            values = list(update_data.values()) + [demand_id]

            with conn.cursor() as cursor:
                cursor.execute(f"""
                    UPDATE position_demands SET {set_clause}
                    WHERE id = %s
                """, values)
                conn.commit()
            return True
        finally:
            conn.close()

    @staticmethod
    def delete(demand_id):
        """删除岗位需求"""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM position_demands WHERE id = %s", (demand_id,))
                conn.commit()
            return True
        finally:
            conn.close()

    @staticmethod
    def update_analysis(demand_id, ai_analysis, ai_score, ai_suggestions):
        """更新 AI 分析结果"""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE position_demands
                    SET ai_analysis = %s, ai_score = %s, ai_suggestions = %s, analyzed_at = NOW()
                    WHERE id = %s
                """, (json.dumps(ai_analysis), ai_score, json.dumps(ai_suggestions), demand_id))
                conn.commit()
            return True
        finally:
            conn.close()

    @staticmethod
    def publish(demand_id):
        """发布岗位需求（审核通过）"""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE position_demands
                    SET status = 1, published_at = NOW()
                    WHERE id = %s
                """, (demand_id,))
                conn.commit()
            return True
        finally:
            conn.close()

    @staticmethod
    def reject(demand_id):
        """拒绝岗位需求"""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("UPDATE position_demands SET status = 3 WHERE id = %s", (demand_id,))
                conn.commit()
            return True
        finally:
            conn.close()

    @staticmethod
    def close(demand_id):
        """关闭岗位需求"""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("UPDATE position_demands SET status = 2 WHERE id = %s", (demand_id,))
                conn.commit()
            return True
        finally:
            conn.close()
