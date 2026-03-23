# 简历附件 API 文档

腾讯云 COS 对象存储 + 数据库管理的简历附件服务。

## 服务地址

- 本地：`http://localhost:8001`
- 服务器：`http://172.24.5.125:8001`

## 配置

配置位于根目录的 `env.json`，包含 COS 和 MySQL 的连接信息。

## 数据库表

`resume_attachments` - 简历附件表，记录文件信息、COS 路径、岗位信息、候选人信息等。

---

## 接口列表

### 1. 健康检查

```http
GET /health
```

**响应示例**
```json
{"status": "ok", "timestamp": "2026-03-21T10:00:00"}
```

---

### 2. 批量上传简历

```http
POST /batch-upload
Content-Type: multipart/form-data
```

**参数说明**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| files[] | File[] | 是 | 文件列表，支持多文件 |
| position_id | int | 否 | 统一岗位 ID |
| position_name | string | 否 | 统一岗位名称 |
| upload_user_id | int | 否 | 上传用户 ID |
| upload_username | string | 否 | 上传用户名 |
| items | JSON | 否 | 每个文件的详细信息（见下方） |

**items 格式**（当每个文件需要独立的岗位/候选人信息时）

```json
[
  {
    "file_index": 0,
    "position_id": 1001,
    "position_name": "Java 开发工程师",
    "candidate_name": "张三",
    "candidate_phone": "13800138000",
    "candidate_email": "zhangsan@example.com"
  },
  {
    "file_index": 1,
    "position_id": 1002,
    "position_name": "前端开发工程师",
    "candidate_name": "李四",
    "candidate_phone": "13900139000",
    "candidate_email": "lisi@example.com"
  }
]
```

**curl 请求示例**

```bash
# 简单模式：所有文件共享同一岗位信息
curl -X POST \
  -F "files=@resume1.pdf" \
  -F "files=@resume2.pdf" \
  -F "position_id=1001" \
  -F "position_name=Java 开发工程师" \
  -F "upload_username=admin" \
  http://localhost:8001/batch-upload

# 高级模式：每个文件独立信息
curl -X POST \
  -F "files=@resume1.pdf" \
  -F "files=@resume2.pdf" \
  -F 'items=[{"file_index":0,"position_id":1001,"position_name":"Java 开发","candidate_name":"张三","candidate_phone":"13800138000"},{"file_index":1,"position_id":1002,"position_name":"前端开发","candidate_name":"李四","candidate_phone":"13900139000"}]' \
  http://localhost:8001/batch-upload
```

**响应示例**
```json
{
  "success": true,
  "count": 2,
  "results": [
    {
      "id": 1,
      "file_name": "resume1.pdf",
      "cos_key": "resume/2026/03/21/20260321100000123456_resume1.pdf",
      "position_id": 1001,
      "position_name": "Java 开发工程师",
      "size": 102400,
      "upload_time": "2026-03-21T10:00:00"
    },
    {
      "id": 2,
      "file_name": "resume2.pdf",
      "cos_key": "resume/2026/03/21/20260321100000123457_resume2.pdf",
      "position_id": 1002,
      "position_name": "前端开发工程师",
      "size": 98304,
      "upload_time": "2026-03-21T10:00:00"
    }
  ],
  "failed": []
}
```

---

### 3. 下载简历文件

```http
GET /download/<文件 ID>
```

**请求示例**
```bash
# 直接下载文件
curl http://localhost:8001/download/1 -o resume.pdf

# 或者获取带文件名的附件
curl -O -J http://localhost:8001/download/1
```

**说明**
- 下载成功后自动增加下载次数
- 文件不存在或已删除返回 404

---

### 4. 获取文件详情

```http
GET /<文件 ID>
```

**响应示例**
```json
{
  "id": 1,
  "file_name": "resume1.pdf",
  "file_size": 102400,
  "file_type": "application/pdf",
  "cos_key": "resume/2026/03/21/20260321100000123456_resume1.pdf",
  "position_id": 1001,
  "position_name": "Java 开发工程师",
  "candidate_name": "张三",
  "candidate_phone": "13800138000",
  "candidate_email": "zhangsan@example.com",
  "upload_user_id": null,
  "upload_username": "admin",
  "status": 1,
  "download_count": 5,
  "created_at": "2026-03-21T10:00:00",
  "updated_at": "2026-03-21T10:30:00"
}
```

---

### 5. 列出简历文件

```http
GET /list?position_id=岗位 ID&status=状态&keyword=关键词&page=页码&page_size=每页数量
```

**参数说明**

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| position_id | int | - | 按岗位 ID 筛选 |
| status | int | 1 | 状态：1-有效，0-无效，空-全部 |
| keyword | string | - | 搜索文件名/候选人姓名/电话 |
| page | int | 1 | 页码 |
| page_size | int | 20 | 每页数量 |

