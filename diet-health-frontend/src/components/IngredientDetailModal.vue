<script setup>
import { computed } from 'vue'
import RelationGraph from './RelationGraph.vue'

const props = defineProps({
  ingredient: { type: Object, default: null },
  visible: { type: Boolean, default: false }
})

const emit = defineEmits(['close'])

// 图片 URL
const imageUrl = computed(() => {
  if (props.ingredient?.image) return props.ingredient.image
  if (!props.ingredient?.images) return ''
  // 确保图片路径正确拼接
  const imageName = props.ingredient.images.trim()
  return `http://127.0.0.1:8001/data/Shicaiimages/${imageName}`
})

// 功效标签数组
const effectTags = computed(() => {
  if (!props.ingredient?.effect) return []
  return props.ingredient.effect.split('、')
})

// 适合体质
const suitableTags = computed(() => {
  if (!props.ingredient?.suitable) return []
  return props.ingredient.suitable.split('、')
})

// 禁忌
const avoidTags = computed(() => {
  if (!props.ingredient?.avoid) return []
  return props.ingredient.avoid.split('、')
})

// 食用方法
const methodsList = computed(() => {
  if (!props.ingredient?.methods) return []
  return props.ingredient.methods.split('、')
})

function handleClose() {
  emit('close')
}
</script>

<template>
  <transition name="slide-up">
    <div v-if="visible" class="ingredient-detail-modal" @click.self="handleClose">
      <div class="modal-content glass-card ink-wash-fade-in">
        <button class="close-btn" @click="handleClose">×</button>
        
        <!-- 图片区域 -->
        <div class="image-section">
          <img 
            v-if="imageUrl" 
            :src="imageUrl" 
            :alt="ingredient?.name"
            class="detail-image"
            @error="$event.target.style.display='none'"
          />
          <div v-else class="image-placeholder">🌿</div>
        </div>

        <!-- 基本信息 -->
        <div class="info-section">
          <h2 class="ingredient-name">{{ ingredient?.name }}</h2>
          
          <!-- 分类标签 -->
          <div v-if="ingredient?.tag" class="category-tags">
            <span 
              v-for="(tag, index) in ingredient.tag.split('、')" 
              :key="index"
              class="tag"
            >
              {{ tag }}
            </span>
          </div>
        </div>

        <!-- [NEW] 古籍考证：宣纸感区块 -->
        <section v-if="ingredient?.ancient_quote" class="detail-block">
          <h3 class="block-title">
            <span class="icon">📜</span>
            古籍考证
          </h3>
          <div class="rice-paper-block">
            “{{ ingredient.ancient_quote }}”
          </div>
        </section>

        <!-- 功效 -->
        <section class="detail-block">
          <h3 class="block-title">
            <span class="icon">✨</span>
            主要功效
          </h3>
          <p class="block-content">{{ ingredient?.effect || '暂无信息' }}</p>
        </section>

        <!-- 适合体质 -->
        <section class="detail-block">
          <h3 class="block-title">
            <span class="icon">💚</span>
            适合体质
          </h3>
          <div class="tags-grid">
            <span 
              v-for="(item, index) in suitableTags" 
              :key="index"
              class="suitable-tag"
            >
              {{ item }}
            </span>
          </div>
        </section>

        <!-- 食用方法 -->
        <section class="detail-block">
          <h3 class="block-title">
            <span class="icon">🍳</span>
            推荐吃法
          </h3>
          <div class="methods-list">
            <div 
              v-for="(method, index) in methodsList" 
              :key="index"
              class="method-item"
            >
              {{ method }}
            </div>
          </div>
        </section>

        <!-- 禁忌 -->
        <section class="detail-block warning">
          <h3 class="block-title">
            <span class="icon">⚠️</span>
            食用禁忌
          </h3>
          <div class="warning-content">
            <p v-if="ingredient?.avoid" class="warning-text">
              不宜与：<span class="highlight">{{ ingredient.avoid }}</span> 同食
            </p>
            <p v-else class="warning-text">暂无特殊禁忌</p>
          </div>
        </section>

        <!-- [NEW] 知识图谱详情 -->
        <section class="detail-block graph-section">
          <h3 class="block-title">
            <span class="icon">🕸️</span>
            药食关联图谱
          </h3>
          <div class="graph-container">
            <RelationGraph :center-node="ingredient?.name" />
          </div>
        </section>

        <!-- 相关菜谱推荐 -->
        <section v-if="ingredient?.related_recipes && ingredient.related_recipes.length > 0" class="detail-block">
          <h3 class="block-title">
            <span class="icon">📖</span>
            推荐菜谱
          </h3>
          <div class="recipe-list">
            <div 
              v-for="(recipe, index) in ingredient.related_recipes.slice(0, 3)" 
              :key="index"
              class="recipe-item"
            >
              {{ recipe.name || recipe }}
            </div>
          </div>
        </section>
      </div>
    </div>
  </transition>
