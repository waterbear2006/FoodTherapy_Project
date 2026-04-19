<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import { useRouter } from 'vue-router'
import { generateRecipeFromIngredients, checkIngredientCompatibility, getRecommendedRecipes } from '../api/mock'
import { getHealthArchive } from '../api/mock'
import RecipeDetailModal from '../components/RecipeDetailModal.vue'

const router = useRouter()
const inputText = ref('')
const selectedIngredients = ref([])
const recommendedIngredients = ref(['山药', '枸杞', '红枣', '鸡肉', '银耳', '百合', '薏米', '红豆'])
const generating = ref(false)
const userConstitution = ref('')
const incompatiblePairs = ref([])
const isSafe = ref(true)

// 生成的菜谱列表
const generatedRecipes = ref([])
// 选中的菜谱详情
const selectedRecipe = ref(null)
// 是否显示详情弹窗
const showDetailModal = ref(false)

// 计算缺失食材
function getMissingIngredients(recipe) {
  if (!recipe.ingredients || !recipe.matched_ingredients) return []
  
  const allIngredients = recipe.ingredients
  const matched = recipe.matched_ingredients || []
  
  // 缺失食材 = 所有食材 - 已匹配食材
  return allIngredients.filter(ing => !matched.includes(ing))
}

// 格式化制作步骤
const formattedSteps = computed(() => {
  if (!selectedRecipe.value?.steps) return []
  const steps = selectedRecipe.value.steps
  if (Array.isArray(steps)) return steps
  
  // 复杂的正则拆分：支持换行、分号，以及数字序号（如 1. 2. 或 1 2）
  // 1. 先按换行和分号拆
  let parts = steps.split(/[;\n；]/).filter(s => s.trim())
  
  // 2. 如果拆出来的部分依然很长且包含数字序号，尝试进一步按数字拆分
  let finalSteps = []
  parts.forEach(part => {
    // 匹配类似 "1. " 或 "2、" 或 "3 " 的起始
    const subParts = part.split(/(?=\d+[.、\s])/).filter(s => s.trim())
    finalSteps.push(...subParts)
  })
  
  return finalSteps.map(s => s.replace(/^\d+[.、\s]*/, '').trim()).filter(s => s)
})

// 加载用户体质
async function loadUserConstitution() {
  try {
    const archive = await getHealthArchive()
    userConstitution.value = archive?.constitution || ''
    console.log('用户体质:', userConstitution.value)
  } catch (err) {
    console.error('❌ 加载体质失败:', err)
  }
}

// 检查食材搭配
async function checkCompatibility() {
  if (selectedIngredients.value.length < 2) {
    incompatiblePairs.value = []
    isSafe.value = true
    return
  }
  
  try {
    const result = await checkIngredientCompatibility(selectedIngredients.value)
    incompatiblePairs.value = result.incompatiblePairs || []
    isSafe.value = result.isSafe
  } catch (err) {
    console.error('❌ 检查食材搭配失败:', err)
    incompatiblePairs.value = []
    isSafe.value = true
  }
}

// 生成菜谱
async function handleGenerate() {
  if (generating.value || selectedIngredients.value.length === 0) return
  generating.value = true
  generatedRecipes.value = []
  selectedRecipe.value = null
  
  try {
    console.log('🥗 选中的食材:', selectedIngredients.value)
    const result = await generateRecipeFromIngredients(selectedIngredients.value, userConstitution.value)
    console.log('✅ 生成的菜谱:', result)
    
    if (result.success && result.recipes && result.recipes.length > 0) {
      // 保存所有生成的菜谱
      generatedRecipes.value = result.recipes.map(r => ({
        id: r.id,
        name: r.name,
        ingredients: r.ingredients,
        effect: Array.isArray(r.effect) ? r.effect.join('、') : r.effect,
        suitable: Array.isArray(r.suitable) ? r.suitable : [],
        steps: r.steps,
        images: r.images,
        taboo: r.taboo,
        match_score: r.match_score,
        matched_ingredients: r.matched_ingredients || []
      }))
    } else {
      // 没有找到匹配的菜谱
      generatedRecipes.value = []
      alert(`未找到包含这些食材的菜谱\n\n建议：\n1. 前往食疗库浏览更多菜谱\n2. 尝试更换其他食材`)
    }
  } catch (err) {
    console.error('❌ 生成菜谱失败:', err)
    alert('生成菜谱失败，请稍后重试')
  } finally {
    generating.value = false
  }
}

// 打开菜谱详情
function openRecipeDetail(recipe) {
  selectedRecipe.value = recipe
  showDetailModal.value = true
}

