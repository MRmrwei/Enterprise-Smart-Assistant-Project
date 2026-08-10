<template>
  <div class="nav-page">
    <!-- 功能入口 -->
    <div class="main-content">
      <div class="card-grid">
        <!-- 对话助手 -->
        <router-link class="nav-card chat" to="/chat">
          <div class="card-icon">
            <el-icon><ChatDotRound /></el-icon>
          </div>
          <h2>AI 对话助手</h2>
          <p>智能问答、文档分析、代码辅助等对话式 AI 服务</p>
          <div class="card-arrow">
            <el-icon><ArrowRight /></el-icon>
          </div>
        </router-link>

        <!-- 文档导入 -->
        <router-link class="nav-card rag" to="/rag">
          <div class="card-icon">
            <el-icon><Upload /></el-icon>
          </div>
          <h2>RAG 文档导入</h2>
          <p>将 TXT 文档向量化导入知识库，增强 AI 检索能力</p>
          <div class="card-arrow">
            <el-icon><ArrowRight /></el-icon>
          </div>
        </router-link>
      </div>
    </div>

    <!-- 页脚 -->
    <div class="page-footer">
      &copy; 2026 企业智能助手 · Enterprise Smart Assistant
    </div>
  </div>
</template>

<script setup>
import { ChatDotRound, Upload, ArrowRight } from '@element-plus/icons-vue'
</script>

<style scoped>
@import '../styles/nav.css';
</style>