</template>

<style scoped>
/* 遮罩层 */
.ingredient-detail-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  display: flex;
  align-items: center; /* 恢复居中显示 */
  justify-content: center;
  z-index: 100;
  padding: 16px; /* 恢复边距 */
}

/* 内容卡片 */
.modal-content {
  width: 100%;
  max-width: 440px;
  max-height: 85vh;
  overflow-y: auto;
  position: relative;
  border-radius: var(--radius-xl);
  /* glass-card 类已在 template 中应用，这里补充局部微调 */
  padding-bottom: 24px;
}

/* 关闭按钮 */
.close-btn {
  position: absolute;
  top: 16px;
  right: 16px;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.05);
  border: none;
  font-size: 20px;
  color: var(--text-secondary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
  transition: all 0.2s;
}

.close-btn:hover {
  background: rgba(0, 0, 0, 0.1);
  transform: scale(1.1);
}

/* 图片区域 */
.image-section {
  width: 100%;
  height: 240px;
  background: white;
  position: relative;
}

.detail-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.image-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 64px;
  background: var(--primary-light);
}

/* 基本信息 */
.info-section {
  padding: 24px 20px 16px;
}

.ingredient-name {
  font-size: 24px;
  font-weight: 700;
  color: var(--text);
  margin: 0 0 12px;
}

.category-tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.tag {
  padding: 4px 12px;
  background: var(--primary-light);
  color: var(--primary);
  border-radius: 99px;
  font-size: 12px;
  font-weight: 600;
}

/* 详情区块 */
.detail-block {
  padding: 20px;
  margin: 0 4px;
}

.block-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: var(--text);
  margin: 0 0 14px;
}

.block-content {
  font-size: 14px;
  line-height: 1.6;
  color: var(--text-secondary);
}

/* 适合体质标签 */
.tags-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.suitable-tag {
  padding: 6px 14px;
  background: white;
  border: 1px solid var(--primary-light);
  color: var(--primary);
  border-radius: 10px;
  font-size: 13px;
  font-weight: 500;
}

/* 食用方法 */
.methods-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.method-item {
  padding: 12px;
  background: rgba(255, 255, 255, 0.5);
  border-radius: 12px;
  font-size: 14px;
  color: var(--text-secondary);
  border: 1px solid rgba(0, 0, 0, 0.03);
}

/* 警告内容 */
.detail-block.warning {
  background: rgba(255, 59, 48, 0.03);
  margin: 12px;
  border-radius: var(--radius);
}

.warning-content {
  padding: 0;
}

.warning-text {
  font-size: 14px;
  color: #d32f2f;
  margin: 0;
}

/* 图谱容器 */
.graph-container {
  height: 300px;
  background: rgba(255, 255, 255, 0.4);
  border-radius: var(--radius);
  overflow: hidden;
  border: 1px solid var(--border-glass);
}

/* 淡入淡出动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 滚动条 */
.modal-content::-webkit-scrollbar {
  width: 4px;
}

.modal-content::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.1);
  border-radius: 10px;
}
</style>
