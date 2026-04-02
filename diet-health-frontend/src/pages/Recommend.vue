<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { chatWithYibao } from '@/api/yibao'

const router = useRouter()

const messages = ref([
  { role: 'assistant', text: '你好，我是颐宝 AI，可以根据中医思路帮你分析体质、搭配食疗，有什么想了解的吗？' }
])
const input = ref('')
const isLoading = ref(false)

async function send() {
  if (!input.value.trim() || isLoading.value) return
  
  const text = input.value.trim()
  messages.value.push({ role: 'user', text })
  input.value = ''
  isLoading.value = true
  
  // 添加加载中的消息
  const loadingIndex = messages.value.length
  messages.value.push({
    role: 'assistant',
    text: '正在思考中...'
  })
  
  try {
    const res = await chatWithYibao(text)
    console.log('颐宝 AI 回复:', res)
    
    // 更新最后一条消息（移除加载中消息，替换为真实回复）
    messages.value.pop()
    
    // 后端返回格式：{ reply: "AI回复内容", status: "success" }
    if (res.status === 'success' && res.reply) {
      messages.value.push({
        role: 'assistant',
        text: res.reply
      })
    } else {
      messages.value.push({
        role: 'assistant',
        text: res.reply || '抱歉，我暂时无法回答这个问题。'
      })
    }
  } catch (err) {
    console.error('AI 回复失败:', err)
    messages.value.pop()
    messages.value.push({
      role: 'assistant',
      text: '抱歉，连接服务器失败，请稍后再试。'
    })
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <div class="page-ai app-page">
    <header class="page-header">
      <button class="back-btn" type="button" @click="router.back()">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M19 12H5M12 19l-7-7 7-7"/>
        </svg>
      </button>
      <h1 class="page-title">颐宝 AI</h1>
      <span class="header-placeholder"></span>
    </header>

    <section class="block">
      <div class="intro-card">
        <h2 class="intro-title">你可以这样问我：</h2>
        <ul class="intro-list">
          <li>“最近总是熬夜，第二天很疲劳，吃什么可以缓解？”</li>
          <li>“手脚冰凉是不是阳虚？平时怎么调理？”</li>
          <li>“我想减脂但又怕伤胃，有没有暖胃的减脂晚餐推荐？”</li>
        </ul>
      </div>
    </section>

    <section class="block chat-block">
      <div class="chat-box">
        <div
          v-for="(msg, index) in messages"
          :key="index"
          class="chat-row"
          :class="msg.role"
        >
          <div class="avatar" v-if="msg.role === 'assistant'">颐</div>
          <div class="bubble">{{ msg.text }}</div>
          <div class="avatar user" v-if="msg.role === 'user'">我</div>
        </div>
      </div>
      <div class="input-row">
        <input
          v-model="input"
          type="text"
          class="chat-input"
          placeholder="例如：最近总是睡不好，该怎么调理？"
          @keyup.enter="send"
        />
        <button type="button" class="send-btn" @click="send" :disabled="isLoading">
          {{ isLoading ? '发送中' : '发送' }}
        </button>
      </div>
    </section>
  </div>
</template>

<style scoped>
.page-ai {
  background: var(--bg);
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  background: transparent;
  position: sticky;
  top: 0;
  z-index: 100;
}

.back-btn {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  border: none;
  background: #ffffff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #333;
}

.back-btn:active {
  transform: scale(0.95);
  background: #f8f9fa;
}

.back-btn svg {
  width: 22px;
  height: 22px;
}

.page-title {
  font-size: 20px;
  font-weight: 700;
  color: #1a1a1a;
  margin: 0;
  letter-spacing: -0.3px;
}

.header-placeholder {
  width: 40px;
}

.page-subtitle {
  font-size: 13px;
  color: var(--text-secondary);
  text-align: center;
  margin-top: -4px;
  margin-bottom: 12px;
  padding: 0 20px;
}

.block {
  margin-bottom: 20px;
}

.intro-card {
  background: var(--bg-card);
  border-radius: 14px;
  padding: 12px 14px;
  box-shadow: var(--shadow);
}

.intro-title {
  margin: 0 0 6px;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-h);
}

.intro-list {
  margin: 0;
  padding-left: 18px;
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.6;
}

.chat-block {
  padding-bottom: 4px;
}

.chat-box {
  max-height: 360px;
  min-height: 200px;
  padding: 10px 8px;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.9);
  box-shadow: var(--shadow);
  overflow-y: auto;
}

.chat-row {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  margin-bottom: 8px;
}

.chat-row.user {
  flex-direction: row-reverse;
}

.avatar {
  width: 28px;
  height: 28px;
  border-radius: 999px;
  background: var(--primary);
  color: #fff;
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar.user {
  background: #666;
}

.bubble {
  max-width: 70%;
  padding: 8px 10px;
  border-radius: 14px;
  font-size: 14px;
  line-height: 1.5;
  background: var(--primary-light);
  color: var(--text-h);
}

.chat-row.user .bubble {
  background: #ffffff;
}

.input-row {
  margin-top: 10px;
  display: flex;
  gap: 8px;
  align-items: center;
}

.chat-input {
  flex: 1;
  height: 40px;
  border-radius: 999px;
  border: 1px solid #e0e0e0;
  padding: 0 12px;
  font-size: 14px;
}

.send-btn {
  width: 64px;
  height: 40px;
  border-radius: 999px;
  border: none;
  background: var(--primary);
  color: #fff;
  font-size: 14px;
}

.send-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.bubble:contains('正在思考中') {
  color: #999;
  font-style: italic;
}
</style>
