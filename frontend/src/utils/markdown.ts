/**
 * Markdown 渲染工具
 * 
 * 功能：
 * - 使用 marked 解析 Markdown 语法
 * - 使用 highlight.js 实现代码高亮
 * - 自定义渲染器增强表格、引用块、代码块样式
 * - 支持代码块一键复制功能
 * 
 * 使用方式：
 * import { renderMarkdown } from './markdown'
 * const html = renderMarkdown(markdownText)
 */

import { marked } from 'marked'
import hljs from 'highlight.js'
import 'highlight.js/styles/vs.css'

// 配置marked选项
marked.setOptions({
  breaks: true,
  gfm: true,
  pedantic: false
})

// 自定义渲染器
const renderer = new marked.Renderer()

// 增强代码块渲染
renderer.code = function(code: string, language?: string) {
  const validLang = language && hljs.getLanguage(language) ? language : 'plaintext'
  const highlightedCode = hljs.highlight(code, { language: validLang }).value
  
  return `
    <div class="code-block-container">
      <div class="code-block-header">
        <span class="code-language">${validLang}</span>
        <button class="copy-code-btn" onclick="copyCode(this)" data-code="${encodeURIComponent(code)}">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
            <path d="M16 1H4c-1.1 0-2 .9-2 2v14h2V3h12V1zm3 4H8c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h11c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 16H8V7h11v14z"/>
          </svg>
          复制
        </button>
      </div>
      <pre class="hljs"><code class="language-${validLang}">${highlightedCode}</code></pre>
    </div>
  `
}

// 增强表格渲染
renderer.table = function(header: string, body: string) {
  return `
    <div class="table-container">
      <table class="markdown-table">
        <thead>${header}</thead>
        <tbody>${body}</tbody>
      </table>
    </div>
  `
}

// 增强引用块渲染
renderer.blockquote = function(quote: string) {
  return `
    <div class="blockquote-container">
      <div class="blockquote-icon">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
          <path d="M6 17h3l2-4V7H5v6h3l-2 4zm8 0h3l2-4V7h-6v6h3l-2 4z"/>
        </svg>
      </div>
      <blockquote class="enhanced-blockquote">${quote}</blockquote>
    </div>
  `
}

// 增强链接渲染（添加外链图标）
renderer.link = function(href: string, title: string, text: string) {
  const isExternal = href.startsWith('http') && !href.includes(window.location.host)
  const target = isExternal ? ' target="_blank" rel="noopener noreferrer"' : ''
  const icon = isExternal ? '<svg class="external-link-icon" width="12" height="12" viewBox="0 0 24 24" fill="currentColor"><path d="M19 19H5V5h7V3H5c-1.11 0-2 .9-2 2v14c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2v-7h-2v7zM14 3v2h3.59l-9.83 9.83 1.41 1.41L19 6.41V10h2V3h-7z"/></svg>' : ''
  
  return `<a href="${href}"${title ? ` title="${title}"` : ''}${target} class="markdown-link">${text}${icon}</a>`
}

// 任务列表支持
renderer.listitem = function(text: string, task?: boolean, checked?: boolean) {
  if (task) {
    const checkboxClass = checked ? 'task-checked' : 'task-unchecked'
    const checkIcon = checked ? '✓' : ''
    return `
      <li class="task-list-item ${checkboxClass}">
        <span class="task-checkbox">${checkIcon}</span>
        <span class="task-text">${text}</span>
      </li>
    `
  }
  return `<li>${text}</li>`
}

// 警告/提示框支持
const alertTypes = ['note', 'tip', 'warning', 'danger', 'info']

function processAlerts(html: string): string {
  alertTypes.forEach(type => {
    const regex = new RegExp(`<blockquote>\\s*<p>\\[!${type.toUpperCase()}\\]([\\s\\S]*?)</p>\\s*</blockquote>`, 'gi')
    html = html.replace(regex, (_match, content) => {
      const icons = {
        note: 'NOTE',
        tip: 'TIP', 
        warning: 'WARN',
        danger: 'DANGER',
        info: 'INFO'
      }
      
      return `
        <div class="alert alert-${type}">
          <div class="alert-icon">${icons[type as keyof typeof icons]}</div>
          <div class="alert-content">${content.trim()}</div>
        </div>
      `
    })
  })
  return html
}

