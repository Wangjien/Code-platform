import axios, { type AxiosResponse, type AxiosError } from 'axios'
import { ref, readonly } from 'vue'
import { ElMessage } from 'element-plus'
import { API_CONFIG } from '../config/api'
import router from '../router'

// 创建 axios 实例
const http = axios.create({
  baseURL: API_CONFIG.baseURL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器 - 自动添加 token
http.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器 - 统一错误处理
http.interceptors.response.use(
  (response: AxiosResponse) => {
    return response
  },
  (error: AxiosError<any>) => {
    console.error('API Error:', error)
    
    // 处理 401 未授权 - 自动跳转登录
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      ElMessage.error('登录已过期，请重新登录')
      router.push('/login')
      return Promise.reject(error)
    }
    
    // 处理 403 权限不足
    if (error.response?.status === 403) {
      ElMessage.error('权限不足')
      return Promise.reject(error)
    }
    
    // 处理 404 资源不存在
    if (error.response?.status === 404) {
      ElMessage.error('请求的资源不存在')
      return Promise.reject(error)
    }
    
    // 处理 500 服务器错误
    if (error.response?.status === 500) {
      ElMessage.error('服务器内部错误，请稍后重试')
      return Promise.reject(error)
    }
    
    // 处理网络错误
    if (!error.response) {
      ElMessage.error('网络连接失败，请检查网络')
      return Promise.reject(error)
    }
    
    // 处理其他错误
    const message = error.response?.data?.message || '请求失败'
    ElMessage.error(message)
    return Promise.reject(error)
  }
)

// 加载状态管理
export const useLoading = () => {
  const loading = ref(false)
  
  const withLoading = async <T>(fn: () => Promise<T>): Promise<T> => {
    loading.value = true
    try {
      const result = await fn()
      return result
    } finally {
      loading.value = false
    }
  }
  
  return {
    loading: readonly(loading),
    withLoading
  }
}

export default http
