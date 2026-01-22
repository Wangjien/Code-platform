<template>
  <div class="markdown-publish-container">
    <el-card class="publish-card">
      <div class="card-header">
        <h2>Markdown文档发布</h2>
        <p>创建包含代码和说明的一体化文档</p>
      </div>

      <el-form :model="publishForm" label-width="120px" class="publish-form">
        <!-- 基本信息 -->
        <div class="form-section">
          <h3>基本信息</h3>
          
          <el-form-item label="文档标题" required>
            <el-input v-model="publishForm.title" placeholder="请输入文档标题" />
          </el-form-item>
          
          <el-form-item label="简短描述" required>
            <el-input
              v-model="publishForm.description"
              type="textarea"
              :rows="2"
              placeholder="简要描述这篇文档的内容"
            />
          </el-form-item>
          
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="主要语言">
                <el-select v-model="publishForm.language" placeholder="选择主要编程语言">
                  <el-option label="Python" value="Python" />
                  <el-option label="R" value="R" />
                  <el-option label="Shell" value="Shell" />
                  <el-option label="Perl" value="Perl" />
                  <el-option label="Rust" value="Rust" />
                  <el-option label="MATLAB" value="MATLAB" />
                  <el-option label="Julia" value="Julia" />
                  <el-option label="Nextflow" value="Nextflow" />
                  <el-option label="Snakemake" value="Snakemake" />
                  <el-option label="WDL" value="WDL" />
                  <el-option label="AWK" value="AWK" />
                  <el-option label="JavaScript" value="JavaScript" />
                  <el-option label="Java" value="Java" />
                  <el-option label="其他" value="Other" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="分类">
                <el-select v-model="publishForm.category_id" placeholder="选择分类">
                  <el-option
                    v-for="category in categories"
                    :key="category.id"
                    :label="category.name"
                    :value="category.id"
                  />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
          
          <el-form-item label="标签">
            <el-input
              v-model="tagInput"
              placeholder="输入标签，按Enter添加"
              @keyup.enter="addTag"
            />
            <div class="tags-display" v-if="publishForm.tags.length > 0">
              <el-tag
                v-for="(tag, index) in publishForm.tags"
                :key="index"
                closable
                @close="removeTag(index)"
                style="margin: 4px 8px 4px 0"
              >
                {{ tag }}
              </el-tag>
            </div>
          </el-form-item>
        </div>

        <!-- Markdown内容编辑 -->
        <div class="form-section">
          <h3>文档内容</h3>
          <div class="markdown-editor">
            <el-tabs type="border-card" v-model="activeTab">
              <el-tab-pane label="编辑" name="edit">
                <div class="markdown-editor-container">
                  <el-input
                    ref="markdownEditor"
                    v-model="publishForm.content"
                    type="textarea"
                    :rows="20"
                    class="markdown-textarea"
                    placeholder="使用Markdown语法编写您的文档...
支持直接粘贴图片 (Ctrl+V) 或拖拽图片到此处

# 示例格式

## 项目描述
这里描述您的项目目标和背景

## 代码实现

```python
# 您的代码
import pandas as pd
df = pd.read_csv('data.csv')
print(df.head())
```

## 运行结果
这里描述代码的运行结果

