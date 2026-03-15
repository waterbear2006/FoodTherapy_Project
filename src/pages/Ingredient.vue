<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import IngredientCard from '../components/IngredientCard.vue'
import { getIngredientCategoryList, getIngredientList } from '../api/mock'

const router = useRouter()
const searchKeyword = ref('')
const activeCategory = ref(0)
const categories = ref(['全部'])
const ingredients = ref([])

async function loadList() {
  const cat = categories.value[activeCategory.value] || '全部'
  const list = await getIngredientList(cat, searchKeyword.value)
  ingredients.value = list
}

onMounted(async () => {
  categories.value = await getIngredientCategoryList()
  await loadList()
})

watch([activeCategory, searchKeyword], loadList)
</script>

<template>
  <div class="page-ingredient app-page">
    <header class="page-header">
      <span class="back" @click="router.back()">←</span>
      <h1 class="page-title">食疗本草·养生智库</h1>
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
      <IngredientCard
        v-for="item in ingredients"
        :key="item.id"
        :name="item.name"
        :effect="item.effect"
        :image="item.image"
      />
    </div>
  </div>
</template>

<style scoped>
.page-ingredient {
  background: var(--bg);
}
.page-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 0 16px;
}
.back {
  font-size: 20px;
  color: var(--text-h);
  cursor: pointer;
}
.page-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-h);
  margin: 0;
  flex: 1;
  text-align: center;
}
.search-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #eee;
  border-radius: var(--radius-sm);
  padding: 12px 14px;
  margin-bottom: 16px;
}
.search-icon {
  font-size: 18px;
}
.search-input {
  flex: 1;
  border: none;
  background: transparent;
  font-size: 14px;
  outline: none;
}
.search-input::placeholder {
  color: var(--text-muted);
}
.category-tabs {
  display: flex;
  gap: 10px;
  margin-bottom: 16px;
  overflow-x: auto;
  padding-bottom: 4px;
}
.category-tabs::-webkit-scrollbar {
  display: none;
}
.tab-btn {
  flex-shrink: 0;
  padding: 8px 16px;
  border-radius: 20px;
  border: 1px solid var(--primary);
  background: var(--bg-card);
  color: var(--primary);
  font-size: 14px;
  cursor: pointer;
}
.tab-btn.active {
  background: var(--primary);
  color: #fff;
  border-color: var(--primary);
}
.ingredient-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}
</style>
