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
.recipe-card {
  background: var(--bg-card);
  border-radius: var(--radius);
  overflow: hidden;
  box-shadow: var(--shadow);
  cursor: pointer;
}
.card-image-wrap {
  width: 100%;
  height: 140px;
  background: var(--primary-light);
}
.card-image,
.card-image-placeholder {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.card-body {
  padding: 12px 14px;
}
.card-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  margin-bottom: 6px;
}
.card-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-h);
  margin: 0;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.card-tag {
  font-size: 12px;
  color: var(--primary);
  background: var(--primary-light);
  padding: 2px 8px;
  border-radius: 4px;
  flex-shrink: 0;
}
.card-desc {
  font-size: 13px;
  color: var(--text-secondary);
  margin: 0 0 8px;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.card-meta {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: var(--text-muted);
}
.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
}
</style>
