<template>
  <div class="chat-page">
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

    <main class="app-main" ref="mainContainer">
      <div class="messages">
        <div v-if="messages.length === 0" class="empty-state">
          <div class="empty-icon">💬</div>
          <div class="empty-text">开始你的第一次对话</div>
          <div class="empty-sub">输入问题，AI 将流式展示推理过程</div>
        </div>

        <div v-for="(msg, idx) in messages" :key="idx" class="message" :class="msg.type">
          <div class="avatar">{{ msg.type === 'ai' ? 'AI' : '我' }}</div>
          <div class="bubble">
            <template v-if="msg.type === 'user'">
              <div class="text">{{ msg.content }}</div>
            </template>
            <template v-if="msg.type === 'ai'">
              <div v-if="msg.thinking" class="thinking-placeholder">
                <span>正在思考</span>
                <span class="dots"><span></span><span></span><span></span></span>
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

    <footer class="app-footer">
      <div class="input-wrapper">
        <el-input
          type="textarea" v-model="inputText" :rows="1"
          placeholder="输入你的问题，按 Enter 发送…"
          @keydown.enter.prevent="handleSend"
          :disabled="isProcessing" ref="inputArea" autofocus
        />
        <el-button class="send-btn" :disabled="!inputText.trim() || isProcessing" @click="handleSend" type="primary">
          <el-icon><Promotion /></el-icon> 发送
        </el-button>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { onMounted, nextTick } from 'vue'
import { Promotion } from '@element-plus/icons-vue'
import { useChat } from '../composables/useChat'

const { messages, inputText, isProcessing, mainContainer, inputArea, handleSend } = useChat()

onMounted(() => {
  nextTick(() => inputArea.value?.focus())
})
</script>

<style scoped>
@import '../styles/chat.css';
</style>
