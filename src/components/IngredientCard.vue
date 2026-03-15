<script setup>
defineProps({
  name: { type: String, default: '' },
  effect: { type: String, default: '' },
  image: { type: String, default: '' }
})
</script>

<template>
  <div class="ingredient-card">
    <div class="card-img-wrap">
      <img v-if="image" :src="image" :alt="name" class="card-img" />
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
}
.card-img-wrap {
  width: 100%;
  aspect-ratio: 1;
  background: var(--primary-light);
}
.card-img,
.card-img-placeholder {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.card-img-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
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
