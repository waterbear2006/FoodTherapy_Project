<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getNews } from '@/api/news'
import { getWellnessReport, fetchRealWeather } from '@/api/mock'

const router = useRouter()

// 新闻列表
const newsList = ref([])

// 加载新闻
async function loadNews() {
  try {
    const res = await getNews()
    console.log('📰 后端返回的新闻数据:', res)
    
    // 后端返回格式：{ status: "success", data: [新闻数组], total: 5 }
    if (res.status === 'success' && Array.isArray(res.data)) {
      newsList.value = res.data
      console.log('✅ 新闻列表长度:', newsList.value.length)
    } else if (res.data && Array.isArray(res.data)) {
      // 兼容其他格式
      newsList.value = res.data
      console.log('✅ 新闻列表长度:', newsList.value.length)
    } else {
      console.warn('⚠️ 返回数据格式不符合预期:', res)
      newsList.value = []
    }
  } catch (err) {
    console.error('❌ 获取新闻失败:', err)
    newsList.value = []
  }
}

// 气象模拟模式
const weatherModes = [
  { mode: 'default', label: '🌤️ 默认/无天气', payload: null },
  { mode: 'real_time', label: '🌍 真实: 获取周边实时数据', isReal: true, city: '北京' }, // 默认以北京为例，或者前端可改成其他
  { mode: 'hot_humid', label: '🔥 模拟: 大暑高湿', payload: { temperature: 34, humidity: 88, city: '广州(模拟)' } },
  { mode: 'cold_dry', label: '❄️ 模拟: 深冬干冷', payload: { temperature: 5, humidity: 20, city: '北京(模拟)' } }
]
const weatherIdx = ref(1)
const envTags = ref([])
const weatherLoading = ref(false)

// 获取用户动态 GPS 定位
function getCurrentLocation() {
  return new Promise((resolve) => {
    // 1. 检查是否有用户手动设置的城市
    const customCity = localStorage.getItem('customCity')
    if (customCity && customCity.trim() !== '') {
      resolve(customCity.trim())
      return
    }

    if (!navigator.geolocation) {
      resolve('北京') // 浏览器不支持定位时，默认使用北京
      return
    }
    
    navigator.geolocation.getCurrentPosition(
      (position) => {
        // 和风天气的 GeoAPI 支持传入坐标，格式为: 经度,纬度
        const lon = position.coords.longitude.toFixed(3)
        const lat = position.coords.latitude.toFixed(3)
        resolve(`${lon},${lat}`)
      },
      (error) => {
        console.warn('⚠️ 获取 GPS 定位失败 (可能是无权限或被拒绝)，退回默认北京:', error)
        resolve('北京')
      },
      { timeout: 5000, maximumAge: 60000 } // 5 秒超时限制，以及 1 分钟缓存
    )
  })
}

async function toggleWeather() {
  weatherIdx.value = (weatherIdx.value + 1) % weatherModes.length
  await loadTodayCard()
}

// 手动修改定位城市
function editLocation() {
  const current = localStorage.getItem('customCity') || '';
  const city = window.prompt("请输入您所在的城市 (留空并确认则恢复自动GPS):", current);
  if (city !== null) {
      if (city.trim() === '') {
          localStorage.removeItem('customCity');
      } else {
          localStorage.setItem('customCity', city.trim());
      }
      weatherIdx.value = 1; // 强制切换到 'real_time' 以便立刻看效果
      loadTodayCard();
  }
}

