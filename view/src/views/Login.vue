<template>
  <div class="login-page">
    <div class="login-container">
      <div class="login-title"><span>用户登录</span></div>

      <el-form ref="loginFormRef" :model="loginForm" :rules="loginRules" label-width="0"
        status-icon @submit.native.prevent="handleLogin">
        <el-form-item prop="username">
          <el-input v-model="loginForm.username" placeholder="请输入账号" :prefix-icon="User"
            clearable size="large" @keyup.enter="handleLogin" />
        </el-form-item>
        <el-form-item prop="password">
          <el-input v-model="loginForm.password" placeholder="请输入密码" :prefix-icon="Lock"
            show-password clearable size="large" @keyup.enter="handleLogin" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" size="large" :loading="loading" @click="handleLogin">
            {{ loading ? '登录中...' : '登 录' }}
          </el-button>
        </el-form-item>
      </el-form>

      <div class="login-footer"><span>演示 · 账号密码任意 (非空即可)</span></div>
    </div>
  </div>
</template>

<script setup>
import { User, Lock } from '@element-plus/icons-vue'
import { useLogin } from '../composables/useLogin'

const { loginForm, loginRules, loading, loginFormRef, handleLogin } = useLogin()
</script>

<style scoped>
@import '../styles/login.css';
</style>
