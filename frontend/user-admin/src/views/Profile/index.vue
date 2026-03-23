<template>
  <div class="profile-container">
    <el-row :gutter="20">
      <!-- 个人信息 -->
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>个人信息</span>
          </template>
          <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
            <el-form-item label="用户名">
              <el-input v-model="form.username" disabled />
            </el-form-item>
            <el-form-item label="昵称" prop="nickname">
              <el-input v-model="form.nickname" />
            </el-form-item>
            <el-form-item label="邮箱" prop="email">
              <el-input v-model="form.email" />
            </el-form-item>
            <el-form-item label="手机号" prop="phone">
              <el-input v-model="form.phone" />
            </el-form-item>
            <el-form-item label="部门">
              <el-input v-model="form.department_name" disabled />
            </el-form-item>
            <el-form-item label="职位">
              <el-input v-model="form.position" disabled />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="handleUpdateProfile" :loading="updateLoading">更新资料</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <!-- 修改密码 -->
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>修改密码</span>
          </template>
          <el-form ref="passwordFormRef" :model="passwordForm" :rules="passwordRules" label-width="100px">
            <el-form-item label="原密码" prop="old_password">
              <el-input v-model="passwordForm.old_password" type="password" show-password />
            </el-form-item>
            <el-form-item label="新密码" prop="new_password">
              <el-input v-model="passwordForm.new_password" type="password" show-password />
            </el-form-item>
            <el-form-item label="确认密码" prop="confirm_password">
              <el-input v-model="passwordForm.confirm_password" type="password" show-password />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="handleUpdatePassword" :loading="passwordLoading">修改密码</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { getProfile, updateProfile, updatePassword } from '@/api/profile'

const userStore = useUserStore()
const formRef = ref(null)
const passwordFormRef = ref(null)
const updateLoading = ref(false)
const passwordLoading = ref(false)

const form = reactive({
  id: null,
  username: '',
  nickname: '',
  email: '',
  phone: '',
  department_name: '',
  position: ''
})

const rules = {
  email: [{ type: 'email', message: '请输入正确的邮箱', trigger: 'blur' }]
}

const passwordForm = reactive({
  old_password: '',
  new_password: '',
  confirm_password: ''
})

const passwordRules = {
  old_password: [{ required: true, message: '请输入原密码', trigger: 'blur' }],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少 6 位', trigger: 'blur' }
  ],
  confirm_password: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== passwordForm.new_password) {
          callback(new Error('两次密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

const fetchProfile = async () => {
  try {
    const res = await getProfile()
    if (res.data) {
      Object.assign(form, {
        id: res.data.id,
        username: res.data.username,
        nickname: res.data.nickname || '',
        email: res.data.email || '',
        phone: res.data.phone || '',
        department_name: res.data.department_name || '',
        position: res.data.position || ''
      })
    }
  } catch (error) {
    console.error(error)
    ElMessage.error('加载个人信息失败')
  }
}

const handleUpdateProfile = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    updateLoading.value = true
    try {
      await updateProfile({
        nickname: form.nickname,
        email: form.email,
        phone: form.phone
      })
      ElMessage.success('资料更新成功')
      fetchProfile()
    } catch (error) {
      console.error(error)
    } finally {
      updateLoading.value = false
    }
  })
}

const handleUpdatePassword = async () => {
  if (!passwordFormRef.value) return
  await passwordFormRef.value.validate(async (valid) => {
    if (!valid) return
    passwordLoading.value = true
    try {
      await updatePassword(form.id, {
        old_password: passwordForm.old_password,
        new_password: passwordForm.new_password
      })
      ElMessage.success('密码修改成功')
      passwordForm.old_password = ''
      passwordForm.new_password = ''
      passwordForm.confirm_password = ''
    } catch (error) {
      console.error(error)
    } finally {
      passwordLoading.value = false
    }
  })
}

onMounted(() => {
  fetchProfile()
})
</script>

<style scoped>
.profile-container {
  width: 100%;
  padding: 20px;
  max-width: 1200px;
}

.profile-container :deep(.el-card) {
  border-radius: 16px;
  overflow: hidden;
  margin-bottom: 20px;
}

.profile-container :deep(.el-card__header) {
  padding: 18px 24px;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  border-bottom: 1px solid var(--border-light);
}

.profile-container :deep(.el-card__header span) {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

/* 表单样式 */
.profile-container :deep(.el-form-item__label) {
  font-weight: 500;
  color: var(--text-primary);
}

.profile-container :deep(.el-form-item) {
  margin-bottom: 20px;
}

.profile-container :deep(.el-input__wrapper) {
  border-radius: 10px;
}

/* 按钮样式 */
.profile-container :deep(.el-button--primary) {
  background: linear-gradient(135deg, #2563eb 0%, #3b82f6 100%);
  border: none;
  padding: 10px 24px;
  border-radius: 10px;
}

.profile-container :deep(.el-button--primary:hover) {
  opacity: 0.9;
  transform: translateY(-1px);
}
</style>
