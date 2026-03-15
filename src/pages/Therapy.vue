<script setup>
import { ref, onMounted, watch } from 'vue'
import TherapyCard from '../components/TherapyCard.vue'
import { getTherapyFilters, getTherapyList } from '../api/mock'

const searchKeyword = ref('')
const activeFilter = ref(0)
const filters = ref(['全部'])
const therapyList = ref([])

async function loadList() {
  const filter = filters.value[activeFilter.value] || '全部'
  const list = await getTherapyList(filter, searchKeyword.value)
  therapyList.value = list
}

onMounted(async () => {
  filters.value = await getTherapyFilters()
  await loadList()
})

watch([activeFilter, searchKeyword], loadList)
</script>

<template>
  <div class="page-therapy app-page">
    <header class="page-header">
      <h1 class="page-title">食疗方案</h1>
      <span class="header-icon">🔔</span>
    </header>

    <div class="search-bar">
      <span class="search-icon">🔍</span>
      <input
        v-model="searchKeyword"
        type="text"
        class="search-input"
        placeholder="搜索食材、症状或方案"
      />
    </div>

    <div class="filter-row">
      <button
        v-for="(f, i) in filters"
        :key="f"
        class="filter-btn"
        :class="{ active: activeFilter === i }"
        @click="activeFilter = i"
      >
        {{ f }}
        <span v-if="i > 0" class="filter-arrow">▼</span>
      </button>
    </div>

    <div class="therapy-list">
      <TherapyCard
        v-for="item in therapyList"
        :key="item.id"
        :title="item.title"
        :tag="item.tag"
        :effect="item.effect"
        :desc="item.desc"
        :tags="item.tags"
        :button-text="item.buttonText"
        :primary-button="item.primaryButton"
        :image="item.image"
      />
    </div>
  </div>
</template>

<style scoped>
.page-therapy {
  background: var(--bg);
}
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 0 16px;
}
.page-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-h);
  margin: 0;
}
.header-icon {
  font-size: 22px;
}
.search-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  background: var(--primary-light);
  border-radius: var(--radius-sm);
  padding: 12px 14px;
  margin-bottom: 16px;
}
.search-icon {
  font-size: 18px;
  color: var(--primary);
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
.filter-row {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}
.filter-btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 8px 14px;
  border-radius: var(--radius-sm);
  border: 1px solid var(--primary);
  background: var(--bg-card);
  color: var(--primary);
  font-size: 14px;
  cursor: pointer;
}
.filter-btn.active {
  background: var(--primary);
  color: #fff;
  border-color: var(--primary);
}
.filter-arrow {
  font-size: 10px;
  margin-left: 2px;
  opacity: 0.8;
}
.therapy-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
</style>
