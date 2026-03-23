<template>
  <div class="apps-container">
    <el-card class="header-card">
      <template #header>
        <div class="header-content">
          <h2>应用中心</h2>
          <p>选择要访问的应用</p>
        </div>
      </template>
    </el-card>

    <div class="apps-grid">
      <a
        v-for="app in apps"
        :key="app.id"
        :href="app.url"
        :target="app.target || '_self'"
        class="app-card"
      >
        <el-card shadow="hover" class="app-card-inner">
          <div class="app-icon">{{ app.icon }}</div>
          <h3 class="app-name">{{ app.name }}</h3>
          <p class="app-desc">{{ app.description }}</p>
          <div class="app-status" :class="`status-${app.status}`">
            {{ app.status === 'active' ? '已上线' : '开发中' }}
          </div>
        </el-card>
      </a>

      <!-- 添加应用卡片 -->
      <el-card shadow="hover" class="app-card add-app-card">
        <div class="add-app-content">
          <div class="add-icon">+</div>
          <span>添加应用</span>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const apps = ref([
  {
    id: 'user-admin',
    name: '用户管理',
    description: '用户、角色、部门管理平台',
    icon: '👥',
    url: '/users',
    target: '_self',
    status: 'active'
  },
  {
    id: 'cos-manager',
    name: '文件管理',
    description: 'COS 对象存储文件管理',
    icon: '📁',
    url: 'http://139.196.15.208:5000',
    target: '_blank',
    status: 'active'
  },
  {
    id: 'portal',
    name: '中转平台',
    description: '页面导航中心',
    icon: '🚀',
    url: 'http://139.196.15.208:15508/portal/index.html',
    target: '_blank',
    status: 'active'
  },
  {
    id: 'logs',
    name: '日志中心',
    description: '系统操作日志查看',
    icon: '📊',
    url: '/logs',
    target: '_self',
    status: 'active'
  },
  {
    id: 'profile',
    name: '个人中心',
    description: '个人资料设置',
    icon: '⚙️',
    url: '/profile',
    target: '_self',
    status: 'active'
  },
  {
    id: 'monitor',
    name: '系统监控',
    description: '服务器性能监控',
    icon: '📈',
    url: '#',
    target: '_self',
    status: 'dev'
  }
])
</script>

<style scoped>
.apps-container {
  width: 100%;
  padding: 20px;
}

.header-card {
  margin-bottom: 24px;
  border-radius: 16px;
  overflow: hidden;
  background: linear-gradient(135deg, #2563eb 0%, #3b82f6 100%);
  border: none;
}

.header-card :deep(.el-card__body) {
  padding: 0;
}

.header-content {
  padding: 24px 32px;
  color: #fff;
}

.header-content h2 {
  margin: 0 0 8px 0;
  color: #fff;
  font-size: 22px;
  font-weight: 600;
  letter-spacing: -0.3px;
}

.header-content p {
  margin: 0;
  color: rgba(255, 255, 255, 0.9);
  font-size: 14px;
}

.apps-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

.app-card {
  text-decoration: none;
  color: inherit;
  display: block;
}

.app-card-inner {
  height: 100%;
  transition: all 0.3s ease;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  border-radius: 16px !important;
  border: 1px solid var(--border-light) !important;
}

.app-card:hover .app-card-inner {
  transform: translateY(-6px);
  box-shadow: var(--shadow-lg);
  border-color: transparent;
}

.app-icon {
  width: 72px;
  height: 72px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 24px auto 16px;
  border-radius: 16px;
  font-size: 36px;
  background: linear-gradient(135deg, #eff6ff, #dbeafe);
}

.app-name {
  text-align: center;
  margin: 0 0 8px 0;
  color: var(--text-primary);
  font-size: 16px;
  font-weight: 600;
}

.app-desc {
  text-align: center;
  color: var(--text-secondary);
  font-size: 13px;
  margin: 0 24px 16px;
  line-height: 1.6;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.app-status {
  position: absolute;
  top: 12px;
  right: 12px;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
}

.status-active {
  background: linear-gradient(135deg, #ecfdf5, #a7f3d0);
  color: #059669;
}

.status-dev {
  background: linear-gradient(135deg, #fffbeb, #fde68a);
  color: #d97706;
}

.add-app-card {
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px dashed var(--border) !important;
  background: var(--bg-hover) !important;
  border-radius: 16px !important;
}

.add-app-card:hover {
  border-color: var(--primary-color) !important;
  background: var(--primary-lighter) !important;
}

.add-app-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  color: var(--text-secondary);
  transition: all 0.3s;
}

.add-app-card:hover .add-app-content {
  color: var(--primary-color);
}

.add-icon {
  width: 56px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 40px;
  font-weight: 300;
  margin-bottom: 12px;
  color: inherit;
}

.add-app-content span {
  font-size: 14px;
  font-weight: 500;
}

@media (max-width: 768px) {
  .apps-grid {
    grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
    gap: 16px;
  }
}
</style>
