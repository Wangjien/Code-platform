<template>
  <div class="admin-container">
    <el-card shadow="hover" class="admin-card">
      <div class="admin-header">
        <div class="admin-title">后台管理</div>
        <div class="admin-subtitle">用户管理 / 内容审核 / 评论管理</div>
      </div>

      <el-tabs v-model="activeTab" @tab-change="handleTabChange">
        <el-tab-pane label="用户管理" name="users">
          <div class="toolbar">
            <el-input v-model="userKeyword" placeholder="搜索用户名/邮箱" clearable style="max-width: 320px" />
            <el-button type="primary" @click="fetchUsers">查询</el-button>
          </div>

          <el-table :data="users" border style="width: 100%" v-loading="loadingUsers">
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="username" label="用户名" />
            <el-table-column prop="email" label="邮箱" />
            <el-table-column prop="role" label="角色" width="120">
              <template #default="scope">
                <el-tag :type="scope.row.role === 'admin' ? 'danger' : 'info'">
                  {{ scope.row.role }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="is_active" label="状态" width="120">
              <template #default="scope">
                <el-tag :type="scope.row.is_active ? 'success' : 'warning'">
                  {{ scope.row.is_active ? '正常' : '封禁' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="260">
              <template #default="scope">
                <el-button size="small" type="danger" plain @click="setRole(scope.row, 'admin')" :disabled="scope.row.role === 'admin'">
                  设为管理员
                </el-button>
                <el-button size="small" type="warning" plain @click="toggleActive(scope.row)">
                  {{ scope.row.is_active ? '封禁' : '解封' }}
                </el-button>
              </template>
            </el-table-column>
          </el-table>

          <div class="pager">
            <el-pagination
              v-model:current-page="userPage"
              v-model:page-size="userPerPage"
              layout="prev, pager, next, total"
              :total="userTotal"
              @current-change="fetchUsers"
            />
          </div>
        </el-tab-pane>

        <el-tab-pane label="内容审核" name="codes">
          <div class="toolbar">
            <el-input v-model="codeKeyword" placeholder="搜索标题/描述" clearable style="max-width: 320px" />
            <el-select v-model="codeStatus" placeholder="状态" clearable style="width: 160px">
              <el-option label="pending" value="pending" />
              <el-option label="approved" value="approved" />
              <el-option label="rejected" value="rejected" />
              <el-option label="disabled" value="disabled" />
            </el-select>
            <el-button type="primary" @click="fetchCodes">查询</el-button>
          </div>

          <el-table :data="codes" border style="width: 100%" v-loading="loadingCodes">
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="title" label="标题" />
            <el-table-column prop="author_username" label="作者" width="140" />
            <el-table-column prop="status" label="状态" width="140">
              <template #default="scope">
                <el-tag :type="statusTagType(scope.row.status)">{{ scope.row.status || 'approved' }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="340">
              <template #default="scope">
                <el-button size="small" type="success" plain @click="reviewCode(scope.row, 'approve')">通过</el-button>
                <el-button size="small" type="danger" plain @click="reviewCode(scope.row, 'reject')">驳回</el-button>
                <el-button size="small" type="warning" plain @click="reviewCode(scope.row, 'disable')">下架</el-button>
                <el-button size="small" @click="openCode(scope.row)">查看</el-button>
              </template>
            </el-table-column>
          </el-table>

          <div class="pager">
            <el-pagination
              v-model:current-page="codePage"
              v-model:page-size="codePerPage"
              layout="prev, pager, next, total"
              :total="codeTotal"
              @current-change="fetchCodes"
            />
          </div>
        </el-tab-pane>

        <el-tab-pane label="评论管理" name="comments">
          <div class="toolbar">
            <el-input v-model="commentKeyword" placeholder="搜索评论内容" clearable style="max-width: 320px" />
            <el-button type="primary" @click="fetchComments">查询</el-button>
          </div>

          <el-table :data="comments" border style="width: 100%" v-loading="loadingComments">
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="author_username" label="作者" width="140" />
            <el-table-column prop="code_id" label="CodeID" width="100" />
            <el-table-column prop="content" label="内容" />
            <el-table-column label="操作" width="140">
              <template #default="scope">
                <el-button size="small" type="danger" plain @click="deleteComment(scope.row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>

          <div class="pager">
            <el-pagination
              v-model:current-page="commentPage"
              v-model:page-size="commentPerPage"
              layout="prev, pager, next, total"
              :total="commentTotal"
              @current-change="fetchComments"
            />
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import http from '../utils/http'
import { API_CONFIG } from '../config/api'

const router = useRouter()
const loading = ref(false)

const activeTab = ref<'users' | 'codes' | 'comments'>('users')

// Users
const users = ref<any[]>([])
const userKeyword = ref('')
const userPage = ref(1)
const userPerPage = ref(20)
const userTotal = ref(0)
const loadingUsers = ref(false)

const fetchUsers = async () => {
  loadingUsers.value = true
  try {
    const res = await http.get(API_CONFIG.endpoints.adminUsers, {
      params: { page: userPage.value, per_page: userPerPage.value, keyword: userKeyword.value || undefined }
    })
    users.value = res.data.users || []
    userTotal.value = res.data.total || 0
  } catch (e: any) {
    ElMessage.error(e.response?.data?.message || '获取用户列表失败')
  } finally {
    loadingUsers.value = false
  }
}

const setRole = async (user: any, role: 'user' | 'admin') => {
  try {
    await ElMessageBox.confirm(`确定将 ${user.username} 设置为 ${role} 吗？`, '提示', { type: 'warning' })
    const res = await http.patch(API_CONFIG.endpoints.adminUserDetail(user.id), { role })
    ElMessage.success('更新成功')
    const updated = res.data.user
    const idx = users.value.findIndex(u => u.id === updated.id)
    if (idx >= 0) users.value[idx] = updated
  } catch (e: any) {
    if (e !== 'cancel') ElMessage.error(e.response?.data?.message || '更新失败')
  }
}

const toggleActive = async (user: any) => {
  try {
    const next = !user.is_active
    await ElMessageBox.confirm(`确定要${next ? '解封' : '封禁'} ${user.username} 吗？`, '提示', { type: 'warning' })
    const res = await http.patch(API_CONFIG.endpoints.adminUserDetail(user.id), { is_active: next })
    ElMessage.success('更新成功')
    const updated = res.data.user
    const idx = users.value.findIndex(u => u.id === updated.id)
    if (idx >= 0) users.value[idx] = updated
  } catch (e: any) {
    if (e !== 'cancel') ElMessage.error(e.response?.data?.message || '更新失败')
  }
}

// Codes
const codes = ref<any[]>([])
const codeKeyword = ref('')
const codeStatus = ref<string | null>(null)
const codePage = ref(1)
const codePerPage = ref(20)
const codeTotal = ref(0)
const loadingCodes = ref(false)

const statusTagType = (status: string) => {
  if (status === 'pending') return 'warning'
  if (status === 'approved' || !status) return 'success'
  if (status === 'rejected') return 'danger'
  if (status === 'disabled') return 'info'
  return 'info'
}

const fetchCodes = async () => {
  loadingCodes.value = true
  try {
    const res = await http.get(API_CONFIG.endpoints.adminCodes, {
      params: {
        page: codePage.value,
        per_page: codePerPage.value,
        keyword: codeKeyword.value || undefined,
        status: codeStatus.value || undefined
      }
    })
    codes.value = res.data.codes || []
    codeTotal.value = res.data.total || 0
  } catch (e: any) {
    ElMessage.error(e.response?.data?.message || '获取代码列表失败')
  } finally {
    loadingCodes.value = false
  }
}

const reviewCode = async (code: any, action: 'approve' | 'reject' | 'disable') => {
  try {
    const reason = action === 'approve' ? '' : await ElMessageBox.prompt('请输入原因（可选）', '原因', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      inputPlaceholder: '原因可为空'
    }).then(r => r.value).catch(() => '')

    const res = await http.patch(API_CONFIG.endpoints.adminCodeReview(code.id), { action, reason })
    ElMessage.success('操作成功')
    const updated = res.data.code
    const idx = codes.value.findIndex(c => c.id === updated.id)
    if (idx >= 0) codes.value[idx] = updated
  } catch (e: any) {
    ElMessage.error(e.response?.data?.message || '操作失败')
  }
}

const openCode = (code: any) => {
  router.push(`/code/${code.id}`)
}

// Comments
const comments = ref<any[]>([])
const commentKeyword = ref('')
const commentPage = ref(1)
const commentPerPage = ref(20)
const commentTotal = ref(0)
const loadingComments = ref(false)

const fetchComments = async () => {
  loadingComments.value = true
  try {
    const res = await http.get(API_CONFIG.endpoints.adminComments, {
      params: { page: commentPage.value, per_page: commentPerPage.value, keyword: commentKeyword.value || undefined }
    })
    comments.value = res.data.comments || []
    commentTotal.value = res.data.total || 0
  } catch (e: any) {
    ElMessage.error(e.response?.data?.message || '获取评论列表失败')
  } finally {
    loadingComments.value = false
  }
}

const deleteComment = async (comment: any) => {
  try {
    await ElMessageBox.confirm('确定要删除这条评论吗？', '提示', { type: 'warning' })
    await http.delete(API_CONFIG.endpoints.adminCommentDetail(comment.id))
    ElMessage.success('删除成功')
    comments.value = comments.value.filter(c => c.id !== comment.id)
  } catch (e: any) {
    if (e !== 'cancel') ElMessage.error(e.response?.data?.message || '删除失败')
  }
}

const handleTabChange = () => {
  if (activeTab.value === 'users') fetchUsers()
  if (activeTab.value === 'codes') fetchCodes()
  if (activeTab.value === 'comments') fetchComments()
}

onMounted(() => {
  fetchUsers()
})
</script>

<style scoped>
.admin-container {
  padding: 16px;
}

.admin-card {
  max-width: 1200px;
  margin: 0 auto;
}

.admin-header {
  margin-bottom: 12px;
}

.admin-title {
  font-size: 18px;
  font-weight: 600;
}

.admin-subtitle {
  margin-top: 4px;
  color: #909399;
  font-size: 13px;
}

.toolbar {
  display: flex;
  gap: 12px;
  align-items: center;
  margin-bottom: 12px;
}

.pager {
  margin-top: 12px;
  display: flex;
  justify-content: flex-end;
}
</style>
