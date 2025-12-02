<template>
  <div class="main-layout">
    <!-- 顶部导航栏 -->
    <header class="navbar">
      <div class="navbar-left">
        <div class="logo" @click="goHome">
          <el-icon :size="28" color="#409EFF"><DataAnalysis /></el-icon>
          <span class="logo-text">生信代码分享平台</span>
        </div>
      </div>
      
      <div class="navbar-center">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索代码、标签、作者..."
          class="search-input"
          @keyup.enter="handleSearch"
          clearable
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
      </div>
      
      <div class="navbar-right">
        <el-button type="primary" @click="handlePublish" :icon="Plus">
          发布代码
        </el-button>
        
        <template v-if="isLoggedIn">
          <el-dropdown trigger="click" @command="handleUserCommand">
            <div class="user-avatar">
              <el-avatar :size="36" :icon="UserFilled" />
              <span class="username">{{ user?.username }}</span>
              <el-icon><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">
                  <el-icon><User /></el-icon> 个人中心
                </el-dropdown-item>
                <el-dropdown-item command="mycodes">
                  <el-icon><Document /></el-icon> 我的代码
                </el-dropdown-item>
                <el-dropdown-item command="favorites">
                  <el-icon><Star /></el-icon> 我的收藏
                </el-dropdown-item>
                <el-dropdown-item divided command="logout">
                  <el-icon><SwitchButton /></el-icon> 退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </template>
        <template v-else>
          <el-button text @click="goLogin">登录</el-button>
          <el-button type="primary" plain @click="goRegister">注册</el-button>
        </template>
      </div>
    </header>
    
    <div class="main-container">
      <!-- 侧边栏 -->
      <aside class="sidebar" :class="{ collapsed: sidebarCollapsed }">
        <div class="sidebar-toggle" @click="toggleSidebar">
          <el-icon v-if="sidebarCollapsed"><Expand /></el-icon>
          <el-icon v-else><Fold /></el-icon>
        </div>
        
        <!-- 用户信息卡片 -->
        <div class="user-card" v-if="!sidebarCollapsed">
          <template v-if="isLoggedIn">
            <div class="user-card-header">
              <el-avatar :size="56" :icon="UserFilled" class="user-card-avatar" />
              <div class="user-card-info">
                <div class="user-card-name">{{ user?.username }}</div>
                <div class="user-card-email">{{ user?.email }}</div>
              </div>
            </div>
            <div class="user-card-stats">
              <div class="stat-item">
                <div class="stat-value">{{ userStats.codes }}</div>
                <div class="stat-label">代码</div>
              </div>
              <div class="stat-item">
                <div class="stat-value">{{ userStats.likes }}</div>
                <div class="stat-label">获赞</div>
              </div>
              <div class="stat-item">
                <div class="stat-value">{{ userStats.favorites }}</div>
                <div class="stat-label">收藏</div>
              </div>
            </div>
          </template>
          <template v-else>
            <div class="user-card-guest">
              <el-icon :size="40" color="#909399"><UserFilled /></el-icon>
              <p>登录后查看更多功能</p>
              <el-button type="primary" size="small" @click="goLogin">立即登录</el-button>
            </div>
          </template>
        </div>
        
        <el-menu
          :default-active="activeMenu"
          :collapse="sidebarCollapsed"
          class="sidebar-menu"
          @select="handleMenuSelect"
        >
          <el-menu-item index="home">
            <el-icon><HomeFilled /></el-icon>
            <template #title>首页</template>
          </el-menu-item>
          
          <el-sub-menu index="categories">
            <template #title>
              <el-icon><Menu /></el-icon>
              <span>分类浏览</span>
            </template>
            <el-menu-item
              v-for="category in categories"
              :key="category.id"
              :index="`category-${category.id}`"
            >
              {{ category.name }}
            </el-menu-item>
          </el-sub-menu>
          
          <el-sub-menu index="languages">
            <template #title>
              <el-icon><EditPen /></el-icon>
              <span>编程语言</span>
            </template>
            <el-menu-item index="lang-python">
              <el-icon><Monitor /></el-icon> Python
            </el-menu-item>
            <el-menu-item index="lang-r">
              <el-icon><PieChart /></el-icon> R
            </el-menu-item>
            <el-menu-item index="lang-shell">
              <el-icon><Cpu /></el-icon> Shell
            </el-menu-item>
          </el-sub-menu>
          
          <el-menu-item index="hot">
            <el-icon><Histogram /></el-icon>
            <template #title>热门代码</template>
          </el-menu-item>
          
          <el-menu-item index="recent">
            <el-icon><Clock /></el-icon>
            <template #title>最新发布</template>
          </el-menu-item>
        </el-menu>
        
        <!-- 热门标签 -->
        <div class="sidebar-tags" v-if="!sidebarCollapsed">
          <div class="sidebar-section-title">热门标签</div>
          <div class="tags-list">
            <el-tag
              v-for="tag in hotTags"
              :key="tag.id"
              :type="tag.type"
              size="small"
              effect="plain"
              class="tag-item"
              @click="handleTagClick(tag.name)"
            >
              {{ tag.name }}
            </el-tag>
          </div>
        </div>
      </aside>
      
      <!-- 主内容区 -->
      <main class="main-content" :class="{ expanded: sidebarCollapsed }">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import {
  Search, Plus, UserFilled, ArrowDown, User, Document, Star,
  SwitchButton, HomeFilled, Menu, Histogram, Clock, Expand, Fold,
  DataAnalysis, Monitor, PieChart, Cpu, EditPen
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const router = useRouter()
const route = useRoute()

// 状态
const searchKeyword = ref('')
const sidebarCollapsed = ref(false)
const categories = ref<any[]>([])
const hotTags = ref([
  { id: 1, name: '单细胞分析', type: 'primary' },
  { id: 2, name: 'CNV检测', type: 'success' },
  { id: 3, name: 'RNA-seq', type: 'warning' },
  { id: 4, name: 'Seurat', type: 'danger' },
  { id: 5, name: 'Scanpy', type: 'info' },
  { id: 6, name: 'Python', type: 'primary' },
  { id: 7, name: 'R', type: 'success' },
])

// 用户统计数据
const userStats = ref({
  codes: 0,
  likes: 0,
  favorites: 0
})

// 计算属性
const isLoggedIn = computed(() => !!localStorage.getItem('token'))
const user = computed(() => {
  const userStr = localStorage.getItem('user')
  return userStr ? JSON.parse(userStr) : null
})
const activeMenu = computed(() => {
  if (route.path === '/') return 'home'
  if (route.path === '/publish') return 'publish'
  return 'home'
})

// 方法
const goHome = () => router.push('/')
const goLogin = () => router.push('/login')
const goRegister = () => router.push('/register')

const handlePublish = () => {
  if (!isLoggedIn.value) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }
  router.push('/publish')
}