## 总结
项目的总结和后续计划"
                  />
                  <div class="markdown-editor-hint" v-if="!publishForm.content">
                    <div class="hint-icon">EDIT</div>
                    <div class="hint-text">
                      <p><strong>支持功能：</strong></p>
                      <ul>
                        <li>直接粘贴图片 (Ctrl+V)</li>
                        <li>拖拽图片文件</li>
                        <li>Mermaid图表</li>
                        <li>数学公式 (LaTeX)</li>
                        <li>提示框 [!NOTE]</li>
                      </ul>
                    </div>
                  </div>
                </div>
                <div class="editor-toolbar">
                  <el-button size="small" @click="insertTemplate('header')">插入标题</el-button>
                  <el-button size="small" @click="insertTemplate('code')">插入代码块</el-button>
                  <el-button size="small" @click="insertTemplate('table')">插入表格</el-button>
                  <el-button size="small" @click="insertTemplate('image')">插入图片</el-button>
                </div>
              </el-tab-pane>
              
              <el-tab-pane label="预览" name="preview">
                <div class="markdown-preview markdown-content" v-html="renderMarkdownContent(publishForm.content)"></div>
              </el-tab-pane>
            </el-tabs>
          </div>
        </div>

        <!-- 发布选项 -->
        <div class="form-section">
          <h3>发布选项</h3>
          
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="开源协议">
                <el-select v-model="publishForm.license">
                  <el-option label="MIT" value="MIT" />
                  <el-option label="Apache-2.0" value="Apache-2.0" />
                  <el-option label="GPL-3.0" value="GPL-3.0" />
                  <el-option label="BSD-3-Clause" value="BSD-3-Clause" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="个人分类">
                <el-select v-model="publishForm.user_category_id" placeholder="选择个人分类（可选）">
                  <el-option
                    v-for="userCategory in userCategories"
                    :key="userCategory.id"
                    :label="userCategory.name"
                    :value="userCategory.id"
                  />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
        </div>

        <!-- 操作按钮 -->
        <div class="form-actions">
          <el-button size="large" @click="goBack">取消</el-button>
          <el-button type="primary" size="large" @click="handleSubmit" :loading="loading">
            {{ loading ? '发布中...' : '发布文档' }}
          </el-button>
        </div>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { renderMarkdown } from '../utils/markdown'
import { setupImagePasteHandler, setupImageDropHandler } from '../utils/imagePaste'
import '../styles/markdown.css'
import http, { useLoading } from '../utils/http'
import { API_CONFIG } from '../config/api'

//======================================
// Markdown Publish View
//
// Markdown文档发布页：创建纯文档形式的代码分享
//
// 功能特性：
// - 实时预览：编辑/预览双标签切换
// - 图片粘贴：支持 Ctrl+V 粘贴图片，自动转为 Base64
// - 图片拖拽：支持拖拽图片到编辑区
// - 代码高亮：Markdown 代码块自动语法高亮
//
// 表单字段：
// - title: 文档标题
// - description: 简短描述
// - content: Markdown 正文内容
// - language: 主要编程语言
// - category_id: 系统分类
// - user_category_id: 个人分类（可选）
// - tags: 标签列表
// - license: 开源协议
//
// API 接口：POST /api/codes
// 提交时 results 固定为 [{type: 'markdown', content: ...}]
//======================================

const router = useRouter()
const { loading, withLoading } = useLoading()

// 表单数据
const publishForm = ref({
  title: '',
  description: '',
  content: '',
  language: 'Python',
  category_id: null,
  user_category_id: null,
  license: 'MIT',
  tags: [] as string[],
  results: [{
    type: 'markdown',
    content: '',
    description: 'Markdown文档'
  }]
})

// 分类和标签
interface Category {
  id: number
  name: string
}

interface UserCategory {
  id: number
  name: string
}

const categories = ref<Category[]>([])
const userCategories = ref<UserCategory[]>([])
const tagInput = ref('')
const activeTab = ref('edit')

// 编辑器引用
const markdownEditor = ref()
let cleanupImageHandlers: (() => void)[] = []

// 获取分类数据
const fetchCategories = async () => {
  try {
    const response = await http.get(API_CONFIG.endpoints.categories)
    categories.value = response.data.categories || []
  } catch (error) {
    console.error('获取分类失败:', error)
  }
}

// 获取用户分类
const fetchUserCategories = async () => {
  try {
    const response = await http.get(API_CONFIG.endpoints.userCategories)
    userCategories.value = response.data.user_categories || []
  } catch (error) {
    console.error('获取用户分类失败:', error)
  }
}

// 渲染Markdown
const renderMarkdownContent = (content: string) => {
  if (!content) return '<p class="preview-placeholder">在编辑标签页输入Markdown内容，这里会显示预览效果</p>'
  
  try {
    const { html } = renderMarkdown(content, {
      enableTOC: false,
      enableMermaid: true,
      enableMath: true
    })
    return html
  } catch (error) {
    console.error('Markdown渲染失败:', error)
    return '<p class="preview-error">Markdown渲染失败</p>'
  }
}