**请求示例**
```bash
# 查看所有有效简历
curl "http://localhost:8001/list"

# 按岗位筛选
curl "http://localhost:8001/list?position_id=1001"

# 搜索候选人
curl "http://localhost:8001/list?keyword=张三"

# 分页
curl "http://localhost:8001/list?page=1&page_size=50"
```

**响应示例**
```json
{
  "total": 100,
  "page": 1,
  "page_size": 20,
  "total_pages": 5,
  "files": [
    {
      "id": 1,
      "file_name": "resume1.pdf",
      "file_size": 102400,
      "file_type": "application/pdf",
      "position_id": 1001,
      "position_name": "Java 开发工程师",
      "candidate_name": "张三",
      "candidate_phone": "13800138000",
      "candidate_email": "zhangsan@example.com",
      "upload_username": "admin",
      "status": 1,
      "download_count": 5,
      "created_at": "2026-03-21T10:00:00",
      "updated_at": "2026-03-21T10:30:00"
    }
  ]
}
```

---

### 6. 删除文件（软删除）

```http
DELETE /<文件 ID>
```

**请求示例**
```bash
curl -X DELETE http://localhost:8001/1
```

**响应示例**
```json
{"success": true, "id": 1}
```

**说明**
- 软删除：仅将 status 设为 0，不从 COS 删除文件
- 删除后的文件无法通过 download 接口下载

---

### 7. 生成临时访问链接

```http
GET /url/<文件 ID>?expired=过期时间 (秒)
```

**请求示例**
```bash
# 生成 1 小时有效的下载链接
curl "http://localhost:8001/url/1?expired=3600"

# 生成 5 分钟有效的下载链接
curl "http://localhost:8001/url/1?expired=300"
```

**响应示例**
```json
{
  "id": 1,
  "file_name": "resume1.pdf",
  "url": "https://huangyige-1304042484.cos.ap-guangzhou.myqcloud.com/resume/2026/03/21/xxx?q-sign-algorithm=sha1&q-ak=xxx&q-sign-time=xxx&q-key-time=xxx&q-header-list=xxx&q-url-param-list=xxx&q-signature=xxx",
  "expired": 3600
}
```

---

## 使用场景

### 场景 1：HR 批量上传简历到某个岗位

```bash
curl -X POST \
  -F "files=@张三_简历.pdf" \
  -F "files=@李四_简历.pdf" \
  -F "files=@王五_简历.pdf" \
  -F "position_id=1001" \
  -F "position_name=Java 开发工程师" \
  -F "upload_username=hr001" \
  http://localhost:8001/batch-upload
```

### 场景 2：带候选人信息的批量上传

```bash
curl -X POST \
  -F "files=@zhangsan.pdf" \
  -F "files=@lisi.pdf" \
  -F 'items=[
    {
      "file_index":0,
      "position_id":1001,
      "position_name":"Java 开发",
      "candidate_name":"张三",
      "candidate_phone":"13800138000",
      "candidate_email":"zhangsan@email.com"
    },
    {
      "file_index":1,
      "position_id":1001,
      "position_name":"Java 开发",
      "candidate_name":"李四",
      "candidate_phone":"13900139000",
      "candidate_email":"lisi@email.com"
    }
  ]' \
  http://localhost:8001/batch-upload
```

### 场景 3：查看某岗位的所有简历

```bash
curl "http://localhost:8001/list?position_id=1001"
```

### 场景 4：下载简历

```bash
# 直接下载
curl http://localhost:8001/download/1 -o resume.pdf

# 或者获取临时链接（用于前端直接下载）
curl "http://localhost:8001/url/1?expired=300"
# 返回 URL 后，前端可直接用 <a href="url" download> 下载
```

---

## 文件结构

```
resume-api/
├── app.py           # 主程序
├── requirements.txt # Python 依赖
├── init.sql         # 数据库初始化脚本
└── API.md           # 接口文档（本文件）
```

---

## 启动服务

首次启动前初始化数据库：
```bash
mysql -u root -p user_platform < init.sql
```

启动服务：
```bash
cd resume-api
pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
python app.py
```

后台运行：
```bash
nohup python app.py > resume-api.log 2>&1 &
```

---

## 数据存储说明

1. **文件存储**: 所有简历文件存储于腾讯云 COS，路径格式 `resume/年/月/日/时间戳_文件名`
2. **元数据存储**: 数据库记录文件信息、岗位信息、候选人信息、下载次数等
3. **软删除**: 删除操作仅标记状态，不物理删除 COS 文件，便于恢复
