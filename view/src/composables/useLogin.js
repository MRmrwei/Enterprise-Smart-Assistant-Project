import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { setToken } from '../utils/auth'
import { post } from '../utils/request'

export function useLogin() {
  const router = useRouter()

  const loginForm = reactive({ username: '', password: '' })

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

  async function handleLogin() {
    if (!loginFormRef.value) return
    try {
      await loginFormRef.value.validate()
    } catch {
      return
    }

    loading.value = true
    const payload = { account: loginForm.username, password: loginForm.password }

    try {
      const result = await post('/login', payload, { skipAuth: true })

      if (result.token) {
        setToken(result.token)
        ElMessage({ message: '登录成功，正在跳转...', type: 'success', duration: 1500 })
        setTimeout(() => router.push('/home'), 500)
      } else {
        ElMessage({
          message: result.response?.message || result.message || '登录失败，请检查账号密码',
          type: 'error', duration: 4000,
        })
      }
    } catch (error) {
      ElMessage({ message: error.message || '网络异常，请检查后端服务', type: 'error', duration: 4000 })
    } finally {
      loading.value = false
    }
  }

  return { loginForm, loginRules, loading, loginFormRef, handleLogin }
}
