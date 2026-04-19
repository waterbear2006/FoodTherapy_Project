<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import RecipeCard from '../components/RecipeCard.vue'
import TherapyCard from '../components/TherapyCard.vue'
import IngredientCard from '../components/IngredientCard.vue'
import { fetchRealWeather } from '@/api/mock'

const router = useRouter()

const archive = ref(null)
const therapies = ref([])
const recipe = ref(null)
const ingredients = ref([])
const loading = ref(true)
const weatherInfo = ref(null)

// 获取疗法相关图片（使用可靠的图片源）
function getTherapyImage(therapyName) {
  // 由于 Unsplash 图片可能加载失败，这里返回空字符串
  // TherapyCard 组件会在图片加载失败时显示 emoji 占位符
  // 根据疗法类型返回不同的占位符提示
  return ''
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
    
    // 1.5 获取实时天气以影响推荐
    let weatherData = null;
    try {
      const location = await new Promise((resolve) => {
        const customCity = localStorage.getItem('customCity')
        if (customCity && customCity.trim() !== '') {
          resolve(customCity.trim())
          return
        }
        if (!navigator.geolocation) resolve('北京');
        else {
          navigator.geolocation.getCurrentPosition(
            pos => resolve(`${pos.coords.longitude.toFixed(3)},${pos.coords.latitude.toFixed(3)}`),
            err => resolve('北京'),
            { timeout: 5000, maximumAge: 60000 }
          );
        }
      });
      weatherData = await fetchRealWeather(location);
    } catch(e) {
      console.error('获取天气失败, 继续原逻辑', e);
    }

    let weatherQuery = '';
    if (weatherData) {
      weatherInfo.value = weatherData;
      weatherQuery = `&temperature=${weatherData.temperature}&humidity=${weatherData.humidity}&city=${encodeURIComponent(weatherData.city)}`;
    }
    
    // 2. 调用后端推荐 API
    const response = await fetch(`/api/recommend/daily?user_id=user_${Date.now()}&constitution=${encodeURIComponent(constitution)}&age=${age}&gender=${encodeURIComponent(gender)}${weatherQuery}`)
    const recommendData = await response.json()
    
    console.log('✅ 后端推荐数据:', recommendData)
    
    // 3. 解析症状：增加体质基本特征兜底，确保护理感
    let symptoms = constitutionRecord?.details?.feature || 
                     constitutionRecord?.details?.symptoms || 
                     constitutionRecord?.details?.description
    
    if (!symptoms || symptoms === '暂无明显症状') {
      const constitutionExplanations = {
        '气虚质': '常感神疲乏力、气短懒言、易出汗、舌淡苔白。',
        '阳虚质': '畏寒怕冷、四肢不温、喜热饮食、精神不振。',
        '阴虚质': '手足心热、口燥咽干、形体消瘦、易烦躁。',
        '痰湿质': '感受沉重、多痰、胸闷、舌苔厚腻。',
        '湿热质': '面垢油光、口苦口干、身重困倦。',
        '血瘀质': '面色晦暗、皮肤粗糙、易有瘀斑。',
        '气郁质': '神情抑郁、忧虑脆弱、气机不畅。',
        '特禀质': '对外界环境敏感、易过敏、喷嚏流涕。',
        '平和质': '面色红润、精力充沛、饮食睡眠正常。'
      }
      symptoms = constitutionExplanations[constitution] || '暂无明显症状'
    }
                     
    archive.value = {
      constitution: recommendData.constitution || constitution,
      symptoms: symptoms
    }
    
    // 4. 处理食疗/理疗推荐
    if (recommendData.therapies && Array.isArray(recommendData.therapies)) {
      therapies.value = recommendData.therapies.map(item => {
        // 判断是否为物理理疗 (针灸, 推拿, 刮痧, 拔罐, 艾灸等)
        const isPhysical = /针灸|推拿|刮痧|拔罐|艾灸|穴位|按摩|热敷/.test(item.title)
        return {
          id: item.id || `therapy-${item.title}`,
          name: item.title,
          title: item.title,
          tag: isPhysical ? '建议治疗' : '食疗方案',
          effect: item.reason || '',
          desc: isPhysical ? '专业中医建议' : '体质调理药膳',
          tags: isPhysical ? ['非食疗', '传统疗法'] : [recommendData.constitution],
          image: isPhysical ? '' : item.image, // 理疗不显示图片
          isPhysical: isPhysical,
          ancient_quote: item.ancient_quote || '',
          buttonText: '查看详情',
          primaryButton: true
        }
      })
      console.log('🍲 调理建议:', therapies.value)
    }
    
    // 5. 处理菜谱推荐（后端返回的是数组）
    if (recommendData.recipes && Array.isArray(recommendData.recipes) && recommendData.recipes.length > 0) {
      const firstRecipe = recommendData.recipes[0]
      recipe.value = {
        name: firstRecipe.title || '推荐菜谱',
        desc: firstRecipe.reason || '',
        ancient_quote: firstRecipe.ancient_quote || '',
        image: firstRecipe.image ? `/data/Caipuimages/${firstRecipe.image}` : 'https://fastly.jsdelivr.net/npm/@vant/assets/cat.jpeg'
      }
      console.log('🍳 菜谱推荐:', recipe.value)
    } else {
      console.log('⚠️ 没有菜谱推荐')
      recipe.value = null
    }
    
    // 6. 处理食材推荐
    if (recommendData.ingredients && Array.isArray(recommendData.ingredients)) {
      ingredients.value = recommendData.ingredients.slice(0, 4).map(item => ({
        id: item.id || `ingredient-${item.title}`,
        name: item.title,
        effect: item.reason || '',
        ancient_quote: item.ancient_quote || '',
        image: item.image ? `/data/Shicaiimages/${item.image}` : 'https://fastly.jsdelivr.net/npm/@vant/assets/cat.jpeg'
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
      symptoms: ''
    }
  } finally {
    loading.value = false
  }
})

// RAG 古籍专属正则渲染引擎
const formatAncientText = (text) => {
  if (!text) return ''
  return text.replace(/(《.*?》)/g, '<strong style="color: #8b0000; font-weight: bold;">$1</strong>')
}
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

    <!-- 骨架屏加载状态 -->
    <div v-if="loading" class="skeleton-wrapper">
      <div class="skeleton-block summary">
        <van-skeleton title :row="1" />
      </div>
      <div class="skeleton-block" v-for="i in 2" :key="i">
        <van-skeleton title :row="3" />
      </div>
    </div>

    <!-- 健康信息摘要 -->
    <section v-else-if="archive" class="block">
      <div class="summary-card">
        <div class="summary-top">
          <div>
            <div class="summary-label">当前体质</div>
            <div class="summary-main">{{ archive.constitution }}</div>
          </div>

        </div>
        <div class="summary-row">
          <span>主要症状：{{ archive.symptoms || '暂无记录' }}</span>
        </div>
        <div class="weather-row" v-if="weatherInfo">
           <span>🌤 当前气象：{{ weatherInfo.city }} {{ weatherInfo.temperature }}℃ 湿度{{ weatherInfo.humidity }}%</span>
        </div>
      </div>
    </section>

    <!-- 中医理疗建议 -->
    <section v-if="therapies.some(t => t.isPhysical)" class="block">
      <h2 class="section-title">中医理疗建议</h2>
      <p class="section-subtitle">针灸、推拿等非食疗手段，助您疏通经络：</p>
      <div class="therapy-list">
        <template v-for="item in therapies.filter(t => t.isPhysical)" :key="item.id">
          <TherapyCard
            v-bind="item"
            :button-text="null"
          />
          <div v-if="item.ancient_quote" class="rice-paper-block mini" v-html="formatAncientText(item.ancient_quote)"></div>
        </template>
      </div>
    </section>

    <!-- 推荐食疗方案 -->
    <section v-if="therapies.some(t => !t.isPhysical)" class="block">
      <h2 class="section-title">推荐食疗方案</h2>
      <p class="section-subtitle">根据您的体质，优先推荐以下药膳食疗：</p>
      <div class="therapy-list">
        <template v-for="item in therapies.filter(t => !t.isPhysical)" :key="item.id">
          <TherapyCard
            v-bind="item"
            :button-text="null"
          />
          <div v-if="item.ancient_quote" class="rice-paper-block mini" v-html="formatAncientText(item.ancient_quote)"></div>
        </template>
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
      <div v-if="recipe.ancient_quote" class="rice-paper-block" v-html="formatAncientText(recipe.ancient_quote)"></div>
    </section>
    
    <!-- 推荐食材 -->
    <section v-if="ingredients.length > 0" class="block">
      <h2 class="section-title">推荐食材</h2>
      <p class="section-subtitle">日常可以多多选择这些适合你的基础食材：</p>
      <div class="ingredient-grid">
        <div v-for="item in ingredients" :key="item.id" class="ingredient-item-wrap">
          <IngredientCard
            :name="item.name"
            :effect="item.effect"
            :image="item.image"
          />
          <div v-if="item.ancient_quote" class="rice-paper-block mini" v-html="formatAncientText(item.ancient_quote)"></div>
        </div>
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
  border-radius: var(--radius);
  border: 1px solid var(--border);
  background: var(--bg-card);
  box-shadow: var(--shadow-light);
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-h);
}

