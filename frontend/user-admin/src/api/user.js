import request from './request'

// 获取用户列表
export function getUserList(params) {
  return request({
    url: '/users',
    method: 'get',
    params
  })
}

// 获取用户详情
export function getUserDetail(id) {
  return request({
    url: `/users/${id}`,
    method: 'get'
  })
}

// 创建用户
export function createUser(data) {
  return request({
    url: '/users',
    method: 'post',
    data
  })
}

// 更新用户
export function updateUser(id, data) {
  return request({
    url: `/users/${id}`,
    method: 'put',
    data
  })
}

// 删除用户
export function deleteUser(id) {
  return request({
    url: `/users/${id}`,
    method: 'delete'
  })
}

// 更新用户角色
export function updateUserRoles(id, roleIds) {
  return request({
    url: `/users/${id}/roles`,
    method: 'put',
    data: { role_ids: roleIds }
  })
}

// 修改密码
export function updatePassword(id, data) {
  return request({
    url: `/users/${id}/password`,
    method: 'put',
    data
  })
}
