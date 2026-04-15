<script setup>
import { computed } from 'vue'

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
  <transition name="fade">
    <div v-if="visible" class="ingredient-detail-modal" @click.self="handleClose">
      <div class="modal-content">
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
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  padding: 20px;
  overflow-y: auto;
}

/* 内容卡片 */
.modal-content {
  background: #fff;
  border-radius: 16px;
  width: 100%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
  position: relative;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
  animation: slideUp 0.3s ease;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 关闭按钮 */
.close-btn {
  position: absolute;
  top: 12px;
  right: 12px;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.9);
  border: none;
  font-size: 24px;
  color: #666;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  z-index: 10;
}

.close-btn:hover {
  background: #f5f5f5;
  color: #333;
  transform: rotate(90deg);
}

/* 图片区域 */
.image-section {
  width: 100%;
  height: 280px;
  background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c8 100%);
  position: relative;
  overflow: hidden;
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
  font-size: 80px;
  background: linear-gradient(135deg, #e8f5e9, #c8e6c8);
}

/* 基本信息 */
.info-section {
  padding: 20px;
  background: #fff;
}

.ingredient-name {
  font-size: 26px;
  font-weight: 700;
  color: #1a1a1a;
  margin: 0 0 12px;
}

.category-tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.tag {
  padding: 6px 14px;
  background: linear-gradient(135deg, #1aa39d 0%, #27b3a8 100%);
  color: #fff;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 500;
}

/* 详情区块 */
.detail-block {
  padding: 20px;
  border-top: 1px solid #f0f0f0;
  background: #fff;
}

.detail-block.warning {
  background: #fff5f5;
}

.block-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 17px;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0 0 12px;
}

.block-title .icon {
  font-size: 20px;
}

.block-content {
  font-size: 15px;
  line-height: 1.6;
  color: #333;
  margin: 0;
}

/* 适合体质标签 */
.tags-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
  gap: 8px;
}

.suitable-tag {
  padding: 8px 12px;
  background: #e8f5e9;
  color: #1aa39d;
  border-radius: 8px;
  font-size: 14px;
  text-align: center;
  font-weight: 500;
}

/* 食用方法 */
.methods-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.method-item {
  padding: 10px 14px;
  background: #f8f9fa;
  border-radius: 8px;
  font-size: 14px;
  color: #333;
  border-left: 3px solid #1aa39d;
}

/* 警告内容 */
.warning-content {
  padding: 12px;
  background: #fff;
  border-radius: 8px;
  border: 1px solid #ffcdd2;
}

.warning-text {
  font-size: 14px;
  color: #c62828;
  margin: 0;
  line-height: 1.6;
}

.warning-text .highlight {
  font-weight: 600;
  color: #d32f2f;
}

/* 推荐菜谱 */
.recipe-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.recipe-item {
  padding: 10px 14px;
  background: #fff8e1;
  border-radius: 8px;
  font-size: 14px;
  color: #5d4037;
  border-left: 3px solid #ffb300;
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

/* 滚动条美化 */
.modal-content::-webkit-scrollbar {
  width: 6px;
}

.modal-content::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.modal-content::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.modal-content::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>
