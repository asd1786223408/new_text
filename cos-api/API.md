# COS API 接口文档

腾讯云 COS 对象存储接口服务。

## 服务地址

- 本地：`http://localhost:5000`
- 服务器：`http://172.24.5.125:5000`

## 配置

配置位于根目录的 `env.json`，包含 COS 的 SecretId、SecretKey、Bucket、Region 等信息。

---

## 接口列表

### 1. 健康检查

```http
GET /health
```

**响应示例**
```json
{"status": "ok", "timestamp": "2026-03-20T10:49:30"}
```

---

### 2. 上传文件

```http
POST /upload
Content-Type: multipart/form-data

参数:
- file: 文件（必填）
- key: 存储路径（可选，默认为文件名）
```

**请求示例**
```bash
curl -X POST -F "file=@local.txt" -F "key=remote/path.txt" http://localhost:5000/upload
```

**响应示例**
```json
{"success": true, "key": "remote/path.txt", "etag": "\"xxx\""}
```

---

### 3. 下载文件

```http
GET /download/<key>
```

**请求示例**
```bash
curl http://localhost:5000/download/test/hello.txt -o out.txt
```

---

### 4. 删除文件

```http
DELETE /delete/<key>
```

**请求示例**
```bash
curl -X DELETE http://localhost:5000/delete/test/hello.txt
```

**响应示例**
```json
{"success": true, "key": "test/hello.txt"}
```

---

### 5. 列出文件

```http
GET /list?prefix=<前缀>&limit=<数量>
```

**请求示例**
```bash
curl "http://localhost:5000/list?prefix=test/&limit=50"
```

**响应示例**
```json
{
  "count": 1,
  "files": [
    {"key": "test/hello.txt", "size": 49, "last_modified": "2026-03-20T02:50:39.000Z"}
  ]
}
```

---

### 6. 生成临时链接

```http
GET /url/<key>?expired=<秒数>
```

**请求示例**
```bash
curl "http://localhost:5000/url/test/hello.txt?expired=3600"
```

**响应示例**
```json
{
  "url": "https://bucket.cos.region.myqcloud.com/...?q-sign-algorithm=sha1&...",
  "expired": 3600
}
```

---

## 文件结构

```
cos-api/
├── app.py           # 主程序
├── requirements.txt # Python 依赖
├── README.md        # 快速开始
└── API.md           # 接口文档（本文件）
```

---

## 启动服务

```bash
cd cos-api
python app.py
```

后台运行：
```bash
nohup python app.py > cos-api.log 2>&1 &
```
