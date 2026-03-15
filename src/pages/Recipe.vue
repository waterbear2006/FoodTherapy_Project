<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { generateRecipe, getRecipeHistory } from '../api/mock'

const router = useRouter()
const ingredients = ref('')
const currentRecipe = ref(null)
const historyList = ref([])
const generating = ref(false)

onMounted(async () => {
  const list = await getRecipeHistory()
  historyList.value = list
  currentRecipe.value = await generateRecipe('')
})

async function handleGenerate() {
  if (generating.value) return
  generating.value = true
  try {
    currentRecipe.value = await generateRecipe(ingredients.value)
  } finally {
    generating.value = false
  }
}

function goDetail() {
  router.push('/therapy')
}
function goHistory() {
  router.push('/therapy')
}
</script>

<template>
  <div class="page-recipe app-page">
    <header class="page-header">
      <h1 class="page-title">AI 智能菜谱</h1>
      <span class="header-icon">🔔</span>
    </header>

    <section class="block">
      <h2 class="block-title">输入现有食材</h2>
      <div class="input-row">
        <input
          v-model="ingredients"
          type="text"
          class="ingredient-input"
          placeholder="例如:番茄,鸡蛋,西兰花"
        />
        <button class="btn-generate" :disabled="generating" @click="handleGenerate">{{ generating ? '生成中...' : '✨ 生成' }}</button>
      </div>
      <p class="input-hint">多个食材请用逗号隔开，AI将为您精准匹配</p>
    </section>

    <section class="block">
      <div class="block-head">
        <h2 class="block-title">
          <span class="title-icon">✨</span>
          当前推荐
        </h2>
        <span class="badge-live">实时生成</span>
      </div>
      <div v-if="currentRecipe" class="recommend-card">
        <div class="rec-image-wrap">
          <img v-if="currentRecipe.image" :src="currentRecipe.image" :alt="currentRecipe.name" class="rec-image" />
          <div v-else class="rec-image-placeholder">😊</div>
        </div>
        <div class="rec-meta">
          <span class="rec-match">匹配度 {{ currentRecipe.match }}</span>
          <span class="rec-stars">{{ '★'.repeat(currentRecipe.stars || 3) }}</span>
        </div>
        <h3 class="rec-name">{{ currentRecipe.name }}</h3>
        <p class="rec-desc">{{ currentRecipe.desc }}</p>
        <button class="btn-primary" @click="goDetail">查看详细步骤</button>
      </div>
    </section>

    <section class="block">
      <div class="block-head">
        <h2 class="block-title">
          <span class="title-icon">🔄</span>
          历史生成
        </h2>
        <a class="link-more" @click="goHistory">查看全部</a>
      </div>
      <div class="history-list">
        <div
          v-for="item in historyList"
          :key="item.id"
          class="history-item"
          @click="goDetail"
        >
          <div class="history-thumb">🌿</div>
          <div class="history-info">
            <h4 class="history-name">{{ item.name }}</h4>
            <p class="history-meta">{{ item.time }} · 难度:{{ item.difficulty }}</p>
            <div class="history-tags">
              <span v-for="t in item.tags" :key="t" class="tag">{{ t }}</span>
            </div>
          </div>
          <span class="history-arrow">›</span>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
.page-recipe {
  background: var(--bg);
}
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 0 20px;
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
.block {
  margin-bottom: 24px;
}
.block-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-h);
  margin: 0 0 12px;
  display: flex;
  align-items: center;
  gap: 6px;
}
.title-icon {
  font-size: 18px;
}
.block-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}
.badge-live {
  font-size: 12px;
  color: var(--primary);
  background: var(--primary-light);
  padding: 4px 10px;
  border-radius: 20px;
}
.input-row {
  display: flex;
  gap: 10px;
  margin-bottom: 8px;
}
.ingredient-input {
  flex: 1;
  height: 44px;
  padding: 0 14px;
  border: none;
  border-radius: var(--radius-sm);
  background: #eee;
  font-size: 14px;
}
.btn-generate {
  width: 44px;
  height: 44px;
  border: none;
  border-radius: var(--radius-sm);
  background: var(--primary);
  color: #fff;
  font-size: 18px;
  cursor: pointer;
}
.input-hint {
  font-size: 12px;
  color: var(--text-muted);
  margin: 0;
}
.recommend-card {
  background: #faf8f5;
  border-radius: var(--radius);
  padding: 16px;
  box-shadow: var(--shadow);
}
.rec-image-wrap {
  width: 100%;
  height: 160px;
  background: var(--primary-light);
  border-radius: var(--radius-sm);
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.rec-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: var(--radius-sm);
}
.rec-image-placeholder {
  font-size: 48px;
}
.rec-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}
.rec-match {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-h);
}
.rec-stars {
  color: #f5a623;
  font-size: 14px;
}
.rec-name {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-h);
  margin: 0 0 8px;
}
.rec-desc {
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.5;
  margin: 0 0 16px;
}
.btn-primary {
  width: 100%;
  height: 44px;
  border: none;
  border-radius: var(--radius-sm);
  background: var(--primary);
  color: #fff;
  font-size: 15px;
  cursor: pointer;
}
.link-more {
  font-size: 14px;
  color: var(--primary);
  text-decoration: none;
}
.history-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.history-item {
  display: flex;
  align-items: center;
  gap: 12px;
  background: #faf8f5;
  border-radius: var(--radius);
  padding: 14px;
  cursor: pointer;
  box-shadow: var(--shadow);
}
.history-thumb {
  width: 56px;
  height: 56px;
  border-radius: var(--radius-sm);
  background: var(--primary-light);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  flex-shrink: 0;
}
.history-info {
  flex: 1;
  min-width: 0;
}
.history-name {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-h);
  margin: 0 0 4px;
}
.history-meta {
  font-size: 12px;
  color: var(--text-muted);
  margin: 0 0 6px;
}
.history-tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}
.history-tags .tag {
  font-size: 12px;
  color: var(--text-secondary);
  background: #eee;
  padding: 2px 8px;
  border-radius: 4px;
}
.history-arrow {
  font-size: 20px;
  color: var(--text-muted);
}
</style>
