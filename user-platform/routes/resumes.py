# -*- coding: utf-8 -*-
"""
简历管理模块
"""
import json
import http.client
import re
from flask import Blueprint, request, send_file, session
import io
from ..models.resume import Resume
from ..models.position import Position
from ..utils.response import success, error
from ..utils.db_pool import load_config

resumes_bp = Blueprint('resumes', __name__, url_prefix='/api/resumes')


def get_dashscope_config():
    """获取千问配置"""
    config = load_config()
    return config.get('dashscope', {})


@resumes_bp.route('', methods=['GET'])
def list_resumes():
    """
    获取简历列表
    GET /api/resumes?position_id=岗位 ID&status=状态&keyword=关键词&page=页码&page_size=每页数量&sort=排序字段&order=顺序
    """
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 20))
    position_id = request.args.get('position_id')
    status = request.args.get('status')
    keyword = request.args.get('keyword', '')
    sort = request.args.get('sort', 'created_at')
    order = request.args.get('order', 'desc')

    result = Resume.list(page, page_size, position_id, status, keyword, sort, order)
    return success(result)


@resumes_bp.route('/<int:resume_id>', methods=['GET'])
def get_resume(resume_id):
    """
    获取简历详情
    GET /api/resumes/<简历 ID>
    """
    resume = Resume.get_by_id(resume_id)
    if not resume:
        return error('简历不存在', 404)
    return success(resume)


@resumes_bp.route('/upload', methods=['POST'])
def upload_resume():
    """
    上传简历（单文件）
    POST /api/resumes/upload
    Content-Type: multipart/form-data

    参数:
    - file: 简历文件
    - position_id: 岗位 ID
    - position_name: 岗位名称
    - candidate_name: 候选人姓名
    - candidate_phone: 候选人电话
    - candidate_email: 候选人邮箱
    """
    user_id = session.get('user_id')
    username = session.get('username')

    if 'file' not in request.files:
        return error('未找到文件', 400)

    file = request.files.get('file')
    if file.filename == '':
        return error('文件名为空', 400)

    # 读取文件
    file_data = file.read()
    file_name = file.filename
    file_type = file.content_type or ''

    # 上传到 COS
    try:
        cos_key = Resume.upload_to_cos(file_data, file_name)
    except Exception as e:
        return error(f'上传失败：{str(e)}', 500)

    # 创建记录
    resume_id = Resume.create(
        file_name=file_name,
        cos_key=cos_key,
        file_size=len(file_data),
        file_type=file_type,
        position_id=request.form.get('position_id', type=int),
        position_name=request.form.get('position_name'),
        candidate_name=request.form.get('candidate_name'),
        candidate_phone=request.form.get('candidate_phone'),
        candidate_email=request.form.get('candidate_email'),
        upload_user_id=user_id,
        upload_username=username
    )

    return success({
        'id': resume_id,
        'file_name': file_name,
        'cos_key': cos_key
    }, '上传成功')


@resumes_bp.route('/batch-upload', methods=['POST'])
def batch_upload():
    """
    批量上传简历
    POST /api/resumes/batch-upload
    Content-Type: multipart/form-data

    参数:
    - files[]: 文件列表
    - position_id: 岗位 ID
    - position_name: 岗位名称
    - items: JSON 数组，每个元素包含 {file_index, position_id, position_name, candidate_name, candidate_phone, candidate_email}
    """
    user_id = session.get('user_id')
    username = session.get('username')

    if 'files' not in request.files:
        return error('未找到文件', 400)

    files = request.files.getlist('files')
    if not files:
        return error('文件列表为空', 400)

    # 获取统一的岗位信息
    position_id = request.form.get('position_id', type=int)
    position_name = request.form.get('position_name')

    # 获取每个文件的详细信息
    items_json = request.form.get('items')
    items = json.loads(items_json) if items_json else []

    results = []
    failed = []

    for index, file in enumerate(files):
        if file.filename == '':
            failed.append({'index': index, 'error': '文件名为空'})
            continue

        # 查找该文件的详细信息
        item_info = next((item for item in items if item.get('file_index') == index), {})

        file_position_id = item_info.get('position_id') or position_id
        file_position_name = item_info.get('position_name') or position_name

        try:
            file_data = file.read()
            cos_key = Resume.upload_to_cos(file_data, file.filename)

            resume_id = Resume.create(
                file_name=file.filename,
                cos_key=cos_key,
                file_size=len(file_data),
                file_type=file.content_type or '',
                position_id=file_position_id,
                position_name=file_position_name,
                candidate_name=item_info.get('candidate_name'),
                candidate_phone=item_info.get('candidate_phone'),
                candidate_email=item_info.get('candidate_email'),
                upload_user_id=user_id,
                upload_username=username
            )

            results.append({
                'id': resume_id,
                'file_name': file.filename,
                'cos_key': cos_key
            })
        except Exception as e:
            failed.append({'index': index, 'filename': file.filename, 'error': str(e)})

    return success({
        'success': len(failed) == 0,
        'count': len(results),
        'results': results,
        'failed': failed
    })


