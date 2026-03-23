import request from './request'

// 获取部门列表
export function getDeptList() {
  return request({
    url: '/departments',
    method: 'get'
  })
}

// 获取部门树
export function getDeptTree() {
  return request({
    url: '/departments/tree',
    method: 'get'
  })
}

// 获取部门详情
export function getDeptDetail(id) {
  return request({
    url: `/departments/${id}`,
    method: 'get'
  })
}

// 创建部门
export function createDept(data) {
  return request({
    url: '/departments',
    method: 'post',
    data
  })
}

// 更新部门
export function updateDept(id, data) {
  return request({
    url: `/departments/${id}`,
    method: 'put',
    data
  })
}

// 删除部门
export function deleteDept(id) {
  return request({
    url: `/departments/${id}`,
    method: 'delete'
  })
}