// 插入模板
const insertTemplate = (type: string) => {
  let template = ''
  const textarea = document.querySelector('textarea') as HTMLTextAreaElement
  const cursorPos = textarea?.selectionStart ?? publishForm.value.content.length

  switch (type) {
    case 'header':
      template = '\n## 新标题\n\n'
      break
    case 'code':
      template = '\n```python\n# 在这里输入代码\nprint("Hello World")\n```\n\n'
      break
    case 'table':
      template = '\n| 列1 | 列2 | 列3 |\n|-----|-----|-----|\n| 行1 | 数据 | 数据 |\n| 行2 | 数据 | 数据 |\n\n'
      break
    case 'image':
      template = '\n![图片描述](图片URL)\n\n'
      break
  }

  const content = publishForm.value.content
  publishForm.value.content = content.slice(0, cursorPos) + template + content.slice(cursorPos)
}

// 标签管理
const addTag = () => {
  const tag = tagInput.value.trim()
  if (tag && !publishForm.value.tags.includes(tag)) {
    publishForm.value.tags.push(tag)
    tagInput.value = ''
  }
}

const removeTag = (index: number) => {
  publishForm.value.tags.splice(index, 1)
}

// 提交发布
const handleSubmit = async () => {
  if (!publishForm.value.title || !publishForm.value.description || !publishForm.value.content) {
    ElMessage.error('请填写完整的标题、描述和内容')
    return
  }

  if (!publishForm.value.category_id) {
    ElMessage.error('请选择分类')
    return
  }

  // 将Markdown内容同时存储在content和result中
  if (publishForm.value.results[0]) {
    publishForm.value.results[0].content = publishForm.value.content
  }

  await withLoading(async () => {
    try {
      const response = await http.post(API_CONFIG.endpoints.codes, publishForm.value)
      ElMessage.success('Markdown文档发布成功！')
      router.push(`/codes/${response.data.code.id}`)
    } catch (error) {
      console.error('发布失败:', error)
      ElMessage.error('发布失败，请重试')
    }
  })
}

const goBack = () => {
  router.push('/publish')
}

// 设置图片粘贴功能
const setupImageHandlers = async () => {
  await nextTick()
  
  const textareaEl = markdownEditor.value?.$el?.querySelector('textarea')
  if (!textareaEl) return
  
  // 图片粘贴处理
  const pasteCleanup = setupImagePasteHandler(
    textareaEl,
    (markdown: string) => {
      // 图片粘贴成功回调
      console.log('图片已插入:', markdown)
    },
    {
      maxSize: 5 * 1024 * 1024, // 5MB
      quality: 0.8
    }
  )
  
  // 图片拖拽处理
  const dropCleanup = setupImageDropHandler(
    textareaEl,
    (markdown: string) => {
      // 图片拖拽成功回调
      console.log('图片已拖入:', markdown)
    },
    {
      maxSize: 5 * 1024 * 1024,
      quality: 0.8
    }
  )
  
  cleanupImageHandlers.push(pasteCleanup, dropCleanup)
}

onMounted(() => {
  fetchCategories()
  fetchUserCategories()
  setupImageHandlers()
})

onBeforeUnmount(() => {
  // 清理图片处理器
  cleanupImageHandlers.forEach(cleanup => cleanup())
})
</script>

<style scoped>
.markdown-publish-container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
}

.publish-card {
  border-radius: 12px;
}

.card-header {
  text-align: center;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 2px solid #f0f2f5;
}

.card-header h2 {
  color: #2c3e50;
  margin-bottom: 8px;
  font-size: 24px;
}

.card-header p {
  color: #7f8c8d;
  font-size: 14px;
}

.form-section {
  margin-bottom: 32px;
}

.form-section h3 {
  color: #34495e;
  font-size: 18px;
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 1px solid #e9ecef;
}

.markdown-editor {
  margin-top: 16px;
}

.markdown-editor .el-tabs__content {
  padding: 0;
}

.markdown-editor .el-textarea__inner {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 14px;
  line-height: 1.6;
}

.editor-toolbar {
  margin-top: 12px;
  padding: 12px 16px;
  background: #f8f9fa;
  border-radius: 6px;
}

