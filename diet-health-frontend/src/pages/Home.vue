<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getNews } from '@/api/news'
import { getWellnessReport } from '@/api/mock'

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
    
    const report = await getWellnessReport(constitution, {})
    console.log('📋 今日养生报告:', report)
    
    // 更新今日养生卡片
    todayCard.value = {
      title: report.suggestion_title || '今日养生建议',
      suggestion: report.intro || '根据您的体质特点，建议保持均衡饮食，适量运动。',
      foods: report.recommended_ingredients?.length > 0 ? report.recommended_ingredients : ['山药', '红枣', '枸杞'],
      therapy: report.recommended_recipe || '山药红枣粥',
      tip: report.recipe_tip || '早餐一碗山药红枣粥，有助于暖胃护脾。'
    }
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
  suggestion: '饮用生姜茶可以温中散寒，促进血液循环，适合今天的气候与体质状态。',
  foods: ['山药', '红枣', '枸杞'],
  therapy: '山药红枣粥',
  tip: '早餐一碗山药红枣粥，晚间一杯温热生姜茶，有助于暖胃护脾、驱散寒气。'
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
        <span class="menu-icon">☰</span>
        <span class="logo-text">苏叶食疗</span>
      </div>
    </header>

    <!-- 今日养生卡片 -->
    <section class="block">
      <div class="today-card">
        <div class="today-header">
          <div class="today-title-wrap">
            <span class="today-badge">今日养生</span>
            <h2 class="today-title">{{ todayCard.title }}</h2>
          </div>
          <span class="today-tag">温中 · 补气</span>
        </div>
        <p class="today-suggestion">
          {{ todayCard.suggestion }}
        </p>
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
            <svg v-if="item.icon === 'recipe'" viewBox="0 0 64 64" fill="currentColor" class="shortcut-svg">
              <!-- 生成菜谱 - 古代竹简/食谱 -->
              <rect x="14" y="12" width="36" height="40" rx="2" opacity="0.15" stroke="currentColor" stroke-width="2"/>
              <line x1="22" y1="20" x2="42" y2="20" stroke="currentColor" stroke-width="2.5" opacity="0.9"/>
              <line x1="22" y1="28" x2="42" y2="28" stroke="currentColor" stroke-width="2.5" opacity="0.7"/>
              <line x1="22" y1="36" x2="42" y2="36" stroke="currentColor" stroke-width="2.5" opacity="0.7"/>
              <line x1="22" y1="44" x2="36" y2="44" stroke="currentColor" stroke-width="2.5" opacity="0.7"/>
              <circle cx="32" cy="16" r="3" opacity="0.8"/>
            </svg>
            <svg v-else-if="item.icon === 'ai'" viewBox="0 0 64 64" fill="currentColor" class="shortcut-svg">
              <!-- 颐宝 AI - 中医把脉/问诊 -->
              <circle cx="32" cy="18" r="10" opacity="0.15" stroke="currentColor" stroke-width="2" fill="none"/>
              <path d="M32 8v6" stroke="currentColor" stroke-width="2" opacity="0.6"/>
              <path d="M20 52C20 44 24 38 32 38s12 6 12 14" stroke="currentColor" stroke-width="2.5" fill="none" opacity="0.9"/>
              <circle cx="32" cy="32" r="4" opacity="0.8"/>
              <path d="M26 42c3-2 9-2 12 0" stroke="currentColor" stroke-width="2" fill="none" opacity="0.6"/>
            </svg>
            <svg v-else-if="item.icon === 'test'" viewBox="0 0 64 64" fill="currentColor" class="shortcut-svg">
              <!-- 体质测试 - 太极/阴阳鱼 -->
              <circle cx="32" cy="32" r="22" opacity="0.15" stroke="currentColor" stroke-width="2" fill="none"/>
              <path d="M32 10a22 22 0 1 0 0 44 22 22 0 0 0 0-44z" opacity="0.3"/>
              <circle cx="32" cy="21" r="5" opacity="0.9"/>
              <circle cx="32" cy="43" r="5" opacity="0.9"/>
              <path d="M32 10c0 0-8 10-8 22s8 22 8 22" stroke="currentColor" stroke-width="2" fill="none" opacity="0.6"/>
            </svg>
            <svg v-else-if="item.icon === 'smart'" viewBox="0 0 64 64" fill="currentColor" class="shortcut-svg">
              <!-- 智能推荐 - 药葫芦/炼丹炉 -->
              <circle cx="32" cy="14" r="6" opacity="0.15" stroke="currentColor" stroke-width="2" fill="none"/>
              <path d="M24 24c0-4 4-6 8-6s8 2 8 6v24c0 8-4 12-8 12s-8-4-8-12V24z" opacity="0.9"/>
              <circle cx="32" cy="36" r="5" opacity="0.3"/>
              <path d="M28 24V18h8v6" stroke="currentColor" stroke-width="2" fill="none" opacity="0.6"/>
              <circle cx="32" cy="14" r="2" opacity="0.8"/>
            </svg>
          </div>
          <div class="shortcut-text">
            <div class="shortcut-title">{{ item.title }}</div>
            <div class="shortcut-desc">{{ item.desc }}</div>
          </div>
        </button>
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
  font-size: 20px;
  color: var(--text-h);
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
  background: linear-gradient(135deg, #1aa39d, #27b3a8);
  border-radius: 18px;
  padding: 18px 16px 16px;
  box-shadow: var(--shadow);
  color: #ffffff;
}

