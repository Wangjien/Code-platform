<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import MainLayout from './components/MainLayout.vue'

//======================================
// App Root
//
// 该组件是全局根组件：
// - 根据路由决定是否使用 MainLayout（带导航/侧边栏的主布局）
// - 登录/注册页采用“无布局”模式，避免在登录页展示主导航
//
// 约定：
// - noLayoutPages：无需布局的路由 path 列表
// - needLayout：计算属性，决定 template 渲染 MainLayout 还是 router-view
//======================================

const route = useRoute()

// 不需要布局的页面
const noLayoutPages = ['/login', '/register']
const needLayout = computed(() => {
  return !noLayoutPages.includes(route.path)
})
</script>

<template>
  <div id="app">
    <!-- 需要布局的页面（首页、详情页、发布页） -->
    <template v-if="needLayout">
      <MainLayout />
    </template>
    <!-- 不需要布局的页面（登录、注册） -->
    <template v-else>
      <router-view />
    </template>
  </div>
</template>

<style>
/* 全局样式已在style.css中定义 */
</style>
