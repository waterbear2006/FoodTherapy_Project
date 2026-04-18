<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { chatWithYibao } from '@/api/yibao'

const router = useRouter()
const chatContainer = ref(null)

const quickPrompts = [
  '最近总是熬夜，该吃什么？',
  '手脚冰凉怎么调理？',
  '暖胃的减脂晚餐',
  '最近容易急躁上火'
]

const messages = ref([
  { role: 'assistant', text: '您好，我是您的私人养生管家“颐宝 AI”。您可以根据今天的身体感受向我提问，我会为您提供专业的中医食疗建议。' }
])
const input = ref('')
const isLoading = ref(false)

// 自动滚动到底部
const scrollToBottom = async () => {
  await nextTick()
  if (chatContainer.value) {
    chatContainer.value.scrollTo({
      top: chatContainer.value.scrollHeight,
      behavior: 'smooth'
    })
  }
}

function handleQuickPrompt(text) {
  input.value = text
}

async function send() {
  if (!input.value.trim() || isLoading.value) return
  
  const text = input.value.trim()
  messages.value.push({ role: 'user', text })
  input.value = ''
  isLoading.value = true
  scrollToBottom()
  
  // 添加加载提示
  const loadingMsg = { role: 'assistant', text: '正在为您查询医典并生成解析...', isLoading: true }
  messages.value.push(loadingMsg)
  scrollToBottom()
  
  try {
    const res = await chatWithYibao(text)
    messages.value.pop() // 移除加载提示
    
    if (res.status === 'success' && res.reply) {
      messages.value.push({ role: 'assistant', text: res.reply })
    } else {
      messages.value.push({ role: 'assistant', text: '抱歉，颐宝暂时没能理解您的意思，换个问法试试？' })
    }
  } catch (err) {
    messages.value.pop()
    messages.value.push({ role: 'assistant', text: '系统繁忙，请稍后再试。' })
  } finally {
    isLoading.value = false
    scrollToBottom()
  }
}

onMounted(() => {
  scrollToBottom()
})
</script>

<template>
  <div class="page-ai app-page">
    <header class="glass-header">
      <button class="back-btn" @click="router.back()">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M19 12H5M12 19l-7-7 7-7"/>
        </svg>
      </button>
      <div class="header-content">
        <h1 class="page-title">颐宝 AI 助手</h1>
        <div class="status-dot">在线</div>
      </div>
      <div class="header-action"></div>
    </header>

    <main class="chat-container" ref="chatContainer">
      <!-- 引导卡片 -->
      <div class="welcome-guide">
        <div class="ai-intro">
          <div class="ai-avatar-large">颐</div>
          <div class="ai-info">
            <h3>我是您的指尖食疗师</h3>
            <p>基于中医九种体质学说，为您提供定制建议</p>
          </div>
        </div>
        <div class="quick-chips">
          <div 
            v-for="prompt in quickPrompts" 
            :key="prompt"
            class="chip"
            @click="handleQuickPrompt(prompt)"
          >
            {{ prompt }}
          </div>
        </div>
      </div>

      <!-- 消息列表 -->
      <div class="message-list">
        <div
          v-for="(msg, index) in messages"
          :key="index"
          class="message-wrapper"
          :class="[msg.role, { 'is-loading': msg.isLoading }]"
        >
          <div class="message-avatar">{{ msg.role === 'assistant' ? '颐' : '我' }}</div>
          <div class="message-content">
            <div class="bubble">
              {{ msg.text }}
              <div v-if="msg.isLoading" class="typing-indicator">
                <span></span><span></span><span></span>
              </div>
            </div>
            <div class="msg-time">{{ new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}) }}</div>
          </div>
        </div>
      </div>
    </main>

    <footer class="input-area box-glass">
      <div class="input-wrapper">
        <input
          v-model="input"
          type="text"
          placeholder="有什么养生疑问都可以问我..."
          @keyup.enter="send"
        />
        <button class="send-btn" :disabled="!input.trim() || isLoading" @click="send">
          <svg v-if="!isLoading" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <line x1="22" y1="2" x2="11" y2="13"></line>
            <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
          </svg>
          <div v-else class="btn-loader"></div>
        </button>
      </div>
    </footer>
  </div>
</template>

