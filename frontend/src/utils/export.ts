/**
 * 代码导出工具
 * 支持单个代码、批量代码导出为多种格式
 */

import { downloadFile } from './ui-helpers'
import JSZip from 'jszip'
import { ElMessage } from 'element-plus'

// 编程语言文件扩展名映射
const LANGUAGE_EXTENSIONS: Record<string, string> = {
  'Python': '.py',
  'R': '.r',
  'JavaScript': '.js',
  'TypeScript': '.ts',
  'Java': '.java',
  'C++': '.cpp',
  'C': '.c',
  'Go': '.go',
  'Rust': '.rs',
  'PHP': '.php',
  'Ruby': '.rb',
  'Swift': '.swift',
  'Kotlin': '.kt',
  'Scala': '.scala',
  'HTML': '.html',
  'CSS': '.css',
  'SQL': '.sql',
  'Shell': '.sh',
  'Bash': '.sh',
  'PowerShell': '.ps1',
  'YAML': '.yml',
  'JSON': '.json',
  'XML': '.xml',
  'Markdown': '.md',
  // 生物信息学常用语言
  'Perl': '.pl',
  'MATLAB': '.m',
  'Julia': '.jl',
  'Nextflow': '.nf',
  'Snakemake': '.smk',
  'WDL': '.wdl',
  'AWK': '.awk',
  'Other': '.txt'
}

// 代码接口定义
interface Code {
  id: number
  title: string
  description: string
  content: string
  language: string
  category?: {
    name: string
  }
  user_category?: {
    name: string
  }
  author: {
    username: string
  }
  created_at: string
  tags?: Array<{ name: string }>
}

// 导出格式常量
export const ExportFormat = {
  SOURCE: 'source',      // 源码文件
  MARKDOWN: 'markdown',  // Markdown格式
  JSON: 'json',          // JSON格式
  ZIP: 'zip'             // ZIP压缩包
} as const

export type ExportFormat = typeof ExportFormat[keyof typeof ExportFormat]

/**
 * 获取文件扩展名
 */
function getFileExtension(language: string, format: ExportFormat): string {
  if (format === ExportFormat.MARKDOWN) return '.md'
  if (format === ExportFormat.JSON) return '.json'
  return LANGUAGE_EXTENSIONS[language] || '.txt'
}

/**
 * 生成安全的文件名
 */
