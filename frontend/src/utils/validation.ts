import { ref, computed, readonly } from 'vue'

// 表单验证工具
export interface ValidationRule {
  validator: (value: any) => boolean
  message: string
}

export interface ValidationResult {
  valid: boolean
  message?: string
}

// 常用验证规则
export const validationRules = {
  required: (message = '此字段为必填项'): ValidationRule => ({
    validator: (value: any) => value !== null && value !== undefined && value !== '',
    message
  }),

  email: (message = '请输入有效的邮箱地址'): ValidationRule => ({
    validator: (value: string) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value),
    message
  }),

  minLength: (length: number, message?: string): ValidationRule => ({
    validator: (value: string) => Boolean(value && value.length >= length),
    message: message || `长度至少为${length}位`
  }),

  password: (message = '密码至少6位，包含字母和数字'): ValidationRule => ({
    validator: (value: string) => /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@$!%*#?&]{6,}$/.test(value),
    message
  }),

  username: (message = '用户名3-20位，仅含字母数字下划线'): ValidationRule => ({
    validator: (value: string) => /^[a-zA-Z0-9_]{3,20}$/.test(value),
    message
  })
}

// 验证单个字段
export const validateField = (value: any, rules: ValidationRule[]): ValidationResult => {
  for (const rule of rules) {
    if (!rule.validator(value)) {
      return { valid: false, message: rule.message }
    }
  }
  return { valid: true }
}

// 验证整个表单
export const validateForm = (formData: Record<string, any>, ruleMap: Record<string, ValidationRule[]>): {
  valid: boolean
  errors: Record<string, string>
} => {
  const errors: Record<string, string> = {}
  let allValid = true

  for (const [field, rules] of Object.entries(ruleMap)) {
    const result = validateField(formData[field], rules)
    if (!result.valid) {
      errors[field] = result.message!
      allValid = false
    }
  }

  return { valid: allValid, errors }
}

// 实时验证 hook
export const useFormValidation = () => {
  const errors = ref<Record<string, string>>({})
  
  const validateFieldRealtime = (field: string, value: any, rules: ValidationRule[]) => {
    const result = validateField(value, rules)
    if (result.valid) {
      delete errors.value[field]
    } else {
      errors.value[field] = result.message!
    }
    return result.valid
  }

  const clearError = (field: string) => {
    delete errors.value[field]
  }

  const hasErrors = computed(() => Object.keys(errors.value).length > 0)

  return {
    errors: readonly(errors),
    validateFieldRealtime,
    clearError,
    hasErrors
  }
}
