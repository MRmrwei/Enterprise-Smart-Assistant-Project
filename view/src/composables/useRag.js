import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { getToken, removeToken } from '../utils/auth'

const MAX_FILES = 10

// 下拉选项（业务数据，不依赖响应式）
const docTypes = [
  { label: '规章制度', value: 'regulation' },
  { label: '操作手册', value: 'manual' },
  { label: '技术文档', value: 'tech_doc' },
  { label: '会议纪要', value: 'meeting_minutes' },
  { label: '培训资料', value: 'training' },
  { label: '其他文档', value: 'other' },
]

const departments = [
  { label: '技术部', value: 'tech' },
  { label: '产品部', value: 'product' },
  { label: '运营部', value: 'operation' },
  { label: '市场部', value: 'marketing' },
  { label: '人力资源部', value: 'hr' },
  { label: '财务部', value: 'finance' },
]

const chunkStrategies = [
  { label: '父子块', value: 'parent_child' },
  { label: '通用', value: 'general' },
]

export function useRag() {
  // ---- 表单 ----
  const form = reactive({ docType: '', department: '', version: '', chunkStrategy: '', files: [] })

  const validateVersion = (rule, value, callback) => {
    if (!value) callback(new Error('请输入版本号'))
    else if (!/^\d+(\.\d+)*$/.test(value)) callback(new Error('版本号格式不正确，例如 1.0、2.3.1'))
    else callback()
  }

  const rules = {
    docType: [{ required: true, message: '请选择文档类型', trigger: 'change' }],
    department: [{ required: true, message: '请选择所属部门', trigger: 'change' }],
    version: [{ required: true, validator: validateVersion, trigger: 'blur' }],
  }

  // ---- 上传状态 ----
  const uploading = ref(false)
  const progressPercent = ref(0)
  const progressStatus = ref('')
  const progressText = ref('')
  const importResult = ref(null)
  const fileErrors = reactive({})  // { filename: errorMessage }

  // ---- DOM 引用 ----
  const formRef = ref(null)
  const fileInput = ref(null)

  // ---- 文件操作 ----
  function triggerUpload() {
    if (form.files.length >= MAX_FILES) {
      ElMessage.warning(`最多只能上传 ${MAX_FILES} 个文件`)
      return
    }
    fileInput.value?.click()
  }

  function handleFileChange(e) {
    const files = e.target.files
    if (!files || files.length === 0) return

    const remaining = MAX_FILES - form.files.length
    if (files.length > remaining) {
      ElMessage.warning(`还能添加 ${remaining} 个文件，当前选择了 ${files.length} 个，超出的文件将被跳过`)
    }

    for (let i = 0; i < Math.min(files.length, remaining); i++) {
      const f = files[i]
      if (!f.name.toLowerCase().endsWith('.txt')) { ElMessage.warning(`文件 "${f.name}" 不是 TXT 格式，已跳过`); continue }
      if (form.files.some(item => item.name === f.name && item.size === f.size)) { ElMessage.warning(`文件 "${f.name}" 已存在，已跳过`); continue }
      form.files.push(f)
    }

    if (fileInput.value) fileInput.value.value = ''
  }

  function removeFile(index) {
    const f = form.files[index]
    if (f) delete fileErrors[f.name]
    form.files.splice(index, 1)
  }

  function formatSize(bytes) {
    if (!bytes) return '0 B'
    const units = ['B', 'KB', 'MB', 'GB']
    let i = 0, size = bytes
    while (size >= 1024 && i < units.length - 1) { size /= 1024; i++ }
    return size.toFixed(i === 0 ? 0 : 1) + ' ' + units[i]
  }

  // ---- 提交（XMLHttpRequest 实现上传进度） ----
  function submitImport() {
    formRef.value.validate((valid) => {
      if (!valid) return
      if (form.files.length === 0) { ElMessage.warning('请至少选择一个文档'); return }

      uploading.value = true
      progressPercent.value = 0
      progressStatus.value = ''
      progressText.value = '正在上传...'
      importResult.value = null

      // 构建 FormData
      const fd = new FormData()
      fd.append('doc_type', form.docType)
      fd.append('department', form.department)
      fd.append('version', form.version)
      fd.append('chunk_strategy', form.chunkStrategy)
      for (let i = 0; i < form.files.length; i++) {
        fd.append('files', form.files[i])
      }

      // 使用 XMLHttpRequest 以获取上传进度
      const xhr = new XMLHttpRequest()

      xhr.upload.addEventListener('progress', (e) => {
        if (e.lengthComputable) {
          const pct = Math.round((e.loaded / e.total) * 100)
          progressPercent.value = pct
          progressText.value = `上传中 ${pct}%`
        }
      })

      xhr.addEventListener('load', () => {
        if (xhr.status === 401 || xhr.status === 403) {
          removeToken()
          window.location.href = '/login'
          uploading.value = false
          return
        }

        if (xhr.status >= 200 && xhr.status < 300) {
          progressPercent.value = 100
          progressStatus.value = 'success'

          let body
          try { body = JSON.parse(xhr.responseText) } catch (e) { body = {} }

          const results = body.data?.results || []

          // 记录每个文件的错误信息
          for (const r of results) {
            if (!r.success) {
              fileErrors[r.filename] = r.error || '未知错误'
            } else {
              delete fileErrors[r.filename]
            }
          }

          const failedNames = new Set(
            results.filter(r => !r.success).map(r => r.filename)
          )

          // 移除已成功的文件，只保留失败的让用户重新上传
          form.files = form.files.filter(f => failedNames.has(f.name))

          const msg = body.message || '导入完成'
          progressText.value = msg
          ElMessage.success(msg)
        } else {
          progressStatus.value = 'exception'

          let detail = `请求失败 (${xhr.status})`
          try { const body = JSON.parse(xhr.responseText); detail = body.detail || body.message || detail } catch (e) {}

          progressText.value = detail
          importResult.value = { success: false, message: detail }
          ElMessage.error(detail)
        }

        uploading.value = false
      })

      xhr.addEventListener('error', () => {
        uploading.value = false
        progressStatus.value = 'exception'
        progressText.value = '网络错误，上传失败'
        importResult.value = { success: false, message: '网络错误，上传失败' }
        ElMessage.error('网络错误，上传失败')
      })

      xhr.addEventListener('abort', () => {
        uploading.value = false
        progressStatus.value = 'exception'
        progressText.value = '上传已取消'
      })

      xhr.addEventListener('timeout', () => {
        uploading.value = false
        progressStatus.value = 'exception'
        progressText.value = '处理超时，请稍后重试'
        importResult.value = { success: false, message: '处理超时，请稍后重试' }
        ElMessage.error('处理超时，请稍后重试')
      })

      // 设置认证头
      const token = getToken()
      xhr.open('POST', '/upload_rag_file')
      xhr.timeout = 5 * 60 * 1000  // 5 分钟超时
      if (token) xhr.setRequestHeader('Authorization', 'Bearer ' + token)

      xhr.send(fd)
    })
  }

  function resetForm() {
    form.docType = ''; form.department = ''; form.version = ''; form.chunkStrategy = ''; form.files = []
    uploading.value = false; progressPercent.value = 0; progressStatus.value = ''
    progressText.value = ''; importResult.value = null
    Object.keys(fileErrors).forEach(k => delete fileErrors[k])
    formRef.value?.clearValidate()
  }

  return {
    MAX_FILES,
    docTypes,
    departments,
    chunkStrategies,
    form,
    rules,
    uploading,
    progressPercent,
    progressStatus,
    progressText,
    importResult,
    fileErrors,
    formRef,
    fileInput,
    triggerUpload,
    handleFileChange,
    removeFile,
    formatSize,
    submitImport,
    resetForm,
  }
}
