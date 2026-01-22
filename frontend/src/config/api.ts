/**
 * API 配置文件
 * 
 * 集中管理所有后端 API 端点地址
 * 
 * 环境变量：
 * - VITE_API_BASE_URL: API 基础地址（生产环境在 .env.production 中配置）
 * 
 * 使用方式：
 * import { API_CONFIG } from './config/api'
 * http.get(API_CONFIG.endpoints.codes)
 * http.get(API_CONFIG.endpoints.codeDetail(123))
 */
export const API_CONFIG = {
  // 从环境变量读取 API 基础地址，开发环境默认 localhost:5001
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:5001',
  
  // API 端点
  endpoints: {
    // 认证
    login: '/api/login',
    register: '/api/register',
    
    // 代码
    codes: '/api/codes',
    codeDetail: (id: number) => `/api/codes/${id}`,
    codeComments: (id: number) => `/api/codes/${id}/comments`,
    
    // 用户
    userCodes: '/api/user/codes',
    userFavorites: '/api/user/favorites',
    userProfile: '/api/user/profile',
    userPassword: '/api/user/password',
    
    // 分类和标签
    categories: '/api/categories',
    categoryDetail: (id: number) => `/api/categories/${id}`,
    tags: '/api/tags',
    
    // 用户自定义分类
    userCategories: '/api/user/categories',
    userCategoryDetail: (id: number) => `/api/user/categories/${id}`,
    userCategorySort: '/api/user/categories/sort',
    
    // 管理员
    adminUsers: '/api/admin/users',
    adminCodes: '/api/admin/codes',
    adminComments: '/api/admin/comments',
    adminUserDetail: (id: number) => `/api/admin/users/${id}`,
    adminCodeReview: (id: number) => `/api/admin/codes/${id}/review`,
    adminCommentDetail: (id: number) => `/api/admin/comments/${id}`,
  }
}

// 构建完整 API URL
export const buildApiUrl = (endpoint: string): string => {
  return `${API_CONFIG.baseURL}${endpoint}`
}
