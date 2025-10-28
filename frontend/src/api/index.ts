import axios from 'axios'
import { message } from 'antd'

// 创建axios实例
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    // 添加认证token
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    
    // 添加时间戳防止缓存
    if (config.method === 'get') {
      config.params = {
        ...config.params,
        _t: Date.now()
      }
    }
    
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    const { status, data } = error.response || {}
    
    // 处理不同状态码
    switch (status) {
      case 401:
        // 未授权，清除token并跳转到登录页
        localStorage.removeItem('access_token')
        window.location.href = '/login'
        message.error('登录已过期，请重新登录')
        break
      case 403:
        message.error('权限不足')
        break
      case 404:
        message.error('请求的资源不存在')
        break
      case 500:
        message.error('服务器内部错误')
        break
      default:
        message.error(data?.message || '网络错误，请稍后重试')
    }
    
    return Promise.reject(error)
  }
)

export default api