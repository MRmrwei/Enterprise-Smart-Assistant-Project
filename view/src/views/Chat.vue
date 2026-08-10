<template>
  <div class="chat-page">
    <!-- 页面标题栏（轻量） -->
    <div class="chat-titlebar">
      <div class="titlebar-left">
        <span class="title-icon">✦</span>
        <h2>AI 对话助手</h2>
      </div>
      <div class="status-tag">
        <span class="dot"></span>
        <span>在线 · SSE 流式</span>
      </div>
    </div>

    <!-- 消息区 -->
    <main class="app-main" ref="mainContainer">
      <div class="messages">
        <div v-if="messages.length === 0" class="empty-state">
          <div class="empty-icon">💬</div>
          <div class="empty-text">开始你的第一次对话</div>
          <div class="empty-sub">输入问题，AI 将流式展示推理过程</div>
        </div>

        <div v-for="(msg, idx) in messages" :key="idx" class="message" :class="msg.type">
          <div class="avatar">
            {{ msg.type === 'ai' ? 'AI' : '我' }}
          </div>
          <div class="bubble">
            <template v-if="msg.type === 'user'">
              <div class="text">{{ msg.content }}</div>
            </template>
            <template v-if="msg.type === 'ai'">
              <div v-if="msg.thinking" class="thinking-placeholder">
                <span>正在思考</span>
                <span class="dots">
                  <span></span><span></span><span></span>
                </span>
              </div>
              <div class="ai-reply">
                <div v-if="msg.reasoning && msg.reasoning.length > 0">
                  <div class="reasoning-section">
                    <span class="label"><span>🧠 推理过程</span></span>
                    <span class="divider"></span>
                  </div>
                  <div class="reasoning-blocks">
                    <div v-for="(block, bi) in msg.reasoning" :key="bi" class="reasoning-block">
                      <div class="block-content" v-html="block.content"></div>
                    </div>
                  </div>
                </div>
                <div v-if="msg.answer || msg._answerComplete === false" class="answer-section">
                  <div class="answer-label">最终答案</div>
                  <div v-if="!msg.answer" class="thinking-placeholder">
                    <span class="dots"><span></span><span></span><span></span></span>
                  </div>
                  <div class="answer-text" v-html="msg.answer"></div>
                </div>
                <div v-if="msg.error" class="error-message">⚠️ {{ msg.error }}</div>
              </div>
            </template>
          </div>
        </div>
      </div>
    </main>

    <!-- 输入区 -->
    <footer class="app-footer">
      <div class="input-wrapper">
        <el-input
          type="textarea"
          v-model="inputText"
          :rows="1"
          placeholder="输入你的问题，按 Enter 发送…"
          @keydown.enter.prevent="handleSend"
          :disabled="isProcessing"
          ref="inputArea"
          autofocus
        />
        <el-button
          class="send-btn"
          :disabled="!inputText.trim() || isProcessing"
          @click="handleSend"
          type="primary"
        >
          <el-icon><Promotion /></el-icon>
          发送
        </el-button>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { Promotion } from '@element-plus/icons-vue'
import { getToken, removeToken } from '../utils/auth'

const router = useRouter()

const inputText = ref('')
const isProcessing = ref(false)
const messages = reactive([])
const charQueue = ref([])
const threadId = ref('')
const streamTimer = ref(null)
const mainContainer = ref(null)
const inputArea = ref(null)

onMounted(() => {
  if (!getToken()) { router.push('/login'); return }
  nextTick(() => { scrollToBottom(); inputArea.value?.focus() })
})

onBeforeUnmount(() => {
  if (streamTimer.value) { clearInterval(streamTimer.value); streamTimer.value = null }
})

watch(messages, () => nextTick(scrollToBottom), { deep: true })

// ---- 发送消息 ----
const handleSend = () => {
  const text = inputText.value.trim()
  if (!text || isProcessing.value) return
  if (!getToken()) { router.push('/login'); return }

  if (streamTimer.value) { clearInterval(streamTimer.value); streamTimer.value = null }
  charQueue.value = []

  messages.push({ type: 'user', content: text })
  inputText.value = ''
  isProcessing.value = true

  const aiIdx = messages.length
  messages.push({ type: 'ai', thinking: true, reasoning: [], answer: '', _answerComplete: false, error: null })
  fetchSSE(text, aiIdx)
}

