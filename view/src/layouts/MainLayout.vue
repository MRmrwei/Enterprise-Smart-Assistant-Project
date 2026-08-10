<template>
  <div class="app-shell">
    <!-- ===== 全局顶栏 ===== -->
    <header class="topbar">
      <div class="topbar-left">
        <div class="brand" @click="$router.push('/home')">
          <div class="logo-icon">
            <el-icon><Cpu /></el-icon>
          </div>
          <h1>企业智能助手</h1>
        </div>
        <nav class="topbar-nav">
          <router-link to="/chat" class="nav-tab" active-class="active">
            <el-icon><ChatDotRound /></el-icon>
            <span>AI 对话</span>
          </router-link>
          <router-link to="/rag" class="nav-tab" active-class="active">
            <el-icon><Upload /></el-icon>
            <span>文档导入</span>
          </router-link>
        </nav>
      </div>
      <div class="topbar-right">
        <span class="user-name">
          <el-icon><UserFilled /></el-icon>
          已登录
        </span>
        <el-button class="logout-btn" size="small" @click="handleLogout" :loading="loggingOut">
          <el-icon><SwitchButton /></el-icon>
          {{ loggingOut ? '退出中...' : '退出登录' }}
        </el-button>
      </div>
    </header>

    <!-- ===== 页面内容 ===== -->
    <main class="shell-main">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Cpu, ChatDotRound, Upload, UserFilled, SwitchButton } from '@element-plus/icons-vue'
import { removeToken } from '../utils/auth'
import { post } from '../utils/request'

const router = useRouter()
const loggingOut = ref(false)

const handleLogout = () => {
  loggingOut.value = true
  post('/logout', {})
    .catch(() => {})
    .finally(() => {
      removeToken()
      loggingOut.value = false
      ElMessage({ message: '已退出登录', type: 'success', duration: 1500 })
      setTimeout(() => router.push('/login'), 300)
    })
}
</script>

<style scoped>
/* ========== 整体壳层 ========== */
.app-shell {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background: #f0f2f5;
}

/* ========== 顶栏 ========== */
.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 56px;
  padding: 0 28px;
  background: #fff;
  border-bottom: 1px solid #e8ecf1;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
  flex-shrink: 0;
  z-index: 100;
}

.topbar-left {
  display: flex;
  align-items: center;
  gap: 32px;
}

/* 品牌 */
.brand {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}
.brand .logo-icon {
  width: 34px;
  height: 34px;
  border-radius: 8px;
  background: linear-gradient(135deg, #409EFF, #337ecc);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  color: #fff;
}
.brand h1 {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  white-space: nowrap;
}

/* 导航标签 */
.topbar-nav {
  display: flex;
  gap: 4px;
}
.nav-tab {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 7px 16px;
  border-radius: 8px;
  font-size: 13px;
  color: #606266;
  text-decoration: none;
  transition: all 0.2s;
  font-weight: 500;
}
.nav-tab:hover {
  color: #409EFF;
  background: #ecf5ff;
}
.nav-tab.active {
  color: #409EFF;
  background: #ecf5ff;
  font-weight: 600;
}

/* 右侧用户区 */
.topbar-right {
  display: flex;
  align-items: center;
  gap: 14px;
}
.user-name {
  font-size: 13px;
  color: #909399;
  display: flex;
  align-items: center;
  gap: 4px;
}
.logout-btn {
  font-size: 12px;
}

/* ========== 内容区 ========== */
.shell-main {
  flex: 1;
  display: flex;
  flex-direction: column;
}
</style>
