# COS 对象存储接口

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
```

### 2. 配置 env.json

在根目录的 `env.json` 中配置腾讯云 COS 信息：

```json
{
  "cos": {
    "secret_id": "YOUR_SECRET_ID",
    "secret_key": "YOUR_SECRET_KEY",
    "bucket": "your-bucket-1234567890",
    "region": "ap-shanghai"
  }
}
```

### 3. 启动服务

```bash
python app.py
```

服务默认运行在 `http://0.0.0.0:5000`

---

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/health` | 健康检查 |
| POST | `/upload` | 上传文件 |
| GET | `/download/<key>` | 下载文件 |
| DELETE | `/delete/<key>` | 删除文件 |
| GET | `/list?prefix=&limit=` | 列出文件 |
| GET | `/url/<key>?expire=` | 生成临时访问链接 |

---

## 使用示例

### 上传文件

```bash
curl -X POST -F "file=@localfile.txt" -F "key=remote/path/file.txt" http://localhost:5000/upload
```

### 下载文件

```bash
curl http://localhost:5000/download/remote/path/file.txt -o file.txt
```

### 列出文件

```bash
curl "http://localhost:5000/list?prefix=images/&limit=50"
```

### 生成临时链接

```bash
curl "http://localhost:5000/url/remote/path/file.txt?expire=7200"
```

### 删除文件

```bash
curl -X DELETE http://localhost:5000/delete/remote/path/file.txt
```
