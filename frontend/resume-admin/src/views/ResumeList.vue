<template>
  <div class="resume-list-container">
    <el-card class="list-card">
      <template #header>
        <div class="card-header">
          <span>简历列表</span>
          <div class="header-actions">
            <el-input
              v-model="searchForm.keyword"
              placeholder="搜索简历..."
              clearable
              style="width: 200px"
              @keyup.enter="handleSearch"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
            <el-button type="primary" @click="handleSearch">搜索</el-button>
            <el-button type="success" @click="goToUpload">
              <el-icon><Upload /></el-icon>
              上传简历
            </el-button>
          </div>
        </div>
      </template>

      <!-- 表格 -->
      <el-table :data="tableData" v-loading="loading" border stripe>
        <el-table-column prop="file_name" label="文件名" min-width="200" show-overflow-tooltip />
        <el-table-column prop="file_size" label="文件大小" width="100">
          <template #default="{ row }">
            {{ formatFileSize(row.file_size) }}
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="上传时间" width="180" />
        <el-table-column label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.status === 'processed' ? 'success' : row.status === 'failed' ? 'danger' : 'info'">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" fixed="right" width="280">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="handleView(row)">
              <el-icon><View /></el-icon>
              查看
            </el-button>
            <el-button link type="success" size="small" @click="handleDownload(row)">
              <el-icon><Download /></el-icon>
              下载
            </el-button>
            <el-button link type="warning" size="small" @click="handleCopyUrl(row)">
              <el-icon><Link /></el-icon>
              链接
            </el-button>
            <el-button link type="danger" size="small" @click="handleDelete(row)">
              <el-icon><Delete /></el-icon>
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.limit"
        :total="pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next"
        @current-change="fetchData"
        @size-change="fetchData"
        style="margin-top: 20px; justify-content: flex-end"
      />
    </el-card>

    <!-- 查看简历对话框 -->
    <el-dialog v-model="viewDialogVisible" title="查看简历" width="80%" top="5vh">
      <div class="view-container">
        <el-empty v-if="!currentResume" description="暂无数据" />
        <div v-else class="resume-info">
          <div class="info-row">
            <span class="label">文件名:</span>
            <span class="value">{{ currentResume.file_name }}</span>
          </div>
          <div class="info-row">
            <span class="label">大小:</span>
            <span class="value">{{ formatFileSize(currentResume.file_size) }}</span>
          </div>
          <div class="info-row">
            <span class="label">上传时间:</span>
            <span class="value">{{ currentResume.created_at }}</span>
          </div>
          <div class="info-row">
            <span class="label">状态:</span>
            <el-tag :type="currentResume.status === 'processed' ? 'success' : 'info'">
              {{ getStatusText(currentResume.status) }}
            </el-tag>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="viewDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Search, Upload, View, Download, Delete, Link
} from '@element-plus/icons-vue'
import { useResumeStore } from '@/stores/resume'
import { resumeAPI } from '@/api/resume'

const router = useRouter()
const resumeStore = useResumeStore()

const loading = ref(false)
const viewDialogVisible = ref(false)
const currentResume = ref(null)

const searchForm = reactive({
  keyword: ''
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
    const res = await resumeAPI.getList({
      page: pagination.page,
      limit: pagination.limit,
      keyword: searchForm.keyword
    })
    tableData.value = res.data.files || res.data || []
    pagination.total = res.data.total || 0
  } catch (error) {
    console.error('获取简历列表失败:', error)
    ElMessage.error('获取简历列表失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.page = 1
  fetchData()
}

const goToUpload = () => {
  router.push('/upload')
}

const handleView = (row) => {
  currentResume.value = row
  viewDialogVisible.value = true
}

const handleDownload = async (row) => {
  try {
    const res = await resumeAPI.download(row.id)
    const blob = new Blob([res.data], { type: 'application/pdf' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = row.file_name
    link.click()
    window.URL.revokeObjectURL(url)
    ElMessage.success('下载成功')
  } catch (error) {
    console.error('下载失败:', error)
    ElMessage.error('下载失败')
  }
}

const handleCopyUrl = async (row) => {
  try {
    const res = await resumeAPI.getUrl(row.id)
    const url = res.data.url
    await navigator.clipboard.writeText(url)
    ElMessage.success('链接已复制到剪贴板')
  } catch (error) {
    console.error('获取链接失败:', error)
    ElMessage.error('获取链接失败')
  }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除该简历吗？', '提示', { type: 'warning' })
    await resumeAPI.delete(row.id)
    ElMessage.success('删除成功')
    fetchData()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

const formatFileSize = (bytes) => {
  if (!bytes) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

const getStatusText = (status) => {
  const statusMap = {
    processed: '已处理',
    pending: '待处理',
    failed: '失败'
  }
  return statusMap[status] || status
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.resume-list-container {
  width: 100%;
  padding: 16px;
  height: 100%;
  overflow: auto;
}

.list-card {
  min-height: calc(100vh - 100px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 10px;
  align-items: center;
}

.view-container {
  padding: 20px;
}

.resume-info {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.info-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.label {
  font-weight: 600;
  color: #6b7280;
  min-width: 80px;
}

.value {
  color: #111827;
}
</style>