// 加载今日养生建议
async function loadTodayCard() {
  try {
    // 从 localStorage 获取体质信息
    const records = JSON.parse(localStorage.getItem('healthArchive') || '[]')
    const constitutionRecord = records.find(r => r.type === 'constitution')
    
    let constitution = {}
    if (constitutionRecord?.details) {
      const type = constitutionRecord.details.constitution || '平和质'
      constitution = { [type]: constitutionRecord.details.scores?.[type] || 80 }
    }
    
    let weatherData = null
    const currentMode = weatherModes[weatherIdx.value]
    
    if (currentMode.isReal && currentMode.mode === 'real_time') {
      weatherLoading.value = true
      const isCustom = !!localStorage.getItem('customCity')
      const prefix = isCustom ? '📍 设定' : '🌍 真实'
      
      currentMode.label = `${prefix}: 定位中...`
      
      // 1. 调用 GPS 获取当前经纬度坐标 (或降级回传城市名)
      const locationQuery = await getCurrentLocation()
      
      // 2. 将坐标传给和风天气 API
      weatherData = await fetchRealWeather(locationQuery) 
      weatherLoading.value = false
      
      // 更新一下 label 显示获取到的城市名与温度
      if(weatherData) {
        currentMode.label = `${prefix}: ${weatherData.city} ${weatherData.temperature}℃`
      } else {
        currentMode.label = `❌ ${prefix}: 获取失败`
      }
    } else {
      weatherData = currentMode.payload
    }

    const report = await getWellnessReport(constitution, {}, weatherData)
    console.log('📋 今日养生报告:', report)
    
    // 更新今日养生卡片
    todayCard.value = {
      title: report.suggestion_title || '今日养生建议',
      suggestion: report.intro || '根据您的体质特点，建议保持均衡饮食，适量运动。',
      foods: report.recommended_ingredients?.length > 0 ? report.recommended_ingredients : ['山药', '红枣', '枸杞'],
      therapy: report.recommended_recipe || '山药红枣粥',
      tip: report.recipe_tip || '早餐一碗山药红枣粥，有助于暖胃护脾。',
      season_tag: report.season_tag || '温中 · 补气'
    }
    envTags.value = report.environmental_tags || []
  } catch (err) {
    console.error('❌ 获取今日养生建议失败:', err)
    // 使用默认值
  }
}

// 页面加载时获取数据
onMounted(() => {
  loadNews()
  loadTodayCard()
})

// 今日养生卡片
const todayCard = ref({
  title: '今日养生建议',
  suggestion: '加载中...',
  foods: [],
  therapy: '',
  tip: '',
  season_tag: ''
})

// 功能入口
const shortcuts = [
  {
    key: 'recipe',
    icon: 'recipe',
    title: '生成菜谱',
    desc: '根据现有食材智能搭配',
    route: '/recipe'
  },
  {
    key: 'ai',
    icon: 'ai',
    title: '颐宝 AI',
    desc: '中医问答助手',
    route: '/recommend'
  },
  {
    key: 'test',
    icon: 'test',
    title: '体质测试',
    desc: '了解你的体质类型',
    route: '/constitution'
  },
  {
    key: 'smart',
    icon: 'smart',
    title: '智能推荐',
    desc: '一键获取专属食疗',
    route: '/smart-recommend'
  }
]

// 点击功能入口
function handleShortcut(item) {
  router.push(item.route)
}

// 点击新闻跳转
function openNews(link) {
  window.open(link)
}

// 格式化风险文本
function formatRiskText(tag) {
  if (tag.includes('高湿')) return '高湿风险'
  if (tag.includes('寒冷')) return '寒冷风险'
  if (tag.includes('利湿')) return '利湿干预'
  if (tag.includes('散寒')) return '散寒干预'
  return tag
}

// 图片加载失败处理
function handleImageError(event) {
  // 图片加载失败时显示占位符
  event.target.style.display = 'none'
  const placeholder = event.target.parentElement.querySelector('.cover-placeholder')
  if (placeholder) {
    placeholder.style.display = 'flex'
  }
}
</script>

