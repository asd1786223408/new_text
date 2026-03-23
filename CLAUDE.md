# 项目配置

## NPM 包下载

下载 NPM 包时优先使用淘宝镜像：

```bash
npm install <package> --registry=https://registry.npmmirror.com/
```

如果淘宝镜像无法下载，再尝试其他源。

## PIP 包下载

下载 Python 包时优先使用阿里云镜像：

```bash
pip install <package> -i https://mirrors.aliyun.com/pypi/simple/
```

如果阿里云镜像无法下载，再尝试其他源。

## 配置文件

项目配置文件：`env.json`

存储 API Key 和各类服务配置，使用时从该文件读取配置信息。

常用配置项：
- `cos` - 对象存储配置（secret_id, secret_key, bucket, region）
- `openai` - OpenAI API Key
- `anthropic` - Anthropic API Key
- `server` - 服务器配置（host, port）

## 接口文档

每开发完一个接口，在对应目录创建 `API.md` 文档，并在 `PROJECTS.md` 中更新索引。

## 端口文档

新增服务端口时，在 `PORTS.md` 中注册，并更新 `CLAUDE.md` 中的端口索引。

### 当前端口

| 端口 | 服务 |
|------|------|
| 3306 | MySQL |
| 5000 | COS API |
| 5173 | Frontend (Vue 开发) |
| 6379 | Redis |
| 8000 | User Platform API |
| 8001 | Resume API |
| 15508 | Portal |

---

## 用户模块开发规范

### RBAC 模型要求

开发用户模块时，必须遵循 RBAC（角色 - 权限）模型：

1. **权限存储**: 用户权限冗余存储在 `users.permissions` 字段（JSON）
2. **权限同步**: 用户角色变化时，必须同步更新 `users.permissions`
3. **权限校验**: 每个需要权限的接口，必须检查 `users.permissions` 是否包含对应权限标识
4. **权限标识格式**: `模块：操作` 如 `user:create`, `user:read`

### 认证要求

- 使用 Flask Session
- Session 存储于 Redis（端口 6379）
- 支持邮箱/手机号作为账号登录
- 密码使用 bcrypt 加密

### 默认权限列表

| 权限标识 | 显示名称 |
|---------|---------|
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
