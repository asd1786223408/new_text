# 🚀 中转平台

页面导航管理中心 - 统一管理所有网页项目

## 📁 目录结构

```
~/new_text/portal/
├── index.html              # 中转平台主页（导航页面）
├── README.md               # 本文档
├── config/                 # 配置文件目录
│   ├── pages.json          # 页面配置（核心）
│   ├── page-template.json  # 页面配置模板
│   └── page-template.html  # HTML 页面模板
└── pages/                  # 所有页面目录
    └── helloworld/         # 示例页面
        └── index.html
```

## 🌐 访问地址

- **服务器 IP**: http://139.196.15.208:15508
- **中转平台**: http://139.196.15.208:15508/portal/index.html

## 📝 如何添加新页面

### 步骤 1: 创建页面目录

```bash
mkdir -p ~/new_text/portal/pages/你的页面名
```

### 步骤 2: 创建页面文件

使用模板或从头创建：

```bash
# 复制模板
cp ~/new_text/portal/config/page-template.html ~/new_text/portal/pages/你的页面名/index.html

# 编辑页面
nano ~/new_text/portal/pages/你的页面名/index.html
```

### 步骤 3: 更新配置

编辑 `~/new_text/portal/config/pages.json`，在 `pages` 数组中添加：

```json
{
  "id": "你的页面名",
  "name": "页面显示名称",
  "path": "/pages/你的页面名/index.html",
  "description": "页面描述",
  "icon": "🎨",
  "status": "active",
  "created": "2026-03-19"
}
```

### 步骤 4: 刷新页面

访问中转平台主页，新页面卡片将自动显示。

## 🔧 配置说明

### pages.json 字段

| 字段 | 说明 | 必填 |
|------|------|------|
| id | 页面唯一标识 | ✅ |
| name | 显示名称 | ✅ |
| path | 页面路径（相对于服务器根目录） | ✅ |
| description | 页面描述 | ❌ |
| icon | Emoji 图标 | ❌ |
| status | 状态：active/development | ❌ |
| created | 创建日期 | ❌ |

## 🎨 可用图标

👋 📄 🎨 🛒 📊 📝 🎮 🎵 📷 🗺️ 📅 📬 🔧 ⚙️ 📚 🎯

## 📦 快速命令

```bash
# 查看目录结构
tree ~/new_text/portal -L 3

# 编辑配置
nano ~/new_text/portal/config/pages.json

# 重启 Web 服务（如需要）
sudo systemctl restart nginx
```

---

**版本**: 1.0.0  
**最后更新**: 2026-03-19