<template>
  <div class="page-home app-page">
    <!-- 顶部 -->
    <header class="home-header">
      <div class="left">
        <svg class="menu-icon" viewBox="0 0 24 24">
          <!-- 自然飘逸的叶子图标 -->
          <path d="M12 2C12 2 6 8 6 14c0 3.31 2.69 6 6 6s6-2.69 6-6c0-6-6-12-6-12z" 
                fill="none" 
                stroke="currentColor" 
                stroke-width="1.5" 
                stroke-linecap="round" 
                stroke-linejoin="round"
                opacity="0.9"/>
          <path d="M12 2c0 6-4 10-4 12" 
                fill="none" 
                stroke="currentColor" 
                stroke-width="1.2" 
                stroke-linecap="round"
                opacity="0.6"/>
          <path d="M12 6c2 2 3 4 3 6" 
                fill="none" 
                stroke="currentColor" 
                stroke-width="1.2" 
                stroke-linecap="round"
                opacity="0.6"/>
        </svg>
        <span class="logo-text">苏叶食疗</span>
      </div>
    </header>

    <!-- 今日养生卡片 -->
    <section class="block">
      <div class="today-card">
        <!-- 顶部信息栏：季节标签 + 天气定位 -->
        <div class="today-top-row">
          <div class="season-tag-wrapper">
            <svg viewBox="0 0 24 24" class="season-icon">
              <path d="M12 2C8 2 6 6 6 8c0 3 3 5 6 5s6-2 6-5c0-2-2-6-6-6z" fill="currentColor" opacity="0.9"/>
              <path d="M12 18c-2 0-4 2-4 4h8c0-2-2-4-4-4z" fill="currentColor" opacity="0.7"/>
            </svg>
            <span class="season-text">{{ todayCard.season_tag || '温中 · 补气' }}</span>
          </div>
          <div class="weather-location-wrapper">
            <span class="weather-tag" @click="toggleWeather">
              {{ weatherModes[weatherIdx].label }}
            </span>
            <span class="location-tag" @click="editLocation" title="修改定位城市">
              <svg viewBox="0 0 24 24" class="location-icon">
                <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z" fill="currentColor"/>
              </svg>
              <span class="location-text">修改定位</span>
            </span>
          </div>
        </div>

        <!-- 主标题 -->
        <h2 class="today-title">{{ todayCard.title }}</h2>

        <!-- 风险干预标签（低调显示） -->
        <div class="env-tags" v-if="envTags.length > 0">
          <div v-for="t in envTags" :key="t" class="risk-badge">
            <span class="risk-dot"></span>
            <span class="risk-label">{{ formatRiskText(t) }}</span>
          </div>
        </div>

        <!-- 养生建议正文 -->
        <p class="today-suggestion">
          {{ todayCard.suggestion }}
        </p>

        <!-- 推荐食材和食疗 -->
        <div class="today-row">
          <div class="today-block">
            <div class="label">推荐食材</div>
            <div class="chips">
              <span v-for="food in todayCard.foods" :key="food" class="chip">
                {{ food }}
              </span>
            </div>
          </div>
          <div class="today-block">
            <div class="label">推荐食疗</div>
            <div class="therapy-name">{{ todayCard.therapy }}</div>
          </div>
        </div>

        <!-- 养生小贴士 -->
        <div class="today-tip">
          <span class="tip-icon">🌱</span>
          <span class="tip-text">{{ todayCard.tip }}</span>
        </div>
      </div>
    </section>

    <!-- 功能入口宫格 -->
    <section class="block">
      <div class="shortcut-row">
        <button v-for="item in shortcuts" :key="item.key" class="shortcut-item" type="button"
          @click="handleShortcut(item)">
          <div class="shortcut-icon">
            <svg v-if="item.icon === 'recipe'" viewBox="0 0 64 64" class="shortcut-svg">
              <!-- 生成菜谱 - 简约砂锅图标 -->
              <circle cx="32" cy="32" r="28" fill="currentColor" opacity="0.08"/>
              <!-- 锅身 -->
              <ellipse cx="32" cy="36" rx="16" ry="8" fill="currentColor" opacity="0.85"/>
              <path d="M16 36c0 8 7 14 16 14s16-6 16-14" fill="currentColor" opacity="0.65"/>
              <!-- 锅盖 -->
              <ellipse cx="32" cy="28" rx="14" ry="5" fill="currentColor" opacity="0.45"/>
              <circle cx="32" cy="25" r="3" fill="currentColor" opacity="0.75"/>
              <!-- 锅耳 -->
              <circle cx="14" cy="36" r="3" fill="currentColor" opacity="0.55"/>
              <circle cx="50" cy="36" r="3" fill="currentColor" opacity="0.55"/>
            </svg>
            <svg v-else-if="item.icon === 'ai'" viewBox="0 0 64 64" class="shortcut-svg">
              <!-- 颐宝 AI - AI 智能芯片图标 -->
              <circle cx="32" cy="32" r="28" fill="currentColor" opacity="0.08"/>
              <!-- 芯片外框 -->
              <rect x="22" y="22" width="20" height="20" rx="4" fill="currentColor" opacity="0.85"/>
              <!-- 芯片内核 -->
              <rect x="27" y="27" width="10" height="10" rx="2" fill="currentColor" opacity="0.65"/>
              <!-- 四角连接点 -->
              <circle cx="32" cy="20" r="2.5" fill="currentColor" opacity="0.85"/>
              <circle cx="32" cy="44" r="2.5" fill="currentColor" opacity="0.85"/>
              <circle cx="20" cy="32" r="2.5" fill="currentColor" opacity="0.85"/>
              <circle cx="44" cy="32" r="2.5" fill="currentColor" opacity="0.85"/>
              <!-- 连接线 -->
              <line x1="32" y1="22.5" x2="32" y2="20" stroke="currentColor" stroke-width="2" opacity="0.6"/>
              <line x1="32" y1="44" x2="32" y2="41.5" stroke="currentColor" stroke-width="2" opacity="0.6"/>
              <line x1="22.5" y1="32" x2="20" y2="32" stroke="currentColor" stroke-width="2" opacity="0.6"/>
              <line x1="44" y1="32" x2="41.5" y2="32" stroke="currentColor" stroke-width="2" opacity="0.6"/>
            </svg>
            <svg v-else-if="item.icon === 'test'" viewBox="0 0 64 64" class="shortcut-svg">
              <!-- 体质测试 - 简约人像图标 -->
              <circle cx="32" cy="32" r="28" fill="currentColor" opacity="0.08"/>
              <!-- 头部 -->
              <circle cx="32" cy="24" r="8" fill="currentColor" opacity="0.85"/>
              <!-- 身体 -->
              <path d="M20 34c0-4 5-6 12-6s12 2 12 6v14H20V34z" fill="currentColor" opacity="0.65"/>
              <!-- 经络线 -->
              <line x1="32" y1="34" x2="32" y2="44" stroke="currentColor" stroke-width="2" opacity="0.9"/>
              <circle cx="32" cy="38" r="2" fill="currentColor" opacity="0.85"/>
            </svg>
            <svg v-else-if="item.icon === 'smart'" viewBox="0 0 64 64" class="shortcut-svg">
              <!-- 智能推荐 - 简约星芒图标 -->
              <circle cx="32" cy="32" r="28" fill="currentColor" opacity="0.08"/>
              <!-- 星芒主体 -->
              <path d="M32 16l2 8 8 2-8 2-2 8-2-8-8-2 8-2 2-8z" fill="currentColor" opacity="0.85"/>
              <!-- 中心圆 -->
              <circle cx="32" cy="32" r="6" fill="currentColor" opacity="0.65"/>
              <!-- 环绕光点 -->
              <circle cx="32" cy="20" r="2" fill="currentColor" opacity="0.85"/>
              <circle cx="44" cy="32" r="2" fill="currentColor" opacity="0.85"/>
              <circle cx="32" cy="44" r="2" fill="currentColor" opacity="0.85"/>
              <circle cx="20" cy="32" r="2" fill="currentColor" opacity="0.85"/>
            </svg>
          </div>
          <div class="shortcut-text">
            <div class="shortcut-title">{{ item.title }}</div>
            <div class="shortcut-desc">{{ item.desc }}</div>
          </div>
        </button>
      </div>
    </section>

    <!-- 五行图谱横幅 -->
    <section class="block">
      <div class="wuxing-banner" @click="router.push('/knowledge-graph')">
        <div class="wuxing-bg"></div>
        <div class="wuxing-content">
          <div class="wuxing-icon-wrapper">
            <div class="wuxing-spinning-icon">
              <svg viewBox="0 0 100 100" class="wuxing-svg">
                <!-- 五行相生循环 -->
                <circle cx="50" cy="50" r="45" fill="none" stroke="currentColor" stroke-width="1" opacity="0.3"/>
                <circle cx="50" cy="50" r="35" fill="none" stroke="currentColor" stroke-width="1" opacity="0.5"/>
                <circle cx="50" cy="50" r="25" fill="none" stroke="currentColor" stroke-width="1.5" opacity="0.7"/>
                <!-- 五行元素 -->
                <text x="50" y="20" text-anchor="middle" font-size="12" fill="currentColor" opacity="0.9">金</text>
                <text x="80" y="55" text-anchor="middle" font-size="12" fill="currentColor" opacity="0.9">水</text>
                <text x="50" y="90" text-anchor="middle" font-size="12" fill="currentColor" opacity="0.9">木</text>
                <text x="20" y="55" text-anchor="middle" font-size="12" fill="currentColor" opacity="0.9">火</text>
                <text x="50" y="50" text-anchor="middle" font-size="10" fill="currentColor" opacity="0.6">土</text>
              </svg>
            </div>
          </div>
          <div class="wuxing-text">
            <h3 class="wuxing-title">探索五行食疗宇宙：知识图谱</h3>
            <p class="wuxing-desc">可视化呈现五行相生相克，解锁中医食疗智慧</p>
          </div>
          <div class="wuxing-arrow">›</div>
        </div>
      </div>
    </section>

    <!-- 饮食资讯 -->
    <section class="block">
      <h2 class="section-title">饮食资讯</h2>
      <div class="article-list">
        <article v-for="item in newsList" :key="item.link" class="article-card no-image" @click="openNews(item.link)">
          <div class="article-body">
            <div class="article-head">
              <span class="article-tag">{{ item.source }}</span>
            </div>
            <h3 class="article-title">{{ item.title }}</h3>
            <p class="article-desc">
              {{ item.summary }}
            </p>
          </div>
        </article>
      </div>
    </section>
  </div>
