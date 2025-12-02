<template>
  <div class="code-publish-container">
    <el-card shadow="hover" class="publish-card">
      <template #header>
        <div class="card-header">
          <span>发布代码</span>
        </div>
      </template>
      
      <el-form :model="publishForm" label-position="top" class="publish-form">
        <!-- 基本信息 -->
        <el-card shadow="hover" class="form-section">
          <template #header>
            <div class="section-header">基本信息</div>
          </template>
          
          <el-form-item label="标题" required>
            <el-input v-model="publishForm.title" placeholder="请输入代码标题" />
          </el-form-item>
          
          <el-form-item label="描述" required>
            <el-input
              v-model="publishForm.description"
              type="textarea"
              placeholder="请输入代码描述，包括功能、使用场景等"
              :rows="4"
            />
          </el-form-item>
          
          <el-form-item label="编程语言" required>
            <el-select v-model="publishForm.language" placeholder="请选择编程语言">
              <el-option label="Python" value="Python" />
              <el-option label="R" value="R" />
              <el-option label="Shell" value="Shell" />
            </el-select>
          </el-form-item>
          
          <el-form-item label="分类" required>
            <el-select v-model="publishForm.category_id" placeholder="请选择分类">
              <el-option
                v-for="category in categories"
                :key="category.id"
                :label="category.name"
                :value="category.id"
              />
            </el-select>
          </el-form-item>
          
          <el-form-item label="开源协议">
            <el-select v-model="publishForm.license" placeholder="请选择开源协议">
              <el-option label="MIT" value="MIT" />
              <el-option label="GPL-3.0" value="GPL-3.0" />
              <el-option label="Apache-2.0" value="Apache-2.0" />
              <el-option label="BSD-3-Clause" value="BSD-3-Clause" />
            </el-select>
          </el-form-item>
          
          <el-form-item label="标签">
            <el-select
              v-model="publishForm.tags"
              multiple
              placeholder="请选择或输入标签"
              filterable
              allow-create
            >
              <el-option
                v-for="tag in availableTags"
                :key="tag.id"
                :label="tag.name"
                :value="tag.name"
              />
            </el-select>
          </el-form-item>
        </el-card>
        
        <!-- 代码内容 -->
        <el-card shadow="hover" class="form-section">
          <template #header>
            <div class="section-header">代码内容</div>
          </template>
          
          <el-form-item required>
            <div v-loading="editorLoading" element-loading-text="编辑器加载中..." class="editor-wrapper">
              <div ref="editorContainer" class="editor"></div>
            </div>
          </el-form-item>
        </el-card>
        
        <!-- 环境配置 -->
        <el-card shadow="hover" class="form-section">
          <template #header>
            <div class="section-header">环境配置</div>
          </template>
          
          <el-form-item label="环境说明">
            <el-input
              v-model="publishForm.environment"
              type="textarea"
              placeholder="请输入环境配置，如Dockerfile片段、conda环境.yml文件或依赖列表"
              :rows="6"
            />
          </el-form-item>
        </el-card>
        
        <!-- 效果展示（可选） -->
        <el-card shadow="hover" class="form-section">
          <template #header>
            <div class="section-header">效果展示 <span class="optional-tag">(可选)</span></div>
          </template>
          
          <div class="results-section">
            <div v-for="(result, index) in publishForm.results" :key="index" class="result-item">
              <el-card shadow="hover">
                <div class="result-header">
                  <span>结果 {{ index + 1 }}</span>
                  <el-button type="danger" size="small" @click="removeResult(index)">
                    <el-icon><Delete /></el-icon> 删除
                  </el-button>
                </div>
                
                <el-form-item label="结果类型">
                  <el-select v-model="result.type" placeholder="请选择结果类型">
                    <el-option label="图片" value="image" />
                    <el-option label="文本" value="text" />
                    <el-option label="图表" value="chart" />
                    <el-option label="表格" value="table" />
                  </el-select>
                </el-form-item>
                
                <el-form-item label="结果描述">
                  <el-input v-model="result.description" placeholder="请输入结果描述" />
                </el-form-item>
                
                <el-form-item label="结果内容">
                  <!-- 图片结果 -->
                  <div v-if="result.type === 'image'" class="result-content-image">
                    <el-upload
                      v-model:file-list="result.fileList"
                      action="#"
                      list-type="picture-card"
                      :auto-upload="false"
                      :on-change="(file: any) => handleImageChange(index, file)"
                    >
                      <el-icon><Plus /></el-icon>
                    </el-upload>
                    <el-input
                      v-if="result.content"
                      v-model="result.content"
                      placeholder="图片URL"
                      readonly
                    />
                  </div>
                  
                  <!-- 文本结果 -->
                  <el-input
                    v-else-if="result.type === 'text'"
                    v-model="result.content"
                    type="textarea"
                    placeholder="请输入文本结果"
                    :rows="6"
                  />
                  
                  <!-- 图表结果 -->
                  <el-input
                    v-else-if="result.type === 'chart'"
                    v-model="result.content"
                    type="textarea"
                    placeholder="请输入图表JSON数据（ECharts配置）"
                    :rows="8"
                  />
                  
                  <!-- 表格结果 -->
                  <el-input
                    v-else-if="result.type === 'table'"
                    v-model="result.content"
                    type="textarea"
                    placeholder='请输入表格JSON数据，格式：{columns: [...], data: [...]} 或CSV内容'
                    :rows="8"
                  />
                </el-form-item>
              </el-card>
            </div>
            
            <el-button type="primary" @click="addResult">
              <el-icon><Plus /></el-icon> 添加结果
            </el-button>
          </div>
        </el-card>
        
        <!-- 提交按钮 -->
        <div class="form-actions">
          <el-button type="primary" @click="handleSubmit" :loading="submitting">
            发布代码
          </el-button>
          <el-button @click="handleCancel">取消</el-button>
        </div>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import { useRouter } from 'vue-router'
