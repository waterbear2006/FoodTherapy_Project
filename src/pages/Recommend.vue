<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getConstitutionTags, getRecommendTherapyList, getTodayAdvice } from '../api/mock'

const router = useRouter()
const activeTag = ref(0)
const tags = ref([])
const therapyList = ref([])
const todayAdvice = ref('')

onMounted(async () => {
  const [t, list, advice] = await Promise.all([
    getConstitutionTags(),
    getRecommendTherapyList(),
    getTodayAdvice()
  ])
  tags.value = t
  therapyList.value = list
  todayAdvice.value = advice
})

function goDetail() {
  router.push('/therapy')
}
</script>

<template>
  <div class="page-recommend app-page">
    <header class="page-header">
      <span class="back" @click="router.back()">←</span>
      <h1 class="page-title">智能推荐</h1>
      <span class="header-icon">🔍</span>
    </header>

    <section class="block">
      <h2 class="block-title">
        <span class="title-icon">📊</span>
        当前体质分析
      </h2>
      <div class="tag-row">
        <button
          v-for="(t, i) in tags"
          :key="t.id || i"
          class="tag-btn"
          :class="{ active: activeTag === i }"
          @click="activeTag = i"
        >
          <span v-if="t.icon !== '✓'" class="tag-emoji">{{ t.icon }}</span>
          <span v-else class="tag-check">✓</span>
          {{ t.label }}
          <span class="tag-arrow">▼</span>
        </button>
      </div>
    </section>

    <section class="block">
      <div class="block-head">
        <h2 class="block-title">针对性食疗方案</h2>
        <a class="link-more" @click="goDetail">查看全部 &gt;</a>
      </div>
      <div class="therapy-cards">
        <div
          v-for="item in therapyList"
          :key="item.id"
          class="therapy-card"
          @click="goDetail"
        >
          <div class="card-img-wrap">
            <img v-if="item.image" :src="item.image" :alt="item.name" class="card-img" />
            <div class="card-bookmark">🔖</div>
          </div>
          <span class="card-match">匹配度 {{ item.match }}</span>
          <h3 class="card-name">{{ item.name }}</h3>
          <p class="card-effect">功效: {{ item.effect }}</p>
          <p class="card-desc">{{ item.desc }}</p>
          <div class="card-footer">
            <div v-if="item.users" class="avatars">
              <span class="avatar">👤</span>
              <span class="avatar">👤</span>
              <span class="avatar-num">+{{ item.users }}</span>
            </div>
            <div v-else class="meta">
              <span>🕐 {{ item.time }}</span>
              <span>🔥 {{ item.calorie }}</span>
            </div>
            <button class="btn-make">立即制作</button>
          </div>
        </div>
      </div>
    </section>

    <section class="block">
      <div class="advice-box">
        <div class="advice-head">
          <span class="advice-icon">💡</span>
          <span class="advice-title">今日调理建议</span>
        </div>
        <p class="advice-text">{{ todayAdvice }}</p>
      </div>
    </section>
  </div>
</template>

<style scoped>
.page-recommend {
  background: var(--bg);
}
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 0 20px;
}
.back {
  font-size: 20px;
  color: var(--text-h);
  cursor: pointer;
  width: 32px;
}
.page-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-h);
  margin: 0;
}
.header-icon {
  font-size: 20px;
  width: 32px;
  text-align: right;
}
.block {
  margin-bottom: 24px;
}
.block-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-h);
  margin: 0 0 12px;
  display: flex;
  align-items: center;
  gap: 6px;
}
.title-icon {
  font-size: 18px;
}
.block-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}
.link-more {
  font-size: 14px;
  color: var(--text-muted);
  text-decoration: none;
}
.tag-row {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}
.tag-btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 8px 14px;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border);
  background: var(--bg-card);
  font-size: 14px;
  color: var(--text);
  cursor: pointer;
}
.tag-btn.active {
  background: var(--primary);
  border-color: var(--primary);
  color: #fff;
}
.tag-emoji, .tag-check {
  margin-right: 2px;
}
.tag-check {
  color: inherit;
}
.tag-arrow {
  font-size: 10px;
  margin-left: 4px;
  opacity: 0.8;
}
.therapy-cards {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.therapy-card {
  background: var(--bg-card);
  border-radius: var(--radius);
  overflow: hidden;
  box-shadow: var(--shadow);
  cursor: pointer;
}
.card-img-wrap {
  position: relative;
  width: 100%;
  height: 160px;
  background: var(--primary-light);
}
.card-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.card-bookmark {
  position: absolute;
  top: 10px;
  right: 10px;
  font-size: 20px;
}
.card-match {
  display: inline-block;
  margin: 10px 0 0 14px;
  font-size: 12px;
  font-weight: 600;
  color: var(--primary);
  background: var(--primary-light);
  padding: 2px 8px;
  border-radius: 4px;
}
.card-name {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-h);
  margin: 8px 14px 4px;
}
.card-effect {
  font-size: 13px;
  color: var(--text-h);
  margin: 0 14px 6px;
}
.card-desc {
  font-size: 13px;
  color: var(--text-muted);
  line-height: 1.5;
  margin: 0 14px 12px;
}
.card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 14px 14px;
}
.avatars {
  display: flex;
  align-items: center;
  gap: 4px;
}
.avatar {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: #ddd;
  font-size: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.avatar-num {
  font-size: 12px;
  color: var(--text-muted);
}
.meta {
  font-size: 12px;
  color: var(--text-muted);
  display: flex;
  gap: 12px;
}
.btn-make {
  padding: 8px 20px;
  border: none;
  border-radius: var(--radius-sm);
  background: var(--primary);
  color: #fff;
  font-size: 14px;
  cursor: pointer;
}
.advice-box {
  background: #f0f0f0;
  border-radius: var(--radius);
  padding: 16px;
}
.advice-head {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 8px;
}
.advice-icon {
  font-size: 18px;
}
.advice-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-h);
}
.advice-text {
  font-size: 14px;
  color: var(--text);
  line-height: 1.5;
  margin: 0;
}
</style>
