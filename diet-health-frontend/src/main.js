import { createApp } from 'vue'
import App from './App.vue'

import Vant from 'vant'
import 'vant/lib/index.css'
import './style.css'

import router from './router'

// 初始化用户 ID，确保会话一致性
if (!localStorage.getItem('user_id')) {
  localStorage.setItem('user_id', 'user_' + Math.random().toString(36).substr(2, 9))
}

const app = createApp(App)
app.use(router)
app.use(Vant)
app.mount('#app')