import { Delete, Plus } from '@element-plus/icons-vue'
import loader from '@monaco-editor/loader'
import axios from 'axios'
import { ElMessage } from 'element-plus'

// 配置 Monaco 编辑器 CDN 源
loader.config({
  paths: {
    vs: 'https://cdn.jsdelivr.net/npm/monaco-editor@0.45.0/min/vs'
  }
})

const router = useRouter()

// 发布表单
const publishForm = ref({
  title: '',
  description: '',
  content: '',
  language: 'Python',
  category_id: '',
  license: 'MIT',
  environment: '',
  tags: [] as string[],
  results: [
    {
      type: 'image',
      description: '',
      content: '',
      fileList: [] as any[]
    }
  ]
})

// 分类列表
const categories = ref<any[]>([])

// 可用标签
const availableTags = ref<any[]>([])

// 提交状态
const submitting = ref(false)

// 编辑器加载状态
const editorLoading = ref(true)

// Monaco编辑器实例
let editor: any = null
let monacoInstance: any = null
const editorContainer = ref<HTMLElement | null>(null)

// 添加结果
const addResult = () => {
  publishForm.value.results.push({
    type: 'image',
    description: '',
    content: '',
    fileList: [] as any[]
  })
}

// 删除结果
const removeResult = (index: number) => {
  publishForm.value.results.splice(index, 1)
}

// 处理图片上传
const handleImageChange = (index: number, uploadFile: any) => {
  // 这里可以实现图片上传到服务器的逻辑
  // 暂时使用本地URL
  if (uploadFile && uploadFile.raw) {
    const reader = new FileReader()
    reader.onload = (e) => {
      publishForm.value.results[index].content = e.target?.result as string
    }
    reader.readAsDataURL(uploadFile.raw)
  }
}

