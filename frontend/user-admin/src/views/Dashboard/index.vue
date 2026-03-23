<template>
  <div class="dashboard-container">
    <!-- 欢迎卡片 -->
    <el-card class="welcome-card">
      <div class="welcome-content">
        <div class="welcome-text">
          <h2 class="welcome-title">欢迎回来，{{ userInfo?.nickname || userInfo?.username }}</h2>
          <p class="welcome-subtitle">今天又是充满希望的一天，加油！</p>
        </div>
        <div class="welcome-icon">
          <el-icon :size="48" color="#2563eb"><House /></el-icon>
        </div>
      </div>
    </el-card>

    <!-- 统计卡片 -->
    <el-row :gutter="16" class="stats-row">
      <el-col :span="6">
        <div class="stat-card stat-blue">
          <div class="stat-icon">
            <el-icon :size="24"><User /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.userCount }}</div>
            <div class="stat-label">用户总数</div>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card stat-purple">
          <div class="stat-icon">
            <el-icon :size="24"><Setting /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.roleCount }}</div>
            <div class="stat-label">角色总数</div>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card stat-orange">
          <div class="stat-icon">
            <el-icon :size="24"><OfficeBuilding /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.deptCount }}</div>
            <div class="stat-label">部门总数</div>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card stat-green">
          <div class="stat-icon">
            <el-icon :size="24"><VideoPlay /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.onlineCount }}</div>
            <div class="stat-label">在线用户</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 快捷入口 -->
    <el-card class="quick-card">
      <template #header>
        <div class="card-header-content">
          <el-icon style="margin-right: 8px; color: var(--primary-color);"><Grid /></el-icon>
          <span>快捷入口</span>
        </div>
      </template>
      <div class="quick-links">
        <div class="quick-item" @click="$router.push('/users')">
          <div class="quick-icon quick-blue">
            <el-icon :size="24"><User /></el-icon>
          </div>
          <span class="quick-label">用户管理</span>
        </div>
        <div class="quick-item" @click="$router.push('/roles')">
          <div class="quick-icon quick-purple">
            <el-icon :size="24"><Setting /></el-icon>
          </div>
          <span class="quick-label">角色管理</span>
        </div>
        <div class="quick-item" @click="$router.push('/departments')">
          <div class="quick-icon quick-orange">
            <el-icon :size="24"><OfficeBuilding /></el-icon>
          </div>
          <span class="quick-label">部门管理</span>
        </div>
        <div class="quick-item" @click="$router.push('/permissions')">
          <div class="quick-icon quick-green">
            <el-icon :size="24"><Lock /></el-icon>
          </div>
          <span class="quick-label">权限管理</span>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useUserStore } from '@/stores/user'
import { User, Setting, OfficeBuilding, House, Grid, Lock, VideoPlay } from '@element-plus/icons-vue'

const userStore = useUserStore()

const userInfo = computed(() => userStore.userInfo)

const stats = ref({
  userCount: 0,
  roleCount: 0,
  deptCount: 0,
  onlineCount: 0
})
</script>

<style scoped>
.dashboard-container {
  width: 100%;
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

/* 欢迎卡片 */
.welcome-card {
  margin-bottom: 20px;
  border-radius: 16px;
  overflow: hidden;
  background: linear-gradient(135deg, #2563eb 0%, #3b82f6 100%);
  border: none;
}

.welcome-card :deep(.el-card__body) {
  padding: 0;
}

.welcome-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px 32px;
  color: #fff;
}

.welcome-text {
  flex: 1;
}

.welcome-title {
  font-size: 22px;
  font-weight: 600;
  margin-bottom: 8px;
  letter-spacing: -0.3px;
}

.welcome-subtitle {
  font-size: 14px;
  opacity: 0.9;
}

.welcome-icon {
  width: 80px;
  height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.15);
  border-radius: 20px;
  backdrop-filter: blur(10px);
}

/* 统计卡片 */
.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  display: flex;
  align-items: center;
  padding: 20px;
  border-radius: 16px;
  background: var(--bg-white);
  border: 1px solid var(--border-light);
  box-shadow: var(--shadow-sm);
  transition: all 0.3s ease;
  cursor: pointer;
}

.stat-card:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}

.stat-icon {
  width: 56px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 14px;
  margin-right: 16px;
  flex-shrink: 0;
}

.stat-blue .stat-icon {
  background: linear-gradient(135deg, #eff6ff, #dbeafe);
  color: #2563eb;
}

.stat-purple .stat-icon {
  background: linear-gradient(135deg, #faf5ff, #f3e8ff);
  color: #9333ea;
}

.stat-orange .stat-icon {
  background: linear-gradient(135deg, #fffbeb, #fde68a);
  color: #d97706;
}

.stat-green .stat-icon {
  background: linear-gradient(135deg, #ecfdf5, #a7f3d0);
  color: #059669;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1;
  margin-bottom: 6px;
}

.stat-label {
  font-size: 13px;
  color: var(--text-secondary);
  font-weight: 400;
}

/* 快捷入口 */
.quick-card {
  border-radius: 16px;
  overflow: hidden;
}

.quick-card :deep(.el-card__header) {
  padding: 18px 24px;
  border-bottom: 1px solid var(--border-light);
}

.card-header-content {
  display: flex;
  align-items: center;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.quick-links {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  padding: 8px;
}

.quick-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 24px 16px;
  border-radius: 14px;
  background: var(--bg-hover);
  cursor: pointer;
  transition: all 0.2s ease;
  border: 1px solid transparent;
}

.quick-item:hover {
  background: var(--bg-white);
  border-color: var(--border-light);
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}

.quick-icon {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  margin-bottom: 12px;
}

.quick-blue {
  background: linear-gradient(135deg, #eff6ff, #dbeafe);
  color: #2563eb;
}

.quick-purple {
  background: linear-gradient(135deg, #faf5ff, #f3e8ff);
  color: #9333ea;
}

.quick-orange {
  background: linear-gradient(135deg, #fffbeb, #fde68a);
  color: #d97706;
}

.quick-green {
  background: linear-gradient(135deg, #ecfdf5, #a7f3d0);
  color: #059669;
}

.quick-label {
  font-size: 14px;
  color: var(--text-regular);
  font-weight: 500;
}

@media (max-width: 1200px) {
  .quick-links {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .stats-row {
    --el-row-margin: -8px;
  }

  .stat-card {
    margin-bottom: 12px;
  }

  .welcome-content {
    flex-direction: column;
    text-align: center;
    gap: 20px;
  }
}
</style>