const handleSearch = () => {
  router.push({ path: '/', query: { keyword: searchKeyword.value } })
}

const handleUserCommand = (command: string) => {
  switch (command) {
    case 'logout':
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      ElMessage.success('已退出登录')
      window.location.href = '/'
      break
    case 'profile':
      router.push('/profile')
      break
    case 'mycodes':
      router.push('/profile?tab=codes')
      break
    case 'favorites':
      router.push('/profile?tab=favorites')
      break
  }
}

const toggleSidebar = () => {
  sidebarCollapsed.value = !sidebarCollapsed.value
}

const handleMenuSelect = (index: string) => {
  if (index === 'home') {
    router.push('/')
  } else if (index.startsWith('category-')) {
    const categoryId = index.replace('category-', '')
    router.push({ path: '/', query: { category_id: categoryId } })
  } else if (index.startsWith('lang-')) {
    const lang = index.replace('lang-', '')
    const langMap: Record<string, string> = { python: 'Python', r: 'R', shell: 'Shell' }
    router.push({ path: '/', query: { language: langMap[lang] } })
  } else if (index === 'hot') {
    router.push({ path: '/', query: { sort: 'views' } })
  } else if (index === 'recent') {
    router.push({ path: '/', query: { sort: 'recent' } })
  }
}

const handleTagClick = (tagName: string) => {
  router.push({ path: '/', query: { keyword: tagName } })
}

// 获取分类
const fetchCategories = async () => {
  try {
    const response = await axios.get('http://localhost:5001/api/categories')
    categories.value = response.data
  } catch (error) {
    console.error('获取分类失败:', error)
  }
}

onMounted(() => {
  fetchCategories()
})
</script>

<style scoped>
.main-layout {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e8eb 100%);
}

