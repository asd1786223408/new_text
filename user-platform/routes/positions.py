# -*- coding: utf-8 -*-
"""
岗位管理模块
"""
import json
import http.client
import re
from flask import Blueprint, request, session
from ..models.position import Position
from ..models.resume import Resume
from ..utils.response import success, error
from ..utils.db_pool import load_config

positions_bp = Blueprint('positions', __name__, url_prefix='/api/positions')


def get_dashscope_config():
    """获取千问配置"""
    config = load_config()
    return config.get('dashscope', {})


@positions_bp.route('', methods=['GET'])
def list_positions():
    """
    获取岗位列表
    GET /api/positions?status=状态&department=部门&keyword=关键词&page=页码&page_size=每页数量
    """
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 20))
    status = request.args.get('status')
    department = request.args.get('department', '')
    keyword = request.args.get('keyword', '')

    result = Position.list(page, page_size, status, department, keyword)
    return success(result)


@positions_bp.route('/<int:position_id>', methods=['GET'])
def get_position(position_id):
    """
    获取岗位详情
    GET /api/positions/<岗位 ID>
    """
    position = Position.get_by_id(position_id)
    if not position:
        return error('岗位不存在', 404)
    return success(position)


@positions_bp.route('', methods=['POST'])
def create_position():
    """
    创建岗位
    POST /api/positions
    Content-Type: application/json

    参数:
    - title: 岗位名称（必填）
    - description: 岗位描述
    - requirements: 任职要求
    - department: 所属部门
    - skills_required: 技能要求列表
    - headcount: 招聘人数
    - hire_by_date: 期望入职时间
    """
    data = request.get_json()
    if not data:
        return error('参数不能为空', 400)

    title = data.get('title', '').strip()
    if not title:
        return error('岗位名称不能为空', 400)

    user_id = session.get('user_id')

    position_id = Position.create(
        title=title,
        description=data.get('description', ''),
        requirements=data.get('requirements', ''),
        department=data.get('department'),
        skills_required=data.get('skills_required'),
        headcount=data.get('headcount', 1),
        hire_by_date=data.get('hire_by_date'),
        created_by=user_id
    )

    return success({'position_id': position_id}, '岗位创建成功')


@positions_bp.route('/<int:position_id>', methods=['PUT'])
def update_position(position_id):
    """
    更新岗位
    PUT /api/positions/<岗位 ID>
    Content-Type: application/json

    参数:
    - title: 岗位名称
    - description: 岗位描述
    - requirements: 任职要求
    - department: 所属部门
    - skills_required: 技能要求列表
    - headcount: 招聘人数
    - hire_by_date: 期望入职时间
    - status: 状态
    """
    data = request.get_json()
    if not data:
        return error('参数不能为空', 400)

    position = Position.get_by_id(position_id)
    if not position:
        return error('岗位不存在', 404)

    Position.update(position_id, **data)
    return success(message='岗位更新成功')


@positions_bp.route('/<int:position_id>', methods=['DELETE'])
def delete_position(position_id):
    """
    删除岗位（软删除，设为已结束）
    DELETE /api/positions/<岗位 ID>
    """
    position = Position.get_by_id(position_id)
    if not position:
        return error('岗位不存在', 404)

    Position.delete(position_id)
    return success(message='岗位已结束')


@positions_bp.route('/<int:position_id>/statistics', methods=['GET'])
def get_position_statistics(position_id):
    """
    获取岗位统计数据
    GET /api/positions/<岗位 ID>/statistics
    """
    position = Position.get_by_id(position_id)
    if not position:
        return error('岗位不存在', 404)

    stats = Position.get_statistics(position_id)
    top_candidates = Position.get_top_candidates(position_id, 10)

    return success({
        'position': {
            'id': position['id'],
            'title': position['title']
        },
        'statistics': stats,
        'top_candidates': top_candidates
    })


@positions_bp.route('/<int:position_id>/analyze', methods=['POST'])
def batch_analyze(position_id):
    """
    批量分析岗位下的简历
    POST /api/positions/<岗位 ID>/analyze

    参数:
    - unanalyzed_only: 是否只分析未分析过的简历（默认 true）
    """
    data = request.get_json() or {}
    unanalyzed_only = data.get('unanalyzed_only', True)

    position = Position.get_by_id(position_id)
    if not position:
        return error('岗位不存在', 404)

    # 获取简历列表
    resumes = Resume.list(page=1, page_size=1000, position_id=position_id, status=1)

    if unanalyzed_only:
        resume_list = [r for r in resumes.get('resumes', []) if r.get('analysis_score') is None]
    else:
        resume_list = resumes.get('resumes', [])

    if not resume_list:
        return success({'count': 0, 'message': '没有需要分析的简历'})

    # 构建岗位信息
    position_info = f"岗位：{position['title']}\n"
    if position.get('description'):
        position_info += f"岗位描述：{position['description']}\n"
    if position.get('requirements'):
        position_info += f"任职要求：{position['requirements']}"

    results = []
    failed = []

    for resume in resume_list:
        try:
            # 下载并解析简历
            file_data = Resume.download_from_cos(resume['cos_key'])
            resume_text = parse_resume_text(file_data, resume.get('file_type', ''), resume.get('file_name', ''))

            # 调用 AI 分析
            analysis, err = analyze_resume_by_qwen(resume_text, position_info)
            if err:
                failed.append({'id': resume['id'], 'error': err})
                continue

            # 保存分析结果
            Resume.update(resume['id'],
                analysis_score=analysis.get('match_score', 0),
                analysis_report=analysis
            )

            results.append({
                'id': resume['id'],
                'candidate': resume.get('candidate_name') or resume['file_name'],
                'score': analysis.get('match_score', 0)
            })
        except Exception as e:
            failed.append({'id': resume['id'], 'error': str(e)})

    return success({
        'total': len(resume_list),
        'success': len(results),
        'failed': len(failed),
        'results': results,
        'failed_details': failed
    }, f'分析完成，成功{len(results)}份，失败{len(failed)}份')


def parse_resume_text(file_data, file_type, file_name=''):
    """解析简历文件"""
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
        return ""


def analyze_resume_by_qwen(resume_text, position_info):
    """调用千问 API 分析简历"""
    config = get_dashscope_config()
    api_key = config.get('api_key', '')
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
