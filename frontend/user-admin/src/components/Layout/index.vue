<template>
  <div class="layout-container">
    <el-container>
      <!-- 侧边栏 -->
      <el-aside :width="sidebarCollapsed ? '64px' : '220px'" class="sidebar">
        <div class="logo">
          <div class="logo-icon">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <rect width="24" height="24" rx="6" fill="url(#logo-gradient)"/>
              <path d="M7 7H12V17H7V7Z" fill="white" fill-opacity="0.9"/>
              <path d="M12 7H17V12H12V7Z" fill="white" fill-opacity="0.7"/>
              <defs>
                <linearGradient id="logo-gradient" x1="0" y1="0" x2="24" y2="24">
                  <stop offset="0%" stop-color="#2563eb"/>
                  <stop offset="100%" stop-color="#3b82f6"/>
                </linearGradient>
              </defs>
            </svg>
          </div>
          <span v-if="!sidebarCollapsed" class="logo-text">用户管理平台</span>
        </div>
        <el-menu
          :collapse="sidebarCollapsed"
          :default-active="activeMenu"
          background-color="#f8fafc"
          text-color="#475569"
          active-text-color="#2563eb"
          router
          class="sidebar-menu"
        >
          <el-menu-item index="/apps">
            <el-icon class="menu-icon"><Grid /></el-icon>
            <span>应用中心</span>
          </el-menu-item>
          <el-menu-item index="/dashboard">
            <el-icon class="menu-icon"><House /></el-icon>
            <span>首页</span>
          </el-menu-item>
          <el-menu-item index="/users" v-if="hasPermission('user:read')">
            <el-icon class="menu-icon"><User /></el-icon>
            <span>用户管理</span>
          </el-menu-item>
          <el-menu-item index="/roles" v-if="hasPermission('role:read')">
            <el-icon class="menu-icon"><Setting /></el-icon>
            <span>角色管理</span>
          </el-menu-item>
          <el-menu-item index="/departments" v-if="hasPermission('dept:read')">
            <el-icon class="menu-icon"><OfficeBuilding /></el-icon>
            <span>部门管理</span>
          </el-menu-item>
          <el-menu-item index="/permissions" v-if="hasPermission('permissions:read')">
            <el-icon class="menu-icon"><Lock /></el-icon>
            <span>权限管理</span>
          </el-menu-item>
          <el-menu-item index="/logs" v-if="hasPermission('system:logs')">
            <el-icon class="menu-icon"><Document /></el-icon>
            <span>操作日志</span>
          </el-menu-item>
        </el-menu>
      </el-aside>

      <el-container>
        <!-- 顶部导航 -->
        <el-header class="header">
          <div class="header-left">
            <el-icon class="collapse-icon" @click="toggleSidebar">
              <Fold v-if="!sidebarCollapsed" />
              <Expand v-else />
            </el-icon>
            <div class="breadcrumb-divider"></div>
          </div>
          <div class="header-right">
            <el-dropdown @command="handleCommand" placement="bottom-end">
              <div class="user-info">
                <div class="user-avatar">
                  <el-avatar :size="36" :icon="UserFilled" style="background: linear-gradient(135deg, #2563eb, #3b82f6);" />
                </div>
                <div class="user-details">
                  <span class="username">{{ userInfo?.nickname || userInfo?.username }}</span>
                </div>
                <el-icon class="arrow-icon"><ArrowDown /></el-icon>
              </div>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="profile">
                    <el-icon style="margin-right: 8px;"><User /></el-icon>
                    个人中心
                  </el-dropdown-item>
                  <el-dropdown-item divided command="logout">
                    <el-icon style="margin-right: 8px; color: #ef4444;"><SwitchButton /></el-icon>
                    退出登录
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </el-header>

        <!-- 主内容区 -->
        <el-main class="main-content">
          <router-view />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useAppStore } from '@/stores/app'
import {
  User, Setting, OfficeBuilding, Fold, Expand, UserFilled, Lock, Document, Grid, House, ArrowDown, SwitchButton
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const appStore = useAppStore()

const activeMenu = computed(() => route.path)
const sidebarCollapsed = computed(() => appStore.sidebarCollapsed)
const userInfo = computed(() => userStore.userInfo)

const toggleSidebar = () => {
  appStore.toggleSidebar()
}

const hasPermission = (permission) => {
  return userStore.hasPermission(permission)
}

const handleCommand = async (command) => {
  if (command === 'logout') {
    await userStore.logoutAction()
    localStorage.removeItem('token')
    router.push('/login')
  } else if (command === 'profile') {
    router.push('/profile')
  }
}
</script>

<style scoped>
.layout-container {
  height: 100vh;
  background-color: var(--bg-body);
}

.el-container {
  height: 100%;
}

.sidebar {
  background-color: #f8fafc;
  border-right: 1px solid var(--border-light);
  transition: width 0.3s ease;
  overflow: hidden;
}

.logo {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 0 20px;
  background-color: #f8fafc;
  border-bottom: 1px solid var(--border-light);
}

.logo-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.logo-text {
  color: var(--text-primary);
  font-size: 16px;
  font-weight: 600;
  white-space: nowrap;
  transition: opacity 0.3s;
}

.sidebar-menu {
  padding: 12px 8px;
  background-color: transparent;
}

.sidebar-menu :deep(.el-menu-item) {
  margin: 4px 8px;
  height: 44px;
  line-height: 44px;
  border-radius: 10px;
  font-size: 14px;
  color: var(--text-regular);
}

.sidebar-menu :deep(.el-menu-item:hover) {
  background-color: rgba(37, 99, 235, 0.08);
  color: var(--text-primary);
}

.sidebar-menu :deep(.el-menu-item.is-active) {
  background-color: var(--primary-color) !important;
  color: #fff !important;
  box-shadow: 0 2px 8px rgba(37, 99, 235, 0.25);
}

.sidebar-menu :deep(.el-menu-item .el-icon) {
  width: 18px;
  height: 18px;
  margin-right: 12px;
  color: inherit;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: var(--bg-white);
  border-bottom: 1px solid var(--border-light);
  padding: 0 20px;
  height: 64px;
  box-shadow: var(--shadow-sm);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.collapse-icon {
  font-size: 20px;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 8px;
  border-radius: 8px;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.collapse-icon:hover {
  background-color: var(--bg-hover);
  color: var(--text-primary);
  transform: scale(1.05);
}

.breadcrumb-divider {
  width: 1px;
  height: 20px;
  background-color: var(--border-light);
}

.header-right {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 6px 12px 6px 6px;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.user-info:hover {
  background-color: var(--bg-hover);
}

.user-avatar {
  flex-shrink: 0;
}

.user-details {
  display: flex;
  flex-direction: column;
}

.username {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.arrow-icon {
  font-size: 14px;
  color: var(--text-secondary);
}

.main-content {
  background-color: var(--bg-body);
  padding: 0;
  overflow: auto;
}
</style>
