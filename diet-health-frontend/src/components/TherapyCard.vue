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
  <div class="therapy-card">
    <div v-if="image || therapyData?.image" class="card-img-wrap" @click="handleClick">
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
      <div v-if="tags && tags.length" class="card-tags">
        <span v-for="(t, index) in tags.slice(0, 2)" :key="t" class="tag" :class="{ 'tag-hidden': index >= 2 }">{{ t }}</span>
      </div>
      <button
        v-if="buttonText"
        class="card-btn"
        :class="{ primary: primaryButton }"
        @click.stop="handleClick"
      >
        {{ buttonText }}
      </button>
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
  padding: 16px;
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
  line-height: 1.6;
  margin: 0 0 12px;
  overflow: hidden;
  text-overflow: ellipsis;
  -webkit-line-clamp: 10;
  -webkit-box-orient: vertical;
  display: -webkit-box;
}
.card-tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  margin-bottom: 12px;
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
.card-btn {
  width: 100%;
  height: 38px;
  border-radius: var(--radius-sm);
  border: 1px solid var(--primary);
  background: var(--primary-light);
  color: var(--primary);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  letter-spacing: 0.5px;
}
.card-btn.primary {
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
  color: #fff;
  border-color: var(--primary);
  box-shadow: 0 2px 8px rgba(125, 157, 138, 0.3);
}
.card-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(125, 157, 138, 0.2);
}
.card-btn.primary:hover {
  box-shadow: 0 4px 16px rgba(125, 157, 138, 0.4);
}
</style>
