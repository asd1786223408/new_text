#!/bin/bash

# 中转平台 - Web 服务启动脚本
# 服务器：http://139.196.15.208:15508

PORT=15508
ROOT_DIR="$HOME/new_text/portal"

echo "🚀 启动中转平台 Web 服务..."
echo "📁 根目录：$ROOT_DIR"
echo "🌐 访问地址：http://139.196.15.208:$PORT"
echo ""

# 检查 Python 是否可用
if command -v python3 &> /dev/null; then
    echo "✅ 使用 Python3 HTTP 服务器"
    cd "$ROOT_DIR" && python3 -m http.server $PORT
elif command -v python &> /dev/null; then
    echo "✅ 使用 Python HTTP 服务器"
    cd "$ROOT_DIR" && python -m SimpleHTTPServer $PORT
else
    echo "❌ 未找到 Python，请安装 Python3"
    exit 1
fi
