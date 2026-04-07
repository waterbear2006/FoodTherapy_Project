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
    <h3 class="card-name">{{ name }}</h3>
    <p class="card-effect">{{ effect }}</p>
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
  font-size: 15px;
  font-weight: 600;
  color: var(--text-h);
  margin: 8px 10px 4px;
}

.card-effect {
  font-size: 13px;
  color: var(--primary);
  margin: 0 10px 10px;
}
</style>