.markdown-preview {
  min-height: 400px;
  max-height: 600px;
  overflow-y: auto;
  padding: 20px;
  background: white;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  line-height: 1.6;
}

.preview-placeholder {
  color: #909399;
  text-align: center;
  font-style: italic;
  margin-top: 100px;
}

.preview-error {
  color: #f56c6c;
  text-align: center;
}

.tags-display {
  margin-top: 8px;
}

.form-actions {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #e9ecef;
}

/* Markdown预览样式 */
.markdown-preview h1,
.markdown-preview h2,
.markdown-preview h3,
.markdown-preview h4,
.markdown-preview h5,
.markdown-preview h6 {
  margin: 20px 0 12px 0;
  font-weight: 600;
  color: #2c3e50;
}

.markdown-preview h1 {
  font-size: 2em;
  border-bottom: 2px solid #3498db;
  padding-bottom: 10px;
}

.markdown-preview h2 {
  font-size: 1.5em;
  border-bottom: 1px solid #bdc3c7;
  padding-bottom: 6px;
}

.markdown-preview pre {
  background-color: #f8f8f8;
  border: 1px solid #e1e8ed;
  border-radius: 6px;
  padding: 16px;
  overflow: auto;
  margin: 16px 0;
}

.markdown-preview code {
  background-color: #f1f3f4;
  padding: 2px 6px;
  border-radius: 3px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 0.9em;
}

.markdown-preview pre code {
  background-color: transparent;
  padding: 0;
}

.markdown-preview blockquote {
  border-left: 4px solid #3498db;
  padding-left: 16px;
  margin: 16px 0;
  color: #7f8c8d;
  font-style: italic;
}

.markdown-preview table {
  border-collapse: collapse;
  width: 100%;
  margin: 16px 0;
}

.markdown-preview table th,
.markdown-preview table td {
  border: 1px solid #dfe2e5;
  padding: 8px 12px;
  text-align: left;
}

.markdown-preview table th {
  background-color: #f6f8fa;
  font-weight: 600;
}

.markdown-preview img {
  max-width: 100%;
  height: auto;
  border-radius: 4px;
  margin: 10px 0;
}

/* Markdown编辑器增强样式 */
.markdown-editor-container {
  position: relative;
}

.markdown-textarea .el-textarea__inner {
  font-family: 'JetBrains Mono', 'Monaco', 'Consolas', monospace;
  line-height: 1.6;
  transition: border-color 0.3s ease;
}

.markdown-textarea .el-textarea__inner:focus {
  border-color: #3182ce;
  box-shadow: 0 0 0 2px rgba(49, 130, 206, 0.2);
}

.markdown-textarea .el-textarea__inner.drag-over {
  border-color: #38a169;
  background-color: #f0fff4;
  border-style: dashed;
}

.markdown-editor-hint {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
  color: #a0aec0;
  pointer-events: none;
  z-index: 1;
}

.hint-icon {
  font-size: 48px;
  margin-bottom: 16px;
  opacity: 0.6;
}

.hint-text p {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 12px;
  color: #4a5568;
}

.hint-text ul {
  list-style: none;
  padding: 0;
  font-size: 14px;
}

.hint-text li {
  margin: 8px 0;
  padding: 4px 8px;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 6px;
  display: inline-block;
  margin-right: 8px;
}

.editor-toolbar {
  margin-top: 12px;
  padding: 12px 16px;
  background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%);
  border-radius: 6px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.editor-toolbar .el-button {
  font-size: 12px;
  padding: 6px 12px;
}

/* 移动端适配 */
@media (max-width: 768px) {
  .markdown-publish-container {
    padding: 10px;
  }
  
  .markdown-editor .el-textarea__inner {
    font-size: 13px;
  }
  
  .form-actions {
    flex-direction: column;
  }
  
  .form-actions .el-button {
    width: 100%;
  }
  
  .hint-icon {
    font-size: 36px;
  }
  
  .hint-text p {
    font-size: 14px;
  }
  
  .hint-text li {
    font-size: 12px;
    margin: 4px 2px;
    padding: 3px 6px;
  }
  
  .editor-toolbar {
    justify-content: center;
  }
}
</style>