/* 顶部导航栏 */
.navbar {
  height: 64px;
  background: linear-gradient(90deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.15);
}

.navbar-left {
  display: flex;
  align-items: center;
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  transition: opacity 0.3s;
}

.logo:hover {
  opacity: 0.85;
}

.logo-text {
  font-size: 20px;
  font-weight: 700;
  background: linear-gradient(90deg, #409EFF, #67C23A);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.navbar-center {
  flex: 1;
  max-width: 500px;
  margin: 0 40px;
}

.search-input {
  width: 100%;
}

.search-input :deep(.el-input__wrapper) {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 20px;
  box-shadow: none;
}

.search-input :deep(.el-input__wrapper):hover,
.search-input :deep(.el-input__wrapper.is-focus) {
  background: rgba(255, 255, 255, 0.15);
  border-color: #409EFF;
}

.search-input :deep(.el-input__inner) {
  color: #fff;
}

.search-input :deep(.el-input__inner::placeholder) {
  color: rgba(255, 255, 255, 0.6);
}

.search-input :deep(.el-input__prefix .el-icon) {
  color: rgba(255, 255, 255, 0.6);
}

.navbar-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.user-avatar {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 4px 12px;
  border-radius: 20px;
  transition: background 0.3s;
}

.user-avatar:hover {
  background: rgba(255, 255, 255, 0.1);
}

.username {
  color: #fff;
  font-size: 14px;
}

.user-avatar .el-icon {
  color: rgba(255, 255, 255, 0.8);
}

/* 主容器 */
.main-container {
  display: flex;
  margin-top: 64px;
  min-height: calc(100vh - 64px);
}

/* 侧边栏 */
.sidebar {
  width: 240px;
  background: #fff;
  position: fixed;
  top: 64px;
  left: 0;
  bottom: 0;
  overflow-y: auto;
  transition: width 0.3s;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.05);
  z-index: 100;
}

.sidebar.collapsed {
  width: 64px;
}

.sidebar-toggle {
  display: flex;
  justify-content: flex-end;
  padding: 12px 16px;
  cursor: pointer;
  color: #909399;
  transition: color 0.3s;
}

.sidebar-toggle:hover {
  color: #409EFF;
}

/* 用户信息卡片 */
.user-card {
  padding: 16px;
  border-bottom: 1px solid #f0f0f0;
}

.user-card-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.user-card-avatar {
  background: linear-gradient(135deg, #667eea, #764ba2);
}

.user-card-info {
  flex: 1;
  overflow: hidden;
}

.user-card-name {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.user-card-email {
  font-size: 12px;
  color: #909399;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.user-card-stats {
  display: flex;
  justify-content: space-around;
  background: #f5f7fa;
  border-radius: 8px;
  padding: 12px 0;
}

.user-card-stats .stat-item {
  text-align: center;
}

.user-card-stats .stat-value {
  font-size: 18px;
  font-weight: 700;
  color: #409EFF;
}

.user-card-stats .stat-label {
  font-size: 11px;
  color: #909399;
  margin-top: 2px;
}

.user-card-guest {
  text-align: center;
  padding: 16px 0;
}

.user-card-guest p {
  font-size: 13px;
  color: #909399;
  margin: 12px 0;
}

.sidebar-menu {
  border-right: none;
}

.sidebar-menu:not(.el-menu--collapse) {
  width: 240px;
}

.sidebar-tags {
  padding: 16px;
  border-top: 1px solid #f0f0f0;
  margin-top: 16px;
}

.sidebar-section-title {
  font-size: 12px;
  color: #909399;
  margin-bottom: 12px;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.tags-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag-item {
  cursor: pointer;
  transition: transform 0.2s;
}

.tag-item:hover {
  transform: scale(1.05);
}

/* 主内容区 */
.main-content {
  flex: 1;
  margin-left: 240px;
  padding: 24px;
  transition: margin-left 0.3s;
  min-height: calc(100vh - 64px);
}

.main-content.expanded {
  margin-left: 64px;
}

/* 响应式 */
@media (max-width: 768px) {
  .navbar-center {
    display: none;
  }
  
  .sidebar {
    width: 64px;
  }
  
  .sidebar.collapsed {
    width: 0;
  }
  
  .main-content {
    margin-left: 64px;
  }
  
  .main-content.expanded {
    margin-left: 0;
  }
}
</style>
