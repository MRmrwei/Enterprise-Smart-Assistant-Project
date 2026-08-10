<template>
  <div class="login-page">
    <div class="login-container">
      <div class="login-title">
        <span>用户登录</span>
      </div>

      <el-form
        ref="loginFormRef"
        :model="loginForm"
        :rules="loginRules"
        label-width="0"
        status-icon
        @submit.native.prevent="handleLogin"
      >
        <el-form-item prop="username">
          <el-input
            v-model="loginForm.username"
            placeholder="请输入账号"
            :prefix-icon="User"
            clearable
            size="large"
            @keyup.enter="handleLogin"
          />
        </el-form-item>

        <el-form-item prop="password">
          <el-input
            v-model="loginForm.password"
            placeholder="请输入密码"
            :prefix-icon="Lock"
            show-password
            clearable
            size="large"
            @keyup.enter="handleLogin"
          />
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            size="large"
            :loading="loading"
            @click="handleLogin"
          >
            {{ loading ? '登录中...' : '登 录' }}
          </el-button>
        </el-form-item>
      </el-form>

      <div class="login-footer">
        <span>演示 · 账号密码任意 (非空即可)</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'
import { getToken, setToken } from '../utils/auth'

const router = useRouter()

const loginForm = reactive({
  username: '',
  password: '',
})

const loginRules = {
  username: [
    { required: true, message: '请输入账号', trigger: 'blur' },
    { min: 1, message: '账号不能为空', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 1, message: '密码不能为空', trigger: 'blur' },
  ],
}

const loading = ref(false)
const loginFormRef = ref(null)

const handleLogin = async () => {
  if (!loginFormRef.value) return
  try {
    await loginFormRef.value.validate()
  } catch {
    return
  }

  loading.value = true
  const payload = {
    account: loginForm.username,
    password: loginForm.password,
  }

  try {
    const response = await fetch('/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })

    const result = await response.json()

    if (response.ok && result.token) {
      setToken(result.token)

      ElMessage({
        message: '登录成功，正在跳转...',
        type: 'success',
        duration: 1500,
      })

      setTimeout(() => {
        router.push('/home')
      }, 500)
    } else {
      const errMsg = result.response?.message || result.message || '登录失败，请检查账号密码'
      ElMessage({
        message: errMsg,
        type: 'error',
        duration: 4000,
      })
    }
  } catch (error) {
    ElMessage({
      message: `网络异常: ${error.message || '请检查后端服务'}`,
      type: 'error',
      duration: 4000,
    })
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  const token = getToken()
  if (token) {
    router.push('/home')
  }
})
</script>

<style scoped>
@import '../styles/login.css';
</style>
