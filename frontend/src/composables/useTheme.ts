import { ref, watch, onMounted } from 'vue'

export type Theme = 'light' | 'dark' | 'system'

const THEME_KEY = 'theme-preference'

// 全局主题状态
const currentTheme = ref<Theme>('system')
const isDark = ref(false)

// 获取系统主题偏好
const getSystemTheme = (): 'light' | 'dark' => {
  if (typeof window !== 'undefined' && window.matchMedia) {
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
  }
  return 'light'
}

// 应用主题到 DOM
const applyTheme = (dark: boolean) => {
  isDark.value = dark
  if (typeof document !== 'undefined') {
    document.documentElement.classList.toggle('dark', dark)
    document.documentElement.setAttribute('data-theme', dark ? 'dark' : 'light')
  }
}

// 更新主题
const updateTheme = () => {
  if (currentTheme.value === 'system') {
    applyTheme(getSystemTheme() === 'dark')
  } else {
    applyTheme(currentTheme.value === 'dark')
  }
}

// 设置主题
const setTheme = (theme: Theme) => {
  currentTheme.value = theme
  if (typeof localStorage !== 'undefined') {
    localStorage.setItem(THEME_KEY, theme)
  }
  updateTheme()
}

// 切换主题
const toggleTheme = () => {
  if (isDark.value) {
    setTheme('light')
  } else {
    setTheme('dark')
  }
}

// 初始化主题
const initTheme = () => {
  if (typeof localStorage !== 'undefined') {
    const saved = localStorage.getItem(THEME_KEY) as Theme | null
    if (saved && ['light', 'dark', 'system'].includes(saved)) {
      currentTheme.value = saved
    }
  }
  updateTheme()

  // 监听系统主题变化
  if (typeof window !== 'undefined' && window.matchMedia) {
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
      if (currentTheme.value === 'system') {
        updateTheme()
      }
    })
  }
}

export function useTheme() {
  onMounted(() => {
    initTheme()
  })

  return {
    currentTheme,
    isDark,
    setTheme,
    toggleTheme
  }
}

// 导出初始化函数供 main.ts 使用
export { initTheme }
