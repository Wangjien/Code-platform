<template>
  <div class="profile-container" v-loading="loading" element-loading-text="加载中...">
    <!-- 用户信息卡片 -->
    <el-card shadow="hover" class="profile-card">
      <div class="profile-header">
        <el-avatar :size="80" :icon="UserFilled" class="profile-avatar" />
        <div class="profile-info">
          <h2 class="profile-name">{{ user?.username }}</h2>
          <p class="profile-email">{{ user?.email }}</p>
          <p class="profile-join">加入时间：{{ formatDate(user?.created_at) }}</p>
        </div>
        <el-button type="primary" @click="showEditDialog = true">
          <el-icon><Edit /></el-icon> 编辑资料
        </el-button>
      </div>
      
      <div class="profile-stats">
        <div class="stat-item">
          <div class="stat-value">{{ userStats.codes }}</div>
          <div class="stat-label">发布代码</div>
        </div>
        <div class="stat-item">
          <div class="stat-value">{{ userStats.likes }}</div>
          <div class="stat-label">获得点赞</div>
        </div>
        <div class="stat-item">
          <div class="stat-value">{{ userStats.favorites }}</div>
          <div class="stat-label">收藏代码</div>
        </div>
        <div class="stat-item">
          <div class="stat-value">{{ userStats.views }}</div>
          <div class="stat-label">总浏览量</div>
        </div>
      </div>
    </el-card>
    
    <!-- 标签页切换 -->
    <el-card shadow="hover" class="content-card">
      <el-tabs v-model="activeTab" @tab-change="handleTabChange">
        <el-tab-pane label="我的代码" name="codes">
          <div class="codes-header" v-if="myCodes.length > 0">
            <el-dropdown @command="handleBatchExport">
              <el-button type="primary">
                <el-icon><Download /></el-icon> 批量导出 <el-icon><ArrowDown /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="source">源码文件打包 (.zip)</el-dropdown-item>
                  <el-dropdown-item command="markdown">Markdown格式 (.zip)</el-dropdown-item>
                  <el-dropdown-item command="json">JSON数据 (.zip)</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
            <span class="codes-count">共 {{ myCodes.length }} 个代码</span>
          </div>
          <div v-if="myCodes.length > 0" class="code-list">
            <el-card 
              v-for="code in myCodes" 
              :key="code.id" 
              shadow="hover" 
              class="code-item"
              @click="goToCode(code.id)"
            >
              <div class="code-item-header">
                <span class="code-title">{{ code.title }}</span>
                <el-tag :type="getLanguageType(code.language)" size="small">
                  {{ code.language }}
                </el-tag>
              </div>
              <p class="code-desc">{{ code.description }}</p>
              <div class="code-meta">
                <span><el-icon><View /></el-icon> {{ code.views || 0 }}</span>
                <span><el-icon><Star /></el-icon> {{ code.likes || 0 }}</span>
                <span>{{ formatDate(code.created_at) }}</span>
              </div>
              <div class="code-actions" @click.stop>
                <el-button size="small" type="primary" @click="editCode(code.id)">
                  <el-icon><Edit /></el-icon> 编辑
                </el-button>
                <el-button size="small" type="danger" @click="deleteCode(code.id)">
                  <el-icon><Delete /></el-icon> 删除
                </el-button>
              </div>
            </el-card>
          </div>
          <el-empty v-else description="暂无发布的代码">
            <el-button type="primary" @click="goPublish">发布第一个代码</el-button>
          </el-empty>
        </el-tab-pane>
        
        <el-tab-pane label="我的收藏" name="favorites">
          <div v-if="myFavorites.length > 0" class="code-list">
            <el-card 
              v-for="code in myFavorites" 
              :key="code.id" 
              shadow="hover" 
              class="code-item"
              @click="goToCode(code.id)"
            >
              <div class="code-item-header">
                <span class="code-title">{{ code.title }}</span>
                <el-tag :type="getLanguageType(code.language)" size="small">
                  {{ code.language }}
                </el-tag>
              </div>
              <p class="code-desc">{{ code.description }}</p>
              <div class="code-meta">
                <span>作者：{{ code.author_username }}</span>
                <span><el-icon><Star /></el-icon> {{ code.likes || 0 }}</span>
              </div>
            </el-card>
          </div>
          <el-empty v-else description="暂无收藏的代码" />
        </el-tab-pane>
        
        <el-tab-pane label="分类管理" name="categories">
          <UserCategoryManager />
        </el-tab-pane>
        
        <el-tab-pane label="账号设置" name="settings">
          <el-form :model="settingsForm" label-width="100px" class="settings-form">
            <el-form-item label="用户名">
              <el-input v-model="settingsForm.username" placeholder="请输入用户名" />
            </el-form-item>
            <el-form-item label="邮箱">
              <el-input v-model="settingsForm.email" placeholder="请输入邮箱" disabled />
            </el-form-item>
            <el-form-item label="个人简介">
              <el-input 
                v-model="settingsForm.bio" 
                type="textarea" 
                :rows="4"
                placeholder="介绍一下自己..." 
              />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="saveSettings">保存修改</el-button>
            </el-form-item>
            
            <el-divider content-position="left">修改密码</el-divider>
            
            <el-form-item label="当前密码">
              <el-input v-model="passwordForm.oldPassword" type="password" show-password />
            </el-form-item>
            <el-form-item label="新密码">
              <el-input v-model="passwordForm.newPassword" type="password" show-password />
            </el-form-item>
            <el-form-item label="确认密码">
              <el-input v-model="passwordForm.confirmPassword" type="password" show-password />
            </el-form-item>
            <el-form-item>
              <el-button type="warning" @click="changePassword">修改密码</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Star, UserFilled, Download, ArrowDown } from '@element-plus/icons-vue'
