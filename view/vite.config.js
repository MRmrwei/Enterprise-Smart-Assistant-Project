import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const backend = env.VITE_BACKEND_URL || 'http://127.0.0.1:8888'

  return {
    plugins: [vue()],
    server: {
      port: parseInt(env.VITE_PORT) || 5173,
      proxy: {
        // 登录 API — 只代理 POST，GET 留给 SPA 路由（否则 F5 刷新白屏）
        '/login': {
          target: backend,
          bypass: (req) => req.method === 'GET' ? req.url : null,
        },
        '/logout': backend,
        // 对话 SSE — 只代理 POST，GET 留给 SPA 路由
        '/chat': {
          target: backend,
          bypass: (req) => req.method === 'GET' ? req.url : null,
        },
        '/upload_rag_file': backend,
        '/api': backend,
      },
    },
    build: {
      outDir: 'dist',
    },
  }
})
