<template>
  <div class="home-container" v-loading="loading" element-loading-text="加载中...">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">探索生信代码</h1>
        <p class="page-subtitle">发现、学习、分享生物信息学分析代码</p>
      </div>
      <div class="header-stats">
        <div class="stat-item">
          <div class="stat-value">{{ pagination.total }}</div>
          <div class="stat-label">代码片段</div>
        </div>
        <div class="stat-item">
          <div class="stat-value">{{ categories.length }}</div>
          <div class="stat-label">分析类型</div>
        </div>
        <div class="stat-item">
          <div class="stat-value">3</div>
          <div class="stat-label">编程语言</div>
        </div>
      </div>
    </div>
    
    <!-- 筛选栏 -->
    <div class="filter-bar">
      <div class="filter-left">
        <el-button 
          type="primary" 
          @click="clearAllFilters"
          v-if="hasActiveFilters"
          class="clear-filters-btn"
          size="small"
        >
          <el-icon><RefreshLeft /></el-icon>
          清空筛选
        </el-button>
        
        <el-select v-model="searchForm.language" placeholder="编程语言" clearable class="filter-select" @change="handleSearch">
          <el-option label="Python" value="Python">
            <span class="lang-option"><span class="lang-dot python"></span>Python</span>
          </el-option>
          <el-option label="R" value="R">
            <span class="lang-option"><span class="lang-dot r"></span>R</span>
          </el-option>
          <el-option label="Shell" value="Shell">
            <span class="lang-option"><span class="lang-dot shell"></span>Shell</span>
          </el-option>
        </el-select>
        
        <el-select v-model="searchForm.category_id" placeholder="分析类型" clearable class="filter-select" @change="handleSearch">
          <el-option
            v-for="category in categories"
            :key="category.id"
            :label="category.name"
            :value="category.id"
          />
        </el-select>
        
        <el-select 
          v-model="searchForm.user_category_id" 
          placeholder="个人分类" 
          clearable 
          class="filter-select" 
          @change="handleSearch"
          v-if="userCategories.length > 0"
        >
          <el-option
            v-for="category in userCategories"
            :key="category.id"
            :label="category.name"
            :value="category.id"
          >
            <span :style="{ color: category.color }">{{ category.name }}</span>
          </el-option>
        </el-select>
        
        <el-button-group class="sort-buttons">
          <el-button :type="sortBy === 'recent' ? 'primary' : 'default'" @click="setSortBy('recent')">
            <el-icon><Clock /></el-icon> 最新
          </el-button>
          <el-button :type="sortBy === 'views' ? 'primary' : 'default'" @click="setSortBy('views')">
            <el-icon><View /></el-icon> 最热
          </el-button>
          <el-button :type="sortBy === 'likes' ? 'primary' : 'default'" @click="setSortBy('likes')">
            <el-icon><Star /></el-icon> 最赞
          </el-button>
        </el-button-group>
      </div>
      
      <div class="filter-right">
        <span class="result-count">共 {{ pagination.total }} 个结果</span>
      </div>
    </div>
    
    <!-- 代码列表 -->
    <div class="code-grid" v-if="codes.length > 0">
      <div class="code-card" v-for="code in codes" :key="code.id" @click="handleCodeClick(code.id)">
        <div class="card-header">
          <div class="lang-badge" :class="code.language.toLowerCase()">
            {{ code.language }}
          </div>
          <div class="card-actions">
            <el-tooltip content="浏览量">
              <span class="action-item"><el-icon><View /></el-icon> {{ code.views }}</span>
            </el-tooltip>
            <el-tooltip content="点赞数">
              <span class="action-item"><el-icon><Star /></el-icon> {{ code.likes }}</span>
            </el-tooltip>
          </div>
        </div>
        
        <h3 class="card-title">{{ code.title }}</h3>
        <p class="card-description">{{ code.description }}</p>
        
        <div class="card-tags">
          <el-tag 
            v-for="tag in code.tags.slice(0, 3)" 
            :key="tag" 
            size="small" 
            effect="plain"
            class="code-tag"
          >
            {{ tag }}
          </el-tag>
          <el-tag v-if="code.tags.length > 3" size="small" type="info" effect="plain">
            +{{ code.tags.length - 3 }}
          </el-tag>
        </div>
        
        <div class="card-footer">
          <div class="author-info">
            <el-avatar :size="24" :icon="UserFilled" class="author-avatar" />
            <span class="author-name">{{ code.author_username }}</span>
          </div>
          <div class="card-meta">
            <el-tag size="small" type="success" effect="light">{{ code.category?.name || '未分类' }}</el-tag>
            <span class="card-date">{{ formatDate(code.created_at) }}</span>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 空状态 -->
    <div class="empty-state" v-else>
      <el-empty description="暂无代码，快来发布第一个吧！">
        <el-button type="primary" @click="handlePublish">发布代码</el-button>
      </el-empty>
    </div>
    
    <!-- 分页 -->
    <div class="pagination" v-if="pagination.total > 0">
      <el-pagination
        v-model:current-page="pagination.current_page"
        v-model:page-size="pagination.per_page"
        :page-sizes="[12, 24, 48]"
        layout="total, sizes, prev, pager, next"
        :total="pagination.total"
        background
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import http, { useLoading } from '../utils/http'
import { API_CONFIG } from '../config/api'
import { cache, CACHE_KEYS, CACHE_TTL } from '../utils/cache'
import { debounce } from '../utils/ui-helpers'
import { Star, View, Clock, RefreshLeft, UserFilled } from '@element-plus/icons-vue'

