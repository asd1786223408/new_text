<template>
  <div class="upload-container">
    <el-card class="upload-card">
      <template #header>
        <div class="card-header">
          <span>批量上传简历</span>
        </div>
      </template>

      <!-- 上传区域 -->
      <div class="upload-section">
        <el-upload
          ref="uploadRef"
          drag
          multiple
          :file-list="fileList"
          :before-upload="beforeUpload"
          :on-change="handleChange"
          :on-remove="handleRemove"
          :http-request="customUpload"
          class="upload-area"
        >
          <el-icon class="upload-icon"><Upload-Filled /></el-icon>
          <div class="upload-text">
            <p class="upload-title">将文件拖到此处，或<em>点击上传</em></p>
            <p class="upload-hint">支持 PDF、DOC、DOCX 格式，单个文件不超过 10MB</p>
          </div>
        </el-upload>
      </div>

      <!-- 文件列表 -->
      <div v-if="fileList.length > 0" class="file-list-section">
        <div class="section-title">
          <span>已选择文件 ({{ fileList.length }})</span>
          <el-button type="primary" :loading="uploading" @click="startUpload">
            开始上传
          </el-button>
        </div>
        <el-table :data="fileList" style="margin-top: 10px" border>
          <el-table-column prop="name" label="文件名" min-width="200" show-overflow-tooltip />
          <el-table-column label="大小" width="100">
            <template #default="{ row }">
              {{ formatFileSize(row.size || row.raw?.size) }}
            </template>
          </el-table-column>
          <el-table-column label="状态" width="100">
            <template #default="{ row }">
              <el-tag v-if="row.status === 'success'" type="success">成功</el-tag>
              <el-tag v-else-if="row.status === 'error'" type="danger">失败</el-tag>
              <el-tag v-else-if="row.status === 'uploading'" type="info">上传中</el-tag>
              <el-tag v-else type="info">待上传</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="80">
            <template #default="{ row, $index }">
              <el-button
                v-if="row.status !== 'uploading'"
                link
                type="danger"
                size="small"
                @click="handleRemoveFile($index)"
              >
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 上传进度 -->
      <div v-if="uploading" class="progress-section">
        <el-progress
          :percentage="uploadProgress"
          :status="uploadComplete ? 'success' : undefined"
        />
        <p class="progress-text">
          已上传 {{ uploadedCount }} / {{ fileList.length }} 个文件
        </p>
      </div>

      <!-- 上传结果 -->
      <div v-if="uploadResult.length > 0" class="result-section">
        <div class="section-title">
          <span>上传结果</span>
        </div>
        <el-table :data="uploadResult" border>
          <el-table-column prop="name" label="文件名" min-width="200" show-overflow-tooltip />
          <el-table-column label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="row.success ? 'success' : 'danger'">
                {{ row.success ? '成功' : '失败' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="message" label="消息" min-width="200" />
        </el-table>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'
import { resumeAPI } from '@/api/resume'

const router = useRouter()
const uploadRef = ref(null)
const fileList = ref([])
const uploading = ref(false)
const uploadProgress = ref(0)
const uploadedCount = ref(0)
const uploadComplete = ref(false)
const uploadResult = ref([])

const ALLOWED_TYPES = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
const MAX_SIZE = 10 * 1024 * 1024 // 10MB

const beforeUpload = (file) => {
  if (!ALLOWED_TYPES.includes(file.type)) {
    ElMessage.error('只支持 PDF、DOC、DOCX 格式的文件')
    return false
  }
  if (file.size > MAX_SIZE) {
    ElMessage.error('单个文件不能超过 10MB')
    return false
  }
  return true
}

const handleChange = (file, files) => {
  fileList.value = files
}

const handleRemove = (file, files) => {
  fileList.value = files
}

const handleRemoveFile = (index) => {
  fileList.value.splice(index, 1)
}

const customUpload = async (options) => {
  const { file, onSuccess, onError } = options
  try {
    const formData = new FormData()
    formData.append('file', file)
    const res = await resumeAPI.batchUpload(formData)
    file.status = 'success'
    onSuccess(res)
  } catch (error) {
    file.status = 'error'
    onError(error)
  }
}

const startUpload = async () => {
  if (fileList.value.length === 0) {
    ElMessage.warning('请选择要上传的文件')
    return
  }

  uploading.value = true
  uploadProgress.value = 0
  uploadedCount.value = 0
  uploadComplete.value = false
  uploadResult.value = []

  const pendingFiles = fileList.value.filter(f => !f.status || f.status === 'ready')

  for (let i = 0; i < pendingFiles.length; i++) {
    const file = pendingFiles[i]
    file.status = 'uploading'

    try {
      const formData = new FormData()
      formData.append('file', file.raw || file)
      await resumeAPI.batchUpload(formData)
      file.status = 'success'
      uploadResult.value.push({
        name: file.name,
        success: true,
        message: '上传成功'
      })
      ElMessage.success(`${file.name} 上传成功`)
    } catch (error) {
      file.status = 'error'
      uploadResult.value.push({
        name: file.name,
        success: false,
        message: error.message || '上传失败'
      })
      ElMessage.error(`${file.name} 上传失败`)
    }

    uploadedCount.value++
    uploadProgress.value = Math.round((uploadedCount.value / pendingFiles.length) * 100)
  }

  uploading.value = false
  uploadComplete.value = true

  if (uploadResult.value.some(r => r.success)) {
    ElMessage.success('部分文件上传成功')
    // 延迟跳转到列表页
    setTimeout(() => {
      router.push('/')
    }, 1500)
  }
}

const formatFileSize = (bytes) => {
  if (!bytes) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}
</script>

<style scoped>
.upload-container {
  width: 100%;
  padding: 16px;
  height: 100%;
  overflow: auto;
}

.upload-card {
  min-height: calc(100vh - 100px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.upload-section {
  margin: 20px 0;
}

.upload-area {
  width: 100%;
}

.upload-area :deep(.el-upload-dragger) {
  padding: 40px 20px;
  border-radius: 12px;
  border: 2px dashed #d9d9d9;
  transition: all 0.3s;
}

.upload-area :deep(.el-upload-dragger:hover) {
  border-color: #5b5fc7;
  background-color: rgba(91, 95, 199, 0.04);
}

.upload-icon {
  font-size: 64px;
  color: #5b5fc7;
  margin-bottom: 16px;
}

.upload-text {
  text-align: center;
}

.upload-title {
  font-size: 16px;
  color: #111827;
  margin-bottom: 8px;
}

.upload-title em {
  color: #5b5fc7;
  font-style: normal;
  text-decoration: underline;
}

.upload-hint {
  font-size: 13px;
  color: #9ca3af;
}

.file-list-section {
  margin-top: 20px;
}

.section-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.section-title span {
  font-size: 14px;
  font-weight: 600;
  color: #6b7280;
}

.progress-section {
  margin-top: 20px;
  padding: 20px;
  background: #f9fafb;
  border-radius: 8px;
}

.progress-text {
  text-align: center;
  margin-top: 10px;
  font-size: 14px;
  color: #6b7280;
}

.result-section {
  margin-top: 20px;
}
</style>