import { exportMultipleCodes, ExportFormat } from '../utils/export'
import { ElMessage, ElMessageBox } from 'element-plus'
import http, { useLoading } from '../utils/http'
import { API_CONFIG } from '../config/api'
import { validationRules, validateForm } from '../utils/validation'
import UserCategoryManager from '../components/UserCategoryManager.vue'

//======================================
// Profile View
//
// 个人中心：展示用户信息，并提供“我的代码/我的收藏/账号设置”。
// - 数据来源：localStorage(user) + 后端接口补充列表数据
// - Tab：codes/favorites/settings
// - 写操作：更新资料、修改密码、删除代码（都需要 token）
//
// 关键点：
// - 登录态：页面加载时若 user 不存在则跳转登录
// - 统计：通过 myCodes 聚合 likes/views 等数据
// - 后端对齐：/api/user/favorites 当前后端是空实现（如果要展示收藏需要改后端）
//======================================

const router = useRouter()
const { loading, withLoading } = useLoading()

// 用户信息
const user = computed(() => {
  const userStr = localStorage.getItem('user')
  return userStr ? JSON.parse(userStr) : null
})

// 用户统计
const userStats = ref({
  codes: 0,
  likes: 0,
  favorites: 0,
  views: 0
})

// 当前标签页
const activeTab = ref('codes')

// 我的代码
const myCodes = ref<any[]>([])

// 我的收藏
const myFavorites = ref<any[]>([])

// 编辑对话框
const showEditDialog = ref(false)

// 设置表单
const settingsForm = ref({
  username: '',
  email: '',
  bio: ''
})

