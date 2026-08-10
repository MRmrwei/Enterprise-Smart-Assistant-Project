<template>
  <div class="rag-page">
    <div class="page-wrapper">
      <div class="page-card">
        <!-- 头部 -->
        <div class="page-header">
          <div class="icon-wrap">
            <el-icon><Upload /></el-icon>
          </div>
          <div>
            <h1>文档导入 · 向量数据库</h1>
            <div class="subtitle">将 TXT 文档向量化存入 RAG 知识库</div>
          </div>
        </div>

        <!-- 表单 -->
        <el-form
          ref="formRef"
          :model="form"
          :rules="rules"
          label-width="100px"
          label-position="right"
          size="default"
        >
          <!-- 文档类型 -->
          <el-form-item label="文档类型" prop="docType">
            <el-select v-model="form.docType" placeholder="请选择文档类型" style="width: 100%" clearable>
              <el-option v-for="item in docTypes" :key="item.value" :label="item.label" :value="item.value" />
            </el-select>
          </el-form-item>

          <!-- 所属部门 -->
          <el-form-item label="所属部门" prop="department">
            <el-select v-model="form.department" placeholder="请选择所属部门" style="width: 100%" clearable>
              <el-option v-for="item in departments" :key="item.value" :label="item.label" :value="item.value" />
            </el-select>
          </el-form-item>

          <!-- 版本号 -->
          <el-form-item label="版本号" prop="version">
            <el-input v-model="form.version" placeholder="请输入版本号，例如 1.0、2.3.1" clearable />
          </el-form-item>

          <!-- 多文件上传 -->
          <el-form-item label="选择文档" prop="files">
            <div class="upload-area" @click="triggerUpload" v-if="form.files.length === 0">
              <div class="upload-icon">
                <el-icon><FolderOpened /></el-icon>
              </div>
              <div class="upload-text">点击此处选择文档</div>
              <div class="upload-hint">仅支持 .txt 文本文件，可多选</div>
            </div>

            <div style="width: 100%" v-if="form.files.length > 0">
              <div class="file-list">
                <div class="file-item" v-for="(file, index) in form.files" :key="index">
                  <div class="file-info">
                    <el-icon class="file-icon"><Document /></el-icon>
                    <span class="file-name">{{ file.name }}</span>
                    <span class="file-size">{{ formatSize(file.size) }}</span>
                  </div>
                  <el-icon class="file-remove" @click="removeFile(index)"><Close /></el-icon>
                </div>
              </div>
              <el-button type="primary" plain size="small" :icon="Plus" @click="triggerUpload" style="margin-top: 8px">
                继续添加文档
              </el-button>
            </div>

            <input ref="fileInput" type="file" accept=".txt" multiple style="display: none" @change="handleFileChange" />
          </el-form-item>

          <!-- 提交 -->
          <el-form-item label=" ">
            <div style="width: 100%">
              <div class="submit-section">
                <el-button
                  type="primary" class="submit-btn"
                  :loading="uploading" :disabled="form.files.length === 0"
                  @click="submitImport" :icon="Upload"
                >
                  {{ uploading ? '导入中...' : '开始导入到向量数据库' }}
                </el-button>
                <el-button class="submit-btn" style="flex: 0.4" @click="resetForm" :disabled="uploading">
                  重置
                </el-button>
              </div>
              <div class="progress-wrap" v-if="uploading">
                <el-progress :percentage="progressPercent" :status="progressStatus" :stroke-width="16" :text-inside="true" />
                <div style="margin-top: 6px; font-size: 13px; color: #909399; text-align: center">
                  {{ progressText }}
                </div>
              </div>
            </div>
          </el-form-item>
        </el-form>

        <!-- 导入结果 -->
        <div class="result-panel" v-if="importResult">
          <el-alert
            :title="importResult.message"
            :type="importResult.success ? 'success' : 'error'"
            :closable="true" show-icon
            @close="importResult = null"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Upload, FolderOpened, Document, Close, Plus } from '@element-plus/icons-vue'
import { getToken, removeToken } from '../utils/auth'

const router = useRouter()

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

const uploading = ref(false)
const progressPercent = ref(0)
const progressStatus = ref('')
const progressText = ref('')
const importResult = ref(null)
const formRef = ref(null)
const fileInput = ref(null)

onMounted(() => { if (!getToken()) router.push('/login') })

const triggerUpload = () => fileInput.value?.click()

const handleFileChange = (e) => {
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

const removeFile = (index) => form.files.splice(index, 1)

const formatSize = (bytes) => {
  if (!bytes) return '0 B'
  const units = ['B', 'KB', 'MB', 'GB']
  let i = 0, size = bytes
  while (size >= 1024 && i < units.length - 1) { size /= 1024; i++ }
  return size.toFixed(i === 0 ? 0 : 1) + ' ' + units[i]
}

const submitImport = () => {
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

      const p = fetch('/api/rag/documents/upload', {
        method: 'POST',
        headers: { 'Authorization': 'Bearer ' + getToken() },
        body: fd,
      })
        .then(res => {
          if (res.status === 401 || res.status === 403) { removeToken(); router.push('/login'); throw new Error('登录已过期') }
          if (!res.ok) throw new Error('HTTP ' + res.status)
          return res.json()
        })
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

const resetForm = () => {
  form.docType = ''; form.department = ''; form.version = ''; form.files = []
  uploading.value = false; progressPercent.value = 0; progressStatus.value = ''
  progressText.value = ''; importResult.value = null
  formRef.value?.clearValidate()
}
</script>

<style scoped>
@import '../styles/rag.css';
</style>
