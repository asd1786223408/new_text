import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000
})

// 简历相关 API
export const resumeAPI = {
  // 获取简历列表
  getList(params) {
    return api.get('/list', { params })
  },

  // 获取简历详情
  getById(id) {
    return api.get(`/${id}`)
  },

  // 批量上传
  batchUpload(formData) {
    return api.post('/batch-upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  // 下载简历
  download(id) {
    return api.get(`/download/${id}`, {
      responseType: 'blob'
    })
  },

  // 删除简历（软删除）
  delete(id) {
    return api.delete(`/${id}`)
  },

  // 获取临时下载链接
  getUrl(id, expired = 3600) {
    return api.get(`/url/${id}`, { params: { expired } })
  }
}

export default api
