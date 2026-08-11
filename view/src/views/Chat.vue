<template>
  <div class="chat-page">
    <!-- ── 标题栏 ── -->
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

    <!-- ── 消息列表 ── -->
    <main class="app-main" ref="mainContainer">
      <div class="messages">
        <!-- 空状态 -->
        <div v-if="messages.length === 0" class="empty-state">
          <div class="empty-icon">💬</div>
          <div class="empty-text">开始你的第一次对话</div>
          <div class="empty-sub">输入问题，AI 将流式展示推理过程</div>
        </div>

        <!-- 消息气泡 -->
        <div
          v-for="(msg, idx) in messages"
          :key="idx"
          class="message"
          :class="msg.type"
        >
          <div class="avatar">{{ msg.type === 'ai' ? 'AI' : '我' }}</div>
          <div class="bubble">
            <!-- 用户消息 -->
            <template v-if="msg.type === 'user'">
              <div class="text">{{ msg.content }}</div>
            </template>

            <!-- AI 消息 -->
            <template v-if="msg.type === 'ai'">
              <!-- 思考中动画 -->
              <div v-if="msg.thinking || (!msg.answer && !msg._answerComplete)" class="thinking-placeholder">
                <span>正在思考</span>
                <span class="dots"><span></span><span></span><span></span></span>
              </div>

              <div class="ai-reply">
                <!-- 推理过程（仅当有推理内容时显示） -->
                <template v-if="msg.reasoning?.length">
                  <div class="reasoning-section">
                    <span class="label">🧠 推理过程</span>
                    <span class="divider"></span>
                  </div>
                  <div class="reasoning-blocks">
                    <div
                      v-for="(block, bi) in msg.reasoning"
                      :key="bi"
                      class="reasoning-block"
                    >
                      <div
                        class="block-content"
                        :class="{ 'is-streaming': !msg.answer && bi === msg.reasoning.length - 1 }"
                        v-html="block.content"
                      ></div>
                    </div>
                  </div>
                </template>

                <!-- 最终答案：仅当有答案内容时才显示，推理阶段不出现 -->
                <div
                  v-if="msg.answer"
                  class="answer-section"
                  :class="{ 'no-divider': !msg.reasoning?.length }"
                >
                  <div class="answer-label">最终答案</div>
                  <div
                    class="answer-text"
                    :class="{ 'is-streaming': !msg._answerComplete }"
                    v-html="msg.answer"
                  ></div>
                </div>

                <!-- 错误信息 -->
                <div v-if="msg.error" class="error-message">⚠️ {{ msg.error }}</div>
              </div>
            </template>
          </div>
        </div>
      </div>
    </main>

    <!-- ── 底部输入区 ── -->
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

const {
  messages,
  inputText,
  isProcessing,
  mainContainer,
  inputArea,
  handleSend,
} = useChat()

onMounted(() => {
  nextTick(() => inputArea.value?.focus())
})
</script>

<style scoped>
@import '../styles/chat.css';
</style>