// Mermaid图表支持
function processMermaid(html: string): string {
  return html.replace(/<pre><code class="language-mermaid">([\s\S]*?)<\/code><\/pre>/g, (_match, code) => {
    const id = `mermaid-${Math.random().toString(36).substr(2, 9)}`
    return `<div class="mermaid-container"><div class="mermaid" id="${id}">${code}</div></div>`
  })
}

// 数学公式支持 (KaTeX)
function processMath(html: string): string {
  // 行内公式 $formula$
  html = html.replace(/\$([^$\n]+)\$/g, (_match, formula) => {
    return `<span class="katex-inline" data-formula="${encodeURIComponent(formula)}">$${formula}$</span>`
  })
  
  // 块级公式 $$formula$$
  html = html.replace(/\$\$([\s\S]*?)\$\$/g, (_match, formula) => {
    return `<div class="katex-block" data-formula="${encodeURIComponent(formula.trim())}">$$${formula}$$</div>`
  })
  
  return html
}

// 目录生成
function generateTOC(html: string): { toc: string; html: string } {
  const headings: { level: number; text: string; id: string }[] = []
  
  const htmlWithIds = html.replace(/<h([1-6])>(.*?)<\/h[1-6]>/g, (_match, level, text) => {
    const cleanText = text.replace(/<[^>]*>/g, '')
    const id = cleanText.toLowerCase()
      .replace(/[^a-z0-9\u4e00-\u9fa5]+/g, '-')
      .replace(/^-+|-+$/g, '')
    
    headings.push({ level: parseInt(level), text: cleanText, id })
    
    return `<h${level} id="${id}">${text}<a class="header-link" href="#${id}">#</a></h${level}>`
  })
  
  if (headings.length === 0) {
    return { toc: '', html: htmlWithIds }
  }
  
  let toc = '<div class="table-of-contents"><h3>目录</h3><ul class="toc-list">'
  
  headings.forEach(({ level, text, id }) => {
    const indent = level > 1 ? ` style="margin-left: ${(level - 1) * 20}px"` : ''
    toc += `<li${indent}><a href="#${id}" class="toc-link">${text}</a></li>`
  })
  
  toc += '</ul></div>'
  
  return { toc, html: htmlWithIds }
}

// 主渲染函数
export function renderMarkdown(content: string, options: { 
  enableTOC?: boolean
  enableMermaid?: boolean 
  enableMath?: boolean
} = {}): { html: string; toc?: string } {
  if (!content?.trim()) {
    return { 
      html: '<div class="empty-content">暂无内容</div>' 
    }
  }
  
  try {
    // 基础markdown渲染
    let html = marked(content, { renderer })
    
    // 处理警告框
    html = processAlerts(html)
    
    // 处理图表
    if (options.enableMermaid) {
      html = processMermaid(html)
    }
    
    // 处理数学公式
    if (options.enableMath) {
      html = processMath(html)
    }
    
    // 生成目录
    if (options.enableTOC) {
      const { toc, html: htmlWithTOC } = generateTOC(html)
      return { html: htmlWithTOC, toc }
    }
    
    return { html }
    
  } catch (error) {
    console.error('Markdown渲染失败:', error)
    return { 
      html: '<div class="render-error">Markdown渲染失败，请检查语法</div>' 
    }
  }
}

// 复制代码功能
declare global {
  interface Window {
    copyCode: (button: HTMLButtonElement) => void
  }
}

if (typeof window !== 'undefined') {
  window.copyCode = function(button: HTMLButtonElement) {
    const code = decodeURIComponent(button.dataset.code || '')
    navigator.clipboard.writeText(code).then(() => {
      const originalText = button.innerHTML
      button.innerHTML = `
        <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
          <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
        </svg>
        已复制
      `
      button.classList.add('copied')
      
      setTimeout(() => {
        button.innerHTML = originalText
        button.classList.remove('copied')
      }, 2000)
    }).catch(err => {
      console.error('复制失败:', err)
    })
  }
}

export default { renderMarkdown }
