# 用户平台 - API 接口文档

## 服务地址

- 本地：`http://localhost:8000`
- 服务器：`http://172.24.5.125:8000`

## 配置

配置文件位于 `config/env.json`，包含：
- MySQL 数据库配置
- Redis Session 配置
- COS 对象存储配置
- Dashscope（千问）AI 配置

---

## 认证模块 `/api/auth`

### 1. 用户登录

```http
POST /api/auth/login
Content-Type: application/json
```

**请求参数**
```json
{
  "account": "admin",
  "password": "admin123"
}
```

**响应示例**
```json
{
  "code": 0,
  "message": "登录成功",
  "data": {
    "user_id": 1,
    "username": "admin",
    "nickname": "管理员",
    "avatar": null,
    "permissions": ["user:create", "user:read", "..."]
  }
}
```

---

### 2. 用户登出

```http
POST /api/auth/logout
```

**响应示例**
```json
{
  "code": 0,
  "message": "登出成功",
  "data": {}
}
```

---

### 3. 获取当前用户信息

```http
GET /api/auth/info
```

**响应示例**
```json
{
  "code": 0,
  "message": "操作成功",
  "data": {
    "id": 1,
    "username": "admin",
    "nickname": "管理员",
    "email": "admin@example.com",
    "phone": null,
    "department_id": 1,
    "position": null,
    "permissions": ["user:create", "user:read", "..."]
  }
}
```

---

### 4. 修改密码

```http
POST /api/auth/change-password
Content-Type: application/json
```

**请求参数**
```json
{
  "old_password": "admin123",
  "new_password": "new123456"
}
```

---

## 用户管理模块 `/api/users`

### 1. 获取用户列表

```http
GET /api/users?department_id=1&status=1&keyword=张三&page=1&page_size=20
```

**响应示例**
```json
{
  "code": 0,
  "message": "操作成功",
  "data": {
    "total": 10,
    "page": 1,
    "page_size": 20,
    "total_pages": 1,
    "users": [
      {
        "id": 1,
        "username": "admin",
        "nickname": "管理员",
        "email": "admin@example.com",
        "department_id": 1,
        "department_name": "总公司",
        "status": 1,
        "created_at": "2026-03-20T10:00:00"
      }
    ]
  }
}
```

---

### 2. 获取用户详情

```http
GET /api/users/<用户 ID>
```

---

### 3. 创建用户

```http
POST /api/users
Content-Type: application/json
```

**请求参数**
```json
{
  "username": "zhangsan",
  "password": "123456",
  "email": "zhangsan@example.com",
  "phone": "13800138000",
  "nickname": "张三",
  "department_id": 2,
  "position": "工程师",
  "role_ids": [3]
}
```

---

### 4. 更新用户

```http
PUT /api/users/<用户 ID>
Content-Type: application/json
```

**请求参数**
```json
{
  "nickname": "张三丰",
  "phone": "13900139000",
  "status": 1,
  "role_ids": [2, 3]
}
```

---

### 5. 删除用户

```http
DELETE /api/users/<用户 ID>
```

---

## 部门管理模块 `/api/departments`

### 1. 获取部门树

```http
GET /api/departments/tree
```

**响应示例**
```json
{
  "code": 0,
  "message": "操作成功",
  "data": [
    {
      "id": 1,
      "name": "总公司",
      "parent_id": 0,
      "level": 1,
      "user_count": 5,
      "children": [
        {
          "id": 2,
          "name": "技术部",
          "parent_id": 1,
          "level": 2,
          "user_count": 3,
          "children": []
        }
      ]
    }
  ]
}
```

---

### 2. 获取部门列表（扁平化）

```http
GET /api/departments/list
```

---

### 3. 获取部门详情

```http
GET /api/departments/<部门 ID>
```

---

### 4. 创建部门

```http
POST /api/departments
Content-Type: application/json
```

**请求参数**
```json
{
  "name": "市场部",
  "parent_id": 1,
  "leader_id": 5
}
```

---

### 5. 更新部门

```http
PUT /api/departments/<部门 ID>
Content-Type: application/json
```

---

### 6. 删除部门

```http
DELETE /api/departments/<部门 ID>
```

---

## 角色管理模块 `/api/roles`

### 1. 获取角色列表

```http
GET /api/roles?keyword=管理员&page=1&page_size=20
```

