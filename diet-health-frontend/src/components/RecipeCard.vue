<script setup>
defineProps({
  title: { type: String, default: '' },
  tag: { type: String, default: '' },
  desc: { type: String, default: '' },
  time: { type: String, default: '' },
  calorie: { type: String, default: '' },
  image: { type: String, default: '' }
})
</script>

<template>
  <div class="recipe-card" @click="$emit('click')">
    <div class="card-image-wrap">
      <img v-if="image" :src="image" :alt="title" class="card-image" />
      <div v-else class="card-image-placeholder" />
    </div>
    <div class="card-body">
      <div class="card-head">
        <h3 class="card-title">{{ title }}</h3>
        <span v-if="tag" class="card-tag">{{ tag }}</span>
      </div>
      <p class="card-desc">{{ desc }}</p>
      <div class="card-meta">
        <span class="meta-item">🕐 {{ time }}</span>
        <span class="meta-item">🔥 {{ calorie }}</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* 核心：玻璃态卡片换肤 */
.recipe-card {
  background: rgba(255, 255, 255, 0.8); /* 高透明微灰/白 */
  backdrop-filter: blur(12px);          /* 毛玻璃效果 */
  -webkit-backdrop-filter: blur(12px);
  border-radius: 16px;                  /* 大圆角 */
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05); /* 极弱弥散阴影 */
  border: 1px solid rgba(255, 255, 255, 0.4); /* 苹果风高光描边 */
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.recipe-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
}

.card-image-wrap { width: 100%; height: 140px; background: rgba(0,0,0,0.03); }
.card-image, .card-image-placeholder { width: 100%; height: 100%; object-fit: cover; }
.card-body { padding: 14px 16px; }
.card-head { display: flex; align-items: center; justify-content: space-between; gap: 8px; margin-bottom: 6px; }
.card-title { font-size: 16px; font-weight: 600; color: #1a1a1a; margin: 0; flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.card-tag { font-size: 11px; color: #333; background: rgba(0,0,0,0.04); padding: 4px 10px; border-radius: 12px; flex-shrink: 0; font-weight: 500;}
.card-desc { font-size: 13px; color: #666; margin: 0 0 10px; line-height: 1.5; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.card-meta { display: flex; gap: 16px; font-size: 12px; color: #999; }
.meta-item { display: flex; align-items: center; gap: 4px; }
</style>