</template>

<style scoped>
.page-home {
  background: var(--bg);
}

.home-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 0 18px;
}

.home-header .left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.menu-icon {
  width: 24px;
  height: 24px;
  color: var(--text-h);
  opacity: 0.8;
  transition: all 0.3s ease;
}

.menu-icon:hover {
  opacity: 1;
  transform: rotate(-5deg);
}

.logo-text {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-h);
}

.header-icon {
  font-size: 20px;
}

.block {
  margin-bottom: 24px;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-h);
  margin: 0 0 12px;
}

.today-card {
  background: linear-gradient(135deg, rgba(125, 157, 138, 0.65) 0%, rgba(90, 122, 104, 0.60) 100%),
              url('@/今日养生建议.jpg');
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  border-radius: var(--radius-lg);
  padding: 20px 20px 18px;
  box-shadow: var(--shadow-lg);
  color: #ffffff;
  position: relative;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.28);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
}

.today-card::before {
  content: '';
  position: absolute;
  top: -50%;
  right: -20%;
  width: 200px;
  height: 200px;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.12) 0%, transparent 70%);
  border-radius: 50%;
  pointer-events: none;
}

/* 顶部信息行 */
.today-top-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 14px;
}

.season-tag-wrapper {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
  border-radius: 999px;
}