**响应示例**
```json
{
  "code": 0,
  "message": "操作成功",
  "data": {
    "total": 3,
    "page": 1,
    "page_size": 20,
    "total_pages": 1,
    "roles": [
      {
        "id": 1,
        "name": "super_admin",
        "display_name": "超级管理员",
        "description": "拥有所有权限",
        "permissions": ["user:create", "user:read", "..."],
        "status": 1,
        "created_at": "2026-03-20T10:00:00"
      }
    ]
  }
}
```

---

### 2. 获取所有角色（简化）

```http
GET /api/roles/all
```

---

### 3. 获取角色详情

```http
GET /api/roles/<角色 ID>
```

---

### 4. 创建角色

```http
POST /api/roles
Content-Type: application/json
```

**请求参数**
```json
{
  "name": "hr",
  "display_name": "HR 专员",
  "description": "负责简历管理",
  "permissions": ["resume:upload", "resume:read", "resume:analyze", "position:read"]
}
```

---

### 5. 更新角色

```http
PUT /api/roles/<角色 ID>
Content-Type: application/json
```

---

### 6. 删除角色

```http
DELETE /api/roles/<角色 ID>
```

---

### 7. 获取角色下的用户

```http
GET /api/roles/<角色 ID>/users
```

---

## 权限管理模块 `/api/permissions`

### 1. 获取所有权限

```http
GET /api/permissions
```

**响应示例**
```json
{
  "code": 0,
  "message": "操作成功",
  "data": [
    {
      "id": 1,
      "name": "user:create",
      "display_name": "创建用户",
      "module": "user",
      "action": "create",
      "icon": null,
      "sort": 1,
      "status": 1
    }
  ]
}
```

---

### 2. 获取按模块分组的权限

```http
GET /api/permissions/grouped
```

**响应示例**
```json
{
  "code": 0,
  "message": "操作成功",
  "data": {
    "user": ["user:create", "user:read", "user:update", "user:delete"],
    "role": ["role:create", "role:read", "role:update", "role:delete"],
    "dept": ["dept:read", "dept:manage"],
    "resume": ["resume:upload", "resume:read", "resume:delete", "resume:analyze"],
    "position": ["position:create", "position:read", "position:update", "position:delete"]
  }
}
```

---

## 简历管理模块 `/api/resumes`

### 1. 获取简历列表

```http
GET /api/resumes?position_id=1&status=1&keyword=张三&page=1&page_size=20&sort=created_at&order=desc
```

**响应示例**
```json
{
  "code": 0,
  "message": "操作成功",
  "data": {
    "total": 50,
    "page": 1,
    "page_size": 20,
    "total_pages": 3,
    "resumes": [
      {
        "id": 1,
        "file_name": "张三简历.pdf",
        "file_size": 102400,
        "file_type": "application/pdf",
        "position_id": 1,
        "position_name": "Java 开发工程师",
        "candidate_name": "张三",
        "candidate_phone": "13800138000",
        "candidate_email": "zhangsan@example.com",
        "upload_username": "hr001",
        "status": 1,
        "download_count": 5,
        "analysis_score": 85,
        "created_at": "2026-03-21T10:00:00"
      }
    ]
  }
}
```

---

### 2. 获取简历详情

```http
GET /api/resumes/<简历 ID>
```

---

### 3. 上传简历（单文件）

```http
POST /api/resumes/upload
Content-Type: multipart/form-data
```

**参数**
- `file`: 简历文件（必填）
- `position_id`: 岗位 ID
- `position_name`: 岗位名称
- `candidate_name`: 候选人姓名
- `candidate_phone`: 候选人电话
- `candidate_email`: 候选人邮箱

---

### 4. 批量上传简历

```http
POST /api/resumes/batch-upload
Content-Type: multipart/form-data
```

**参数**
- `files[]`: 文件列表
- `position_id`: 岗位 ID
- `position_name`: 岗位名称
- `items`: JSON 数组（可选），每个元素包含：
  - `file_index`: 文件索引
  - `position_id`: 岗位 ID
  - `position_name`: 岗位名称
  - `candidate_name`: 候选人姓名
  - `candidate_phone`: 电话
  - `candidate_email`: 邮箱

---

### 5. 下载简历

```http
GET /api/resumes/<简历 ID>/download
```

---

### 6. 生成临时访问链接

```http
GET /api/resumes/<简历 ID>/url?expired=3600
```

**响应示例**
```json
{
  "code": 0,
  "message": "操作成功",
  "data": {
    "id": 1,
    "file_name": "张三简历.pdf",
    "url": "https://bucket.cos.ap-guangzhou.myqcloud.com/...?q-sign-algorithm=...",
    "expired": 3600
  }
}
```

---

### 7. 更新简历

```http
PUT /api/resumes/<简历 ID>
Content-Type: application/json
```

