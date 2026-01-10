<template>
  <div class="login-page">
    <div class="login-left">
      <div class="brand">
        <div class="brand-logo">
          <el-icon :size="48" color="#fff"><DataAnalysis /></el-icon>
        </div>
        <h1 class="brand-title">生信代码分享平台</h1>
        <p class="brand-subtitle">发现、学习、分享生物信息学分析代码</p>
      </div>
    </div>
    
    <div class="login-right">
      <div class="login-card">
        <h2 class="login-title">欢迎回来</h2>
        <p class="login-subtitle">登录您的账号继续</p>
        
        <el-form :model="loginForm" class="login-form" @submit.prevent="handleLogin">
          <el-form-item>
            <el-input
              v-model="loginForm.email"
              type="email"
              placeholder="请输入邮箱"
              size="large"
              :prefix-icon="Message"
            />
          </el-form-item>
          
          <el-form-item>
            <el-input
              v-model="loginForm.password"
              type="password"
              placeholder="请输入密码"
              size="large"
              :prefix-icon="Lock"
              show-password
            />
          </el-form-item>
          
          <el-form-item>
            <el-button type="primary" class="login-button" size="large" @click="handleLogin" :loading="loading">
              登录
            </el-button>
          </el-form-item>
        </el-form>
        
        <div class="login-footer">
          <span>还没有账号？</span>
          <el-button type="primary" link @click="handleRegister">立即注册</el-button>
        </div>
        
        <div class="back-home">
          <el-button type="info" link @click="goHome">
            <el-icon><ArrowLeft /></el-icon> 返回首页
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { Message, Lock, DataAnalysis, ArrowLeft } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import http, { useLoading } from '../utils/http'
import { API_CONFIG } from '../config/api'
import { validationRules, validateForm } from '../utils/validation'

//======================================
// Login View
//
// 登录页：提交邮箱+密码到后端获取 JWT。
// - 成功后将 token 与 user 写入 localStorage
// - 然后跳转到首页
//
// 关键点：
// - 接口：POST /api/login
// - 登录态存储：localStorage(token/user)
// - UI loading：避免重复提交
//
// 注意：
// - localStorage 存储 token 有 XSS 风险（前端需保证不引入不可信脚本）。
//   真正安全边界仍在后端 JWT 校验。
//======================================

const router = useRouter()
const { loading, withLoading } = useLoading()

// 登录表单
const loginForm = ref({
  email: '',
  password: ''
})

// 表单验证规则
const loginRules = {
  email: [validationRules.required('请输入邮箱'), validationRules.email()],
  password: [validationRules.required('请输入密码'), validationRules.minLength(6)]
}

// 处理登录
const handleLogin = async () => {
  // 表单验证
  const { valid, errors } = validateForm(loginForm.value, loginRules)
  if (!valid) {
    const firstError = Object.values(errors)[0]
    ElMessage.warning(firstError)
    return
  }
  
  await withLoading(async () => {
    const response = await http.post(API_CONFIG.endpoints.login, loginForm.value)
    
    // 保存token和用户信息
    localStorage.setItem('token', response.data.access_token)
    localStorage.setItem('user', JSON.stringify(response.data.user))
    
    ElMessage.success('登录成功')
    router.push('/')
  })
}

// 跳转到注册页面
const handleRegister = () => {
  router.push('/register')
}

// 返回首页
const goHome = () => {
  router.push('/')
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
}

.login-left {
  flex: 1;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 60px;
  color: #fff;
}

.brand {
  text-align: center;
  margin-bottom: 60px;
}

.brand-logo {
  width: 80px;
  height: 80px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 24px;
  box-shadow: 0 10px 40px rgba(102, 126, 234, 0.4);
}

.brand-title {
  font-size: 28px;
  font-weight: 700;
  margin: 0 0 12px 0;
  background: linear-gradient(90deg, #fff, #a5b4fc);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.brand-subtitle {
  font-size: 14px;
  opacity: 0.8;
  margin: 0;
}

.features {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 24px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  backdrop-filter: blur(10px);
  font-size: 14px;
}

.login-right {
  width: 480px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 60px;
  background: #f5f7fa;
}

.login-card {
  width: 100%;
  max-width: 360px;
}

.login-title {
  font-size: 28px;
  font-weight: 700;
  color: #1a1a2e;
  margin: 0 0 8px 0;
}

.login-subtitle {
  font-size: 14px;
  color: #909399;
  margin: 0 0 32px 0;
}

.login-form {
  margin-bottom: 24px;
}

.login-form :deep(.el-input__wrapper) {
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.login-button {
  width: 100%;
  border-radius: 10px;
  font-weight: 600;
}

.login-footer {
  text-align: center;
  font-size: 14px;
  color: #606266;
}

.back-home {
  text-align: center;
  margin-top: 24px;
}

/* 响应式 */
@media (max-width: 900px) {
  .login-left {
    display: none;
  }
  
  .login-right {
    width: 100%;
  }
}
</style>
