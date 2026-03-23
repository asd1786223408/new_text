<template>
  <div class="permission-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>权限管理</span>
          <el-button type="primary" @click="handleAdd">新增权限</el-button>
        </div>
      </template>

      <!-- 搜索栏 -->
      <el-form :inline="true" :model="searchForm">
        <el-form-item label="模块">
          <el-select v-model="searchForm.module" placeholder="全部模块" clearable @change="fetchData">
            <el-option v-for="m in modules" :key="m" :label="m" :value="m" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="fetchData">刷新</el-button>
        </el-form-item>
      </el-form>

      <!-- 表格 -->
      <el-table :data="tableData" v-loading="loading" border stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="权限标识" width="180" />
        <el-table-column prop="display_name" label="显示名称" width="150" />
        <el-table-column prop="module" label="模块" width="100" />
        <el-table-column prop="action" label="操作类型" width="100" />
        <el-table-column prop="icon" label="图标" width="80" />
        <el-table-column prop="sort" label="排序" width="80" />
        <el-table-column label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'danger'">
              {{ row.status === 1 ? '正常' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" fixed="right" width="150">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>

  <!-- 权限表单对话框 -->
  <el-dialog v-model="dialogVisible" :title="dialogTitle" width="500px">
    <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
      <el-form-item label="权限标识" prop="name">
        <el-input v-model="form.name" :disabled="!!form.id" placeholder="如：user:create" />
      </el-form-item>
      <el-form-item label="显示名称" prop="display_name">
        <el-input v-model="form.display_name" placeholder="如：创建用户" />
      </el-form-item>
      <el-form-item label="模块" prop="module">
        <el-input v-model="form.module" placeholder="如：user" />
      </el-form-item>
      <el-form-item label="操作类型" prop="action">
        <el-select v-model="form.action" placeholder="请选择">
          <el-option label="create" value="create" />
          <el-option label="read" value="read" />
          <el-option label="update" value="update" />
          <el-option label="delete" value="delete" />
          <el-option label="manage" value="manage" />
          <el-option label="view" value="view" />
          <el-option label="config" value="config" />
        </el-select>
      </el-form-item>
      <el-form-item label="图标" prop="icon">
        <el-input v-model="form.icon" placeholder="如图标名称" />
      </el-form-item>
      <el-form-item label="排序" prop="sort">
        <el-input-number v-model="form.sort" :min="0" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="dialogVisible = false">取消</el-button>
      <el-button type="primary" @click="handleSubmit" :loading="submitLoading">确定</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getPermissionList, createPermission, updatePermission, deletePermission, getModuleList } from '@/api/permission'

const loading = ref(false)
const submitLoading = ref(false)
const dialogVisible = ref(false)
const dialogTitle = ref('新增权限')
const formRef = ref(null)

const searchForm = reactive({ module: '' })
const modules = ref([])
const tableData = ref([])

const form = reactive({
  id: null,
  name: '',
  display_name: '',
  module: '',
  action: '',
  icon: '',
  sort: 0
})

const rules = {
  name: [{ required: true, message: '请输入权限标识', trigger: 'blur' }],
  display_name: [{ required: true, message: '请输入显示名称', trigger: 'blur' }],
  module: [{ required: true, message: '请输入模块', trigger: 'blur' }],
  action: [{ required: true, message: '请选择操作类型', trigger: 'change' }]
}

const fetchData = async () => {
  loading.value = true
  try {
    const res = await getPermissionList({ module: searchForm.module })
    tableData.value = res.data || []
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

const fetchModules = async () => {
  try {
    const res = await getModuleList()
    modules.value = res.data || []
  } catch (error) {
    console.error(error)
  }
}

const handleAdd = () => {
  dialogTitle.value = '新增权限'
  Object.assign(form, { id: null, name: '', display_name: '', module: '', action: '', icon: '', sort: 0 })
  dialogVisible.value = true
}

const handleEdit = (row) => {
  dialogTitle.value = '编辑权限'
  Object.assign(form, { ...row })
  dialogVisible.value = true
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除该权限吗？', '提示', { type: 'warning' })
    await deletePermission(row.id)
    ElMessage.success('删除成功')
    fetchData()
  } catch (error) {
    if (error !== 'cancel') console.error(error)
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    submitLoading.value = true
    try {
      if (form.id) {
        await updatePermission(form.id, form)
        ElMessage.success('更新成功')
      } else {
        await createPermission(form)
        ElMessage.success('创建成功')
      }
      dialogVisible.value = false
      fetchData()
    } catch (error) {
      console.error(error)
    } finally {
      submitLoading.value = false
    }
  })
}

onMounted(() => {
  fetchData()
  fetchModules()
})
</script>

<style scoped>
.permission-container {
  width: 100%;
  padding: 20px;
}

.permission-container :deep(.el-card) {
  border-radius: 16px;
  overflow: hidden;
}

.permission-container :deep(.el-card__header) {
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

/* 表格样式 */
.permission-container :deep(.el-table) {
  --el-table-header-bg-color: #f8fafc;
}

.permission-container :deep(.el-table th) {
  font-weight: 600;
  color: var(--text-primary);
  font-size: 14px;
  background-color: #f8fafc !important;
}

.permission-container :deep(.el-table td) {
  padding: 14px 0;
}

.permission-container :deep(.el-table .cell) {
  padding: 0 24px;
  font-size: 14px;
}

/* 操作按钮 */
.permission-container :deep(.el-button--link) {
  font-size: 13px;
  padding: 4px 8px;
  margin: 0 2px;
}

/* Dialog 样式优化 */
.permission-container :deep(.el-dialog) {
  border-radius: 16px;
  overflow: hidden;
}

.permission-container :deep(.el-dialog__header) {
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  padding: 20px 24px;
}

.permission-container :deep(.el-dialog__title) {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.permission-container :deep(.el-dialog__body) {
  padding: 24px;
}

.permission-container :deep(.el-dialog__footer) {
  padding: 16px 24px;
  border-top: 1px solid var(--border-light);
}

/* 表单样式 */
.permission-container :deep(.el-form-item__label) {
  font-weight: 500;
  color: var(--text-primary);
}

.permission-container :deep(.el-form-item) {
  margin-bottom: 20px;
}

.permission-container :deep(.el-input__wrapper) {
  border-radius: 10px;
}
</style>
