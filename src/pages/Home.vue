<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import RecipeCard from '../components/RecipeCard.vue'
import { getWellnessReport, getIngredientCategories, getPopularTherapy } from '../api/mock'

const router = useRouter()
const wellness = ref({ score: 0, change: '', advice: '' })
const categories = ref([])
const popularTherapy = ref([])
const loading = ref(true)

onMounted(async () => {
  try {
    const [w, c, p] = await Promise.all([
      getWellnessReport(),
      getIngredientCategories(),
      getPopularTherapy()
    ])
    wellness.value = w
    categories.value = c
    popularTherapy.value = p
  } finally {
    loading.value = false
  }
})

function goIngredient() {
  router.push('/ingredient')
}
function goTherapy() {
  router.push('/therapy')
}

function categoryIcon(icon) {
  const map = { leaf: '🌿', water: '💧', wind: '🍃', all: '▦' }
  return map[icon] || '▦'
}
</script>

<template>
  <div class="page-home app-page">
    <!-- 顶部 -->
    <header class="home-header">
      <span class="logo-icon">🌿</span>
      <span class="logo-text">草本养生</span>
    </header>

    <!-- 今日养生报告 -->
    <section class="block">
      <h2 class="block-title">今日养生报告</h2>
      <div class="score-card">
        <div class="score-label">今日健康评分</div>
        <div class="score-value">
          <span class="num">{{ wellness.score }}</span>
          <span class="change up">{{ wellness.change || '' }}</span>
        </div>
      </div>
      <div class="advice-card">
        <div class="advice-head">
          <span class="advice-icon">💡</span>
          <span class="advice-title">健康建议</span>
        </div>
        <p class="advice-text">{{ wellness.advice || '' }}</p>
        <a class="advice-link" href="javascript:;">查看详细建议 →</a>
      </div>
    </section>

    <!-- 食材百科 -->
    <section class="block">
      <h2 class="block-title">食材百科</h2>
      <div class="search-bar" @click="goIngredient">
        <span class="search-icon">🔍</span>
        <span class="search-placeholder">搜索食材</span>
        <span class="search-hint">人参、茯苓、枸杞...</span>
      </div>
      <div class="category-row">
        <div
          v-for="(cat, i) in categories"
          :key="cat.id || i"
          class="category-item"
          @click="cat.icon === 'all' ? goIngredient() : null"
        >
          <div class="category-icon">{{ categoryIcon(cat.icon) }}</div>
          <span class="category-label">{{ cat.label }}</span>
        </div>
      </div>
    </section>

    <!-- 热门食疗 -->
    <section class="block">
      <div class="block-head">
        <h2 class="block-title">热门食疗</h2>
        <a class="block-more" @click="goTherapy">更多</a>
      </div>
      <div class="therapy-list">
        <RecipeCard
          v-for="item in popularTherapy"
          :key="item.id"
          :title="item.title"
          :tag="item.tag"
          :desc="item.desc"
          :time="item.time"
          :calorie="item.calorie"
          :image="item.image"
          @click="goTherapy"
        />
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
  gap: 8px;
  padding: 16px 0 20px;
}
.logo-icon {
  font-size: 24px;
}
.logo-text {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-h);
}
.block {
  margin-bottom: 24px;
}
.block-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-h);
  margin: 0 0 12px;
}
.block-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}
.block-more {
  font-size: 14px;
  color: var(--primary);
}
.score-card {
  background: var(--primary-light);
  border-radius: var(--radius);
  padding: 16px;
  margin-bottom: 12px;
}
.score-label {
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 4px;
}
.score-value {
  display: flex;
  align-items: baseline;
  gap: 8px;
}
.score-value .num {
  font-size: 36px;
  font-weight: 700;
  color: var(--primary);
}
.score-value .change.up {
  font-size: 14px;
  color: var(--primary);
}
.advice-card {
  background: var(--bg-card);
  border-radius: var(--radius);
  padding: 16px;
  box-shadow: var(--shadow);
}
.advice-head {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 8px;
}
.advice-icon {
  font-size: 18px;
}
.advice-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-h);
}
.advice-text {
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.5;
  margin: 0 0 12px;
}
.advice-link {
  font-size: 14px;
  color: var(--primary);
  text-decoration: none;
}
.search-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  background: var(--bg-card);
  border-radius: var(--radius-sm);
  padding: 12px 14px;
  margin-bottom: 16px;
  box-shadow: var(--shadow);
}
.search-icon {
  font-size: 18px;
}
.search-placeholder {
  font-size: 14px;
  color: var(--text-muted);
}
.search-hint {
  margin-left: auto;
  font-size: 12px;
  color: var(--text-muted);
}
.category-row {
  display: flex;
  justify-content: space-between;
  gap: 12px;
}
.category-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  color: var(--primary);
  cursor: pointer;
}
.category-icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: var(--primary-light);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
}
.category-label {
  font-size: 12px;
}
.therapy-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
</style>
