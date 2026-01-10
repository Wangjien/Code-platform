import { createApp } from 'vue'
import './style.css'
import App from './App.vue'

//======================================
// App Entry (Vite + Vue3)
//
// 该文件是前端应用入口：
// - 创建 Vue app 实例
// - 注册全局插件（ElementPlus / Router / Pinia）
// - 挂载到 #app
//
// 关键点：
// - 插件注册顺序通常不敏感，但要在 mount 前完成
// - 全局样式在此处统一引入（style.css / element-plus css）
//======================================

// 引入 Element Plus
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'

// 引入 Vue Router
import router from './router'

// 引入 Pinia（全局状态管理）
import { createPinia } from 'pinia'
const pinia = createPinia()

const app = createApp(App)

// 注册全局插件
app.use(ElementPlus)
app.use(router)
app.use(pinia)

// 挂载应用
app.mount('#app')
