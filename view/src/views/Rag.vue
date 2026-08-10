<template>
  <div class="rag-page">
    <div class="page-wrapper">
      <div class="page-card">
        <div class="page-header">
          <div class="icon-wrap"><el-icon><Upload /></el-icon></div>
          <div>
            <h1>文档导入 · 向量数据库</h1>
            <div class="subtitle">将 TXT 文档向量化存入 RAG 知识库</div>
          </div>
        </div>

        <el-form ref="formRef" :model="form" :rules="rules" label-width="100px" label-position="right" size="default">
          <el-form-item label="文档类型" prop="docType">
            <el-select v-model="form.docType" placeholder="请选择文档类型" style="width: 100%" clearable>
              <el-option v-for="item in docTypes" :key="item.value" :label="item.label" :value="item.value" />
            </el-select>
          </el-form-item>

          <el-form-item label="所属部门" prop="department">
            <el-select v-model="form.department" placeholder="请选择所属部门" style="width: 100%" clearable>
              <el-option v-for="item in departments" :key="item.value" :label="item.label" :value="item.value" />
            </el-select>
          </el-form-item>

          <el-form-item label="版本号" prop="version">
            <el-input v-model="form.version" placeholder="请输入版本号，例如 1.0、2.3.1" clearable />
          </el-form-item>

          <el-form-item label="选择文档" prop="files">
            <div class="upload-area" @click="triggerUpload" v-if="form.files.length === 0">
              <div class="upload-icon"><el-icon><FolderOpened /></el-icon></div>
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

          <el-form-item label=" ">
            <div style="width: 100%">
              <div class="submit-section">
                <el-button type="primary" class="submit-btn" :loading="uploading" :disabled="form.files.length === 0"
                  @click="submitImport" :icon="Upload">
                  {{ uploading ? '导入中...' : '开始导入到向量数据库' }}
                </el-button>
                <el-button class="submit-btn" style="flex: 0.4" @click="resetForm" :disabled="uploading">重置</el-button>
              </div>
              <div class="progress-wrap" v-if="uploading">
                <el-progress :percentage="progressPercent" :status="progressStatus" :stroke-width="16" :text-inside="true" />
                <div style="margin-top: 6px; font-size: 13px; color: #909399; text-align: center">{{ progressText }}</div>
              </div>
            </div>
          </el-form-item>
        </el-form>

        <div class="result-panel" v-if="importResult">
          <el-alert :title="importResult.message" :type="importResult.success ? 'success' : 'error'"
            :closable="true" show-icon @close="importResult = null" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Upload, FolderOpened, Document, Close, Plus } from '@element-plus/icons-vue'
import { useRag } from '../composables/useRag'

const {
  docTypes, departments,
  form, rules,
  uploading, progressPercent, progressStatus, progressText, importResult,
  formRef, fileInput,
  triggerUpload, handleFileChange, removeFile, formatSize, submitImport, resetForm,
} = useRag()
</script>

<style scoped>
@import '../styles/rag.css';
</style>