//======================================
// Home View
//
// 首页：代码列表浏览与筛选。
// - 支持分页：page/per_page
// - 支持筛选：language/category_id
// - 支持排序：recent/views/likes
// - 通过路由 query 与筛选表单双向同步
//
// 关键点：
// - 数据来源：后端 /api/codes、/api/categories
// - 交互：筛选变化/分页变化会触发 fetchCodes
// - 路由：MainLayout 的菜单/搜索会通过 query 驱动本页筛选
//
// 注意：
// - 当前 axios 地址写死 localhost（建议后续抽到统一 api client）
// - sort 参数在此文件中用于前端控制，但后端是否支持需要对应实现
//======================================

const route = useRoute()
const router = useRouter()
const { loading, withLoading } = useLoading()

// 搜索表单
const searchForm = ref({
  keyword: '',
  language: '',
  category_id: '',
  user_category_id: ''
})

// 排序方式
const sortBy = ref('recent')

// 响应式数据
const codes = ref<any[]>([])
const categories = ref<any[]>([])
const userCategories = ref<any[]>([])
const pagination = ref({
  current_page: 1,
  per_page: 10,
  total: 0,
  pages: 0
})

// 格式化日期
const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  
  if (days === 0) return '今天'
  if (days === 1) return '昨天'
  if (days < 7) return `${days}天前`
  if (days < 30) return `${Math.floor(days / 7)}周前`
  return date.toLocaleDateString()
}

// 防抖搜索功能
const debouncedSearch = debounce(() => {
  pagination.value.current_page = 1
  fetchCodes()
}, 500)

// 设置排序方式
const setSortBy = (sort: string) => {
  sortBy.value = sort
  fetchCodes()
}

// 判断是否有激活的筛选条件
const hasActiveFilters = computed(() => {
  return searchForm.value.keyword || 
         searchForm.value.language || 
         searchForm.value.category_id || 
         searchForm.value.user_category_id
})

// 清空所有筛选条件
const clearAllFilters = () => {
  searchForm.value.keyword = ''
  searchForm.value.language = ''
  searchForm.value.category_id = ''
  searchForm.value.user_category_id = ''
  pagination.value.current_page = 1
  fetchCodes()
}

// 处理搜索
const handleSearch = () => {
  pagination.value.current_page = 1
  fetchCodes()
}

// 处理代码点击
const handleCodeClick = (codeId: number) => {
  router.push(`/code/${codeId}`)
}

// 处理发布代码
const handlePublish = () => {
  router.push('/publish')
}

// 处理分页大小变化
const handleSizeChange = (size: number) => {
  pagination.value.per_page = size
  fetchCodes()
}

// 处理当前页变化
const handleCurrentChange = (page: number) => {
  pagination.value.current_page = page
  fetchCodes()
}

// 获取分类列表 (带缓存)
const fetchCategories = async () => {
  await withLoading(async () => {
    const cachedCategories = await cache.cacheRequest(
      CACHE_KEYS.CATEGORIES,
      () => http.get(API_CONFIG.endpoints.categories).then(res => res.data),
      CACHE_TTL.LONG // 分类数据缓存15分钟
    )
    categories.value = cachedCategories
  })
}

// 获取用户自定义分类列表 (带缓存)
const fetchUserCategories = async () => {
  try {
    const token = localStorage.getItem('token')
    if (!token) return // 未登录用户跳过
    
    const cachedUserCategories = await cache.cacheRequest(
      CACHE_KEYS.USER_CATEGORIES,
      () => http.get(API_CONFIG.endpoints.userCategories).then(res => res.data),
      CACHE_TTL.MEDIUM // 用户分类缓存5分钟
    )
    userCategories.value = cachedUserCategories
  } catch (error) {
    // 静默失败，用户分类是可选功能
    console.log('获取用户分类列表失败:', error)
  }
}