@resumes_bp.route('/<int:resume_id>/download', methods=['GET'])
def download_resume(resume_id):
    """
    下载简历
    GET /api/resumes/<简历 ID>/download
    """
    resume = Resume.get_by_id(resume_id)
    if not resume:
        return error('简历不存在', 404)
    if resume['status'] == 0:
        return error('简历已被删除', 404)

    try:
        file_data = Resume.download_from_cos(resume['cos_key'])
        Resume.increment_download_count(resume_id)

        return send_file(
            io.BytesIO(file_data),
            as_attachment=True,
            download_name=resume['file_name']
        )
    except Exception as e:
        return error(f'下载失败：{str(e)}', 500)


@resumes_bp.route('/<int:resume_id>/url', methods=['GET'])
def get_resume_url(resume_id):
    """
    生成临时访问链接
    GET /api/resumes/<简历 ID>/url?expired=过期时间 (秒)
    """
    resume = Resume.get_by_id(resume_id)
    if not resume:
        return error('简历不存在', 404)

    expired = int(request.args.get('expired', 3600))
    url = Resume.get_presigned_url(resume['cos_key'], expired)

    return success({
        'id': resume_id,
        'file_name': resume['file_name'],
        'url': url,
        'expired': expired
    })


@resumes_bp.route('/<int:resume_id>', methods=['PUT'])
def update_resume(resume_id):
    """
    更新简历
    PUT /api/resumes/<简历 ID>
    Content-Type: application/json

    参数:
    - position_id: 岗位 ID
    - position_name: 岗位名称
    - candidate_name: 候选人姓名
    - candidate_phone: 候选人电话
    - candidate_email: 候选人邮箱
    - status: 状态
    """
    data = request.get_json()
    if not data:
        return error('参数不能为空', 400)

    resume = Resume.get_by_id(resume_id)
    if not resume:
        return error('简历不存在', 404)

    Resume.update(resume_id, **data)
    return success(message='更新成功')


@resumes_bp.route('/<int:resume_id>', methods=['DELETE'])
def delete_resume(resume_id):
    """
    删除简历（软删除）
    DELETE /api/resumes/<简历 ID>
    """
    resume = Resume.get_by_id(resume_id)
    if not resume:
        return error('简历不存在', 404)

    Resume.delete(resume_id)
    return success(message='删除成功')


# ==================== 简历分析接口 ====================

def parse_resume_text(file_data, file_type, file_name=''):
    """解析简历文件，提取文本内容"""
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


@resumes_bp.route('/<int:resume_id>/analyze', methods=['POST'])
def analyze_resume(resume_id):
    """
    分析简历
    POST /api/resumes/<简历 ID>/analyze
    """
    resume = Resume.get_by_id(resume_id)
    if not resume:
        return error('简历不存在', 404)

    # 获取岗位信息
    position_info = f"岗位：{resume.get('position_name', '未指定')}\n"
    if resume.get('position_id'):
        position = Position.get_by_id(resume['position_id'])
        if position:
            if position.get('description'):
                position_info += f"岗位描述：{position['description']}\n"
            if position.get('requirements'):
                position_info += f"任职要求：{position['requirements']}"

    # 下载并解析简历
    try:
        file_data = Resume.download_from_cos(resume['cos_key'])
        resume_text = parse_resume_text(file_data, resume.get('file_type', ''), resume.get('file_name', ''))
    except Exception as e:
        return error(f'读取简历失败：{str(e)}', 500)

    # 调用 AI 分析
    analysis, err = analyze_resume_by_qwen(resume_text, position_info)
    if err:
        return error(f'AI 分析失败：{err}', 500)

    # 保存分析结果
    Resume.update(resume_id,
        analysis_score=analysis.get('match_score', 0),
        analysis_report=analysis,
        analyzed_at=None  # 由数据库自动设置
    )

    return success({
        'id': resume_id,
        'score': analysis.get('match_score', 0),
        'analysis': analysis
    }, '分析完成')