<style scoped>
.page-ai {
  background: linear-gradient(135deg, #f7f4ef 0%, #e8f5e9 100%);
  height: 100vh;
  display: flex;
  flex-direction: column;
  padding: 0;
  overflow: hidden;
}

/* 磨砂玻璃头部 */
.glass-header {
  position: relative;
  z-index: 10;
  padding: 12px 20px;
  background: rgba(255, 255, 255, 0.75);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  border-bottom: 1px solid rgba(0, 0, 0, 0.08);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.header-content {
  text-align: center;
}

.page-title {
  font-size: 17px;
  font-weight: 700;
  margin: 0;
  color: #1a1a1a;
}

.status-dot {
  font-size: 10px;
  color: var(--primary);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
}

.status-dot::before {
  content: '';
  width: 6px;
  height: 6px;
  background: var(--primary);
  border-radius: 50%;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% { transform: scale(0.9); opacity: 0.8; }
  50% { transform: scale(1.2); opacity: 1; }
  100% { transform: scale(0.9); opacity: 0.8; }
}

.back-btn {
  background: rgba(255, 255, 255, 0.8);
  border: none;
  width: 36px;
  height: 36px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #333;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
}

.header-action {
  width: 36px;
}

/* 对话区域 */
.chat-container {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  padding-bottom: 120px; /* 为吸底输入框留空 */
  display: flex;
  flex-direction: column;
  gap: 20px;
  scroll-behavior: smooth;
}

/* 欢迎引导 */
.welcome-guide {
  animation: fadeInDown 0.6s ease-out;
  margin-bottom: 10px;
}

.ai-intro {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.ai-avatar-large {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, var(--primary), var(--primary-dark));
  color: white;
  border-radius: 16px;
  font-size: 20px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8px 16px rgba(39, 179, 168, 0.2);
}

.ai-info h3 { font-size: 16px; margin: 0 0 2px; color: #1a1a1a; }
.ai-info p { font-size: 12px; color: #666; margin: 0; }

.quick-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.chip {
  padding: 8px 16px;
  background: white;
  border-radius: 99px;
  font-size: 13px;
  color: var(--primary-dark);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  border: 1px solid rgba(224, 224, 224, 0.5);
  transition: all 0.2s;
  cursor: pointer;
}

.chip:active {
  transform: scale(0.95);
  background: #f0f0f0;
}

/* 消息样式 */
.message-list {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.message-wrapper {
  display: flex;
  gap: 10px;
  max-width: 85%;
  animation: messageIn 0.4s cubic-bezier(0.18, 0.89, 0.32, 1.28) both;
}

@keyframes messageIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.message-wrapper.user {
  align-self: flex-end;
  flex-direction: row-reverse;
}

.message-avatar {
  width: 32px;
  height: 32px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  flex-shrink: 0;
  font-weight: 600;
}

.assistant .message-avatar {
  background: white;
  color: var(--primary);
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.user .message-avatar {
  background: #2c3e50;
  color: white;
}

.bubble {
  padding: 12px 16px;
  border-radius: 18px;
  font-size: 14px;
  line-height: 1.6;
  position: relative;
  box-shadow: 0 4px 15px rgba(0,0,0,0.03);
}

.assistant .bubble {
  background: white;
  color: #2c3e50;
  border-top-left-radius: 4px;
}

.user .bubble {
  background: linear-gradient(135deg, var(--primary), var(--primary-dark));
  color: white;
  border-top-right-radius: 4px;
}

.msg-time {
  font-size: 10px;
  color: #999;
  margin-top: 5px;
  margin-left: 4px;
}

.user .msg-time {
  text-align: right;
  margin-right: 4px;
}

/* 打字指示器 */
.typing-indicator {
  display: flex;
  gap: 4px;
  padding-top: 8px;
}

.typing-indicator span {
  width: 6px;
  height: 6px;
  background: #ccc;
  border-radius: 50%;
  animation: typing 1.4s infinite ease-in-out;
}

.typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
.typing-indicator span:nth-child(3) { animation-delay: 0.4s; }

@keyframes typing {
  0%, 80%, 100% { transform: scale(0.6); opacity: 0.4; }
  40% { transform: scale(1.1); opacity: 1; }
}

/* 底部输入区 */
.input-area {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 16px 20px 32px;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-top: 1px solid rgba(0,0,0,0.05);
  z-index: 100;
}

.input-wrapper {
  background: white;
  border-radius: 20px;
  padding: 4px 4px 4px 18px;
  display: flex;
  align-items: center;
  box-shadow: 0 8px 24px rgba(0,0,0,0.06);
  border: 1px solid rgba(224, 224, 224, 0.5);
}

.input-wrapper input {
  flex: 1;
  border: none;
  height: 44px;
  font-size: 15px;
  background: transparent;
  color: #1a1a1a;
}

.input-wrapper input:focus { outline: none; }

.send-btn {
  width: 44px;
  height: 44px;
  border-radius: 16px;
  border: none;
  background: var(--primary);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
  cursor: pointer;
}

.send-btn:active {
  transform: scale(0.9);
}

.send-btn:disabled {
  background: #f0f0f0;
  color: #ccc;
  cursor: not-allowed;
}

.btn-loader {
  width: 20px;
  height: 20px;
  border: 3px solid rgba(255,255,255,0.3);
  border-top: 3px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@keyframes fadeInDown {
  from { opacity: 0; transform: translateY(-20px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