// 关闭详情弹窗
function closeDetailModal() {
  showDetailModal.value = false
  selectedRecipe.value = null
}

onMounted(async () => {
  await loadUserConstitution()
})

// 监听食材变化，自动检查搭配
watch(() => selectedIngredients.value, () => {
  checkCompatibility()
}, { deep: true })

function addFromInput() {
  const text = inputText.value.trim()
  if (!text) return
  text.split(/[,、\s]+/).forEach((t) => {
    if (t && !selectedIngredients.value.includes(t)) {
      selectedIngredients.value.push(t)
    }
  })
  inputText.value = ''
}

function addRecommended(name) {
  if (!selectedIngredients.value.includes(name)) {
    selectedIngredients.value.push(name)
  }
}

function removeIngredient(name) {
  selectedIngredients.value = selectedIngredients.value.filter((i) => i !== name)
}
</script>

<template>
  <div class="page-recipe app-page">
    <header class="page-header">
      <button class="back-btn" type="button" @click="router.back()">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M19 12H5M12 19l-7-7 7-7"/>
        </svg>
      </button>
      <h1 class="page-title">生成菜谱</h1>
      <span class="header-placeholder"></span>
    </header>

    <section class="block">
      <h2 class="block-title">您现在有什么食材？</h2>
      <div class="input-row">
        <input
          v-model="inputText"
          type="text"
          class="ingredient-input"
          placeholder="例如：鸡蛋、番茄、土豆"
        />
        <button class="btn-add" type="button" @click="addFromInput">+</button>
      </div>

      <div class="tag-group">
        <div class="tag-label">已选食材</div>
        <div class="tag-list">
          <button
            v-for="name in selectedIngredients"
            :key="name"
            type="button"
            class="tag-chip selected"
            @click="removeIngredient(name)"
          >
            {{ name }} ×
          </button>
          <span v-if="selectedIngredients.length === 0" class="empty-tag">点击添加食材</span>
        </div>
      </div>

      <div class="tag-group recommended-group">
        <div class="tag-label">推荐食材</div>
        <div class="tag-list">
          <button
            v-for="name in recommendedIngredients"
            :key="name"
            type="button"
            class="tag-chip"
            @click="addRecommended(name)"
          >
            {{ name }}
          </button>
        </div>
      </div>

      <!-- 食材搭配警告 -->
      <div v-if="!isSafe && incompatiblePairs.length > 0" class="warning-box">
        <div class="warning-icon">⚠️</div>
        <div class="warning-content">
          <div class="warning-title">食材搭配注意</div>
          <div class="warning-text">
            以下食材可能不适合一起食用：
            <span v-for="(pair, index) in incompatiblePairs" :key="index" class="warning-pair">
              {{ pair.ingredients?.join(' + ') || pair }}<span v-if="index < incompatiblePairs.length - 1">，</span>
            </span>
          </div>
        </div>
      </div>

      <button
        class="btn-generate-main"
        type="button"
        :disabled="generating || !selectedIngredients.length"
        @click="handleGenerate"
      >
        {{ generating ? '生成中...' : '✨ 生成菜谱' }}
      </button>
    </section>

    <!-- 生成的菜谱列表 -->
    <section v-if="generatedRecipes.length > 0" class="block result-block">
      <div class="block-head">
        <h2 class="block-title">为你推荐 {{ generatedRecipes.length }} 道菜</h2>
      </div>
      
      <!-- 菜谱列表 -->
      <div class="recipe-list">
        <div
          v-for="(recipe, index) in generatedRecipes"
          :key="recipe.id"
          class="recipe-list-item"
          @click="openRecipeDetail(recipe)"
        >
          <div class="recipe-number">{{ index + 1 }}</div>
          <div class="recipe-info">
            <h3 class="recipe-name">{{ recipe.name }}</h3>
            <p class="recipe-effect">{{ recipe.effect }}</p>
            <div class="recipe-meta">
              <span class="meta-tag match">匹配度 {{ Math.round(recipe.match_score * 100) }}%</span>
              <span v-if="recipe.matched_ingredients && recipe.matched_ingredients.length > 0" class="meta-tag matched">
                已匹配 {{ recipe.matched_ingredients.length }} 种
              </span>
              <span v-if="getMissingIngredients(recipe).length > 0" class="meta-tag missing">
                还需购买 {{ getMissingIngredients(recipe).length }} 种
              </span>
            </div>
            <div v-if="getMissingIngredients(recipe).length > 0" class="missing-ingredients">
              <span class="missing-label">缺：</span>
              <span class="missing-list">{{ getMissingIngredients(recipe).join('、') }}</span>
            </div>
          </div>
          <div class="recipe-arrow">›</div>
        </div>
      </div>
    </section>

    <!-- 空状态 -->
    <section v-else-if="!generating && selectedIngredients.length > 0" class="block">
      <div class="empty-state">
        <div class="empty-icon">🍳</div>
        <p class="empty-text">点击上方按钮生成菜谱</p>
      </div>
    </section>

    <!-- 初始状态 -->
    <section v-else-if="!generating && selectedIngredients.length === 0" class="block">
      <div class="empty-state">
        <div class="empty-icon">🥗</div>
        <p class="empty-text">选择食材后开始生成菜谱</p>
      </div>
    </section>

    <!-- 加载中 (骨架屏) -->
    <section v-if="generating" class="block">
      <div class="skeleton-generating-card">
        <van-skeleton-image block class="skeleton-img" />
        <div class="skeleton-padding">
          <van-skeleton title :row="3" />
        </div>
      </div>
    </section>

    <!-- 菜谱详情弹窗 (已重构为独立组件) -->
    <RecipeDetailModal
      :recipe="selectedRecipe"
      :visible="showDetailModal"
      @close="closeDetailModal"
    />
  </div>
