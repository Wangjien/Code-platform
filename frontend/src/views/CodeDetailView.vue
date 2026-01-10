<template>
  <div class="code-detail-container" v-loading="loading" element-loading-text="加载中...">
    <el-card shadow="hover" class="code-detail-card">
      <!-- 代码基本信息 -->
      <div class="code-info">
        <h1 class="code-title">{{ code.title }}</h1>
        <div class="code-meta">
          <span class="author">作者: {{ code.author_username }}</span>
          <span class="language">{{ code.language }}</span>
          <span class="license">{{ code.license }}</span>
          <span class="created-at">{{ formatDate(code.created_at) }}</span>
          <span class="updated-at">{{ formatDate(code.updated_at) }}</span>
        </div>
        <div class="code-tags">
          <el-tag v-for="tag in code.tags" :key="tag">{{ tag }}</el-tag>
        </div>
        <div class="code-actions">
          <el-button type="primary" @click="handleCopyCode">
            <el-icon><DocumentCopy /></el-icon> 复制代码
          </el-button>
          <el-button @click="handleDownloadCode">
            <el-icon><Download /></el-icon> 下载代码
          </el-button>
          <el-button type="success" @click="handleLike">
            <el-icon><Star /></el-icon> 点赞 ({{ code.likes }})
          </el-button>
        </div>
      </div>
      
      <!-- 代码描述 -->
      <div class="code-description">
        <h3>描述</h3>
        <p>{{ code.description }}</p>
      </div>
      
      <!-- 代码内容与效果展示 -->
      <div class="code-content-container">
        <!-- 代码编辑器 -->
        <div class="code-editor">
          <h3>代码</h3>
          <div ref="editorContainer" class="editor"></div>
        </div>
        
        <!-- 效果展示区 -->
        <div class="code-results">
          <h3>效果展示</h3>
          <div v-if="code.results && code.results.length > 0">
            <el-tabs v-model="activeResultTab" type="card">
              <el-tab-pane
                v-for="result in code.results"
                :key="result.id"
                :label="result.description || `结果 ${result.id}`"
              >
                <!-- 图片结果 -->
                <div v-if="result.type === 'image'" class="result-image">
                  <el-image :src="result.content" fit="contain" />
                </div>
                
                <!-- 文本结果 -->
                <div v-else-if="result.type === 'text'" class="result-text">
                  <el-input
                    type="textarea"
                    :value="result.content"
                    :rows="10"
                    readonly
                  />
                </div>
                
                <!-- 图表结果 -->
                <div v-else-if="result.type === 'chart'" class="result-chart">
                  <div ref="chartContainer" class="chart" :id="`chart-${result.id}`"></div>
                </div>
                
                <!-- 表格结果 -->
                <div v-else-if="result.type === 'table'" class="result-table">
                  <el-table :data="JSON.parse(result.content).data" style="width: 100%">
                    <el-table-column
                      v-for="column in JSON.parse(result.content).columns"
                      :key="column"
                      :prop="column"
                      :label="column"
                    />
                  </el-table>
                </div>
              </el-tab-pane>
            </el-tabs>
          </div>
          <div v-else class="no-results">
            <el-empty description="暂无效果展示" />
          </div>
        </div>
      </div>
      
      <!-- 环境配置 -->
      <div v-if="code.environment" class="code-environment">
        <h3>环境配置</h3>
        <el-input
          type="textarea"
          :value="code.environment"
          :rows="5"
          readonly
        />
      </div>
      
      <!-- 评论区 -->
      <div class="code-comments">
        <h3>评论 ({{ comments.length }})</h3>
        <el-input
          v-model="newComment"
          type="textarea"
          placeholder="写下你的评论..."
          :rows="3"
          @keyup.enter="handleSubmitComment"
        >
          <template #append>
            <el-button type="primary" @click="handleSubmitComment">提交评论</el-button>
          </template>
        </el-input>
        
        <div class="comments-list">
          <el-card shadow="hover" v-for="comment in comments" :key="comment.id">
            <div class="comment-item">
              <div class="comment-header">
                <span class="comment-author">{{ comment.author_username }}</span>
                <span class="comment-time">{{ formatDate(comment.created_at) }}</span>
              </div>
              <div class="comment-content">{{ comment.content }}</div>
            </div>
          </el-card>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import { useRoute } from 'vue-router'
