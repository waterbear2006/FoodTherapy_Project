<script setup>
import { ref, onMounted, watch } from 'vue'
import TherapyCard from '../components/TherapyCard.vue'
import TherapyDetailModal from '../components/TherapyDetailModal.vue'
import { getTherapyFilters, getTherapyList } from '@/api/mock'

const searchKeyword = ref('')
const activeFilter = ref(0)
const filters = ref(['全部'])
const filterCounts = ref({}) // 每个分类的数量统计
const therapyList = ref([])
const loading = ref(false)
const error = ref('')
const selectedTherapy = ref(null)
const showModal = ref(false)

async function loadList() {
  loading.value = true
  error.value = ''
  try {
    const filter = filters.value[activeFilter.value] || '全部'
    console.log('🔍 正在加载分类:', filter)
    
    // 调用 API 时传递参数
    const list = await getTherapyList(filter, searchKeyword.value)
    console.log(`✅ 分类 [${filter}] 加载到 ${list.length} 条数据`)
    
    if (list && list.length > 0) {
      console.log('第一条评论数据:', {
        id: list[0].id,
        name: list[0].name,
        suitable: list[0].suitable
      })
    } else {
      console.warn(`⚠️ 分类 [${filter}] 没有数据`)
    }
    
    therapyList.value = list
    
    // 更新分类统计（只在加载全部时统计）
    if (filter === '全部') {
      const counts = {}
      list.forEach(item => {
        if (item.suitable && Array.isArray(item.suitable)) {
          item.suitable.forEach(tag => {
            counts[tag] = (counts[tag] || 0) + 1
          })
        }
      })
      filterCounts.value = counts
      console.log('📊 体质统计:', counts)
    }
  } catch (err) {
    console.error('加载食疗方案失败:', err)
    error.value = '加载失败，请检查网络连接或稍后重试'
  } finally {
    loading.value = false
  }
}

function handleCardClick(therapy) {
  console.log('点击食疗卡片:', therapy)
  if (therapy) {
    selectedTherapy.value = therapy
    showModal.value = true
  }
}

onMounted(async () => {
  loading.value = true
  try {
    filters.value = await getTherapyFilters()
    // 先加载全部数据用于统计
    await loadList()
  } catch (err) {
    console.error('初始化失败:', err)
    error.value = '初始化失败，请刷新页面重试'
  } finally {
    loading.value = false
  }
})

watch([activeFilter, searchKeyword], loadList)
</script>

<template>
  <div class="page-therapy app-page">
    <header class="page-header">
      <h1 class="page-title">食疗库</h1>
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
        <span class="filter-name">{{ f }}</span>
        <span v-if="i === 0" class="filter-count">{{ therapyList.length }}</span>
        <span v-else class="filter-count">{{ filterCounts[f] || 0 }}</span>
      </button>
    </div>

    <div class="therapy-list">
      <!-- 骨架屏状态 -->
      <template v-if="loading && therapyList.length === 0">
        <div v-for="i in 4" :key="i" class="skeleton-card">
          <van-skeleton-image block class="skeleton-img" />
          <van-skeleton-paragraph :row="2" class="skeleton-info" />
        </div>
      </template>

      <div v-else-if="error" class="error-state">
        <span class="error-icon">⚠️</span>
        <span class="error-text">{{ error }}</span>
      </div>
      <div v-else-if="!loading && therapyList.length === 0" class="empty-state">
        <span class="empty-icon">📭</span>
        <span class="empty-text">暂无食疗方案</span>
      </div>
      <TherapyCard
        v-else
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
        :therapy-data="item"
        @click="handleCardClick"
      />
    </div>

    <!-- 详情弹窗 -->
    <TherapyDetailModal
      v-if="showModal"
      :therapy="selectedTherapy"
      :visible="showModal"
      @close="showModal = false"
    />
  </div>
</template>

<style scoped>
.page-therapy {
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

.filter-row {
  display: flex;
  gap: 10px;
  margin: 0 16px 20px;
  flex-wrap: wrap;
}

.filter-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 10px 16px;
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

.filter-btn:active {
  transform: scale(0.95);
}

.filter-btn.active {
  background: linear-gradient(135deg, #1aa39d 0%, #27b3a8 100%);
  color: #fff;
  border-color: transparent;
  box-shadow: 0 4px 12px rgba(26, 163, 157, 0.3);
}

.filter-arrow {
  font-size: 10px;
  margin-left: 2px;
  opacity: 0.8;
}
.therapy-list {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  padding: 0 16px;
}

/* 骨架屏样式 */
.skeleton-card {
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
  padding-bottom: 10px;
}

.skeleton-img {
  width: 100% !important;
  height: 140px !important;
}

.skeleton-info {
  padding: 10px;
}

.error-state,
.empty-state {
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
