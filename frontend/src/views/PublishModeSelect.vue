<template>
  <div class="mode-select-container">
    <div class="mode-select-card">
      <div class="header">
        <h2>选择发布模式</h2>
        <p>请选择最适合您内容的发布方式</p>
      </div>
      
      <div class="modes">
        <div class="mode-option" @click="selectMode('traditional')" :class="{ active: selectedMode === 'traditional' }">
          <div class="mode-icon">
            <el-icon size="48"><DocumentCopy /></el-icon>
          </div>
          <div class="mode-info">
            <h3>传统模式</h3>
            <p>代码与结果分离，支持多种结果类型</p>
            <ul>
              <li>代码编辑器</li>
              <li>多个结果展示（图片、表格、图表）</li>
              <li>标签和分类</li>
              <li>适合数据分析项目</li>
            </ul>
          </div>
        </div>

        <div class="mode-option" @click="selectMode('markdown')" :class="{ active: selectedMode === 'markdown' }">
          <div class="mode-icon">
            <el-icon size="48"><Document /></el-icon>
          </div>
          <div class="mode-info">
            <h3>Markdown模式</h3>
            <p>纯文档模式，代码和说明融为一体</p>
            <ul>
              <li>Markdown实时预览</li>
              <li>代码块语法高亮</li>
              <li>图文混排</li>
              <li>适合教程和文档</li>
            </ul>
          </div>
        </div>
      </div>

      <div class="actions">
        <el-button size="large" @click="goBack">取消</el-button>
        <el-button type="primary" size="large" @click="continuePublish" :disabled="!selectedMode">
          继续发布
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { Document, DocumentCopy } from '@element-plus/icons-vue'

const router = useRouter()
const selectedMode = ref<'traditional' | 'markdown' | null>(null)

const selectMode = (mode: 'traditional' | 'markdown') => {
  selectedMode.value = mode
}

const continuePublish = () => {
  if (selectedMode.value === 'traditional') {
    router.push('/publish/traditional')
  } else if (selectedMode.value === 'markdown') {
    router.push('/publish/markdown')
  }
}

const goBack = () => {
  router.push('/')
}
</script>

<style scoped>
.mode-select-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.mode-select-card {
  background: white;
  border-radius: 16px;
  padding: 40px;
  max-width: 800px;
  width: 100%;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
}

.header {
  text-align: center;
  margin-bottom: 40px;
}

.header h2 {
  font-size: 28px;
  color: #2c3e50;
  margin-bottom: 12px;
  font-weight: 600;
}

.header p {
  color: #7f8c8d;
  font-size: 16px;
}

.modes {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  margin-bottom: 40px;
}

.mode-option {
  border: 2px solid #e1e8ed;
  border-radius: 12px;
  padding: 30px 24px;
  cursor: pointer;
  transition: all 0.3s ease;
  background: #fafbfc;
}

.mode-option:hover {
  border-color: #3498db;
  background: #f8fbff;
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(52, 152, 219, 0.15);
}

.mode-option.active {
  border-color: #3498db;
  background: linear-gradient(135deg, #3498db, #2980b9);
  color: white;
}

.mode-option.active .mode-info h3,
.mode-option.active .mode-info p,
.mode-option.active .mode-info li {
  color: white;
}

.mode-icon {
  text-align: center;
  margin-bottom: 20px;
  color: #3498db;
}

.mode-option.active .mode-icon {
  color: white;
}

.mode-info h3 {
  font-size: 20px;
  font-weight: 600;
  margin-bottom: 12px;
  color: #2c3e50;
}

.mode-info p {
  color: #7f8c8d;
  margin-bottom: 16px;
  font-size: 14px;
}

.mode-info ul {
  list-style: none;
  padding: 0;
}

.mode-info li {
  color: #5a6c7d;
  font-size: 13px;
  padding: 4px 0;
  position: relative;
  padding-left: 16px;
}

.mode-info li::before {
  content: "✓";
  position: absolute;
  left: 0;
  color: #27ae60;
  font-weight: 600;
}

.mode-option.active .mode-info li::before {
  color: #a8e6cf;
}

.actions {
  display: flex;
  justify-content: center;
  gap: 20px;
}

.actions .el-button {
  min-width: 120px;
}

/* 移动端适配 */
@media (max-width: 768px) {
  .mode-select-card {
    padding: 24px;
    margin: 10px;
  }
  
  .modes {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .mode-option {
    padding: 20px 16px;
  }
  
  .header h2 {
    font-size: 24px;
  }
  
  .actions {
    flex-direction: column;
  }
  
  .actions .el-button {
    width: 100%;
  }
}
</style>
