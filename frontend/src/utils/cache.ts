/**
 * 前端数据缓存工具
 * 提供内存缓存和localStorage缓存功能
 */

interface CacheItem<T> {
  data: T
  timestamp: number
  ttl?: number
}

class DataCache {
  private memoryCache = new Map<string, CacheItem<any>>()
  private defaultTTL = 5 * 60 * 1000 // 5分钟默认TTL

  /**
   * 设置缓存数据
   */
  set<T>(key: string, data: T, ttl?: number): void {
    const item: CacheItem<T> = {
      data,
      timestamp: Date.now(),
      ttl: ttl || this.defaultTTL
    }
    this.memoryCache.set(key, item)
  }

  /**
   * 获取缓存数据
   */
  get<T>(key: string): T | null {
    const item = this.memoryCache.get(key)
    
    if (!item) {
      return null
    }

    // 检查是否过期
    if (item.ttl && Date.now() - item.timestamp > item.ttl) {
      this.memoryCache.delete(key)
      return null
    }

    return item.data as T
  }

  /**
   * 删除缓存数据
   */
  delete(key: string): boolean {
    return this.memoryCache.delete(key)
  }

  /**
   * 清空所有缓存
   */
  clear(): void {
    this.memoryCache.clear()
  }

  /**
   * 检查缓存是否存在且有效
   */
  has(key: string): boolean {
    return this.get(key) !== null
  }

  /**
   * 设置localStorage缓存
   */
  setLocal<T>(key: string, data: T, ttl?: number): void {
    const item: CacheItem<T> = {
      data,
      timestamp: Date.now(),
      ttl: ttl || this.defaultTTL
    }
    
    try {
      localStorage.setItem(`cache_${key}`, JSON.stringify(item))
    } catch (error) {
      console.warn('LocalStorage cache set failed:', error)
    }
  }

  /**
   * 获取localStorage缓存
   */
  getLocal<T>(key: string): T | null {
    try {
      const stored = localStorage.getItem(`cache_${key}`)
      if (!stored) {
        return null
      }

      const item: CacheItem<T> = JSON.parse(stored)
      
      // 检查是否过期
      if (item.ttl && Date.now() - item.timestamp > item.ttl) {
        localStorage.removeItem(`cache_${key}`)
        return null
      }

      return item.data
    } catch (error) {
      console.warn('LocalStorage cache get failed:', error)
      return null
    }
  }

  /**
   * 删除localStorage缓存
   */
  deleteLocal(key: string): void {
    try {
      localStorage.removeItem(`cache_${key}`)
    } catch (error) {
      console.warn('LocalStorage cache delete failed:', error)
    }
  }

  /**
   * 缓存HTTP请求结果
   */
  async cacheRequest<T>(
    key: string, 
    requestFn: () => Promise<T>, 
    ttl?: number,
    useLocal = false
  ): Promise<T> {
    // 先检查缓存
    const cached = useLocal ? this.getLocal<T>(key) : this.get<T>(key)
    if (cached !== null) {
      return cached
    }

    // 缓存未命中，执行请求
    try {
      const result = await requestFn()
      
      // 缓存结果
      if (useLocal) {
        this.setLocal(key, result, ttl)
      } else {
        this.set(key, result, ttl)
      }
      
      return result
    } catch (error) {
      // 请求失败，不缓存
      throw error
    }
  }

  /**
   * 批量清理过期缓存
   */
  cleanup(): void {
    const now = Date.now()
    const toDelete: string[] = []

    for (const [key, item] of this.memoryCache.entries()) {
      if (item.ttl && now - item.timestamp > item.ttl) {
        toDelete.push(key)
      }
    }

    toDelete.forEach(key => this.memoryCache.delete(key))
  }
}

// 导出单例实例
export const cache = new DataCache()

// 预设的缓存键名常量
export const CACHE_KEYS = {
  CATEGORIES: 'categories',
  USER_CATEGORIES: 'user_categories',
  TAGS: 'tags',
  USER_PROFILE: 'user_profile',
  CODES_LIST: 'codes_list',
  CODE_DETAIL: (id: number) => `code_detail_${id}`,
  USER_CODES: 'user_codes',
  ADMIN_USERS: 'admin_users',
  ADMIN_CODES: 'admin_codes'
} as const

// 缓存时间常量
export const CACHE_TTL = {
  SHORT: 2 * 60 * 1000,      // 2分钟
  MEDIUM: 5 * 60 * 1000,     // 5分钟  
  LONG: 15 * 60 * 1000,      // 15分钟
  VERY_LONG: 60 * 60 * 1000  // 1小时
} as const

// 自动清理过期缓存
setInterval(() => {
  cache.cleanup()
}, 60 * 1000) // 每分钟清理一次
