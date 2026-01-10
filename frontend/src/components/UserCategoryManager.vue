<template>
  <div class="category-manager">
    <!-- 添加分类按钮 -->
    <div class="add-category-section">
      <el-button type="primary" :icon="Plus" @click="showAddDialog = true">
        创建新分类
      </el-button>
    </div>
    
    <!-- 分类列表 -->
    <div class="category-list" v-loading="loading">
      <div
        v-for="category in categories"
        :key="category.id"
        class="category-item"
        :style="{ borderLeft: `4px solid ${category.color}` }"
      >
        <div class="category-info">
          <div class="category-header">
            <h4 class="category-name">{{ category.name }}</h4>
            <el-tag size="small">{{ category.code_count }} 个代码</el-tag>
          </div>
          <p class="category-description" v-if="category.description">
            {{ category.description }}
          </p>
        </div>
        
        <div class="category-actions">
          <el-button size="small" :icon="Edit" @click="editCategory(category)" />
          <el-button 
            size="small" 
            type="danger" 
            :icon="Delete" 
            @click="deleteCategory(category)"
            :disabled="category.code_count > 0"
          />
        </div>
      </div>
      
      <div v-if="categories.length === 0" class="empty-state">
        <el-empty description="暂无自定义分类">
          <el-button type="primary" @click="showAddDialog = true">创建第一个分类</el-button>
        </el-empty>
      </div>
    </div>
    
    <!-- 添加/编辑分类对话框 -->
    <el-dialog
      v-model="showAddDialog"
      :title="isEditing ? '编辑分类' : '创建分类'"
      width="500px"
      @close="resetForm"
    >
      <el-form :model="categoryForm" :rules="categoryRules" ref="formRef" label-width="80px">
        <el-form-item label="分类名称" prop="name">
          <el-input v-model="categoryForm.name" placeholder="请输入分类名称" />
        </el-form-item>
        
        <el-form-item label="分类描述" prop="description">
          <el-input
            v-model="categoryForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入分类描述（可选）"
          />
        </el-form-item>
        
        <el-form-item label="分类颜色" prop="color">
          <el-color-picker 
            v-model="categoryForm.color"
            :predefine="predefineColors"
            show-alpha
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button 
          type="primary" 
          @click="submitCategory"
          :loading="submitting"
        >
          {{ isEditing ? '更新' : '创建' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Plus, Edit, Delete } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox, ElForm } from 'element-plus'
import http, { useLoading } from '../utils/http'
import { API_CONFIG } from '../config/api'
import { validationRules } from '../utils/validation'
import { cache, CACHE_KEYS, CACHE_TTL } from '../utils/cache'

// 响应式数据
const { loading, withLoading } = useLoading()
const categories = ref<any[]>([])
const showAddDialog = ref(false)
const isEditing = ref(false)
const submitting = ref(false)
const formRef = ref<InstanceType<typeof ElForm>>()

// 表单数据
const categoryForm = ref({
  id: null,
  name: '',
  description: '',
  color: '#409EFF'
})

// 预设颜色
const predefineColors = [
  '#409EFF', '#67C23A', '#E6A23C', '#F56C6C', '#909399',
  '#9C27B0', '#673AB7', '#3F51B5', '#2196F3', '#00BCD4',
  '#009688', '#4CAF50', '#8BC34A', '#CDDC39', '#FFEB3B',
  '#FF9800', '#FF5722', '#795548', '#607D8B'
]

// 表单验证规则
const categoryRules = {
  name: [
    validationRules.required('请输入分类名称'),
    { min: 1, max: 50, message: '分类名称长度在 1 到 50 个字符', trigger: 'blur' }
  ],
  description: [
    { max: 200, message: '描述长度不能超过 200 个字符', trigger: 'blur' }
  ],
  color: [
    validationRules.required('请选择分类颜色')
  ]
}

// 获取分类列表 (带缓存)
const fetchCategories = async () => {
  await withLoading(async () => {
    const cachedCategories = await cache.cacheRequest(
      CACHE_KEYS.USER_CATEGORIES,
      () => http.get(API_CONFIG.endpoints.userCategories).then(res => res.data),
      CACHE_TTL.SHORT // 分类管理页面使用较短缓存时间，确保数据实时性
    )
    categories.value = cachedCategories
  })
}

// 编辑分类
const editCategory = (category: any) => {
  isEditing.value = true
  categoryForm.value = {
    id: category.id,
    name: category.name,
    description: category.description || '',
    color: category.color || '#409EFF'
  }
  showAddDialog.value = true
}

// 删除分类
const deleteCategory = async (category: any) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除分类"${category.name}"吗？`,
      '删除分类',
      {
        type: 'warning',
        confirmButtonText: '确定删除',
        cancelButtonText: '取消'
      }
    )
    
    await http.delete(API_CONFIG.endpoints.userCategoryDetail(category.id))
    ElMessage.success('分类删除成功')
    
    // 清理缓存并重新获取数据
    cache.delete(CACHE_KEYS.USER_CATEGORIES)
    fetchCategories()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// 提交分类
const submitCategory = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
  } catch {
    return
  }
  
  submitting.value = true
  
  try {
    if (isEditing.value) {
      // 更新分类
      await http.put(API_CONFIG.endpoints.userCategoryDetail(categoryForm.value.id!), {
        name: categoryForm.value.name,
        description: categoryForm.value.description,
        color: categoryForm.value.color
      })
      ElMessage.success('分类更新成功')
    } else {
      // 创建分类
      await http.post(API_CONFIG.endpoints.userCategories, categoryForm.value)
      ElMessage.success('分类创建成功')
    }
    
    showAddDialog.value = false
    
    // 清理缓存并重新获取数据
    cache.delete(CACHE_KEYS.USER_CATEGORIES)
    fetchCategories()
  } catch (error: any) {
    ElMessage.error(error.response?.data?.message || '操作失败')
  } finally {
    submitting.value = false
  }
}

// 重置表单
const resetForm = () => {
  isEditing.value = false
  categoryForm.value = {
    id: null,
    name: '',
    description: '',
    color: '#409EFF'
  }
  formRef.value?.resetFields()
}

// 页面加载时获取数据
onMounted(() => {
  fetchCategories()
})
</script>

<style scoped>
.category-manager {
  padding: 16px;
}

.add-category-section {
  margin-bottom: 24px;
}

.category-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.category-item {
  background: white;
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: transform 0.2s, box-shadow 0.2s;
}

.category-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.category-info {
  flex: 1;
}

.category-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.category-name {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.category-description {
  margin: 0;
  color: #606266;
  font-size: 14px;
  line-height: 1.4;
}

.category-actions {
  display: flex;
  gap: 8px;
}

.empty-state {
  text-align: center;
  padding: 40px;
}
</style>
