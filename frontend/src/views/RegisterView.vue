<template>
  <div class="register-page">
    <div class="register-left">
      <div class="brand">
        <div class="brand-logo">
          <el-icon :size="48" color="#fff"><DataAnalysis /></el-icon>
        </div>
        <h1 class="brand-title">生信代码分享平台</h1>
        <p class="brand-subtitle">加入我们，开启生信代码分享之旅</p>
      </div>
    </div>
    
    <div class="register-right">
      <div class="register-card">
        <h2 class="register-title">创建账号</h2>
        <p class="register-subtitle">填写以下信息完成注册</p>
        
        <el-form :model="registerForm" class="register-form" @submit.prevent="handleRegister">
          <el-form-item>
            <el-input
              v-model="registerForm.username"
              placeholder="请输入用户名"
              size="large"
              :prefix-icon="User"
            />
          </el-form-item>
          
          <el-form-item>
            <el-input
              v-model="registerForm.email"
              type="email"
              placeholder="请输入邮箱"
              size="large"
              :prefix-icon="Message"
            />
          </el-form-item>
          
          <el-form-item>
            <el-input
              v-model="registerForm.password"
              type="password"
              placeholder="请输入密码（至少6位）"
              size="large"
              :prefix-icon="Lock"
              show-password
            />
          </el-form-item>
          
          <el-form-item>
            <el-input
              v-model="registerForm.confirmPassword"
              type="password"
              placeholder="请确认密码"
              size="large"
              :prefix-icon="Lock"
              show-password
            />
          </el-form-item>
          
          <el-form-item>
            <el-button type="primary" class="register-button" size="large" @click="handleRegister" :loading="loading">
              立即注册
            </el-button>
          </el-form-item>
        </el-form>
        
        <div class="register-footer">
          <span>已有账号？</span>
          <el-button type="primary" link @click="handleLogin">立即登录</el-button>
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
import { User, Message, Lock, DataAnalysis, ArrowLeft } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import http, { useLoading } from '../utils/http'
import { API_CONFIG } from '../config/api'
import { validationRules, validateForm } from '../utils/validation'

//======================================
// Register View
//
// 注册页：创建新用户。
// - 前端做基础校验（必填、两次密码一致、最小长度）
// - 通过后端接口创建用户
// - 成功后跳转登录页
//
// 关键点：
// - 接口：POST /api/register
// - UI loading：避免重复提交
// - 注册成功不自动登录（当前逻辑是提示后跳登录）
//======================================

const router = useRouter()
const { loading, withLoading } = useLoading()

// 注册表单
const registerForm = ref({
  username: '',
  email: '',
  password: '',
  confirmPassword: ''
})

// 表单验证规则
const registerRules = {
  username: [validationRules.required('请输入用户名'), validationRules.username()],
  email: [validationRules.required('请输入邮箱'), validationRules.email()],
  password: [validationRules.required('请输入密码'), validationRules.password()],
  confirmPassword: [validationRules.required('请确认密码')]
}

// 处理注册
const handleRegister = async () => {
  // 表单验证
  const { valid, errors } = validateForm(registerForm.value, registerRules)
  if (!valid) {
    const firstError = Object.values(errors)[0]
    ElMessage.warning(firstError)
    return
  }
  
  // 密码一致性校验
  if (registerForm.value.password !== registerForm.value.confirmPassword) {
    ElMessage.warning('两次输入的密码不一致')
    return
  }
  
  await withLoading(async () => {
    await http.post(API_CONFIG.endpoints.register, {
      username: registerForm.value.username,
      email: registerForm.value.email,
      password: registerForm.value.password
    })
    
    ElMessage.success('注册成功，请登录')
    router.push('/login')
  })
}

// 跳转到登录页面
const handleLogin = () => {
  router.push('/login')
}

// 返回首页
const goHome = () => {
  router.push('/')
}
</script>

<style scoped>
.register-page {
  min-height: 100vh;
  display: flex;
}

.register-left {
  flex: 1;
  background: linear-gradient(135deg, #0f3460 0%, #16213e 50%, #1a1a2e 100%);
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
  background: linear-gradient(135deg, #764ba2, #667eea);
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 24px;
  box-shadow: 0 10px 40px rgba(118, 75, 162, 0.4);
}

.brand-title {
  font-size: 28px;
  font-weight: 700;
  margin: 0 0 12px 0;
  background: linear-gradient(90deg, #a5b4fc, #fff);
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

.register-right {
  width: 480px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 60px;
  background: #f5f7fa;
}

.register-card {
  width: 100%;
  max-width: 360px;
}

.register-title {
  font-size: 28px;
  font-weight: 700;
  color: #1a1a2e;
  margin: 0 0 8px 0;
}

.register-subtitle {
  font-size: 14px;
  color: #909399;
  margin: 0 0 32px 0;
}

.register-form {
  margin-bottom: 24px;
}

.register-form :deep(.el-input__wrapper) {
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.register-button {
  width: 100%;
  border-radius: 10px;
  font-weight: 600;
}

.register-footer {
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
  .register-left {
    display: none;
  }
  
  .register-right {
    width: 100%;
  }
}
</style>
