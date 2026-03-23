<template>
  <div class="layout-container">
    <el-container>
      <!-- 侧边栏 -->
      <el-aside :width="sidebarCollapsed ? '64px' : '200px'" class="sidebar">
        <div class="logo">
          <span v-if="!sidebarCollapsed">简历管理系统</span>
          <span v-else>R</span>
        </div>
        <el-menu
          :collapse="sidebarCollapsed"
          :default-active="activeMenu"
          background-color="#5b5fc7"
          text-color="#e0e0e0"
          active-text-color="#ffffff"
          router
        >
          <el-menu-item index="/">
            <el-icon><Document /></el-icon>
            <span>简历列表</span>
          </el-menu-item>
          <el-menu-item index="/upload">
            <el-icon><Upload /></el-icon>
            <span>批量上传</span>
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
          </div>
          <div class="header-right">
            <span class="app-title">Resume Admin</span>
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
import { useRoute } from 'vue-router'
import { ref } from 'vue'
import {
  Document, Upload, Fold, Expand
} from '@element-plus/icons-vue'

const route = useRoute()
const sidebarCollapsed = ref(false)

const activeMenu = computed(() => route.path)

const toggleSidebar = () => {
  sidebarCollapsed.value = !sidebarCollapsed.value
}
</script>

<style scoped>
.layout-container {
  height: 100vh;
}

.el-container {
  height: 100%;
}

.sidebar {
  background-color: #5b5fc7;
  transition: width 0.3s;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 18px;
  font-weight: bold;
  background-color: rgba(0, 0, 0, 0.1);
}

.el-menu {
  border-right: none;
  background-color: #5b5fc7;
}

.el-menu-item {
  color: #e0e0e0;
}

.el-menu-item:hover {
  background-color: rgba(255, 255, 255, 0.1) !important;
}

.el-menu-item.is-active {
  background-color: rgba(255, 255, 255, 0.2) !important;
  color: #fff;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #fff;
  border-bottom: 1px solid #e5e7eb;
  padding: 0 20px;
}

.header-left {
  display: flex;
  align-items: center;
}

.collapse-icon {
  font-size: 20px;
  cursor: pointer;
  transition: all 0.3s;
}

.collapse-icon:hover {
  transform: scale(1.1);
}

.header-right {
  display: flex;
  align-items: center;
}

.app-title {
  font-size: 16px;
  font-weight: 600;
  color: #5b5fc7;
}

.main-content {
  background-color: #f9fafb;
  padding: 0;
  overflow: auto;
}
</style>
