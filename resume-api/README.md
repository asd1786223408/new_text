# 简历附件管理服务

基于 Flask + 腾讯云 COS 的简历附件上传下载服务。

## 功能特性

- ✅ 批量上传简历文件
- ✅ 每个文件关联岗位信息
- ✅ 支持候选人信息（姓名、电话、邮箱）
- ✅ 数据库记录 COS 路径
- ✅ 通过数据库 ID 下载文件
- ✅ 按岗位筛选简历列表
- ✅ 软删除功能
- ✅ 临时访问链接生成

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
```

### 2. 初始化数据库

```bash
mysql -u root -p user_platform < init.sql
```

### 3. 启动服务

```bash
python app.py
```

服务将在 `http://localhost:8001` 启动。

## 接口文档

详见 [API.md](./API.md)

## 配置说明

配置位于 `env.json`，需要包含：

```json
{
  "cos": {
    "secret_id": "xxx",
    "secret_key": "xxx",
    "bucket": "xxx",
    "region": "ap-guangzhou"
  },
  "mysql": {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "xxx",
    "database": "user_platform"
  }
}
```
