# -*- coding: utf-8 -*-
"""
岗位需求管理模块
"""
import json
import http.client
import re
from flask import Blueprint, request, session
from ..models.position_demand import PositionDemand
from ..utils.response import success, error
from ..utils.db_pool import load_config

demands_bp = Blueprint('demands', __name__, url_prefix='/api/demands')


def get_dashscope_config():
    """获取千问配置"""
    config = load_config()
    return config.get('dashscope', {})


@demands_bp.route('', methods=['GET'])
def list_demands():
    """
    获取岗位需求列表
    GET /api/demands?status=状态&user_id=用户 ID&keyword=关键词&job_type=工作性质&page=页码&page_size=每页数量

    参数:
    - status: 状态（0-待审核，1-已发布，2-已关闭，3-已拒绝）
    - user_id: 发布人 ID
    - keyword: 搜索关键词
    - job_type: 工作性质（full_time/part_time/intern）
    """
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 20))
    status = request.args.get('status')
    user_id = request.args.get('user_id')
    keyword = request.args.get('keyword', '')
    job_type = request.args.get('job_type', '')

    result = PositionDemand.list(page, page_size, status, user_id, keyword, job_type)
    return success(result)


@demands_bp.route('/<int:demand_id>', methods=['GET'])
def get_demand(demand_id):
    """
    获取岗位需求详情
    GET /api/demands/<需求 ID>
    """
    demand = PositionDemand.get_by_id(demand_id)
    if not demand:
        return error('需求不存在', 404)
    return success(demand)


@demands_bp.route('', methods=['POST'])
def create_demand():
    """
    发布岗位需求
    POST /api/demands
    Content-Type: application/json

    参数:
    - title: 需求标题（必填）
    - description: 岗位描述
    - requirements: 任职要求
    - custom_field: 自定义字段（用户自定义内容，可以是字符串或 JSON 对象）
    - salary_min: 最低薪资
    - salary_max: 最高薪资
    - work_location: 工作地点
    - experience_years: 经验要求（如：3-5 年）
    - education_required: 学历要求（专科/本科/硕士/博士）
    - skills_required: 技能要求列表（JSON 数组）
    - department: 所属部门
    - headcount: 招聘人数
    - job_type: 工作性质（full_time-全职，part_time-兼职，intern-实习）
    - contact_info: 联系方式
    """
    user_id = session.get('user_id')
    username = session.get('username')

    if not user_id:
        return error('请先登录', 401)

    data = request.get_json()
    if not data:
        return error('参数不能为空', 400)

    title = data.get('title', '').strip()
    if not title:
        return error('需求标题不能为空', 400)

    # 创建需求
    demand_id = PositionDemand.create(
        title=title,
        description=data.get('description', ''),
        requirements=data.get('requirements', ''),
        custom_field=data.get('custom_field'),  # 自定义字段
        salary_min=data.get('salary_min'),
        salary_max=data.get('salary_max'),
        work_location=data.get('work_location'),
        experience_years=data.get('experience_years'),
        education_required=data.get('education_required'),
        skills_required=data.get('skills_required'),
        department=data.get('department'),
        headcount=data.get('headcount', 1),
        job_type=data.get('job_type', 'full_time'),
        contact_info=data.get('contact_info'),
        user_id=user_id,
        username=username
    )

    return success({'demand_id': demand_id}, '需求发布成功，请等待审核')


@demands_bp.route('/<int:demand_id>', methods=['PUT'])
def update_demand(demand_id):
    """
    更新岗位需求
    PUT /api/demands/<需求 ID>
    Content-Type: application/json

    参数:
    - title: 需求标题
    - description: 岗位描述
    - requirements: 任职要求
    - custom_field: 自定义字段
    - salary_min: 最低薪资
    - salary_max: 最高薪资
    - work_location: 工作地点
    - experience_years: 经验要求
    - education_required: 学历要求
    - skills_required: 技能要求列表
    - department: 所属部门
    - headcount: 招聘人数
    - job_type: 工作性质
    - contact_info: 联系方式
    """
    user_id = session.get('user_id')
    if not user_id:
        return error('请先登录', 401)

    demand = PositionDemand.get_by_id(demand_id)
    if not demand:
        return error('需求不存在', 404)

    # 只能更新自己的需求
    if demand['user_id'] != user_id:
        return error('无权限修改该需求', 403)

    # 已发布或已关闭的需求不能修改
    if demand['status'] in [1, 2, 3]:
        return error('当前状态无法修改', 400)

    data = request.get_json() or {}
    PositionDemand.update(demand_id, **data)

    return success(message='需求更新成功')


@demands_bp.route('/<int:demand_id>', methods=['DELETE'])
def delete_demand(demand_id):
    """
    删除岗位需求
    DELETE /api/demands/<需求 ID>
    """
    user_id = session.get('user_id')
    if not user_id:
        return error('请先登录', 401)

    demand = PositionDemand.get_by_id(demand_id)
    if not demand:
        return error('需求不存在', 404)

    # 只能删除自己的需求
    if demand['user_id'] != user_id:
        return error('无权限删除该需求', 403)

    PositionDemand.delete(demand_id)
    return success(message='需求删除成功')


@demands_bp.route('/<int:demand_id>/close', methods=['POST'])
def close_demand(demand_id):
    """
    关闭岗位需求
    POST /api/demands/<需求 ID>/close
    """
    user_id = session.get('user_id')
    if not user_id:
        return error('请先登录', 401)

    demand = PositionDemand.get_by_id(demand_id)
    if not demand:
        return error('需求不存在', 404)

    if demand['user_id'] != user_id:
        return error('无权限操作', 403)

    PositionDemand.close(demand_id)
    return success(message='需求已关闭')


