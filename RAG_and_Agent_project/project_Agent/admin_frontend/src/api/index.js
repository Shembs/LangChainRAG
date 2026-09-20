import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '../router'

const api = axios.create({
  baseURL: '/api/admin',
  timeout: 120000,
})

// 请求拦截器：注入 Bearer token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('admin_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 响应拦截器：统一返回 data，处理 401
api.interceptors.response.use(
  (res) => res.data,
  (err) => {
    const status = err.response?.status
    if (status === 401) {
      localStorage.removeItem('admin_token')
      ElMessage.error('登录已过期，请重新登录')
      router.push({ name: 'login' })
    } else {
      const detail = err.response?.data?.detail
      ElMessage.error(typeof detail === 'string' ? detail : err.message || '请求失败')
    }
    return Promise.reject(err)
  }
)

export default api
