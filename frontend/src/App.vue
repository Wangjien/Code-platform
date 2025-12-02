<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import MainLayout from './components/MainLayout.vue'

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
