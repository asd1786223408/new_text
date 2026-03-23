<template>
  <div class="role-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>角色列表</span>
          <el-button type="primary" @click="handleAdd">新增角色</el-button>
        </div>
      </template>

      <el-table :data="tableData" v-loading="loading" border stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="角色标识" width="150" />
        <el-table-column prop="display_name" label="显示名称" width="150" />
        <el-table-column prop="description" label="描述" />
        <el-table-column label="权限" width="200">
          <template #default="{ row }">
            <el-tag v-for="perm in (row.permissions || []).slice(0, 3)" :key="perm" size="small" style="margin-right: 5px">
              {{ perm }}
            </el-tag>
            <el-tag v-if="(row.permissions || []).length > 3" size="small">+{{ (row.permissions || []).length - 3 }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'danger'">
              {{ row.status === 1 ? '正常' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" fixed="right" width="200">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button link type="primary" @click="handlePermissions(row)">权限</el-button>
            <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>

  <!-- 角色表单对话框 -->
  <el-dialog v-model="dialogVisible" :title="dialogTitle" width="500px">
    <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
      <el-form-item label="角色标识" prop="name">
        <el-input v-model="form.name" :disabled="!!form.id" />
      </el-form-item>
      <el-form-item label="显示名称" prop="display_name">
        <el-input v-model="form.display_name" />
      </el-form-item>
      <el-form-item label="描述" prop="description">
        <el-input v-model="form.description" type="textarea" :rows="3" />
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
import { getRoleList, createRole, updateRole, deleteRole } from '@/api/role'

const loading = ref(false)
const submitLoading = ref(false)
const dialogVisible = ref(false)
const dialogTitle = ref('新增角色')
const formRef = ref(null)

const tableData = ref([])

const form = reactive({
  id: null,
  name: '',
  display_name: '',
  description: ''
})

const rules = {
  name: [{ required: true, message: '请输入角色标识', trigger: 'blur' }],
  display_name: [{ required: true, message: '请输入显示名称', trigger: 'blur' }]
}

const fetchData = async () => {
  loading.value = true
  try {
    const res = await getRoleList()
    tableData.value = res.data || []
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

const handleAdd = () => {
  dialogTitle.value = '新增角色'
  Object.assign(form, { id: null, name: '', display_name: '', description: '' })
  dialogVisible.value = true
}

const handleEdit = (row) => {
  dialogTitle.value = '编辑角色'
  Object.assign(form, { ...row })
  dialogVisible.value = true
}

const handlePermissions = (row) => {
  ElMessage.info('权限配置功能待实现')
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除该角色吗？', '提示', { type: 'warning' })
    await deleteRole(row.id)
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
        await updateRole(form.id, form)
        ElMessage.success('更新成功')
      } else {
        await createRole(form)
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
})
</script>

<style scoped>
.role-container {
  width: 100%;
  padding: 20px;
}

.role-container :deep(.el-card) {
  border-radius: 16px;
  overflow: hidden;
}

.role-container :deep(.el-card__header) {
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
.role-container :deep(.el-table) {
  --el-table-header-bg-color: #f8fafc;
}

.role-container :deep(.el-table th) {
  font-weight: 600;
  color: var(--text-primary);
  font-size: 14px;
  background-color: #f8fafc !important;
}

.role-container :deep(.el-table td) {
  padding: 14px 0;
}

.role-container :deep(.el-table .cell) {
  padding: 0 24px;
  font-size: 14px;
}

/* 操作按钮 */
.role-container :deep(.el-button--link) {
  font-size: 13px;
  padding: 4px 8px;
  margin: 0 2px;
}

/* Dialog 样式优化 */
.role-container :deep(.el-dialog) {
  border-radius: 16px;
  overflow: hidden;
}

.role-container :deep(.el-dialog__header) {
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  padding: 20px 24px;
}

.role-container :deep(.el-dialog__title) {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.role-container :deep(.el-dialog__body) {
  padding: 24px;
}

.role-container :deep(.el-dialog__footer) {
  padding: 16px 24px;
  border-top: 1px solid var(--border-light);
}

/* 表单样式 */
.role-container :deep(.el-form-item__label) {
  font-weight: 500;
  color: var(--text-primary);
}

.role-container :deep(.el-form-item) {
  margin-bottom: 20px;
}

.role-container :deep(.el-input__wrapper) {
  border-radius: 10px;
}
</style>
