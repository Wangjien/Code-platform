// 图片粘贴处理工具
import { ElMessage } from 'element-plus'

export interface PasteImageOptions {
  maxSize?: number // 最大文件大小 (字节)
  allowedTypes?: string[] // 允许的文件类型
  quality?: number // 图片质量 (0-1)
  maxWidth?: number // 最大宽度
  maxHeight?: number // 最大高度
  uploadEndpoint?: string // 上传接口
}

const DEFAULT_OPTIONS: PasteImageOptions = {
  maxSize: 5 * 1024 * 1024, // 5MB
  allowedTypes: ['image/png', 'image/jpeg', 'image/gif', 'image/webp'],
  quality: 0.8,
  maxWidth: 1920,
  maxHeight: 1080,
}

/**
 * 处理粘贴的图片文件
 */
export async function handlePastedImage(
  file: File, 
  options: PasteImageOptions = {}
): Promise<string> {
  const opts = { ...DEFAULT_OPTIONS, ...options }
  
  // 验证文件类型
  if (!opts.allowedTypes?.includes(file.type)) {
    throw new Error(`不支持的图片格式: ${file.type}`)
  }
  
  // 验证文件大小
  if (opts.maxSize && file.size > opts.maxSize) {
    throw new Error(`图片大小超过限制: ${(file.size / 1024 / 1024).toFixed(1)}MB`)
  }
  
  // 压缩图片
  const compressedFile = await compressImage(file, opts)
  
  // 转换为base64或上传
  if (opts.uploadEndpoint) {
    return await uploadImage(compressedFile, opts.uploadEndpoint)
  } else {
    return await fileToBase64(compressedFile)
  }
}

/**
 * 压缩图片
 */
async function compressImage(file: File, options: PasteImageOptions): Promise<File> {
  return new Promise((resolve) => {
    const canvas = document.createElement('canvas')
    const ctx = canvas.getContext('2d')!
    const img = new Image()
    
    img.onload = () => {
      // 计算压缩后的尺寸
      let { width, height } = img
      const maxWidth = options.maxWidth || DEFAULT_OPTIONS.maxWidth!
      const maxHeight = options.maxHeight || DEFAULT_OPTIONS.maxHeight!
      
      if (width > maxWidth || height > maxHeight) {
        const ratio = Math.min(maxWidth / width, maxHeight / height)
        width *= ratio
        height *= ratio
      }
      
      // 设置canvas尺寸
      canvas.width = width
      canvas.height = height
      
      // 绘制图片
      ctx.drawImage(img, 0, 0, width, height)
      
      // 导出为blob
      canvas.toBlob((blob) => {
        if (blob) {
          const compressedFile = new File([blob], file.name, {
            type: file.type,
            lastModified: Date.now()
          })
          resolve(compressedFile)
        } else {
          resolve(file)
        }
      }, file.type, options.quality || DEFAULT_OPTIONS.quality)
    }
    
    img.src = URL.createObjectURL(file)
  })
}

/**
 * 文件转base64
 */
function fileToBase64(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => resolve(reader.result as string)
    reader.onerror = reject
    reader.readAsDataURL(file)
  })
}

/**
 * 上传图片到服务器
 */
async function uploadImage(file: File, uploadEndpoint: string): Promise<string> {
  const formData = new FormData()
  formData.append('image', file)
  
  try {
    const response = await fetch(uploadEndpoint, {
      method: 'POST',
      body: formData,
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })
    
    if (!response.ok) {
      throw new Error(`上传失败: ${response.statusText}`)
    }
    
    const result = await response.json()
    return result.url || result.data?.url
  } catch (error) {
    console.error('图片上传失败:', error)
    throw error
  }
}

/**
 * 设置粘贴事件监听
 */