</template>

<style scoped>
.page-recipe {
  background: linear-gradient(180deg, #f8f9fa 0%, #ffffff 100%);
  min-height: 100vh;
  padding-bottom: 30px;
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

.block {
  margin-bottom: 24px;
  padding: 0 16px;
}

.result-block {
  margin-top: 8px;
}

.block-title {
  font-size: 18px;
  font-weight: 700;
  color: #1a1a1a;
  margin: 0 0 16px;
  letter-spacing: -0.3px;
}

.input-row {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.ingredient-input {
  flex: 1;
  padding: 14px 18px;
  border: 2px solid #e8e8e8;
  border-radius: 16px;
  font-size: 15px;
  background: #ffffff;
  transition: all 0.2s ease;
}

.ingredient-input:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 3px var(--primary-light), var(--shadow);
}

.btn-add {
  width: 48px;
  height: 48px;
  border-radius: var(--radius);
  border: none;
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
  color: #fff;
  font-size: 28px;
  font-weight: 300;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: var(--shadow);
}

.btn-add:active {
  transform: scale(0.95);
  box-shadow: var(--shadow-sm);
}

.tag-group {
  margin-bottom: 16px;
}

.tag-label {
  font-size: 14px;
  font-weight: 600;
  color: #666;
  margin-bottom: 10px;
  display: block;
}

.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag-chip {
  padding: 8px 14px;
  border-radius: 999px;
  border: 1px solid var(--border);
  background: var(--bg-card);
  font-size: 14px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.04);
  font-weight: 500;
}

.tag-chip:active {
  transform: scale(0.96);
}

.tag-chip.selected {
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
  border-color: transparent;
  color: #fff;
  font-weight: 600;
  box-shadow: 0 4px 12px rgba(125, 157, 138, 0.35);
}

.empty-tag {
  color: #999;
  font-size: 14px;
  padding: 8px 0;
}

.recommended-group .tag-chip {
  background: #f8f9fa;
}

.btn-generate-main {
  width: 100%;
  padding: 18px;
  border-radius: var(--radius-lg);
  border: none;
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
  color: #fff;
  font-size: 16px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: var(--shadow-lg);
  margin-top: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  letter-spacing: 0.5px;
}

.btn-generate-main:active {
  transform: scale(0.98);
  box-shadow: var(--shadow);
}

.btn-generate-main:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.warning-box {
  display: flex;
  gap: 12px;
  padding: 16px;
  background: linear-gradient(135deg, #fff3e6 0%, #ffe8cc 100%);
  border-radius: 16px;
  border: 1px solid #ffd699;
  margin-bottom: 16px;
}

.warning-icon {
  font-size: 24px;
  flex-shrink: 0;
}

.warning-content {
  flex: 1;
}

.warning-title {
  font-size: 15px;
  font-weight: 600;
  color: #cc6600;
  margin-bottom: 6px;
}

.warning-text {
  font-size: 14px;
  color: #994d00;
  line-height: 1.6;
}

.skeleton-generating-card {
  background: #fff;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.05);
}

.skeleton-img {
  width: 100% !important;
  height: 180px !important;
}

.skeleton-padding {
  padding: 16px;
}

.loading-text {
  font-size: 15px;
  color: #666;
  font-weight: 500;
}

/* 菜谱列表 */
.recipe-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.recipe-list-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background: #ffffff;
  border-radius: 16px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
  cursor: pointer;
  transition: all 0.2s ease;
  border: 1px solid #f0f0f0;
}

.recipe-list-item:active {
  transform: scale(0.98);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  border-color: #1aa39d;
}

.recipe-number {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: linear-gradient(135deg, #1aa39d 0%, #27b3a8 100%);
  color: #fff;
  font-size: 16px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.recipe-info {
  flex: 1;
  min-width: 0;
}

.recipe-name {
  font-size: 17px;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0 0 6px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.recipe-effect {
  font-size: 13px;
  color: #666;
  margin: 0 0 8px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.recipe-meta {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.meta-tag {
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 500;
}

.meta-tag.match {
  background: rgba(26, 163, 157, 0.1);
  color: #1aa39d;
}

.meta-tag.matched {
  background: rgba(52, 199, 89, 0.1);
  color: #34c759;
}

.meta-tag.missing {
  background: rgba(255, 149, 0, 0.1);
  color: #ff9500;
  font-weight: 600;
}

.recipe-arrow {
  font-size: 24px;
  color: #ccc;
  font-weight: 300;
}

.missing-ingredients {
  margin-top: 8px;
  padding: 8px 10px;
  background: rgba(255, 149, 0, 0.08);
  border-radius: 8px;
  border-left: 3px solid #ff9500;
  font-size: 13px;
  line-height: 1.5;
}

.missing-label {
  font-weight: 600;
  color: #ff9500;
  margin-right: 4px;
}

.missing-list {
  color: #cc7a00;
  font-weight: 500;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  background: #ffffff;
  border-radius: 20px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.06);
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
  opacity: 0.5;
}

.empty-text {
  font-size: 15px;
  color: #999;
  font-weight: 500;
}

/* 详情弹窗 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.modal-content {
  background: #ffffff;
  border-radius: 24px;
  width: 100%;
  max-width: 480px;
  max-height: 90vh;
  overflow: hidden;
  position: relative;
  animation: modalSlideUp 0.3s ease;
}

@keyframes modalSlideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.modal-close {
  position: absolute;
  top: 16px;
  right: 16px;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: none;
  background: rgba(255, 255, 255, 0.9);
  font-size: 24px;
  color: #666;
  cursor: pointer;
  z-index: 10;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.modal-close:active {
  background: #f0f0f0;
}

.detail-card {
  overflow-y: auto;
  max-height: 90vh;
}

.detail-image-section {
  position: relative;
  width: 100%;
  height: 200px;
  background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c8 100%);
  overflow: hidden;
}

.detail-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.detail-image-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 80px;
}

.detail-match-badge {
  position: absolute;
  top: 16px;
  left: 16px;
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  font-size: 14px;
  font-weight: 600;
  color: #1aa39d;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.detail-content {
  padding: 24px;
}

.detail-title {
  font-size: 22px;
  font-weight: 700;
  color: #1a1a1a;
  margin: 0 0 16px;
  line-height: 1.3;
}

.detail-tags {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 20px;
}

.detail-tag {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  border-radius: 12px;
  font-size: 13px;
  font-weight: 500;
  width: fit-content;
}

.detail-tag.effect {
  background: rgba(52, 199, 89, 0.1);
  color: #34c759;
}

.detail-tag.suitable {
  background: rgba(26, 163, 157, 0.1);
  color: #1aa39d;
}

.detail-section {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #f0f0f0;
}

.detail-section.warning {
  background: rgba(255, 153, 0, 0.05);
  border: 1px solid rgba(255, 153, 0, 0.2);
  border-radius: 12px;
  padding: 16px;
  margin-top: 20px;
}

.section-title {
  font-size: 15px;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0 0 12px;
}

.matched-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.matched-tag {
  padding: 6px 12px;
  background: rgba(52, 199, 89, 0.1);
  border-radius: 8px;
  font-size: 13px;
  color: #34c759;
  font-weight: 500;
}

.ingredient-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.ingredient-tag {
  padding: 6px 12px;
  background: #f8f9fa;
  border-radius: 8px;
  font-size: 13px;
  color: #555;
  border: 1px solid #e8e8e8;
}

.steps-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.step-row {
  display: flex;
  gap: 10px;
  align-items: flex-start;
}

.step-num {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: linear-gradient(135deg, #1aa39d 0%, #27b3a8 100%);
  color: #fff;
  font-size: 12px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.step-text {
  flex: 1;
  font-size: 14px;
  line-height: 1.6;
  color: #555;
  padding-top: 2px;
}

.taboo-text {
  font-size: 14px;
  color: #cc6600;
  line-height: 1.6;
  margin: 0;
}
</style>
