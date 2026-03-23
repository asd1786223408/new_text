import request from './request'

// 获取角色列表
export function getRoleList() {
  return request({
    url: '/roles',
    method: 'get'
  })
}

// 获取角色详情
export function getRoleDetail(id) {
  return request({
    url: `/roles/${id}`,
    method: 'get'
  })
}

// 创建角色
export function createRole(data) {
  return request({
    url: '/roles',
    method: 'post',
    data
  })
}

// 更新角色
export function updateRole(id, data) {
  return request({
    url: `/roles/${id}`,
    method: 'put',
    data
  })
}

// 删除角色
export function deleteRole(id) {
  return request({
    url: `/roles/${id}`,
    method: 'delete'
  })
}

// 更新角色权限
export function updateRolePermissions(id, permissionIds) {
  return request({
    url: `/roles/${id}/permissions`,
    method: 'put',
    data: { permission_ids: permissionIds }
  })
}