function sanitizeFilename(filename: string): string {
  return filename
    .replace(/[<>:"/\\|?*]/g, '_')  // 替换非法字符
    .replace(/\s+/g, '_')           // 替换空格
    .substring(0, 100)              // 限制长度
}

/**
 * 导出单个代码文件
 */
export async function exportSingleCode(
  code: Code, 
  format: ExportFormat = ExportFormat.SOURCE
): Promise<void> {
  try {
    const extension = getFileExtension(code.language, format)
    const baseFilename = sanitizeFilename(code.title)
    const filename = `${baseFilename}${extension}`

    let content: string
    let mimeType: string

    switch (format) {
      case ExportFormat.SOURCE:
        content = generateSourceContent(code)
        mimeType = 'text/plain'
        break
        
      case ExportFormat.MARKDOWN:
        content = generateMarkdownContent(code)
        mimeType = 'text/markdown'
        break
        
      case ExportFormat.JSON:
        content = generateJsonContent(code)
        mimeType = 'application/json'
        break
        
      default:
        throw new Error(`不支持的导出格式: ${format}`)
    }

    downloadFile(content, filename, mimeType)
    ElMessage.success(`代码 "${code.title}" 导出成功`)
    
  } catch (error) {
    console.error('代码导出失败:', error)
    ElMessage.error('代码导出失败，请重试')
  }
}

/**
 * 批量导出代码为ZIP文件
 */
export async function exportMultipleCodes(
  codes: Code[], 
  format: ExportFormat = ExportFormat.SOURCE,
  zipFilename: string = 'codes_export'
): Promise<void> {
  if (codes.length === 0) {
    ElMessage.warning('没有可导出的代码')
    return
  }

  try {
    const zip = new JSZip()
    
    // 按分类创建文件夹结构
    const folderMap = new Map<string, JSZip>()
    
    for (const code of codes) {
      // 确定文件夹名称
      const folderName = code.user_category?.name || 
                        code.category?.name || 
                        '未分类'
      
      // 获取或创建文件夹
      if (!folderMap.has(folderName)) {
        folderMap.set(folderName, zip.folder(sanitizeFilename(folderName))!)
      }
      const folder = folderMap.get(folderName)!
      
      // 生成文件内容
      const extension = getFileExtension(code.language, format)
      const filename = `${sanitizeFilename(code.title)}_${code.id}${extension}`
      
      let content: string
      switch (format) {
        case ExportFormat.SOURCE:
          content = generateSourceContent(code)
          break
        case ExportFormat.MARKDOWN:
          content = generateMarkdownContent(code)
          break
        case ExportFormat.JSON:
          content = generateJsonContent(code)
          break
        default:
          content = generateSourceContent(code)
      }
      
      folder.file(filename, content)
    }

    // 添加导出信息文件
    const exportInfo = generateExportInfo(codes, format)
    zip.file('导出信息.md', exportInfo)

    // 生成ZIP文件并下载
    const zipContent = await zip.generateAsync({ type: 'blob' })
    const zipUrl = URL.createObjectURL(zipContent)
    
    const link = document.createElement('a')
    link.href = zipUrl
    link.download = `${sanitizeFilename(zipFilename)}_${new Date().toISOString().split('T')[0]}.zip`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    
    URL.revokeObjectURL(zipUrl)
    ElMessage.success(`成功导出 ${codes.length} 个代码文件`)
    
  } catch (error) {
    console.error('批量导出失败:', error)
    ElMessage.error('批量导出失败，请重试')
  }
}

/**
 * 生成源码格式内容
 */
function generateSourceContent(code: Code): string {
  const header = `# ${code.title}
# 作者: ${code.author.username}
# 创建时间: ${new Date(code.created_at).toLocaleString('zh-CN')}
# 语言: ${code.language}
${code.description ? `# 描述: ${code.description}` : ''}
${code.tags?.length ? `# 标签: ${code.tags.map(t => t.name).join(', ')}` : ''}

`
  
  return header + code.content
}

/**
 * 生成Markdown格式内容
 */
function generateMarkdownContent(code: Code): string {
  const tags = code.tags?.map(t => `\`${t.name}\``).join(' ') || ''
  
  return `# ${code.title}

## 基本信息

- **作者**: ${code.author.username}
- **创建时间**: ${new Date(code.created_at).toLocaleString('zh-CN')}
- **编程语言**: ${code.language}
- **分类**: ${code.user_category?.name || code.category?.name || '未分类'}
${tags ? `- **标签**: ${tags}` : ''}

## 代码描述

${code.description || '暂无描述'}

## 源代码

\`\`\`${code.language.toLowerCase()}
${code.content}
\`\`\`

---

*导出时间: ${new Date().toLocaleString('zh-CN')}*
`
}

/**
 * 生成JSON格式内容
 */
function generateJsonContent(code: Code): string {
  const exportData = {
    id: code.id,
    title: code.title,
    description: code.description,
    content: code.content,
    language: code.language,
    category: code.category?.name,
    user_category: code.user_category?.name,
    author: code.author.username,
    created_at: code.created_at,
    tags: code.tags?.map(t => t.name) || [],
    exported_at: new Date().toISOString()
  }
  
  return JSON.stringify(exportData, null, 2)
}

/**
 * 生成导出信息文档
 */
function generateExportInfo(codes: Code[], format: ExportFormat): string {
  const categories = new Set<string>()
  const languages = new Set<string>()
  
  codes.forEach(code => {
    categories.add(code.user_category?.name || code.category?.name || '未分类')
    languages.add(code.language)
  })
  
  return `# 代码导出信息

## 导出统计

- **导出时间**: ${new Date().toLocaleString('zh-CN')}
- **导出格式**: ${format}
- **代码总数**: ${codes.length} 个
- **涉及分类**: ${Array.from(categories).join(', ')}
- **编程语言**: ${Array.from(languages).join(', ')}

## 文件结构

代码文件按分类组织在不同文件夹中：

${Array.from(categories).map(category => {
  const categoryCount = codes.filter(code => 
    (code.user_category?.name || code.category?.name || '未分类') === category
  ).length
  return `- **${category}**: ${categoryCount} 个文件`
}).join('\n')}

## 使用说明

1. **源码文件**: 可直接运行或编辑
2. **Markdown文件**: 包含完整的元数据信息
3. **JSON文件**: 适合程序处理和数据交换

---

*由代码分享平台自动生成*
`
}

/**
 * 按用户分类导出
 */
export async function exportByUserCategory(
  categoryName: string,
  codes: Code[],
  format: ExportFormat = ExportFormat.SOURCE
): Promise<void> {
  const filteredCodes = codes.filter(code => 
    code.user_category?.name === categoryName
  )
  
  if (filteredCodes.length === 0) {
    ElMessage.warning(`分类 "${categoryName}" 中没有代码可导出`)
    return
  }
  
  await exportMultipleCodes(
    filteredCodes, 
    format, 
    `用户分类_${categoryName}`
  )
}

/**
 * 按编程语言导出
 */
export async function exportByLanguage(
  language: string,
  codes: Code[],
  format: ExportFormat = ExportFormat.SOURCE
): Promise<void> {
  const filteredCodes = codes.filter(code => code.language === language)
  
  if (filteredCodes.length === 0) {
    ElMessage.warning(`没有 ${language} 语言的代码可导出`)
    return
  }
  
  await exportMultipleCodes(
    filteredCodes, 
    format, 
    `${language}_代码集合`
  )
}