@demands_bp.route('/<int:demand_id>/analyze', methods=['POST'])
def analyze_demand(demand_id):
    """
    AI 分析岗位需求
    POST /api/demands/<需求 ID>/analyze

    AI 会分析岗位需求的合理性，并给出优化建议
    """
    demand = PositionDemand.get_by_id(demand_id)
    if not demand:
        return error('需求不存在', 404)

    # 构建分析内容
    demand_info = f"""
岗位名称：{demand.get('title', '')}
岗位描述：{demand.get('description', '')}
任职要求：{demand.get('requirements', '')}
自定义要求：{demand.get('custom_field', '')}
工作地点：{demand.get('work_location', '')}
经验要求：{demand.get('experience_years', '')}
学历要求：{demand.get('education_required', '')}
薪资范围：{demand.get('salary_min', '')}-{demand.get('salary_max', '')}
工作性质：{demand.get('job_type', '')}
"""

    # 调用 AI 分析
    analysis, err = analyze_demand_by_qwen(demand_info)
    if err:
        return error(f'AI 分析失败：{err}', 500)

    # 保存分析结果
    PositionDemand.update_analysis(
        demand_id,
        analysis.get('analysis', {}),
        analysis.get('score', 0),
        analysis.get('suggestions', [])
    )

    return success({
        'id': demand_id,
        'score': analysis.get('score', 0),
        'analysis': analysis.get('analysis', {}),
        'suggestions': analysis.get('suggestions', [])
    }, 'AI 分析完成')


# ==================== 管理员审核接口 ====================

@demands_bp.route('/<int:demand_id>/approve', methods=['POST'])
def approve_demand(demand_id):
    """
    审核通过岗位需求（管理员）
    POST /api/demands/<需求 ID>/approve
    """
    user_id = session.get('user_id')
    if not user_id:
        return error('请先登录', 401)

    # TODO: 这里应该检查用户是否有管理员权限
    demand = PositionDemand.get_by_id(demand_id)
    if not demand:
        return error('需求不存在', 404)

    PositionDemand.publish(demand_id)
    return success(message='需求已发布')


@demands_bp.route('/<int:demand_id>/reject', methods=['POST'])
def reject_demand(demand_id):
    """
    拒绝岗位需求（管理员）
    POST /api/demands/<需求 ID>/reject

    参数:
    - reason: 拒绝原因
    """
    user_id = session.get('user_id')
    if not user_id:
        return error('请先登录', 401)

    data = request.get_json() or {}
    reason = data.get('reason', '')

    # TODO: 这里应该检查用户是否有管理员权限
    demand = PositionDemand.get_by_id(demand_id)
    if not demand:
        return error('需求不存在', 404)

    # 可以在这里记录拒绝原因到 ai_suggestions 或其他字段
    PositionDemand.reject(demand_id)
    return success(message=f'需求已拒绝：{reason}')


# ==================== AI 分析函数 ====================

def analyze_demand_by_qwen(demand_info):
    """调用千问 API 分析岗位需求"""
    config = get_dashscope_config()
    api_key = config.get('api_key', '')
    if not api_key:
        return None, "未配置千问 API Key"

    prompt = f"""你是一位专业的 HR 顾问和招聘专家，请分析以下岗位需求的合理性和完整性。

{demand_info}

请从以下维度进行分析：
1. 岗位描述是否清晰完整
2. 任职要求是否合理（与岗位名称是否匹配）
3. 薪资范围是否符合市场水平（如果提供了）
4. 学历要求和经验要求是否合理
5. 自定义字段是否有特殊要求需要注意

请按照以下 JSON 格式输出分析结果（不要输出其他内容）：
{{
    "score": 85,
    "analysis": {{
        "title_clarity": "岗位名称清晰度评价",
        "description_quality": "岗位描述质量评价",
        "requirements_reasonable": "任职要求合理性评价",
        "salary_competitive": "薪资竞争力评价（如有）",
        "overall_comment": "整体评价"
    }},
    "suggestions": [
        "建议 1：具体优化建议",
        "建议 2：具体优化建议"
    ]
}}

评分标准：
- score: 0-100 分，岗位需求的整体质量分
- suggestions: 至少给出 2-3 条具体的优化建议
"""

    try:
        connection = http.client.HTTPSConnection("dashscope.aliyuncs.com")
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = json.dumps({
            "model": config.get('model', 'qwen-plus'),
            "input": {
                "messages": [
                    {"role": "system", "content": "你是一位专业的 HR 顾问和招聘专家，负责分析岗位需求的合理性和完整性。"},
                    {"role": "user", "content": prompt}
                ]
            },
            "parameters": {
                "temperature": 0.3,
                "max_tokens": 1500
            }
        })

        connection.request("POST", "/api/v1/services/aigc/text-generation/generation", payload, headers)
        response = connection.getresponse()
        result = response.read().decode('utf-8')
        connection.close()

        result_json = json.loads(result)

        if 'output' in result_json and 'choices' in result_json['output']:
            content = result_json['output']['choices'][0]['message']['content']
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                analysis = json.loads(json_match.group())
                return analysis, None
            else:
                return None, "解析 AI 返回结果失败"
        else:
            return None, result_json.get('message', 'API 调用失败')

    except Exception as e:
        return None, str(e)
