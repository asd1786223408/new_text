import request from './request'

/**
 * 获取当前用户个人信息
 */
export function getProfile() {
  return request({
    url: '/users/profile',
    method: 'get'
  })
}

/**
 * 更新当前用户个人信息
 * @param {Object} data - 用户信息
 */
export function updateProfile(data) {
  return request({
    url: '/users/profile',
    method: 'put',
    data
  })
}

/**
 * 修改密码
 * @param {number} userId - 用户 ID
 * @param {Object} data - 密码信息
 * @param {string} data.old_password - 原密码
 * @param {string} data.new_password - 新密码
 */
export function updatePassword(userId, data) {
  return request({
    url: `/users/${userId}/password`,
    method: 'put',
    data
  })
}
