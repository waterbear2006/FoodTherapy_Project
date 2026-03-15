<script setup>
defineProps({
  title: { type: String, default: '' },
  tag: { type: String, default: '' },
  effect: { type: String, default: '' },
  desc: { type: String, default: '' },
  tags: { type: Array, default: () => [] },
  buttonText: { type: String, default: '查看详情' },
  primaryButton: { type: Boolean, default: true },
  image: { type: String, default: '' }
})
</script>

<template>
  <div class="therapy-card">
    <div class="card-img-wrap">
      <img v-if="image" :src="image" :alt="title" class="card-img" />
      <div v-else class="card-img-placeholder" />
    </div>
    <div class="card-body">
      <div class="card-head">
        <h3 class="card-title">{{ title }}</h3>
        <span v-if="tag" class="card-tag">{{ tag }}</span>
      </div>
      <p v-if="desc" class="card-desc">{{ desc }}</p>
      <p v-else-if="effect" class="card-effect">功效: {{ effect }}</p>
      <div v-if="tags && tags.length" class="card-tags">
        <span v-for="t in tags" :key="t" class="tag">{{ t }}</span>
      </div>
      <button
        class="card-btn"
        :class="{ primary: primaryButton }"
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
}
.card-img-wrap {
  width: 100%;
  height: 160px;
  background: var(--primary-light);
}
.card-img,
.card-img-placeholder {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.card-body {
  padding: 14px;
}
.card-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  margin-bottom: 8px;
}
.card-title {
  font-size: 17px;
  font-weight: 600;
  color: var(--text-h);
  margin: 0;
  flex: 1;
}
.card-tag {
  font-size: 12px;
  color: #fff;
  background: var(--primary);
  padding: 2px 8px;
  border-radius: 4px;
  flex-shrink: 0;
}
.card-desc,
.card-effect {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.5;
  margin: 0 0 10px;
}
.card-tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 12px;
}
.card-tags .tag {
  font-size: 12px;
  color: var(--primary);
  background: var(--primary-light);
  padding: 4px 10px;
  border-radius: 4px;
}
.card-btn {
  width: 100%;
  height: 40px;
  border-radius: var(--radius-sm);
  border: 1px solid var(--primary);
  background: var(--primary-light);
  color: var(--primary);
  font-size: 14px;
  cursor: pointer;
}
.card-btn.primary {
  background: var(--primary);
  color: #fff;
  border-color: var(--primary);
}
</style>
