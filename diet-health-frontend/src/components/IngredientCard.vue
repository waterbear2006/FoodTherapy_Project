<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  name: { type: String, default: '' },
  effect: { type: String, default: '' },
  image: { type: String, default: '' },
  tag: { type: String, default: '' },
  suitable: { type: String, default: '' },
  avoid: { type: String, default: '' },
  methods: { type: String, default: '' },
  ancient_quote: { type: String, default: '' },
  ingredientData: { type: Object, default: null }
})

const emit = defineEmits(['click'])
const imageError = ref(false)

// 调试：监听 image 属性变化
watch(() => props.image, (newVal) => {
  console.log('IngredientCard 收到的完整数据:', {
    name: props.name,
    image: newVal,
    hasImage: !!newVal,
    ingredientData: props.ingredientData
  })
}, { immediate: true })

function handleImageError() {
  console.error('图片加载失败:', {
    name: props.name,
    imageUrl: props.image
  })
  imageError.value = true
}

function handleClick() {
  emit('click', props.ingredientData)
}
</script>

<template>
  <div class="ingredient-card" @click="handleClick">
    <div class="card-img-wrap">
      <img 
        v-if="image && !imageError" 
        :src="image" 
        :alt="name" 
        class="card-img" 
        loading="lazy"
        @error="handleImageError"
      />
      <div v-else class="card-img-placeholder">🌿</div>
    </div>
    <div class="card-content">
      <h3 class="card-name">{{ name }}</h3>
      <p class="card-effect">{{ effect }}</p>
      <!-- 古籍预览 -->
      <div v-if="ancient_quote" class="ancient-preview">
        <span class="preview-icon">📜</span>
        <span class="preview-text">{{ ancient_quote }}</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.ingredient-card {
  background: var(--bg-card);
  border-radius: var(--radius);
  overflow: hidden;
  box-shadow: var(--shadow);
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.ingredient-card:hover {
  transform: translateY(-4px) scale(1.02);
  box-shadow: var(--shadow-lg);
}

.ingredient-card:active {
  transform: scale(0.98);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.card-img-wrap {
  width: 100%;
  aspect-ratio: 1;
  background: var(--primary-light);
  position: relative;
  overflow: hidden;
}

.card-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.card-img-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 48px;
  background: linear-gradient(135deg, #e8f5e9, #c8e6c8);
}

.card-name {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-h);
  margin: 0 0 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  letter-spacing: -0.2px;
}

.card-effect {
  font-size: 11px;
  color: var(--primary);
  margin-bottom: 8px;
  padding: 2px 8px;
  border-radius: 999px;
  display: inline-block;
  background: var(--primary-light);
  font-weight: 500;
  letter-spacing: 0.3px;
}

.ancient-preview {
  display: flex;
  gap: 4px;
  background: #fdfaf5;
  padding: 6px 8px;
  border-radius: 8px;
  border-left: 2px solid var(--accent);
}

.preview-icon {
  font-size: 10px;
  flex-shrink: 0;
  margin-top: 1px;
}

.preview-text {
  font-size: 10px;
  color: #5c4b37;
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  font-family: serif;
}

.card-content {
  padding: 10px;
}
</style>
