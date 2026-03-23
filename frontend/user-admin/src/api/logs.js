import request from './request'

/**
 * 获取操作日志列表
 * @param {Object} params - 查询参数
 * @param {number} params.page - 页码
 * @param {number} params.limit - 每页数量
 * @param {string} params.username - 用户名
 * @param {string} params.module - 模块
 * @param {string} params.action - 操作类型
 */
export function getLogs(params) {
  return request({
    url: '/logs',
    method: 'get',
    params
  })
}

/**
 * 获取日志统计信息
 */
export function getLogsStats() {
  return request({
    url: '/logs/stats',
    method: 'get'
  })
}