// 获取代码列表
const fetchCodes = async () => {
  await withLoading(async () => {
    // 组装分页 + 筛选参数（与后端 CodeList.get 对齐）
    const params: any = {
      page: pagination.value.current_page,
      per_page: pagination.value.per_page,
    }
    
    if (searchForm.value.keyword) params.keyword = searchForm.value.keyword
    if (searchForm.value.language) params.language = searchForm.value.language
    if (searchForm.value.category_id) params.category_id = searchForm.value.category_id
    if (searchForm.value.user_category_id) params.user_category_id = searchForm.value.user_category_id
    
    const response = await http.get(API_CONFIG.endpoints.codes, { params })
    codes.value = response.data.codes
    pagination.value.total = response.data.total
    pagination.value.pages = response.data.pages
  })
}

// 监听路由查询参数变化
watch(() => route.query, (query) => {
  // 将 query 映射到表单，再触发拉取
  if (query.keyword) searchForm.value.keyword = query.keyword as string
  if (query.language) searchForm.value.language = query.language as string
  if (query.category_id) searchForm.value.category_id = query.category_id as string
  fetchCodes()
}, { immediate: true })

// 页面挂载时获取数据
onMounted(() => {
  fetchCategories()
  fetchUserCategories()  // 获取用户自定义分类
})
</script>

<style scoped>
.home-container {
  max-width: 100%;
}

/* 页面头部 */
.page-header {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  border-radius: 16px;
  padding: 32px;
  margin-bottom: 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: #fff;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
}

.page-title {
  margin: 0 0 8px 0;
  font-size: 28px;
  font-weight: 700;
}

.page-subtitle {
  margin: 0;
  opacity: 0.9;
  font-size: 14px;
}

.header-stats {
  display: flex;
  gap: 40px;
}

.stat-item {
  text-align: center;
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
}

.stat-label {
  font-size: 12px;
  opacity: 0.8;
  margin-top: 4px;
}

/* 筛选栏 */
.filter-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding: 16px 20px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
}

.filter-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.filter-select {
  width: 140px;
}

.lang-option {
  display: flex;
  align-items: center;
  gap: 8px;
}

.lang-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.lang-dot.python { background: #3776AB; }
.lang-dot.r { background: #276DC3; }
.lang-dot.shell { background: #4EAA25; }

.sort-buttons {
  margin-left: 8px;
}

.result-count {
  color: #909399;
  font-size: 14px;
}

/* 代码卡片网格 */
.code-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}

.code-card {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
  border: 1px solid transparent;
}

.code-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.1);
  border-color: #409EFF;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.lang-badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  color: #fff;
}

.lang-badge.python { background: linear-gradient(135deg, #3776AB, #FFD43B); }
.lang-badge.r { background: linear-gradient(135deg, #276DC3, #75AADB); }
.lang-badge.shell { background: linear-gradient(135deg, #4EAA25, #89D654); }

.card-actions {
  display: flex;
  gap: 12px;
}

.action-item {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #909399;
  font-size: 13px;
}

.card-title {
  margin: 0 0 8px 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-description {
  margin: 0 0 12px 0;
  font-size: 13px;
  color: #606266;
  line-height: 1.6;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 16px;
}

.code-tag {
  background: #f4f4f5;
  border: none;
  color: #606266;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 12px;
  border-top: 1px solid #f0f0f0;
}

.author-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.author-avatar {
  background: linear-gradient(135deg, #667eea, #764ba2);
}

.author-name {
  font-size: 13px;
  color: #606266;
}

.card-meta {
  display: flex;
  align-items: center;
  gap: 8px;
}

.card-date {
  font-size: 12px;
  color: #909399;
}

/* 空状态 */
.empty-state {
  padding: 60px 0;
  background: #fff;
  border-radius: 12px;
}

/* 分页 */
.pagination {
  display: flex;
  justify-content: center;
  padding: 24px 0;
}

/* 响应式 */
@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    text-align: center;
    gap: 20px;
  }
  
  .header-stats {
    gap: 24px;
  }
  
  .filter-bar {
    flex-direction: column;
    gap: 12px;
  }
  
  .filter-left {
    flex-wrap: wrap;
    justify-content: center;
  }
  
  .code-grid {
    grid-template-columns: 1fr;
  }
}
</style>