export function setupImagePasteHandler(
  textarea: HTMLTextAreaElement,
  onImagePasted: (markdown: string) => void,
  options: PasteImageOptions = {}
) {
  const handlePaste = async (event: ClipboardEvent) => {
    const items = event.clipboardData?.items
    if (!items) return
    
    // 查找图片项
    for (let i = 0; i < items.length; i++) {
      const item = items[i]
      
      if (item && item.type.startsWith('image/')) {
        event.preventDefault()
        
        const file = item.getAsFile()
        if (!file) continue
        
        try {
          // 显示加载提示
          ElMessage.info('正在处理粘贴的图片...')
          
          // 处理图片
          const imageUrl = await handlePastedImage(file, options)
          
          // 生成markdown语法
          const imageMarkdown = `![${file.name}](${imageUrl})`
          
          // 插入到当前光标位置
          const startPos = textarea.selectionStart
          const endPos = textarea.selectionEnd
          const textBefore = textarea.value.substring(0, startPos)
          const textAfter = textarea.value.substring(endPos)
          
          const newText = textBefore + imageMarkdown + textAfter
          textarea.value = newText
          
          // 设置新的光标位置
          const newPos = startPos + imageMarkdown.length
          textarea.setSelectionRange(newPos, newPos)
          
          // 触发input事件以更新Vue响应式数据
          const inputEvent = new Event('input', { bubbles: true })
          textarea.dispatchEvent(inputEvent)
          
          // 回调
          onImagePasted(imageMarkdown)
          
          ElMessage.success('图片粘贴成功！')
          
        } catch (error) {
          console.error('图片粘贴失败:', error)
          ElMessage.error(`图片粘贴失败: ${(error as Error).message}`)
        }
        
        break
      }
    }
  }
  
  textarea.addEventListener('paste', handlePaste)
  
  // 返回清理函数
  return () => {
    textarea.removeEventListener('paste', handlePaste)
  }
}

/**
 * 拖拽上传图片
 */
export function setupImageDropHandler(
  textarea: HTMLTextAreaElement,
  onImageDropped: (markdown: string) => void,
  options: PasteImageOptions = {}
) {
  const handleDragOver = (event: DragEvent) => {
    event.preventDefault()
    textarea.classList.add('drag-over')
  }
  
  const handleDragLeave = (event: DragEvent) => {
    event.preventDefault()
    textarea.classList.remove('drag-over')
  }
  
  const handleDrop = async (event: DragEvent) => {
    event.preventDefault()
    textarea.classList.remove('drag-over')
    
    const files = event.dataTransfer?.files
    if (!files || files.length === 0) return
    
    // 处理第一个图片文件
    const file = files[0]
    if (!file.type.startsWith('image/')) return
    
    try {
      ElMessage.info('正在处理拖拽的图片...')
      
      const imageUrl = await handlePastedImage(file, options)
      const imageMarkdown = `![${file.name}](${imageUrl})`
      
      // 插入到当前光标位置或末尾
      const startPos = textarea.selectionStart || textarea.value.length
      const endPos = textarea.selectionEnd || startPos
      const textBefore = textarea.value.substring(0, startPos)
      const textAfter = textarea.value.substring(endPos)
      
      const newText = textBefore + imageMarkdown + textAfter
      textarea.value = newText
      
      const newPos = startPos + imageMarkdown.length
      textarea.setSelectionRange(newPos, newPos)
      
      const inputEvent = new Event('input', { bubbles: true })
      textarea.dispatchEvent(inputEvent)
      
      onImageDropped(imageMarkdown)
      ElMessage.success('图片拖拽成功！')
      
    } catch (error) {
      console.error('图片拖拽失败:', error)
      ElMessage.error(`图片拖拽失败: ${(error as Error).message}`)
    }
  }
  
  textarea.addEventListener('dragover', handleDragOver)
  textarea.addEventListener('dragleave', handleDragLeave)
  textarea.addEventListener('drop', handleDrop)
  
  return () => {
    textarea.removeEventListener('dragover', handleDragOver)
    textarea.removeEventListener('dragleave', handleDragLeave)
    textarea.removeEventListener('drop', handleDrop)
  }
}

/**
 * 创建图片上传按钮
 */
export function createImageUploadButton(
  onImageSelected: (markdown: string) => void,
  options: PasteImageOptions = {}
): HTMLButtonElement {
  const button = document.createElement('button')
  button.innerHTML = `
    <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
      <path d="M21 19V5c0-1.1-.9-2-2-2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2zM8.5 13.5l2.5 3.01L14.5 12l4.5 6H5l3.5-4.5z"/>
    </svg>
    上传图片
  `
  button.className = 'upload-image-btn'
  button.type = 'button'
  
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = 'image/*'
  input.style.display = 'none'
  
  button.appendChild(input)
  
  button.onclick = () => input.click()
  
  input.onchange = async (event) => {
    const file = (event.target as HTMLInputElement).files?.[0]
    if (!file) return
    
    try {
      ElMessage.info('正在上传图片...')
      
      const imageUrl = await handlePastedImage(file, options)
      const imageMarkdown = `![${file.name}](${imageUrl})`
      
      onImageSelected(imageMarkdown)
      ElMessage.success('图片上传成功！')
      
    } catch (error) {
      console.error('图片上传失败:', error)
      ElMessage.error(`图片上传失败: ${(error as Error).message}`)
    }
    
    // 清空input
    input.value = ''
  }
  
  return button
}

export default {
  setupImagePasteHandler,
  setupImageDropHandler,
  createImageUploadButton,
  handlePastedImage
}