// 密码表单
const passwordForm = ref({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

// 格式化日期
const formatDate = (dateString: string) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN')
}

// 获取语言标签类型
const getLanguageType = (language: string) => {
  const types: Record<string, string> = {
    'Python': 'primary',
    'R': 'success',
    'Shell': 'warning'
  }
  return types[language] || 'info'
}

// 获取我的代码
const fetchMyCodes = async () => {
  await withLoading(async () => {
    const response = await http.get(API_CONFIG.endpoints.userCodes)
    myCodes.value = response.data
    userStats.value.codes = myCodes.value.length
  })
}

// 获取我的收藏
const fetchMyFavorites = async () => {
  await withLoading(async () => {
    const response = await http.get(API_CONFIG.endpoints.userFavorites)
    myFavorites.value = response.data.favorites || response.data || []
  })
}

// 切换标签页
const handleTabChange = (tab: string) => {
  if (tab === 'codes') {
    fetchMyCodes()
  } else if (tab === 'favorites') {
    fetchMyFavorites()
  } else if (tab === 'settings') {
    settingsForm.value.username = user.value?.username || ''
    settingsForm.value.email = user.value?.email || ''
    settingsForm.value.bio = user.value?.bio || ''
  }
}

// 跳转到代码详情
const goToCode = (id: number) => {
  router.push(`/code/${id}`)
}

// 跳转到发布页
const goPublish = () => {
  router.push('/publish')
}

// 处理批量导出
const handleBatchExport = async (format: string) => {
  if (myCodes.value.length === 0) {
    ElMessage.warning('没有可导出的代码')
    return
  }

  try {
    let exportFormat: ExportFormat
    switch (format) {
      case 'source':
        exportFormat = ExportFormat.SOURCE
        break
      case 'markdown':
        exportFormat = ExportFormat.MARKDOWN
        break
      case 'json':
        exportFormat = ExportFormat.JSON
        break
      default:
        exportFormat = ExportFormat.SOURCE
    }

    await exportMultipleCodes(
      myCodes.value, 
      exportFormat, 
      `我的代码_${user.value?.username || 'user'}`
    )
  } catch (error) {
    console.error('批量导出失败:', error)
    ElMessage.error('批量导出失败，请重试')
  }
}

// 编辑代码
const editCode = (_id: number) => {
  ElMessage.info('编辑功能开发中...')
}

// 删除代码
const deleteCode = async (id: number) => {
  try {
    await ElMessageBox.confirm('确定要删除这个代码吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await http.delete(API_CONFIG.endpoints.codeDetail(id))
    ElMessage.success('删除成功')
    fetchMyCodes()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// 保存设置
const saveSettings = async () => {
  // 表单验证
  const settingsRules = {
    username: [validationRules.required('请输入用户名'), validationRules.username()],
    email: [validationRules.required('请输入邮箱'), validationRules.email()]
  }
  
  const { valid, errors } = validateForm(settingsForm.value, settingsRules)
  if (!valid) {
    const firstError = Object.values(errors)[0]
    ElMessage.warning(firstError)
    return
  }
  
  await withLoading(async () => {
    const response = await http.put(API_CONFIG.endpoints.userProfile, settingsForm.value)
    
    // 更新本地存储
    const updatedUser = { ...user.value, ...settingsForm.value }
    localStorage.setItem('user', JSON.stringify(updatedUser))
    
    ElMessage.success('保存成功')
  })
}

// 修改密码
const changePassword = async () => {
  // 表单验证
  const passwordRules = {
    oldPassword: [validationRules.required('请输入当前密码')],
    newPassword: [validationRules.required('请输入新密码'), validationRules.password()],
    confirmPassword: [validationRules.required('请确认密码')]
  }
  
  const { valid, errors } = validateForm(passwordForm.value, passwordRules)
  if (!valid) {
    const firstError = Object.values(errors)[0]
    ElMessage.warning(firstError)
    return
  }
  
  if (passwordForm.value.newPassword !== passwordForm.value.confirmPassword) {
    ElMessage.error('两次密码输入不一致')
    return
  }
  
  await withLoading(async () => {
    await http.put(API_CONFIG.endpoints.userPassword, {
      old_password: passwordForm.value.oldPassword,
      new_password: passwordForm.value.newPassword
    })
    
    ElMessage.success('密码修改成功')
    passwordForm.value = { oldPassword: '', newPassword: '', confirmPassword: '' }
  })
}

// 页面加载时获取数据
onMounted(() => {
  if (!user.value) {
    router.push('/login')
    return
  }
  fetchMyCodes()
  fetchMyFavorites()
})
</script>

<style scoped>
.profile-container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
}

.profile-card {
  margin-bottom: 20px;
}

.profile-header {
  display: flex;
  align-items: center;
  gap: 24px;
  padding-bottom: 20px;
  border-bottom: 1px solid #f0f0f0;
}

.profile-avatar {
  background: linear-gradient(135deg, #667eea, #764ba2);
}

.profile-info {
  flex: 1;
}

.profile-name {
  margin: 0 0 8px 0;
  font-size: 24px;
  font-weight: 600;
  color: #303133;
}

.profile-email {
  margin: 0 0 4px 0;
  color: #606266;
  font-size: 14px;
}

.profile-join {
  margin: 0;
  color: #909399;
  font-size: 13px;
}

.profile-stats {
  display: flex;
  justify-content: space-around;
  padding-top: 20px;
}

.stat-item {
  text-align: center;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #409eff;
}

.codes-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
}

.codes-count {
  color: #666;
  font-size: 14px;
}

.stat-label {
  font-size: 13px;
  color: #909399;
  margin-top: 4px;
}

.content-card {
  min-height: 400px;
}

.code-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.code-item {
  cursor: pointer;
  transition: all 0.3s;
}

.code-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.code-item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.code-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.code-desc {
  margin: 0 0 12px 0;
  color: #606266;
  font-size: 14px;
  line-height: 1.5;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  line-clamp: 2;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.code-meta {
  display: flex;
  gap: 16px;
  font-size: 13px;
  color: #909399;
  margin-bottom: 12px;
}

.code-meta span {
  display: flex;
  align-items: center;
  gap: 4px;
}

.code-actions {
  display: flex;
  gap: 8px;
}

.settings-form {
  max-width: 500px;
}
</style>
