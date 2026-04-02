<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import RecipeCard from '../components/RecipeCard.vue'
import TherapyCard from '../components/TherapyCard.vue'
import IngredientCard from '../components/IngredientCard.vue'

const router = useRouter()

const archive = ref(null)
const therapies = ref([])
const recipe = ref(null)
const ingredients = ref([])
const loading = ref(true)

function buildRecipeReason(baseReason, context) {
  const core = baseReason || '这道菜整体偏温和，适合作为近期日常调理主菜。'
  return `${core} 结合你目前的${context.constitution}体质、${context.season}${context.solarTerm}时令特点，这道菜更有助于稳定状态、减轻不适，并且烹饪难度较低，适合连续食用观察体感变化。`
}

function buildIngredientReason(baseReason, context) {
  const core = baseReason || '该食材性质平和，适合日常搭配。'
  return `${core} 从体质调理角度看，它与${context.constitution}体质匹配度较高；从季节角度看，也更符合${context.season}${context.solarTerm}的饮食节律，建议每周规律摄入并与清淡烹调方式搭配。`
}

onMounted(async () => {
  loading.value = true
  
  try {
    // 1. 从 localStorage 获取健康档案
    const healthRecords = JSON.parse(localStorage.getItem('healthArchive') || '[]')
    const constitutionRecord = healthRecords.find(r => r.type === 'constitution')
    
    let constitution = '平和质'
    let age = 25
    let gender = '男'
    let score = 85
    
    if (constitutionRecord && constitutionRecord.details) {
      constitution = constitutionRecord.details.constitution || '平和质'
      score = Math.round(constitutionRecord.details.scores?.[constitution] || 85)
      
      if (constitutionRecord.details.userInfo) {
        age = constitutionRecord.details.userInfo.age || 25
        gender = constitutionRecord.details.userInfo.gender || '男'
      }
    }
    
    console.log('📊 智能推荐 - 用户信息:', { constitution, age, gender, score })
    
    // 2. 调用后端推荐 API
    const response = await fetch(`http://127.0.0.1:8001/api/recommend/daily?user_id=user_${Date.now()}&constitution=${encodeURIComponent(constitution)}&age=${age}&gender=${encodeURIComponent(gender)}`)
    const recommendData = await response.json()
    
    console.log('✅ 后端推荐数据:', recommendData)
    
    // 3. 解析推荐数据（后端直接返回 RecommendationResponse 对象）
    archive.value = {
      constitution: recommendData.constitution || constitution,
      score: score,
      symptoms: constitutionRecord?.details?.feature || ''
    }
    
    // 4. 处理食疗推荐
    if (recommendData.therapies && Array.isArray(recommendData.therapies)) {
      therapies.value = recommendData.therapies.slice(0, 2).map(item => ({
        id: item.id || `therapy-${item.title}`,
        name: item.title,
        title: item.title,
        tag: '体质调理',
        effect: item.reason || '',
        desc: `${recommendData.season}·${recommendData.solar_term} 推荐`,
        tags: [recommendData.constitution],
        // 按需求移除艾灸/推拿等调理方案图片展示
        image: '',
        buttonText: '查看详情',
        primaryButton: true
      }))
      console.log('🍲 食疗推荐:', therapies.value)
    } else {
      console.log('⚠️ 没有食疗推荐')
    }
    
    // 5. 处理菜谱推荐（后端返回的是数组）
    if (recommendData.recipes && Array.isArray(recommendData.recipes) && recommendData.recipes.length > 0) {
      const firstRecipe = recommendData.recipes[0]
      const reasonContext = {
        constitution: recommendData.constitution || constitution,
        season: recommendData.season || '',
        solarTerm: recommendData.solar_term || ''
      }
      recipe.value = {
        name: firstRecipe.title || '推荐菜谱',
        desc: buildRecipeReason(firstRecipe.reason, reasonContext),
        image: firstRecipe.image ? `http://127.0.0.1:8001/data/Caipuimages/${firstRecipe.image}` : 'https://fastly.jsdelivr.net/npm/@vant/assets/cat.jpeg'
      }
      console.log('🍳 菜谱推荐:', recipe.value)
    } else {
      console.log('⚠️ 没有菜谱推荐')
      recipe.value = null
    }
    
    // 6. 处理食材推荐
    if (recommendData.ingredients && Array.isArray(recommendData.ingredients)) {
      const reasonContext = {
        constitution: recommendData.constitution || constitution,
        season: recommendData.season || '',
        solarTerm: recommendData.solar_term || ''
      }
      ingredients.value = recommendData.ingredients.slice(0, 4).map(item => ({
        id: item.id || `ingredient-${item.title}`,
        name: item.title,
        effect: buildIngredientReason(item.reason, reasonContext),
        image: item.image ? `http://127.0.0.1:8001/data/Shicaiimages/${item.image}` : 'https://fastly.jsdelivr.net/npm/@vant/assets/cat.jpeg'
      }))
      console.log('🥬 食材推荐:', ingredients.value)
    } else {
      console.log('⚠️ 没有食材推荐')
      ingredients.value = []
    }
    
  } catch (error) {
    console.error('❌ 获取推荐数据失败:', error)
    // 兜底数据
    archive.value = {
      constitution: '平和质',
      score: 85,
      symptoms: ''
    }
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="page-smart app-page">
    <header class="page-header">
      <button class="back-btn" type="button" @click="router.back()">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M19 12H5M12 19l-7-7 7-7"/>
        </svg>
      </button>
      <h1 class="page-title">智能推荐</h1>
      <span class="header-placeholder"></span>
    </header>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner">🔄</div>
      <p class="loading-text">正在生成个性化推荐...</p>
    </div>

    <!-- 健康信息摘要 -->
    <section v-else-if="archive" class="block">
      <div class="summary-card">
        <div class="summary-top">
          <div>
            <div class="summary-label">当前体质</div>
            <div class="summary-main">{{ archive.constitution }}</div>
          </div>
          <div class="summary-score-wrap">
            <span class="summary-score-label">综合评分</span>
            <span class="summary-score">{{ archive.score }}</span>
          </div>
        </div>
        <div class="summary-row">
          <span>主要症状：{{ archive.symptoms || '暂无记录' }}</span>
        </div>
      </div>
    </section>

    <!-- 推荐调理方案 -->
    <section v-if="therapies.length > 0" class="block">
      <h2 class="section-title">推荐调理方案</h2>
      <p class="section-subtitle">根据你的体质与当前状态，优先推荐以下调理方案：</p>
      <div class="therapy-list">
        <TherapyCard
          v-for="item in therapies"
          :key="item.id"
          :title="item.title || item.name"
          :tag="item.tag || '推荐'"
          :effect="item.effect"
          :desc="item.desc"
          :tags="item.tags"
          :button-text="null"
          :primary-button="false"
          :image="item.image"
        />
      </div>
    </section>
    
    <!-- 推荐菜谱 -->
    <section v-if="recipe" class="block">
      <h2 class="section-title">推荐菜谱</h2>
      <p class="section-subtitle">结合你的进食习惯与体质，适合的一道菜：</p>
      <RecipeCard
        :title="recipe.name"
        tag="今日首选"
        :desc="recipe.desc"
        time="约 20-30 分钟"
        calorie="约 300 千卡"
        :image="recipe.image"
      />
      <p class="reason-text">
        推荐理由：综合你的<span class="hl">体质特点</span>、近期状态与季节变化，优先选择更容易坚持、且调理目标更明确的菜谱。
      </p>
    </section>
    
    <!-- 推荐食材 -->
    <section v-if="ingredients.length > 0" class="block">
      <h2 class="section-title">推荐食材</h2>
      <p class="section-subtitle">日常可以多多选择这些适合你的基础食材：</p>
      <div class="ingredient-grid">
        <IngredientCard
          v-for="item in ingredients"
          :key="item.id"
          :name="item.name"
          :effect="item.effect"
          :image="item.image"
        />
      </div>
    </section>
  </div>
</template>

<style scoped>
.page-smart {
  background: var(--bg);
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  background: transparent;
  position: sticky;
  top: 0;
  z-index: 100;
}

.back-btn {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  border: none;
  background: #ffffff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #333;
}

.back-btn:active {
  transform: scale(0.95);
  background: #f8f9fa;
}

.back-btn svg {
  width: 22px;
  height: 22px;
}

.page-title {
  font-size: 20px;
  font-weight: 700;
  color: #1a1a1a;
  margin: 0;
  letter-spacing: -0.3px;
}

.header-placeholder {
  width: 40px;
}

.page-subtitle {
  font-size: 13px;
  color: var(--text-secondary);
  text-align: center;
  margin-top: -4px;
  margin-bottom: 12px;
  padding: 0 20px;
}

.block {
  margin-bottom: 24px;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-h);
  margin: 0 0 6px;
}

.section-subtitle {
  font-size: 13px;
  color: var(--text-secondary);
  margin: 0 0 10px;
}

.summary-card {
  background: var(--bg-card);
  border-radius: 16px;
  padding: 14px 14px 12px;
  box-shadow: var(--shadow);
}

.summary-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 6px;
}

.summary-label {
  font-size: 12px;
  color: var(--text-muted);
}

.summary-main {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-h);
}

.summary-score-wrap {
  text-align: right;
}

.summary-score-label {
  font-size: 12px;
  color: var(--text-muted);
  display: block;
}

.summary-score {
  font-size: 22px;
  font-weight: 700;
  color: var(--primary);
}

.summary-row {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: var(--text-secondary);
  margin-top: 2px;
}

.therapy-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.therapy-list :deep(.card-img-wrap) {
  display: none;
}

.reason-text {
  margin-top: 8px;
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.5;
}

.hl {
  color: #b44040;
}

.ingredient-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  text-align: center;
}

.loading-spinner {
  font-size: 48px;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.loading-text {
  font-size: 14px;
  color: var(--text-secondary);
  margin-top: 8px;
}
</style>

