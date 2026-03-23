import { defineStore } from 'pinia'
import { ref } from 'vue'
import { login, logout, getCurrentUser } from '@/api/auth'

export const useUserStore = defineStore('user', () => {
  const token = ref('')
  const userInfo = ref(null)
  const permissions = ref([])

  // 解析权限（处理后端返回字符串格式）
  function parsePermissions(data) {
    if (!data) return []
    if (Array.isArray(data)) return data
    if (typeof data === 'string') {
      try {
        return JSON.parse(data)
      } catch {
        return data.split(',').map(p => p.trim())
      }
    }
    return []
  }

  // 登录
  async function loginAction(loginForm) {
    const res = await login(loginForm)
    if (res.data) {
      userInfo.value = res.data
      permissions.value = parsePermissions(res.data.permissions)
    }
    return res
  }

  // 登出
  async function logoutAction() {
    await logout()
    userInfo.value = null
    permissions.value = []
  }

  // 获取用户信息
  async function getUserInfo() {
    const res = await getCurrentUser()
    if (res.data) {
      userInfo.value = res.data
      permissions.value = parsePermissions(res.data.permissions)
    }
    return res
  }

  // 检查权限
  function hasPermission(permission) {
    if (!permissions.value) return false
    return permissions.value.includes(permission)
  }

  return {
    token,
    userInfo,
    permissions,
    loginAction,
    logoutAction,
    getUserInfo,
    hasPermission,
    parsePermissions
  }
})
