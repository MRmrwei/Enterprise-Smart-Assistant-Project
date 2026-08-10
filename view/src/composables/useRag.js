import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { upload as uploadFile } from '../utils/request'

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

export function useRag() {
  // ---- 表单 ----
  const form = reactive({ docType: '', department: '', version: '', files: [] })

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

  // ---- DOM 引用 ----
  const formRef = ref(null)
  const fileInput = ref(null)

  // ---- 文件操作 ----
  function triggerUpload() {
    fileInput.value?.click()
  }

  function handleFileChange(e) {
    const files = e.target.files
    if (!files || files.length === 0) return
    for (let i = 0; i < files.length; i++) {
      const f = files[i]
      if (!f.name.toLowerCase().endsWith('.txt')) { ElMessage.warning(`文件 "${f.name}" 不是 TXT 格式，已跳过`); continue }
      if (form.files.some(item => item.name === f.name && item.size === f.size)) { ElMessage.warning(`文件 "${f.name}" 已存在，已跳过`); continue }
      form.files.push(f)
    }
    if (fileInput.value) fileInput.value.value = ''
  }

  function removeFile(index) {
    form.files.splice(index, 1)
  }

  function formatSize(bytes) {
    if (!bytes) return '0 B'
    const units = ['B', 'KB', 'MB', 'GB']
    let i = 0, size = bytes
    while (size >= 1024 && i < units.length - 1) { size /= 1024; i++ }
    return size.toFixed(i === 0 ? 0 : 1) + ' ' + units[i]
  }

  // ---- 提交 ----
  function submitImport() {
    formRef.value.validate((valid) => {
      if (!valid) return
      if (form.files.length === 0) { ElMessage.warning('请至少选择一个文档'); return }

      uploading.value = true
      progressPercent.value = 0
      progressStatus.value = ''
      progressText.value = '正在准备...'
      importResult.value = null

      const total = form.files.length
      let successCount = 0, failCount = 0
      const promises = []

      for (let i = 0; i < form.files.length; i++) {
        const file = form.files[i]
        const fd = new FormData()
        fd.append('doc_type', form.docType)
        fd.append('department', form.department)
        fd.append('version', form.version)
        fd.append('file', file)

        const p = uploadFile('/api/rag/documents/upload', fd)
          .then(data => {
            successCount++
            progressPercent.value = Math.round((successCount + failCount) / total * 100)
            progressText.value = `已处理 ${successCount + failCount} / ${total}`
            return { ok: true, file: file.name, data }
          })
          .catch(err => {
            failCount++
            progressPercent.value = Math.round((successCount + failCount) / total * 100)
            progressText.value = `已处理 ${successCount + failCount} / ${total}`
            return { ok: false, file: file.name, error: err.message }
          })
        promises.push(p)
      }

      Promise.all(promises).then(results => {
        uploading.value = false
        progressStatus.value = failCount === 0 ? 'success' : 'exception'
        const msg = `导入完成：成功 ${successCount} 个` + (failCount > 0 ? `，失败 ${failCount} 个` : '')
        importResult.value = { success: failCount === 0, message: msg }
        if (failCount === 0) ElMessage.success(msg)
        else { ElMessage.warning(msg); results.forEach(r => { if (!r.ok) console.error('上传失败:', r.file, r.error) }) }
      })
    })
  }

  function resetForm() {
    form.docType = ''; form.department = ''; form.version = ''; form.files = []
    uploading.value = false; progressPercent.value = 0; progressStatus.value = ''
    progressText.value = ''; importResult.value = null
    formRef.value?.clearValidate()
  }

  return {
    docTypes,
    departments,
    form,
    rules,
    uploading,
    progressPercent,
    progressStatus,
    progressText,
    importResult,
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