// ---- SSE 请求 ----
const fetchSSE = (question, msgIndex) => {
  const token = getToken()
  if (!token) { handleError(msgIndex, '未登录'); router.push('/login'); return }

  fetch('/chat', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'text/event-stream',
      'Authorization': 'Bearer ' + token,
    },
    body: JSON.stringify({ question, thread_id: threadId.value }),
  })
    .then(response => {
      if (response.status === 401) { removeToken(); router.push('/login'); throw new Error('登录已过期') }
      if (!response.ok) throw new Error(`HTTP ${response.status}`)
      const reader = response.body.getReader()
      const decoder = new TextDecoder('utf-8')
      let buffer = ''
      const readStream = () => {
        reader.read().then(({ done, value }) => {
          if (done) { finishAI(msgIndex); return }
          buffer += decoder.decode(value, { stream: true })
          const lines = buffer.split('\n\n')
          buffer = lines.pop() || ''
          for (const event of lines) { if (event.trim()) processSSEEvent(event, msgIndex) }
          readStream()
        }).catch(err => handleError(msgIndex, '读取流失败: ' + err.message))
      }
      readStream()
    })
    .catch(err => { if (!err.message.includes('登录已过期')) handleError(msgIndex, '请求失败: ' + err.message) })
}

const processSSEEvent = (eventData, msgIndex) => {
  const lines = eventData.split('\n')
  let eventType = null, dataLine = ''
  for (const line of lines) {
    const t = line.trim()
    if (t.startsWith('event:')) eventType = t.substring(6).trim()
    else if (t.startsWith('data:')) dataLine = t.substring(5).trim()
  }
  if (!dataLine) return

  let data = null
  try { data = JSON.parse(dataLine) } catch {
    const msg = messages[msgIndex]
    if (msg && msg.answer !== undefined) enqueueContent(msgIndex, 'answer', dataLine, 0)
    return
  }
  if (eventType === 'start') { threadId.value = data.thread_id }
  else updateAIFromEvent(data, msgIndex)
}

const updateAIFromEvent = (data, msgIndex) => {
  const msg = messages[msgIndex]
  if (!msg) return
  if (data.type === 'reasoning' || data.type === 'answer') {
    if (data.content) {
      enqueueContent(msgIndex, data.type, data.content, data.type === 'reasoning' ? (data.index || 0) : null)
      if (msg.thinking) msg.thinking = false
      startStreamTimer()
    }
  } else if (data.type === 'done' || data.type === 'end') {
    msg._answerComplete = true; isProcessing.value = false; nextTick(() => inputArea.value?.focus())
  } else if (data.content) {
    enqueueContent(msgIndex, 'answer', data.content, 0); startStreamTimer()
  }
}

const enqueueContent = (msgIndex, type, content, blockIndex) => {
  const tokens = tokenizeHTML(content)
  for (const token of tokens) charQueue.value.push({ token, type, blockIndex, msgIndex })
}

const tokenizeHTML = (html) => {
  const tokens = []
  const regex = /(<[^>]+>)|(&[a-zA-Z]+;)|([^<&]+)/g
  let match
  while ((match = regex.exec(html)) !== null) {
    if (match[1]) tokens.push(match[1])
    else if (match[2]) tokens.push(match[2])
    else match[3].split('').forEach(ch => tokens.push(ch))
  }
  return tokens
}

const startStreamTimer = () => {
  if (streamTimer.value) return
  streamTimer.value = setInterval(() => {
    if (charQueue.value.length === 0) {
      if (!isProcessing.value) { clearInterval(streamTimer.value); streamTimer.value = null }
      return
    }
    const item = charQueue.value.shift()
    const msg = messages[item.msgIndex]
    if (!msg) return
    if (item.type === 'answer') msg.answer += item.token
    else if (item.type === 'reasoning') {
      const idx = item.blockIndex || 0
      while (msg.reasoning.length <= idx) msg.reasoning.push({ title: '', content: '' })
      msg.reasoning[idx].content += item.token
    }
    scrollToBottom()
  }, 30)
}

const handleError = (msgIndex, errorMsg) => {
  const msg = messages[msgIndex]
  if (msg) { msg.thinking = false; msg.error = errorMsg; msg._answerComplete = true }
  isProcessing.value = false
  if (streamTimer.value) { clearInterval(streamTimer.value); streamTimer.value = null }
  charQueue.value = []
  nextTick(() => inputArea.value?.focus())
}

const finishAI = (msgIndex) => {
  const msg = messages[msgIndex]
  if (msg) { msg.thinking = false; msg._answerComplete = true }
  isProcessing.value = false
  nextTick(() => inputArea.value?.focus())
}

const scrollToBottom = () => {
  if (mainContainer.value) mainContainer.value.scrollTop = mainContainer.value.scrollHeight
}
</script>

<style scoped>
@import '../styles/chat.css';
</style>
