#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
COS API 测试客户端
使用方法：修改 SERVER_URL 为你的服务器 IP
"""

import requests

# 修改为你的服务器 IP
SERVER_URL = "http://172.24.5.125:5000"

def test_health():
    """健康检查"""
    r = requests.get(f"{SERVER_URL}/health")
    print(f"健康检查：{r.json()}")

def test_upload():
    """上传文件"""
    files = {'file': ('test.txt', b'Hello COS!')}
    data = {'key': 'test/test.txt'}
    r = requests.post(f"{SERVER_URL}/upload", files=files, data=data)
    print(f"上传文件：{r.json()}")

def test_list():
    """列出文件"""
    r = requests.get(f"{SERVER_URL}/list")
    print(f"文件列表：{r.json()}")

def test_download():
    """下载文件"""
    r = requests.get(f"{SERVER_URL}/download/test/test.txt")
    print(f"下载文件：{r.text}")

def test_url():
    """生成临时链接"""
    r = requests.get(f"{SERVER_URL}/url/test/test.txt?expired=3600")
    print(f"临时链接：{r.json()}")

def test_delete():
    """删除文件"""
    r = requests.delete(f"{SERVER_URL}/delete/test/test.txt")
    print(f"删除文件：{r.json()}")

if __name__ == "__main__":
    print(f"测试服务器：{SERVER_URL}\n")
    test_health()
    test_upload()
    test_list()
    test_download()
    test_url()
    test_delete()
