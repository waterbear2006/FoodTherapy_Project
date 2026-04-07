import request from './request'

export function getNews() {
  return request({
    url: '/search/news',
    method: 'get'
  })
}