.back-btn:active {
  transform: scale(0.95);
  background: var(--bg-subtle);
  border-color: var(--primary);
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
  border-radius: var(--radius-lg);
  padding: 20px 18px 16px;
  box-shadow: var(--shadow-lg);
}

.summary-top {
  margin-bottom: 6px;
}

.summary-label {
  font-size: 12px;
  color: var(--text-muted);
}

.summary-main {
  font-size: 20px;
  font-weight: 700;
  color: var(--text-h);
  letter-spacing: -0.3px;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: var(--text-secondary);
  margin-top: 2px;
}

.weather-row {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px dashed var(--border);
  font-size: 12px;
  color: var(--primary-dark);
  font-weight: 500;
  background: var(--primary-light);
  padding: 10px 12px;
  border-radius: var(--radius-sm);
  margin-left: -2px;
  margin-right: -2px;
}

.weather-note {
  font-size: 11px;
  color: #999;
  font-weight: normal;
}

.therapy-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
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

.skeleton-wrapper {
  padding: 0 20px;
}

.skeleton-block {
  background: #fff;
  border-radius: 16px;
  padding: 20px;
  margin-bottom: 20px;
}

.skeleton-block.summary {
  height: 100px;
}

.loading-text {
  margin-top: 8px;
}

/* 宣纸考证区块 */
.rice-paper-block {
  background: #fdfaf5 !important;
  background-image: url("data:image/svg+xml,%3Csvg width='100' height='100' viewBox='0 0 100 100' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.8' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100' height='100' filter='url(%23noise)' opacity='0.03'/%3E%3C/svg%3E");
  border-left: 2px solid var(--accent);
  padding: 8px 14px;
  margin: 10px 0;
  border-radius: 4px 12px 12px 4px;
  color: #5c4b37;
  font-size: 12px;
  line-height: 1.5;
  box-shadow: inset 0 0 10px rgba(255, 255, 255, 0.4);
  font-family: var(--serif);
}

.rice-paper-block.mini {
  margin-top: -6px;
  margin-bottom: 8px;
  font-size: 10px;
  padding: 5px 8px;
  line-height: 1.3;
  opacity: 0.85;
  /* 限制高度，防止由于字数多导致的盒子过大 */
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>

