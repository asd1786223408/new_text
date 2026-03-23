# 用户管理平台 - 数据库设计文档

## 概述

企业级用户管理系统数据库，基于 RBAC（角色 - 权限）模型。

**数据库名**: `user_platform`
**字符集**: `utf8mb4`
**创建时间**: 2026-03-20

---

## 表结构

### 1. users - 用户表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | BIGINT | 主键 |
| username | VARCHAR(50) | 用户名（唯一） |
| password_hash | VARCHAR(255) | 密码哈希 |
| email | VARCHAR(100) | 邮箱（唯一） |
| phone | VARCHAR(20) | 手机号（唯一） |
| avatar | VARCHAR(255) | 头像 URL |
| nickname | VARCHAR(50) | 昵称 |
| gender | TINYINT | 性别：0 未知/1 男/2 女 |
| birthday | DATE | 生日 |
| department_id | BIGINT | 部门 ID |
| position | VARCHAR(50) | 职位 |
| status | TINYINT | 状态：0 禁用/1 正常/2 锁定 |
| permissions | JSON | 权限列表（冗余存储） |
| last_login_at | DATETIME | 最后登录时间 |
| last_login_ip | VARCHAR(50) | 最后登录 IP |
| password_changed_at | DATETIME | 密码最后修改时间 |
| login_failure_count | INT | 登录失败次数 |
| locked_until | DATETIME | 锁定截止时间 |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |
| deleted_at | DATETIME | 删除时间（软删除） |

**索引**:
- `uk_username` - 用户名唯一索引
- `uk_email` - 邮箱唯一索引
- `uk_phone` - 手机号唯一索引
- `idx_department` - 部门索引
- `idx_status` - 状态索引

---

### 2. departments - 部门表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | BIGINT | 主键 |
| name | VARCHAR(100) | 部门名称 |
| parent_id | BIGINT | 父部门 ID（0 为顶级） |
| level | INT | 层级 |
| sort | INT | 排序 |
| leader_id | BIGINT | 负责人 ID |
| status | TINYINT | 状态 |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

**索引**:
- `idx_parent` - 父部门索引
- `idx_level` - 层级索引

---

### 3. roles - 角色表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | BIGINT | 主键 |
| name | VARCHAR(50) | 角色标识（唯一） |
| display_name | VARCHAR(100) | 显示名称 |
| description | TEXT | 描述 |
| permissions | JSON | 权限列表（冗余） |
| status | TINYINT | 状态 |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

**索引**:
- `uk_name` - 角色名唯一索引

---

### 4. permissions - 权限表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | BIGINT | 主键 |
| name | VARCHAR(100) | 权限标识（唯一） |
| display_name | VARCHAR(100) | 显示名称 |
| module | VARCHAR(50) | 所属模块 |
| action | VARCHAR(50) | 操作类型 |
| icon | VARCHAR(50) | 图标 |
| sort | INT | 排序 |
| status | TINYINT | 状态 |
| created_at | DATETIME | 创建时间 |

**索引**:
- `uk_name` - 权限标识唯一索引
- `idx_module` - 模块索引

---

### 5. user_roles - 用户角色关联表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | BIGINT | 主键 |
| user_id | BIGINT | 用户 ID |
| role_id | BIGINT | 角色 ID |
| created_at | DATETIME | 创建时间 |

**索引**:
- `uk_user_role` - 用户 - 角色联合唯一索引
- `idx_role` - 角色索引

---

### 6. login_logs - 登录日志表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | BIGINT | 主键 |
| user_id | BIGINT | 用户 ID |
| login_type | VARCHAR(20) | 登录方式 |
| status | TINYINT | 状态：0 失败/1 成功 |
| ip | VARCHAR(50) | IP 地址 |
| user_agent | VARCHAR(255) | User-Agent |
| fail_reason | VARCHAR(255) | 失败原因 |
| created_at | DATETIME | 创建时间 |

**索引**:
- `idx_user` - 用户索引
- `idx_created` - 时间索引

---

## 初始数据

### 默认角色

| 角色标识 | 显示名称 | 权限 |
|---------|---------|------|
| super_admin | 超级管理员 | 所有权限 |
| admin | 管理员 | 大部分权限 |
| user | 普通用户 | 只读权限 |

### 默认权限（12 个）

| 模块 | 权限标识 | 显示名称 |
|------|---------|---------|
| user | user:create | 创建用户 |
| user | user:read | 查看用户 |
| user | user:update | 编辑用户 |
| user | user:delete | 删除用户 |
| role | role:create | 创建角色 |
| role | role:read | 查看角色 |
| role | role:update | 编辑角色 |
| role | role:delete | 删除角色 |
| dept | dept:read | 查看部门 |
| dept | dept:manage | 管理部门 |
| stat | stat:view | 查看统计 |
| system | system:config | 系统配置 |

### 默认部门

| 部门 | 层级 |
|------|------|
| 总公司 | 1 |
| 技术部 | 2 |
| 产品部 | 2 |
| 运营部 | 2 |

### 默认管理员

| 用户名 | 密码 | 角色 |
|-------|------|------|
| admin | admin123 | 超级管理员 |

---

## ER 图

```
users ──┬── user_roles ── roles
        │
        └── departments (department_id)

users ── login_logs (一对多)
```

---

## 权限字段说明

### users.permissions 格式

```json
["user:create", "user:read", "user:update", "role:read"]
```

### 权限标识格式

`模块：操作` 如：
- `user:create` - 创建用户
- `order:read` - 查看订单
- `stat:view` - 查看统计

---

## 连接信息

| 配置 | 值 |
|------|-----|
| 主机 | localhost |
| 端口 | 3306 |
| 数据库 | user_platform |
| 用户 | root |
| 密码 | Root@123456 |

---

**最后更新**: 2026-03-20
