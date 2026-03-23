<template>
  <div class="logs-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>操作日志</span>
          <el-button @click="fetchData">刷新</el-button>
        </div>
      </template>

      <!-- 搜索栏 -->
      <el-form :inline="true" :model="searchForm">
        <el-form-item label="用户">
          <el-input v-model="searchForm.username" placeholder="用户名" clearable />
        </el-form-item>
        <el-form-item label="模块">
          <el-select v-model="searchForm.module" placeholder="全部模块" clearable>
            <el-option label="auth" value="auth" />
            <el-option label="user" value="user" />
            <el-option label="role" value="role" />
            <el-option label="dept" value="dept" />
            <el-option label="permission" value="permissions" />
            <el-option label="log" value="logs" />
          </el-select>
        </el-form-item>
        <el-form-item label="操作">
          <el-input v-model="searchForm.action" placeholder="操作类型" clearable />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 表格 -->
      <el-table :data="tableData" v-loading="loading" border stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="username" label="用户" width="120" />
        <el-table-column prop="nickname" label="昵称" width="100" />
        <el-table-column prop="module" label="模块" width="100" />
        <el-table-column prop="action" label="操作" width="150" />
        <el-table-column prop="method" label="方法" width="80">
          <template #default="{ row }">
            <el-tag :type="row.method === 'GET' ? 'success' : 'primary'" size="small">{{ row.method }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="url" label="URL" width="200" />
        <el-table-column prop="ip" label="IP" width="140" />
        <el-table-column prop="status" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.status === 200 ? 'success' : 'danger'" size="small">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="操作时间" width="180" />
      </el-table>

      <!-- 分页 -->
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.limit"
        :total="pagination.total"
        :page-sizes="[20, 50, 100]"
        layout="total, sizes, prev, pager, next"
        @current-change="fetchData"
        @size-change="fetchData"
        style="margin-top: 20px; justify-content: flex-end"
      />
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getLogs } from '@/api/logs'

const loading = ref(false)
const searchForm = reactive({
  username: '',
  module: '',
  action: ''
})

const pagination = reactive({
  page: 1,
  limit: 20,
  total: 0
})

const tableData = ref([])

const fetchData = async () => {
  loading.value = true
  try {
    const res = await getLogs({
      page: pagination.page,
      limit: pagination.limit,
      ...searchForm
    })
    tableData.value = res.data?.list || []
    pagination.total = res.data?.total || 0
  } catch (error) {
    console.error(error)
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.page = 1
  fetchData()
}

const resetSearch = () => {
  searchForm.username = ''
  searchForm.module = ''
  searchForm.action = ''
  handleSearch()
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.logs-container {
  width: 100%;
  padding: 20px;
}

.logs-container :deep(.el-card) {
  border-radius: 16px;
  overflow: hidden;
}

.logs-container :deep(.el-card__header) {
  padding: 18px 24px;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  border-bottom: 1px solid var(--border-light);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header span {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

/* 搜索表单 */
.logs-container :deep(.el-form) {
  padding: 16px 24px;
  background: var(--bg-white);
  border-bottom: 1px solid var(--border-light);
}

.logs-container :deep(.el-form-item__label) {
  font-weight: 500;
  color: var(--text-primary);
}

.logs-container :deep(.el-input__wrapper) {
  width: 180px;
  border-radius: 10px;
}

.logs-container :deep(.el-select__wrapper) {
  border-radius: 10px;
}

/* 表格样式 */
.logs-container :deep(.el-table) {
  --el-table-header-bg-color: #f8fafc;
}

.logs-container :deep(.el-table th) {
  font-weight: 600;
  color: var(--text-primary);
  font-size: 14px;
  background-color: #f8fafc !important;
}

.logs-container :deep(.el-table td) {
  padding: 14px 0;
}

.logs-container :deep(.el-table .cell) {
  padding: 0 24px;
  font-size: 14px;
}

/* 分页样式 */
.logs-container :deep(.el-pagination) {
  padding: 16px 24px;
  justify-content: flex-end;
}
</style>