.today-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.today-title-wrap {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.today-badge {
  display: inline-flex;
  align-items: center;
  padding: 2px 8px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.24);
  color: #ffffff;
  font-size: 12px;
}

.today-title {
  font-size: 20px;
  font-weight: 600;
  color: #ffffff;
  margin: 0;
}

.today-tag {
  font-size: 13px;
  color: #ffffff;
  background: rgba(0, 0, 0, 0.12);
  padding: 4px 10px;
  border-radius: 999px;
}

.today-suggestion {
  font-size: 14px;
  color: #f5fffe;
  line-height: 1.5;
  margin: 8px 0 12px;
}

.today-row {
  display: flex;
  gap: 12px;
  margin-bottom: 12px;
}

.today-block {
  flex: 1;
  background: rgba(255, 255, 255, 0.14);
  border-radius: 12px;
  padding: 10px 10px 8px;
}

.label {
  font-size: 12px;
  color: #e3fbf9;
  margin-bottom: 6px;
}

.chips {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.chip {
  padding: 4px 10px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.18);
  color: #ffffff;
  font-size: 12px;
}

.therapy-name {
  font-size: 14px;
  font-weight: 600;
  color: #ffffff;
}

.today-tip {
  display: flex;
  align-items: flex-start;
  gap: 6px;
  padding: 8px 10px;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.16);
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
  justify-content: space-between;
  gap: 12px;
}

.shortcut-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  padding: 12px 8px 10px;
  border-radius: 14px;
  border: none;
  background: #ffffff;
  box-shadow: var(--shadow);
  cursor: pointer;
}

.shortcut-icon {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: linear-gradient(135deg, rgba(26, 163, 157, 0.12) 0%, rgba(39, 179, 168, 0.08) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 4px;
  box-shadow: inset 0 2px 8px rgba(26, 163, 157, 0.08);
}

.shortcut-svg {
  width: 36px;
  height: 36px;
  color: #1aa39d;
}

.shortcut-text {
  text-align: center;
}

.shortcut-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-h);
  margin-bottom: 2px;
  line-height: 1.3;
}

.shortcut-desc {
  font-size: 11px;
  color: var(--text-muted);
  line-height: 1.4;
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
  background: linear-gradient(135deg, rgba(26, 163, 157, 0.15) 0%, rgba(39, 179, 168, 0.15) 100%);
  border-radius: 999px;
  font-size: 12px;
  font-weight: 600;
  color: #1aa39d;
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
