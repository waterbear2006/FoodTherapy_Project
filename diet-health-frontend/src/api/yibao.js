// src/api/yibao.js
import request from './request'

export function chatWithYibao(message) {
  return request({
    url: '/assistant/chat',  // 后端接口路径
    method: 'post',
    data: {
      message: message
    }
  })
}