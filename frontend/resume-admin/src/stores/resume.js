import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useResumeStore = defineStore('resume', () => {
  const resumes = ref([])
  const total = ref(0)
  const loading = ref(false)

  // 获取简历列表
  async function fetchResumes(params = {}) {
    loading.value = true
    try {
      const { resumeAPI } = await import('../api/resume')
      const res = await resumeAPI.getList(params)
      resumes.value = res.data.files || []
      total.value = res.data.total || 0
      return res.data
    } catch (error) {
      console.error('获取简历列表失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 删除简历
  async function deleteResume(id) {
    try {
      const { resumeAPI } = await import('../api/resume')
      await resumeAPI.delete(id)
      // 从列表中移除
      const index = resumes.value.findIndex(r => r.id === id)
      if (index > -1) {
        resumes.value.splice(index, 1)
      }
      return true
    } catch (error) {
      console.error('删除简历失败:', error)
      throw error
    }
  }

  // 重置列表
  function resetList() {
    resumes.value = []
    total.value = 0
  }

  return {
    resumes,
    total,
    loading,
    fetchResumes,
    deleteResume,
    resetList
  }
})