.season-icon {
  width: 18px;
  height: 18px;
  color: rgba(255, 255, 255, 0.9);
}

.season-text {
  font-size: 13px;
  font-weight: 600;
  color: #ffffff;
  letter-spacing: 0.5px;
}

.weather-location-wrapper {
  display: flex;
  gap: 6px;
}

.weather-tag {
  font-size: 12px;
  color: #ffffff;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
  padding: 6px 12px;
  border-radius: 999px;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  white-space: nowrap;
  user-select: none;
  transition: all 0.2s ease;
  font-weight: 500;
}

.weather-tag:active {
  transform: scale(0.95);
  background: rgba(255, 255, 255, 0.25);
}

.location-tag {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: var(--primary-dark);
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
  padding: 6px 12px;
  border-radius: 999px;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  white-space: nowrap;
  user-select: none;
  transition: all 0.2s ease;
  font-weight: 600;
}

.location-icon {
  width: 14px;
  height: 14px;
}

.location-text {
  font-size: 12px;
}

.location-tag:active {
  transform: scale(0.95);
  background: #ffffff;
}

/* 主标题 */
.today-title {
  font-size: 24px;
  font-weight: 700;
  color: #ffffff;
  margin: 0 0 12px;
  letter-spacing: -0.3px;
  line-height: 1.3;
}

/* 风险干预标签 - 低调简约 */
.env-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 12px;
}

.risk-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.risk-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #FFB347;
  box-shadow: 0 0 8px rgba(255, 179, 71, 0.6);
  animation: dotPulse 2s ease-in-out infinite;
}

@keyframes dotPulse {
  0%, 100% {
    opacity: 0.6;
    transform: scale(1);
  }
  50% {
    opacity: 1;
    transform: scale(1.2);
  }
}

.risk-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.95);
  font-weight: 500;
  letter-spacing: 0.3px;
}

.today-suggestion {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.95);
  line-height: 1.6;
  margin: 12px 0 16px;
  font-weight: 400;
}

.today-row {
  display: flex;
  gap: 12px;
  margin-bottom: 12px;
}

.today-block {
  flex: 1;
  background: rgba(255, 255, 255, 0.18);
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
  border-radius: 12px;
  padding: 14px 14px 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
}