**请求参数**
```json
{
  "position_id": 2,
  "candidate_name": "张三",
  "candidate_phone": "13800138000",
  "status": 1
}
```

---

### 8. 删除简历

```http
DELETE /api/resumes/<简历 ID>
```

---

### 9. 分析简历

```http
POST /api/resumes/<简历 ID>/analyze
```

**响应示例**
```json
{
  "code": 0,
  "message": "分析完成",
  "data": {
    "id": 1,
    "score": 85,
    "analysis": {
      "match_score": 85,
      "skills_match": ["Java", "Spring Boot", "MySQL"],
      "skills_missing": ["Redis", "Kubernetes"],
      "experience_years": 5,
      "highlights": ["有大厂工作经验", "项目经验丰富"],
      "concerns": ["跳槽频繁"],
      "recommendation": "A",
      "summary": "该候选人具备岗位所需的核心技能..."
    }
  }
}
```

---

## 岗位管理模块 `/api/positions`

### 1. 获取岗位列表

```http
GET /api/positions?status=1&department=技术部&keyword=Java&page=1&page_size=20
```

**响应示例**
```json
{
  "code": 0,
  "message": "操作成功",
  "data": {
    "total": 10,
    "page": 1,
    "page_size": 20,
    "total_pages": 1,
    "positions": [
      {
        "id": 1,
        "title": "Java 开发工程师",
        "description": "负责公司后端开发",
        "requirements": "3 年以上 Java 经验",
        "department": "技术部",
        "skills_required": ["Java", "Spring Boot", "MySQL"],
        "headcount": 5,
        "hire_by_date": "2026-04-01",
        "status": 1,
        "resume_count": 50,
        "avg_score": 75.5,
        "created_at": "2026-03-20T10:00:00"
      }
    ]
  }
}
```

---

### 2. 获取岗位详情

```http
GET /api/positions/<岗位 ID>
```

---

### 3. 创建岗位

```http
POST /api/positions
Content-Type: application/json
```

**请求参数**
```json
{
  "title": "Java 开发工程师",
  "description": "负责公司后端开发",
  "requirements": "3 年以上 Java 经验，熟悉 Spring Boot",
  "department": "技术部",
  "skills_required": ["Java", "Spring Boot", "MySQL"],
  "headcount": 5,
  "hire_by_date": "2026-04-01"
}
```

---

### 4. 更新岗位

```http
PUT /api/positions/<岗位 ID>
Content-Type: application/json
```

---

### 5. 删除岗位（设为已结束）

```http
DELETE /api/positions/<岗位 ID>
```

---

### 6. 获取岗位统计数据

```http
GET /api/positions/<岗位 ID>/statistics
```

**响应示例**
```json
{
  "code": 0,
  "message": "操作成功",
  "data": {
    "position": {
      "id": 1,
      "title": "Java 开发工程师"
    },
    "statistics": {
      "stats": {
        "total": 50,
        "analyzed_count": 45,
        "avg_score": 75.5,
        "max_score": 95,
        "min_score": 45
      },
      "distribution": {
        "s_count": 5,
        "a_count": 15,
        "b_count": 20,
        "c_count": 3,
        "d_count": 2
      }
    },
    "top_candidates": [
      {
        "id": 10,
        "candidate_name": "张三",
        "candidate_phone": "13800138000",
        "candidate_email": "zhangsan@example.com",
        "analysis_score": 95,
        "analysis_report": {...}
      }
    ]
  }
}
```

---

### 7. 批量分析岗位简历

```http
POST /api/positions/<岗位 ID>/analyze
Content-Type: application/json
```

**请求参数**
```json
{
  "unanalyzed_only": true
}
```

**响应示例**
```json
{
  "code": 0,
  "message": "分析完成，成功 45 份，失败 0 份",
  "data": {
    "total": 45,
    "success": 45,
    "failed": 0,
    "results": [
      {
        "id": 1,
        "candidate": "张三",
        "score": 85
      }
    ],
    "failed_details": []
  }
}
```

---

## 错误码说明

| Code | HTTP 状态码 | 说明 |
|------|------------|------|
| 0 | 200 | 操作成功 |
| 1 | 400 | 请求参数错误 |
| - | 401 | 未登录 |
| - | 403 | 无权限 |
| - | 404 | 资源不存在 |
| - | 500 | 服务器内部错误 |

---

## 默认账号

| 用户名 | 密码 | 角色 |
|-------|------|------|
| admin | admin123 | 超级管理员 |

---

**最后更新**: 2026-03-23