import { DocumentCopy, Download, Star } from '@element-plus/icons-vue'
import loader from '@monaco-editor/loader'
import * as echarts from 'echarts'
import { ElMessage } from 'element-plus'
import http, { useLoading } from '../utils/http'
import { API_CONFIG } from '../config/api'

//======================================
// Code Detail View
//
// 代码详情页：展示代码元信息、代码内容、运行结果、评论。
// - 代码展示：Monaco Editor（只读）
// - 结果展示：image/text/chart/table（chart 使用 ECharts）
// - 评论：GET 列表 + POST 新评论（需携带 token）
//
// 关键点：
// - 路由参数：/code/:id
// - API：GET /api/codes/:id、GET/POST /api/codes/:id/comments
// - 资源释放：组件卸载时 dispose editor
//
// 注意：
// - Monaco CDN 写死，离线或网络差时可能加载失败
// - 图表初始化对 result.content(JSON) 有依赖，异常需 catch
//======================================

// 配置 Monaco 编辑器 CDN 源
loader.config({
  paths: {
    vs: 'https://cdn.jsdelivr.net/npm/monaco-editor@0.45.0/min/vs'
  }
})

const route = useRoute()
const codeId = Number(route.params.id)
const { loading, withLoading } = useLoading()

// 代码数据
const code = ref<any>({
  id: codeId,
  title: '',
  description: '',
  content: '',
  language: 'Python',
  author_username: '',
  tags: [],
  results: [],
  likes: 0,
  views: 0,
  created_at: '',
  updated_at: '',
  environment: ''
})

// 评论数据
const comments = ref<any[]>([])
const newComment = ref('')

// 活跃的结果标签页
const activeResultTab = ref(0)

// Monaco编辑器实例
let editor: any = null
let monacoInstance: any = null
const editorContainer = ref<HTMLElement | null>(null)

// 格式化日期
const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleString()
}

// 处理复制代码
const handleCopyCode = () => {
  // 浏览器剪贴板 API：需要 HTTPS 或 localhost
  navigator.clipboard.writeText(code.value.content)
    .then(() => {
      ElMessage.success('代码已复制到剪贴板')
    })
    .catch(err => {
      console.error('复制失败:', err)
      ElMessage.error('复制失败')
    })
}

