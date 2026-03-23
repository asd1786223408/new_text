# 用户管理后台

基于 Vue 3 + Vite + Element Plus 的用户管理系统前端。

## 技术栈

- Vue 3 - 前端框架
- Vite - 构建工具
- Element Plus - UI 组件库
- Vue Router - 路由管理
- Pinia - 状态管理
- Axios - HTTP 请求

## 目录结构

```
src/
├── api/              # API 封装
├── components/       # 公共组件
├── router/           # 路由配置
├── stores/           # 状态管理
├── utils/            # 工具函数
├── views/            # 页面视图
├── App.vue           # 根组件
└── main.js           # 入口文件
```

## 开发

```bash
# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 生产打包
npm run build
```

## 配置

后端 API 代理配置在 `vite.config.js` 中：

```javascript
proxy: {
  '/api': {
    target: 'http://139.196.15.208:8000',
    changeOrigin: true
  }
}
```

## 默认账号

- 用户名：`admin`
- 密码：`admin123`

---

**创建时间**: 2026-03-20
