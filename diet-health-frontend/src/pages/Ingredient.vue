<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import IngredientCard from '../components/IngredientCard.vue'
import IngredientDetailModal from '../components/IngredientDetailModal.vue'
import { getIngredientCategoryList, getIngredientList } from '@/api/mock'

const router = useRouter()
const searchKeyword = ref('')
const activeCategory = ref(0)
const categories = ref(['全部'])
const ingredients = ref([])
const loading = ref(false)
const error = ref('')
const selectedIngredient = ref(null)
const showModal = ref(false)

async function loadList() {
  loading.value = true
  error.value = ''
  try {
    const cat = categories.value[activeCategory.value] || '全部'
    const list = await getIngredientList(cat, searchKeyword.value)
    ingredients.value = list
  } catch (err) {
    console.error('加载食材列表失败:', err)
    error.value = '加载失败，请检查网络连接或稍后重试'
  } finally {
    loading.value = false
  }
}

function handleCardClick(ingredient) {
  console.log('点击食材卡片:', ingredient)
  if (ingredient) {
    selectedIngredient.value = ingredient
    showModal.value = true
  }
}

onMounted(async () => {
  loading.value = true
  try {
    categories.value = await getIngredientCategoryList()
    await loadList()
  } catch (err) {
    console.error('初始化失败:', err)
    error.value = '初始化失败，请刷新页面重试'
  } finally {
    loading.value = false
  }
})

watch([activeCategory, searchKeyword], loadList)
</script>

<template>
  <div class="page-ingredient app-page">
    <header class="page-header">
      <h1 class="page-title">食材百科</h1>
    </header>

    <div class="search-bar">
      <svg viewBox="0 0 24 24" class="search-icon">
        <circle cx="11" cy="11" r="7" stroke="currentColor" stroke-width="2" fill="none"/>
        <line x1="16" y1="16" x2="21" y2="21" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
      </svg>
      <input
        v-model="searchKeyword"
        type="text"
        class="search-input"
        placeholder="搜索食材、功效或方子"
      />
    </div>

    <div class="category-tabs">
      <button
        v-for="(cat, i) in categories"
        :key="cat"
        class="tab-btn"
        :class="{ active: activeCategory === i }"
        @click="activeCategory = i"
      >
        {{ cat }}
      </button>
    </div>

    <div class="ingredient-grid">
      <!-- 骨架屏状态 -->
      <template v-if="loading && ingredients.length === 0">
        <div v-for="i in 6" :key="i" class="skeleton-card">
          <van-skeleton-image block class="skeleton-img" />
          <van-skeleton-paragraph :row="2" class="skeleton-info" />
        </div>
      </template>

      <div v-else-if="error" class="error-state">
        <span class="error-icon">⚠️</span>
        <span class="error-text">{{ error }}</span>
      </div>
      <IngredientCard
        v-else
        v-for="item in ingredients"
        :key="item.id"
        :name="item.name"
        :effect="item.effect"
        :image="item.image"
        :tag="item.tag"
        :suitable="item.suitable"
        :avoid="item.avoid"
        :methods="item.methods"
        :ingredient-data="item"
        @click="handleCardClick"
      />
    </div>

    <!-- 详情弹窗 -->
    <IngredientDetailModal
      v-if="showModal"
      :ingredient="selectedIngredient"
      :visible="showModal"
      @close="showModal = false"
    />
  </div>
</template>

<style scoped>
.page-ingredient {
  background: var(--bg);
}
.page-header {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px 20px 16px;
  background: transparent;
}

.page-title {
  font-size: 22px;
  font-weight: 700;
  color: #1a1a1a;
  margin: 0;
  letter-spacing: -0.3px;
}

.search-bar {
  display: flex;
  align-items: center;
  gap: 10px;
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  padding: 16px 20px;
  margin: 0 16px 20px;
  box-shadow: var(--shadow);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.search-bar:focus-within {
  box-shadow: var(--shadow-lg);
  transform: translateY(-1px);
}

.search-icon {
  width: 20px;
  height: 20px;
  color: var(--text-muted);
  transition: color 0.3s ease;
}

.search-bar:focus-within .search-icon {
  color: var(--primary);
}

.search-input {
  flex: 1;
  border: none;
  background: transparent;
  font-size: 15px;
  outline: none;
  color: var(--text);
}

.search-input::placeholder {
  color: var(--text-muted);
}

.category-tabs {
  display: flex;
  gap: 10px;
  margin: 0 16px 20px;
  overflow-x: auto;
  padding: 4px 0;
  -webkit-overflow-scrolling: touch;
}

.category-tabs::-webkit-scrollbar {
  display: none;
}

.tab-btn {
  flex-shrink: 0;
  padding: 12px 20px;
  border-radius: 999px;
  border: none;
  background: var(--bg-card);
  color: var(--text-secondary);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  white-space: nowrap;
  box-shadow: var(--shadow-sm);
}

.tab-btn:active {
  transform: scale(0.96);
}

.tab-btn.active {
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
  color: #fff;
  box-shadow: var(--shadow);
}
.ingredient-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  padding: 0 16px;
}

/* 骨架屏样式 */
.skeleton-card {
  background: var(--bg-card);
  border-radius: var(--radius);
  overflow: hidden;
  padding-bottom: 10px;
  border: 1px solid var(--border);
}

.skeleton-img {
  width: 100% !important;
  height: 160px !important;
  background: linear-gradient(135deg, var(--primary-light), var(--bg-subtle));
}

.skeleton-info {
  padding: 10px;
}

.error-state {
  grid-column: 1 / -1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  gap: 16px;
}

.error-icon {
  font-size: 56px;
  opacity: 0.5;
  filter: grayscale(0.3);
}

.loading-icon,
.error-icon {
  font-size: 56px;
  opacity: 0.5;
}

.loading-text,
.error-text {
  font-size: 15px;
  color: #999;
  font-weight: 500;
}
</style>