// 处理下载代码
const handleDownloadCode = () => {
  // 将文本内容生成 Blob 并触发下载
  const blob = new Blob([code.value.content], { type: 'text/plain' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `${code.value.title}.${code.value.language.toLowerCase()}`
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

// 处理点赞
const handleLike = () => {
  code.value.likes++
  // 这里调用后端API更新点赞数
  console.log('点赞:', code.value.id)
}

// 处理提交评论
const handleSubmitComment = async () => {
  if (!newComment.value.trim()) {
    return
  }
  
  await withLoading(async () => {
    const response = await http.post(API_CONFIG.endpoints.codeComments(codeId), {
      content: newComment.value
    })
    
    comments.value.unshift(response.data)
    newComment.value = ''
    ElMessage.success('评论提交成功')
  })
}

// 初始化Monaco编辑器
const initEditor = async () => {
  if (editorContainer.value) {
    try {
      monacoInstance = await loader.init()
      editor = monacoInstance.editor.create(editorContainer.value, {
        value: code.value.content,
        language: code.value.language.toLowerCase(),
        theme: 'vs-dark',
        automaticLayout: true,
        readOnly: true,
        minimap: {
          enabled: true
        },
        scrollBeyondLastLine: false,
        fontSize: 14,
        lineNumbers: 'on',
        folding: true,
        scrollbar: {
          vertical: 'visible',
          horizontal: 'visible'
        }
      })
    } catch (error) {
      console.error('Monaco 编辑器加载失败:', error)
    }
  }
}

// 销毁编辑器
const disposeEditor = () => {
  if (editor) {
    editor.dispose()
    editor = null
  }
}

// 初始化图表
const initCharts = () => {
  // 遍历 results，遇到 chart 类型则用 ECharts 渲染
  code.value.results.forEach((result: any) => {
    if (result.type === 'chart') {
      try {
        const chartData = JSON.parse(result.content)
        const chartDom = document.getElementById(`chart-${result.id}`)
        if (chartDom) {
          const chart = echarts.init(chartDom)
          chart.setOption(chartData)
          
          // 监听窗口大小变化，自动调整图表大小
          window.addEventListener('resize', () => {
            chart.resize()
          })
        }
      } catch (error) {
        console.error('初始化图表失败:', error)
      }
    }
  })
}

// 获取代码详情
const fetchCodeDetail = async () => {
  await withLoading(async () => {
    const response = await http.get(API_CONFIG.endpoints.codeDetail(codeId))
    code.value = response.data
    
    // 初始化编辑器
    if (editor && monacoInstance) {
      editor.setValue(code.value.content)
      monacoInstance.editor.setModelLanguage(editor.getModel()!, code.value.language.toLowerCase())
    } else {
      await initEditor()
    }
    
    // 初始化图表
    initCharts()
  })
}

// 获取评论列表
const fetchComments = async () => {
  try {
    const response = await http.get(API_CONFIG.endpoints.codeComments(codeId))
    comments.value = response.data
  } catch (error) {
    console.error('获取评论列表失败:', error)
  }
}

// 页面挂载时获取数据
onMounted(async () => {
  await initEditor()
  fetchCodeDetail()
  fetchComments()
})

// 组件卸载时销毁编辑器
onBeforeUnmount(() => {
  disposeEditor()
})

// 监听代码变化，更新编辑器内容
watch(() => code.value.content, (newContent) => {
  if (editor) {
    editor.setValue(newContent)
  }
})
</script>

<style scoped>
.code-detail-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.code-detail-card {
  padding: 20px;
}

.code-info {
  margin-bottom: 20px;
}

.code-title {
  margin: 0 0 10px 0;
  font-size: 24px;
  font-weight: bold;
  color: #333;
}

.code-meta {
  display: flex;
  gap: 15px;
  margin-bottom: 10px;
  font-size: 14px;
  color: #666;
}

.code-tags {
  display: flex;
  gap: 10px;
  margin-bottom: 15px;
}

.code-actions {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.code-description {
  margin-bottom: 20px;
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 5px;
}

.code-description h3 {
  margin: 0 0 10px 0;
  font-size: 18px;
}

.code-content-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
  margin-bottom: 20px;
}

.code-editor {
  background-color: #f5f7fa;
  padding: 15px;
  border-radius: 5px;
}

.code-editor h3 {
  margin: 0 0 10px 0;
  font-size: 18px;
}

.editor {
  width: 100%;
  height: 500px;
  border: 1px solid #dcdfe6;
  border-radius: 5px;
}

.code-results {
  background-color: #f5f7fa;
  padding: 15px;
  border-radius: 5px;
}

.code-results h3 {
  margin: 0 0 10px 0;
  font-size: 18px;
}

.result-image {
  width: 100%;
  height: 400px;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: white;
  border-radius: 5px;
  overflow: hidden;
}

.result-image img {
  max-width: 100%;
  max-height: 100%;
}

.result-text {
  width: 100%;
  height: 400px;
}

.result-chart {
  width: 100%;
  height: 400px;
  background-color: white;
  border-radius: 5px;
  overflow: hidden;
}

.result-table {
  width: 100%;
  max-height: 400px;
  overflow: auto;
}

.no-results {
  width: 100%;
  height: 200px;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: white;
  border-radius: 5px;
}

.code-environment {
  margin-bottom: 20px;
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 5px;
}

.code-environment h3 {
  margin: 0 0 10px 0;
  font-size: 18px;
}

.code-comments {
  margin-top: 20px;
}

.code-comments h3 {
  margin: 0 0 15px 0;
  font-size: 18px;
}

.comments-list {
  margin-top: 20px;
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.comment-item {
  padding: 10px;
}

.comment-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  font-size: 14px;
  color: #666;
}

.comment-content {
  font-size: 14px;
  line-height: 1.5;
}
</style>