.label {
  font-size: 12px;
  color: rgba(227, 251, 249, 0.9);
  margin-bottom: 8px;
  font-weight: 500;
  letter-spacing: 0.3px;
}

.chips {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.chip {
  padding: 6px 12px;
  border-radius: 999px;
  background: rgba(26, 163, 157, 0.35);
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
  color: #ffffff;
  font-size: 13px;
  font-weight: 600;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.12);
  border: 1px solid rgba(255, 255, 255, 0.25);
}

.therapy-name {
  font-size: 15px;
  font-weight: 700;
  color: #ffffff;
  letter-spacing: -0.2px;
  padding: 6px 12px;
  border-radius: 999px;
  background: rgba(26, 163, 157, 0.35);
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.12);
  border: 1px solid rgba(255, 255, 255, 0.25);
  display: inline-block;
}

.today-tip {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 10px 12px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.tip-icon {
  font-size: 16px;
  margin-top: 2px;
}

.tip-text {
  font-size: 13px;
  color: #e8fffb;
  line-height: 1.5;
}

.shortcut-row {
  display: flex;
  gap: 12px;
}

.shortcut-item {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 14px 12px 12px;
  border-radius: var(--radius-lg);
  border: 1px solid rgba(255, 255, 255, 0.3);
  background: linear-gradient(145deg, #ffffff 0%, rgba(245, 250, 248, 0.95) 100%);
  box-shadow: 
    0 4px 16px rgba(125, 157, 138, 0.1),
    0 1px 3px rgba(0, 0, 0, 0.05);
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.shortcut-item::before {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, var(--primary) 0%, var(--primary-light) 100%);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.shortcut-item:hover {
  transform: translateY(-6px);
  box-shadow: 
    0 12px 32px rgba(125, 157, 138, 0.2),
    0 2px 6px rgba(0, 0, 0, 0.08);
  border-color: rgba(125, 157, 138, 0.3);
}

.shortcut-item:hover::before {
  opacity: 1;
}

.shortcut-item:active {
  transform: translateY(-2px) scale(0.98);
  box-shadow: 
    0 6px 20px rgba(125, 157, 138, 0.15),
    0 1px 2px rgba(0, 0, 0, 0.06);
}

.shortcut-icon {
  width: 52px;
  height: 52px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 2px;
  box-shadow: 
    inset 0 3px 12px rgba(0, 0, 0, 0.08),
    0 4px 12px rgba(0, 0, 0, 0.1);
  transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
  position: relative;
}

/* 生成菜谱 - 浅橘色莫兰迪 */
.shortcut-item:nth-child(1) .shortcut-icon {
  background: linear-gradient(135deg, rgba(230, 180, 150, 0.4) 0%, rgba(240, 200, 170, 0.5) 50%, rgba(250, 220, 200, 0.6) 100%);
}

/* 颐宝 AI - 淡紫色莫兰迪 */
.shortcut-item:nth-child(2) .shortcut-icon {
  background: linear-gradient(135deg, rgba(200, 190, 220, 0.4) 0%, rgba(215, 205, 230, 0.5) 50%, rgba(230, 220, 240, 0.6) 100%);
}

/* 体质测试 - 淡蓝色莫兰迪 */
.shortcut-item:nth-child(3) .shortcut-icon {
  background: linear-gradient(135deg, rgba(180, 200, 220, 0.4) 0%, rgba(200, 215, 230, 0.5) 50%, rgba(220, 230, 240, 0.6) 100%);
}

/* 智能推荐 - 浅绿色莫兰迪 */
.shortcut-item:nth-child(4) .shortcut-icon {
  background: linear-gradient(135deg, rgba(190, 220, 200, 0.4) 0%, rgba(205, 230, 215, 0.5) 50%, rgba(220, 240, 230, 0.6) 100%);
}

.shortcut-item:hover .shortcut-icon {
  transform: scale(1.12) rotate(-5deg);
  box-shadow: 
    inset 0 4px 16px rgba(0, 0, 0, 0.12),
    0 8px 24px rgba(0, 0, 0, 0.15),
    0 0 20px rgba(255, 255, 255, 0.3);
}

.shortcut-item:active .shortcut-icon {
  transform: scale(1.05) rotate(-3deg);
  box-shadow: 
    inset 0 3px 10px rgba(0, 0, 0, 0.1),
    0 4px 16px rgba(0, 0, 0, 0.12);
}

.shortcut-svg {
  width: 44px;
  height: 44px;
  filter: drop-shadow(0 3px 8px rgba(0, 0, 0, 0.2));
  transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
}

/* 生成菜谱 - 橘棕色 */
.shortcut-item:nth-child(1) .shortcut-svg {
  color: #c97c5d;
}

/* 颐宝 AI - 紫灰色 */
.shortcut-item:nth-child(2) .shortcut-svg {
  color: #8b7a9e;
}

/* 体质测试 - 蓝灰色 */
.shortcut-item:nth-child(3) .shortcut-svg {
  color: #5d7a8c;
}

/* 智能推荐 - 绿灰色 */
.shortcut-item:nth-child(4) .shortcut-svg {
  color: #6b8c7a;
}

.shortcut-item:hover .shortcut-svg {
  filter: drop-shadow(0 6px 16px rgba(0, 0, 0, 0.3));
  transform: scale(1.08);
}

.shortcut-item:active .shortcut-svg {
  filter: drop-shadow(0 4px 12px rgba(0, 0, 0, 0.25));
  transform: scale(0.95);
}

.shortcut-text {
  text-align: center;
}

.shortcut-title {
  font-size: 14px;
  font-weight: 700;
  color: var(--text-h);
  margin-bottom: 2px;
  letter-spacing: -0.2px;
}

.shortcut-desc {
  font-size: 11px;
  color: var(--text-muted);
  line-height: 1.4;
  font-weight: 400;
}

/* 五行图谱横幅 */
.wuxing-banner {
  position: relative;
  background: linear-gradient(135deg, #f5f0e6 0%, #e8e0d0 50%, #d4c5b0 100%);
  border-radius: 16px;
  overflow: hidden;
  cursor: pointer;
  box-shadow: 0 4px 20px rgba(139, 119, 90, 0.15);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border: 1px solid rgba(139, 119, 90, 0.2);
}

.wuxing-banner::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: 
    repeating-linear-gradient(
      90deg,
      transparent,
      transparent 2px,
      rgba(139, 119, 90, 0.03) 2px,
      rgba(139, 119, 90, 0.03) 4px
    );
  pointer-events: none;
}

.wuxing-banner:active {
  transform: scale(0.98);
  box-shadow: 0 2px 12px rgba(139, 119, 90, 0.1);
}

.wuxing-content {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px 24px;
}

.wuxing-icon-wrapper {
  flex-shrink: 0;
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: linear-gradient(135deg, rgba(139, 119, 90, 0.1) 0%, rgba(160, 140, 110, 0.15) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: inset 0 2px 8px rgba(139, 119, 90, 0.1);
}

.wuxing-spinning-icon {
  width: 60px;
  height: 60px;
  animation: spin 20s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.wuxing-svg {
  width: 100%;
  height: 100%;
  color: #8b775a;
}

.wuxing-text {
  flex: 1;
  min-width: 0;
}

.wuxing-title {
  font-size: 17px;
  font-weight: 700;
  color: #5c4a3d;
  margin: 0 0 6px;
  letter-spacing: -0.2px;
  line-height: 1.4;
}

.wuxing-desc {
  font-size: 13px;
  color: #8b775a;
  margin: 0;
  line-height: 1.5;
  font-weight: 400;
}

.wuxing-arrow {
  font-size: 32px;
  color: #a08c6e;
  font-weight: 300;
  opacity: 0.6;
}

.article-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.article-card {
  background: #ffffff;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  gap: 12px;
  padding: 12px;
}

.article-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.article-card.no-image {
  padding: 16px;
}

.article-card:active {
  transform: scale(0.98);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}

.article-cover {
  width: 100px;
  height: 80px;
  border-radius: 12px;
  overflow: hidden;
  background: linear-gradient(135deg, rgba(26, 163, 157, 0.1) 0%, rgba(39, 179, 168, 0.1) 100%);
  flex-shrink: 0;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.article-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.article-card:active .article-image {
  transform: scale(1.05);
}

.cover-placeholder {
  font-size: 32px;
  opacity: 0.6;
}

.article-body {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.article-head {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.article-tag {
  padding: 4px 10px;
  background: var(--primary-light);
  border-radius: 999px;
  font-size: 12px;
  font-weight: 600;
  color: var(--primary);
}

.article-title {
  font-size: 16px;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0 0 6px;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.article-desc {
  font-size: 13px;
  color: #999;
  line-height: 1.6;
  margin: 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
