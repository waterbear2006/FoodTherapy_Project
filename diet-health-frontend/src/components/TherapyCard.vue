<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  title: { type: String, default: '' },
  tag: { type: String, default: '' },
  effect: { type: String, default: '' },
  desc: { type: String, default: '' },
  tags: { type: Array, default: () => [] },
  buttonText: { type: String, default: '查看详情' },
  primaryButton: { type: Boolean, default: true },
  image: { type: String, default: '' },
  ancient_quote: { type: String, default: '' },
  // 接收完整的食疗数据对象
  therapyData: { type: Object, default: null }
})

const emit = defineEmits(['click'])

// 处理点击事件
function handleClick(event) {
  console.log('TherapyCard 点击事件，传递数据:', props.therapyData)
  emit('click', props.therapyData)
}

const imageError = ref(false)

// 调试：监听 image 属性变化
watch(() => props.image, (newVal) => {
  console.log('TherapyCard 收到的图片 URL:', newVal)
}, { immediate: true })

function handleImageError() {
  console.error('图片加载失败:', props.image)
  imageError.value = true
}
</script>

<template>
  <div class="therapy-card" @click="handleClick">
    <div v-if="image || therapyData?.image" class="card-img-wrap">
      <img 
        v-if="image && !imageError" 
        :src="image" 
        :alt="title" 
        class="card-img" 
        @error="handleImageError"
      />
      <div v-else class="card-img-placeholder">
        <span class="placeholder-icon">🌿</span>
      </div>
    </div>
    <div class="card-body">
      <h3 class="card-title">{{ title }}</h3>
      <p v-if="effect" class="card-effect">{{ effect }}</p>
      
      <!-- 古籍预览 -->
      <div v-if="ancient_quote" class="ancient-preview">
        <span class="preview-icon">📜</span>
        <span class="preview-text">{{ ancient_quote }}</span>
      </div>

      <div v-if="tags && tags.length" class="card-tags">
        <span v-for="(t, index) in tags.slice(0, 2)" :key="t" class="tag" :class="{ 'tag-hidden': index >= 2 }">{{ t }}</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.therapy-card {
  background: var(--bg-card);
  border-radius: var(--radius);
  overflow: hidden;
  box-shadow: var(--shadow);
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
.therapy-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
}
.card-img-wrap {
  width: 100%;
  height: 140px;
  background: var(--primary-light);
  position: relative;
  overflow: hidden;
}
.card-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.card-img-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--primary-light), var(--bg-subtle));
}
.placeholder-icon {
  font-size: 48px;
  opacity: 0.5;
}
.card-body {
  padding: 12px 16px 10px;
}
.card-title {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-h);
  margin: 0 0 8px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  letter-spacing: -0.2px;
}
.card-effect {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.4;
  margin: 0 0 8px;
  overflow: hidden;
  text-overflow: ellipsis;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  display: -webkit-box;
}
.ancient-preview {
  display: flex;
  gap: 4px;
  background: #fdfaf5;
  padding: 6px 8px;
  border-radius: 8px;
  border-left: 2px solid var(--accent);
  margin-bottom: 12px;
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
.card-tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  margin-bottom: 0px;
}
.card-tags .tag {
  font-size: 11px;
  color: var(--primary);
  background: var(--primary-light);
  padding: 4px 10px;
  border-radius: 999px;
  font-weight: 500;
  letter-spacing: 0.3px;
}
</style>