// 提交表单
const handleSubmit = async () => {
  if (!editor) return
  
  // 检查用户是否已登录
  const token = localStorage.getItem('token')
  if (!token) {
    ElMessage.error('请先登录')
    router.push('/login')
    return
  }
  
  // 获取编辑器内容
  publishForm.value.content = editor.getValue()
  
  // 验证表单
  if (!publishForm.value.title || !publishForm.value.description || !publishForm.value.content) {
    ElMessage.error('请填写必填字段')
    return
  }
  
  if (!publishForm.value.category_id) {
    ElMessage.error('请选择分类')
    return
  }
  
  // 效果展示为可选，但如果添加了则必须填写内容
  if (publishForm.value.results.length > 0) {
    const hasEmptyResult = publishForm.value.results.some(result => !result.content.trim())
    if (hasEmptyResult) {
      ElMessage.error('已添加的效果展示必须填写内容')
      return
    }
  }
  
  submitting.value = true
  
  try {
    // 准备提交数据，确保category_id是整数类型
    const submitData = {
      ...publishForm.value,
      category_id: parseInt(publishForm.value.category_id as string),
      results: publishForm.value.results.map(result => ({
        type: result.type,
        description: result.description,
        content: result.content
      }))
    }
    
    // 调用API发布代码
    const response = await axios.post('http://localhost:5001/api/codes', submitData, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    })
    
    ElMessage.success('代码发布成功')
    router.push(`/code/${response.data.id}`)
  } catch (error: any) {
    console.error('发布代码失败:', error)
    ElMessage.error(error.response?.data?.message || '发布代码失败')
  } finally {
    submitting.value = false
  }
}

// 取消发布
const handleCancel = () => {
  router.push('/')
}

// 初始化编辑器
const initEditor = async () => {
  if (editorContainer.value) {
    try {
      monacoInstance = await loader.init()
      editor = monacoInstance.editor.create(editorContainer.value, {
        value: publishForm.value.content,
        language: publishForm.value.language.toLowerCase(),
        theme: 'vs-dark',
        automaticLayout: true,
        minimap: {
          enabled: true
        },
        scrollBeyondLastLine: false,
        fontSize: 14,
        lineNumbers: 'on',
        folding: true
      })
      editorLoading.value = false
    } catch (error) {
      console.error('Monaco 编辑器加载失败:', error)
      editorLoading.value = false
      ElMessage.error('代码编辑器加载失败，请刷新页面重试')
    }
  } else {
    editorLoading.value = false
  }
}

// 销毁编辑器
const disposeEditor = () => {
  if (editor) {
    editor.dispose()
    editor = null
  }
}

// 获取分类列表
const fetchCategories = async () => {
  try {
    const response = await axios.get('http://localhost:5001/api/categories')
    categories.value = response.data
  } catch (error) {
    console.error('获取分类列表失败:', error)
  }
}

// 获取标签列表
const fetchTags = async () => {
  try {
    const response = await axios.get('http://localhost:5001/api/tags')
    availableTags.value = response.data
  } catch (error) {
    console.error('获取标签列表失败:', error)
  }
}

// 页面挂载时初始化
onMounted(async () => {
  fetchCategories()
  fetchTags()
  await initEditor()
})

// 组件卸载时销毁编辑器
onBeforeUnmount(() => {
  disposeEditor()
})
</script>

<style scoped>
.code-publish-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.publish-card {
  padding: 20px;
}

.card-header {
  font-size: 20px;
  font-weight: bold;
}

.publish-form {
  max-width: 100%;
}

.form-section {
  margin-bottom: 20px;
}

.section-header {
  font-size: 16px;
  font-weight: bold;
}

.optional-tag {
  font-size: 12px;
  font-weight: normal;
  color: #909399;
}

.editor-wrapper {
  width: 100%;
  min-height: 400px;
}

.editor {
  width: 100%;
  height: 400px;
  border: 1px solid #dcdfe6;
  border-radius: 5px;
}

.results-section {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.result-item {
  margin-bottom: 15px;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.result-content-image {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.form-actions {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-top: 20px;
}
</style>
