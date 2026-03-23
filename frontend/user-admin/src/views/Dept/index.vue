<template>
  <div class="dept-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>部门管理</span>
          <el-button type="primary" @click="handleAdd">新增部门</el-button>
        </div>
      </template>

      <!-- 树形表格 -->
      <el-table
        :data="tableData"
        v-loading="loading"
        border
        row-key="id"
        :tree-props="{ children: 'children' }"
      >
        <el-table-column prop="name" label="部门名称" width="200" />
        <el-table-column prop="level" label="层级" width="80" />
        <el-table-column prop="sort" label="排序" width="80" />
        <el-table-column label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'danger'">
              {{ row.status === 1 ? '正常' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" fixed="right" width="200">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>

  <!-- 部门表单对话框 -->
  <el-dialog v-model="dialogVisible" :title="dialogTitle" width="500px">
    <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
      <el-form-item label="部门名称" prop="name">
        <el-input v-model="form.name" />
      </el-form-item>
      <el-form-item label="父部门" prop="parent_id">
        <el-tree-select
          v-model="form.parent_id"
          :data="deptTree"
          check-strictly
          placeholder="选择父部门"
        />
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
import { getDeptTree, createDept, updateDept, deleteDept } from '@/api/dept'

const loading = ref(false)
const submitLoading = ref(false)
const dialogVisible = ref(false)
const dialogTitle = ref('新增部门')
const formRef = ref(null)

const tableData = ref([])
const deptTree = ref([])

const form = reactive({
  id: null,
  name: '',
  parent_id: 0,
  sort: 0
})

const rules = {
  name: [{ required: true, message: '请输入部门名称', trigger: 'blur' }]
}

const fetchData = async () => {
  loading.value = true
  try {
    const res = await getDeptTree()
    tableData.value = res.data || []
    deptTree.value = [{ id: 0, label: '顶级部门', children: res.data || [] }]
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

const handleAdd = () => {
  dialogTitle.value = '新增部门'
  Object.assign(form, { id: null, name: '', parent_id: 0, sort: 0 })
  dialogVisible.value = true
}

const handleEdit = (row) => {
  dialogTitle.value = '编辑部门'
  Object.assign(form, { ...row })
  dialogVisible.value = true
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除该部门吗？', '提示', { type: 'warning' })
    await deleteDept(row.id)
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
        await updateDept(form.id, form)
        ElMessage.success('更新成功')
      } else {
        await createDept(form)
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
.dept-container {
  width: 100%;
  padding: 20px;
}

.dept-container :deep(.el-card) {
  border-radius: 16px;
  overflow: hidden;
}

.dept-container :deep(.el-card__header) {
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
.dept-container :deep(.el-table) {
  --el-table-header-bg-color: #f8fafc;
}

.dept-container :deep(.el-table th) {
  font-weight: 600;
  color: var(--text-primary);
  font-size: 14px;
  background-color: #f8fafc !important;
}

.dept-container :deep(.el-table td) {
  padding: 14px 0;
}

.dept-container :deep(.el-table .cell) {
  padding: 0 24px;
  font-size: 14px;
}

/* 操作按钮 */
.dept-container :deep(.el-button--link) {
  font-size: 13px;
  padding: 4px 8px;
  margin: 0 2px;
}

/* Dialog 样式优化 */
.dept-container :deep(.el-dialog) {
  border-radius: 16px;
  overflow: hidden;
}

.dept-container :deep(.el-dialog__header) {
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  padding: 20px 24px;
}

.dept-container :deep(.el-dialog__title) {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.dept-container :deep(.el-dialog__body) {
  padding: 24px;
}

.dept-container :deep(.el-dialog__footer) {
  padding: 16px 24px;
  border-top: 1px solid var(--border-light);
}

/* 表单样式 */
.dept-container :deep(.el-form-item__label) {
  font-weight: 500;
  color: var(--text-primary);
}

.dept-container :deep(.el-form-item) {
  margin-bottom: 20px;
}

.dept-container :deep(.el-input__wrapper) {
  border-radius: 10px;
}
</style>
