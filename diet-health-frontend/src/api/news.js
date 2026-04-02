import request from './request'

export function getNews() {
  return request({
    url: '/api/search/news',
    method: 'get'
  })
}