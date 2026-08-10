import { ref, reactive, onBeforeUnmount, watch, nextTick } from 'vue'
import { sseRequest } from '../utils/request'

export function useChat() {
  // ---- 状态 ----
  const inputText = ref('')
  const isProcessing = ref(false)
  const messages = reactive([])
  const mainContainer = ref(null)
  const inputArea = ref(null)

  const charQueue = ref([])
  const threadId = ref('')
  const streamTimer = ref(null)

  // ---- 生命周期 ----
  onBeforeUnmount(() => {
    if (streamTimer.value) { clearInterval(streamTimer.value); streamTimer.value = null }
  })

  watch(messages, () => nextTick(scrollToBottom), { deep: true })

  // ---- 发送消息 ----
  function handleSend() {
    const text = inputText.value.trim()
    if (!text || isProcessing.value) return

    if (streamTimer.value) { clearInterval(streamTimer.value); streamTimer.value = null }
    charQueue.value = []

    messages.push({ type: 'user', content: text })
    inputText.value = ''
    isProcessing.value = true

    const aiIdx = messages.length
    messages.push({ type: 'ai', thinking: true, reasoning: [], answer: '', _answerComplete: false, error: null })
    fetchSSE(text, aiIdx)
  }

  // ---- SSE 流 ----
  function fetchSSE(question, msgIndex) {
    sseRequest('/chat', { question, thread_id: threadId.value })
      .then(response => {
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

  function processSSEEvent(eventData, msgIndex) {
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

  function updateAIFromEvent(data, msgIndex) {
    const msg = messages[msgIndex]
    if (!msg) return
    if (data.type === 'reasoning' || data.type === 'answer') {
      if (data.content) {
        enqueueContent(msgIndex, data.type, data.content, data.type === 'reasoning' ? (data.index || 0) : null)
        if (msg.thinking) msg.thinking = false
        startStreamTimer()
      }
    } else if (data.type === 'done' || data.type === 'end') {
      msg._answerComplete = true; isProcessing.value = false; focusInput()
    } else if (data.content) {
      enqueueContent(msgIndex, 'answer', data.content, 0); startStreamTimer()
    }
  }

  // ---- 打字机效果 ----
  function enqueueContent(msgIndex, type, content, blockIndex) {
    const tokens = tokenizeHTML(content)
    for (const token of tokens) charQueue.value.push({ token, type, blockIndex, msgIndex })
  }

  function tokenizeHTML(html) {
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

  function startStreamTimer() {
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

  // ---- 工具 ----
  function handleError(msgIndex, errorMsg) {
    const msg = messages[msgIndex]
    if (msg) { msg.thinking = false; msg.error = errorMsg; msg._answerComplete = true }
    isProcessing.value = false
    if (streamTimer.value) { clearInterval(streamTimer.value); streamTimer.value = null }
    charQueue.value = []
    focusInput()
  }

  function finishAI(msgIndex) {
    const msg = messages[msgIndex]
    if (msg) { msg.thinking = false; msg._answerComplete = true }
    isProcessing.value = false
    focusInput()
  }

  function scrollToBottom() {
    if (mainContainer.value) mainContainer.value.scrollTop = mainContainer.value.scrollHeight
  }

  function focusInput() {
    nextTick(() => inputArea.value?.focus())
  }

  return {
    // 模板需要
    inputText,
    isProcessing,
    messages,
    mainContainer,
    inputArea,
    handleSend,
  }
}
