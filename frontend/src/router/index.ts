import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import CodeDetailView from '../views/CodeDetailView.vue'
import CodePublishView from '../views/CodePublishView.vue'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import ProfileView from '../views/ProfileView.vue'
import AdminView from '../views/AdminView.vue'

//======================================
// Router
//
// 该文件定义前端路由：
// - 页面入口与路径映射
// - meta.requiresAuth：需要登录的页面
// - 全局前置守卫：基于 localStorage token 做简单鉴权
//
// 注意：
// - 目前鉴权策略为“前端拦截 + token 存储在 localStorage”。
//   真实安全边界仍在后端（JWT 校验）。
// - 若后续引入 Pinia 用户态，可将 token 管理收敛到 store。
//======================================

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    {
      path: '/code/:id',
      name: 'code-detail',
      component: CodeDetailView,
      props: true
    },
    {
      path: '/publish',
      name: 'code-publish',
      component: CodePublishView,
      meta: {
        requiresAuth: true
      }
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView
    },
    {
      path: '/register',
      name: 'register',
      component: RegisterView
    },
    {
      path: '/profile',
      name: 'profile',
      component: ProfileView,
      meta: {
        requiresAuth: true
      }
    },
    {
      path: '/admin',
      name: 'admin',
      component: AdminView,
      meta: {
        requiresAuth: true,
        requiresAdmin: true
      }
    }
  ]
})

//======================================
// Route Guard
//
// 路由守卫：检查是否需要登录。
// - requiresAuth 且没有 token -> 跳转登录页
// - 否则放行
//======================================
router.beforeEach((to, _from, next) => {
  const isAuthenticated = localStorage.getItem('token')
  const userStr = localStorage.getItem('user')
  const user = userStr ? JSON.parse(userStr) : null
  
  if (to.meta.requiresAuth && !isAuthenticated) {
    next({ name: 'login' })
    return
  }

  if (to.meta.requiresAdmin && (!user || user.role !== 'admin')) {
    next({ name: 'home' })
    return
  } else {
    next()
  }
})

export default router
