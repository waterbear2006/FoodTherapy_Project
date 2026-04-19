<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { chatWithYibao } from '@/api/yibao'
import { marked } from 'marked' // 引入 Markdown 渲染

const router = useRouter()
const chatContainer = ref(null)

const quickPrompts = [
  '最近总是熬夜，该吃什么？',
  '手脚冰凉怎么调理？',
  '暖胃的减脂晚餐',
  '最近容易急躁上火'
]

const messages = ref([
  { 
    role: 'assistant', 
    text: '见阁下眉间微蹙，可是近日饮食不慎，身子有些沉重？\n\n我是颐宝，出身中医世家。阁下若有任何身体不适或食疗疑问，且听我一言，慢慢向我道来。' 
  }
])
const input = ref('')
const isLoading = ref(false)

const scrollToBottom = async () => {
  await nextTick()
  if (chatContainer.value) {
    chatContainer.value.scrollTo({ top: chatContainer.value.scrollHeight, behavior: 'smooth' })
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
  
  // 模拟思考状态
  const loadingMsg = { role: 'assistant', text: '正在为您翻阅医典，推演配伍...', isLoading: true }
  messages.value.push(loadingMsg)
  scrollToBottom()
  
  try {
    const res = await chatWithYibao(text)
    messages.value.pop()
    
    if (res.status === 'success' && res.reply) {
      messages.value.push({ role: 'assistant', text: res.reply })
    } else {
      messages.value.push({ role: 'assistant', text: '抱歉，颐宝才疏学浅，暂时没能领会阁下的意思。不若换个说法？' })
    }
  } catch (err) {
    messages.value.pop()
    messages.value.push({ role: 'assistant', text: '医馆今日繁忙，回话稍显迟钝，请阁下稍后再试。' })
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
        <h1 class="page-title">颐宝·食疗管家</h1>
        <div class="status-dot">在馆</div>
      </div>
      <div class="header-action"></div>
    </header>

    <main class="chat-container" ref="chatContainer">
      <div class="welcome-guide">
        <div class="ai-intro">
          <div class="ai-avatar-large ink-wash-fade-in">颐</div>
          <div class="ai-info">
            <h3>我是您的私人食疗师</h3>
            <p>基于中医九种体质学说，为您翻阅医典</p>
          </div>
        </div>
        <div class="quick-chips">
          <div v-for="prompt in quickPrompts" :key="prompt" class="chip" @click="handleQuickPrompt(prompt)">
            {{ prompt }}
          </div>
        </div>
      </div>

      <div class="message-list">
        <div v-for="(msg, index) in messages" :key="index" class="message-wrapper" :class="[msg.role, { 'is-loading': msg.isLoading }]">
          <div class="message-avatar" :class="{'ink-wash-fade-in': msg.role === 'assistant'}">
            {{ msg.role === 'assistant' ? '颐' : '我' }}
          </div>
          <div class="message-content">
            <div 
              class="bubble markdown-body" 
              :class="{'ink-wash-fade-in': msg.role === 'assistant'}"
              v-html="marked(msg.text)"
            ></div>
            <div v-if="msg.isLoading" class="typing-indicator">
              <span></span><span></span><span></span>
            </div>
            <div class="msg-time">{{ new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}) }}</div>
          </div>
        </div>
      </div>
    </main>

    <footer class="input-area box-glass">
      <div class="input-wrapper">
        <input v-model="input" type="text" placeholder="向颐宝讨个方子..." @keyup.enter="send" />
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

<!-- 全局古籍样式注入 (不加 scoped 才能影响 marked 渲染出的 HTML) -->
<style>
/* 全局 Markdown 渲染样式微调 (用于通义千问输出结果) */
.markdown-body {
  font-family: var(--sans);
  font-size: 14.5px;
  line-height: 1.7;
  color: var(--text);
}
.markdown-body blockquote {
  background: #fdfaf5 !important;
  background-image: url("data:image/svg+xml,%3Csvg width='100' height='100' viewBox='0 0 100 100' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.8' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100' height='100' filter='url(%23noise)' opacity='0.03'/%3E%3C/svg%3E");
  border-left: 3px solid var(--accent) !important;
  padding: 12px 16px !important;
  margin: 14px 0 !important;
  border-radius: 4px 12px 12px 4px;
  color: #5c4b37;
  font-size: 13.5px;
  box-shadow: inset 0 0 20px rgba(255, 255, 255, 0.5);
}
.markdown-body h1, .markdown-body h2, .markdown-body h3 {
  color: var(--primary) !important;
  margin-top: 16px;
  margin-bottom: 8px;
  font-weight: 700;
}
.markdown-body ul, .markdown-body ol {
  padding-left: 20px;
  margin-bottom: 12px;
}
.markdown-body li {
  margin-bottom: 4px;
}
.markdown-body strong {
  color: var(--primary-dark);
}
</style>

<style scoped>
.page-ai {
  background: var(--bg-ios);
  height: 100vh;
  display: flex;
  flex-direction: column;
  padding: 0;
  overflow: hidden;
}

.glass-header {
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
  display: flex;
  align-items: center;
  justify-content: space-between;
  z-index: 100;
}

.header-content { text-align: center; }
.page-title { font-size: 16px; font-weight: 700; margin: 0; color: var(--text); }
.status-dot { font-size: 10px; color: var(--primary); font-weight: 500; display: flex; align-items: center; gap: 4px; }
.status-dot::before { content: ''; width: 6px; height: 6px; background: var(--primary); border-radius: 50%; opacity: 0.8; }

.back-btn { background: transparent; border: none; width: 40px; height: 40px; border-radius: 12px; display: flex; align-items: center; justify-content: center; color: var(--text); transition: background 0.2s; }
.back-btn:active { background: rgba(0,0,0,0.05); }

.chat-container {
  flex: 1;
  overflow-y: auto;
  padding: 20px 16px;
  padding-bottom: 120px;
  display: flex;
  flex-direction: column;
  gap: 24px;
  scroll-behavior: smooth;
}

.welcome-guide { margin-bottom: 12px; }
.ai-intro { display: flex; align-items: center; gap: 14px; margin-bottom: 20px; }
.ai-avatar-large {
  width: 52px; height: 52px;
  background: var(--primary);
  color: white;
  border-radius: 18px;
  font-size: 22px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8px 16px rgba(90, 123, 104, 0.2);
}
.ai-info h3 { font-size: 17px; margin: 0 0 4px; color: var(--text); }
.ai-info p { font-size: 13px; color: var(--text-secondary); margin: 0; }

.quick-chips { display: flex; flex-wrap: wrap; gap: 10px; }
.chip {
  padding: 8px 16px;
  background: white;
  border-radius: 14px;
  font-size: 13px;
  color: var(--text);
  box-shadow: 0 2px 8px rgba(0,0,0,0.03);
  border: 1px solid rgba(0,0,0,0.02);
  cursor: pointer;
  transition: all 0.2s;
}
.chip:active { transform: scale(0.96); background: var(--primary-light); }

.message-list { display: flex; flex-direction: column; gap: 24px; }
.message-wrapper { display: flex; gap: 12px; max-width: 90%; }
.message-wrapper.user { align-self: flex-end; flex-direction: row-reverse; }

.message-avatar {
  width: 32px; height: 32px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  flex-shrink: 0;
  font-weight: 600;
}
.assistant .message-avatar { background: var(--primary); color: white; }
.user .message-avatar { background: #333336; color: white; }

.message-content { flex: 1; min-width: 0; }
.bubble {
  padding: 12px 14px;
  border-radius: 18px;
  position: relative;
  word-break: break-word;
}
.assistant .bubble {
  background: white;
  color: var(--text);
  border-top-left-radius: 4px;
  box-shadow: var(--shadow-soft);
}
.user .bubble {
  background: var(--primary);
  color: white;
  border-top-right-radius: 4px;
  box-shadow: 0 4px 12px rgba(90, 123, 104, 0.15);
}

.msg-time { font-size: 10px; color: var(--text-muted); margin-top: 6px; padding: 0 4px; }
.user .msg-time { text-align: right; }

.typing-indicator { display: flex; gap: 4px; padding: 10px 0; }
.typing-indicator span {
  width: 6px; height: 6px;
  background: var(--primary);
  border-radius: 50%;
  animation: bounce 1.4s infinite ease-in-out;
}
.typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
.typing-indicator span:nth-child(3) { animation-delay: 0.4s; }

@keyframes bounce {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}

.input-area {
  position: fixed;
  bottom: 0; left: 0; right: 0;
  padding: 16px 16px 36px;
  background: rgba(242, 242, 247, 0.82);
  backdrop-filter: blur(20px);
  z-index: 110;
}
.input-wrapper {
  display: flex;
  gap: 8px;
  background: white;
  border-radius: 50px;
  padding: 6px 6px 6px 16px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.06);
  border: 1px solid rgba(255,255,255,0.8);
}
.input-wrapper input {
  flex: 1;
  border: none;
  outline: none;
  background: transparent;
  font-size: 15px;
  color: var(--text);
}
.send-btn {
  width: 36px; height: 36px;
  border-radius: 50%;
  background: var(--primary);
  color: white;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: opacity 0.2s, transform 0.2s;
}
.send-btn:active { transform: scale(0.9); }
.send-btn:disabled { background: var(--text-muted); opacity: 0.5; }

.btn-loader {
  width: 14px; height: 14px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
</style>