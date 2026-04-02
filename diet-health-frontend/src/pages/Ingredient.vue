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
      <span class="search-icon">🔍</span>
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
      <div v-if="loading" class="loading-state">
        <span class="loading-icon">⏳</span>
        <span class="loading-text">加载中...</span>
      </div>
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
  background: #ffffff;
  border: 2px solid #f0f0f0;
  border-radius: 16px;
  padding: 14px 18px;
  margin: 0 16px 16px;
  transition: all 0.2s ease;
}

.search-bar:focus-within {
  border-color: #1aa39d;
  box-shadow: 0 0 0 3px rgba(26, 163, 157, 0.1);
}

.search-icon {
  font-size: 20px;
  color: #999;
}

.search-input {
  flex: 1;
  border: none;
  background: transparent;
  font-size: 15px;
  outline: none;
  color: #333;
}

.search-input::placeholder {
  color: #bbb;
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
  padding: 10px 18px;
  border-radius: 999px;
  border: 2px solid #f0f0f0;
  background: #ffffff;
  color: #666;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.tab-btn:active {
  transform: scale(0.95);
}

.tab-btn.active {
  background: linear-gradient(135deg, #1aa39d 0%, #27b3a8 100%);
  color: #fff;
  border-color: transparent;
  box-shadow: 0 4px 12px rgba(26, 163, 157, 0.3);
}
.ingredient-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  padding: 0 16px;
}

.loading-state,
.error-state {
  grid-column: 1 / -1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  gap: 16px;
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
