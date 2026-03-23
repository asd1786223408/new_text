# 用户管理平台 - API 接口文档

## 服务地址

- 本地：`http://localhost:8000`
- 服务器：`http://139.196.15.208:8000`

## 认证方式

使用 Flask Session，登录后自动设置 session，后续请求自动携带。

---

## 接口列表

### 认证模块 `/api/auth`

#### 1. 用户登录
```http
POST /api/auth/login
Content-Type: application/json

{
  "account": "admin",      // 用户名/邮箱/手机号
  "password": "admin123"
}
```

**响应**
```json
{
  "code": 0,
  "message": "登录成功",
  "data": {
    "user_id": 1,
    "username": "admin",
    "nickname": "超级管理员",
    "permissions": ["user:create", "user:read", "..."]
  }
}
```

---

#### 2. 用户登出
```http
POST /api/auth/logout
```

---

#### 3. 用户注册
```http
POST /api/auth/register
Content-Type: application/json

{
  "username": "test",
  "password": "test123",
  "email": "test@example.com",  // 可选
  "phone": "13800138000"        // 可选，至少填一项
}
```

---

#### 4. 获取当前用户信息
```http
GET /api/auth/current
```

---

### 用户管理 `/api/users`

#### 1. 用户列表
```http
GET /api/users?page=1&limit=20&keyword=&department_id=&status=
```

**响应**
```json
{
  "code": 0,
  "data": {
    "list": [...],
    "total": 10,
    "page": 1,
    "limit": 20
  }
}
```

---

#### 2. 用户详情
```http
GET /api/users/<user_id>
```

---

#### 3. 创建用户
```http
POST /api/users
Content-Type: application/json

{
  "username": "test",
  "password": "test123",
  "email": "test@example.com",
  "nickname": "测试用户",
  "department_id": 1,
  "position": "工程师",
  "role_ids": [1, 2]  // 角色 ID 列表
}
```

**权限**: `user:create`

---

#### 4. 更新用户
```http
PUT /api/users/<user_id>
Content-Type: application/json

{
  "email": "new@example.com",
  "nickname": "新昵称",
  "position": "新职位"
}
```

**权限**: `user:update`

---

#### 5. 删除用户
```http
DELETE /api/users/<user_id>
```

**权限**: `user:delete`

---

#### 6. 修改密码
```http
PUT /api/users/<user_id>/password
Content-Type: application/json

{
  "old_password": "原密码",    // 修改自己密码时需要
  "new_password": "新密码"
}
```

---

#### 7. 更新用户角色
```http
PUT /api/users/<user_id>/roles
Content-Type: application/json

{
  "role_ids": [1, 2, 3]
}
```

**权限**: `user:update`

---

### 角色管理 `/api/roles`

#### 1. 角色列表
```http
GET /api/roles
```

---

#### 2. 角色详情
```http
GET /api/roles/<role_id>
```

---

#### 3. 创建角色
```http
POST /api/roles
Content-Type: application/json

{
  "name": "manager",
  "display_name": "经理",
  "description": "部门经理角色",
  "permissions": ["user:read", "user:update"]
}
```

**权限**: `role:create`

---

#### 4. 更新角色
```http
PUT /api/roles/<role_id>
Content-Type: application/json

{
  "display_name": "新名称",
  "description": "新描述"
}
```

**权限**: `role:update`

---

#### 5. 删除角色
```http
DELETE /api/roles/<role_id>
```

**权限**: `role:delete`

---

#### 6. 更新角色权限
```http
PUT /api/roles/<role_id>/permissions
Content-Type: application/json

{
  "permission_ids": [1, 2, 3, 4]
}
```

**权限**: `role:update`

---

### 部门管理 `/api/departments`

#### 1. 部门列表
```http
GET /api/departments
```

---

#### 2. 部门树形结构
```http
GET /api/departments/tree
```

---

#### 3. 部门详情
```http
GET /api/departments/<dept_id>
```

---

#### 4. 创建部门
```http
POST /api/departments
Content-Type: application/json

{
  "name": "研发部",
  "parent_id": 0,    // 0 为顶级部门
  "sort": 1,
  "leader_id": 1     // 负责人 ID
}
```

**权限**: `dept:manage`

---

#### 5. 更新部门
```http
PUT /api/departments/<dept_id>
Content-Type: application/json

{
  "name": "新名称",
  "parent_id": 1,
  "sort": 2
}
```

**权限**: `dept:manage`

---

#### 6. 删除部门
```http
DELETE /api/departments/<dept_id>
```

**权限**: `dept:manage`

---

### 权限管理 `/api/permissions`

#### 1. 权限列表
```http
GET /api/permissions?module=user
```

---

#### 2. 模块列表
```http
GET /api/permissions/modules
```

---

## 响应格式

### 成功响应
```json
{
  "code": 0,
  "message": "操作成功",
  "data": {...}
}
```

### 错误响应
```json
{
  "code": 400,
  "message": "错误信息",
  "data": null
}
```

---

## 权限标识

| 权限标识 | 说明 |
|---------|------|
| user:create | 创建用户 |
| user:read | 查看用户 |
| user:update | 编辑用户 |
| user:delete | 删除用户 |
| role:create | 创建角色 |
| role:read | 查看角色 |
| role:update | 编辑角色 |
| role:delete | 删除角色 |
| dept:read | 查看部门 |
| dept:manage | 管理部门 |
| stat:view | 查看统计 |
| system:config | 系统配置 |

---

## 默认账号

| 用户名 | 密码 | 角色 |
|-------|------|------|
| admin | admin123 | 超级管理员 |

---

**最后更新**: 2026-03-20
