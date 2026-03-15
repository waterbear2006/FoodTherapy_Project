<script setup>
import { ref, onMounted } from 'vue'
import { getProfile, getHealthArchive, getExpertAdvice } from '../api/mock'

const user = ref({ name: '', days: 0, avatar: '' })
const health = ref({})
const expertAdvice = ref('')

onMounted(async () => {
  const [p, h, e] = await Promise.all([
    getProfile(),
    getHealthArchive(),
    getExpertAdvice()
  ])
  user.value = p
  health.value = h
  expertAdvice.value = e
})
</script>

<template>
  <div class="page-profile app-page">
    <header class="page-header">
      <h1 class="page-title">我的</h1>
      <span class="header-icon">⚙️</span>
    </header>

    <section class="profile-section">
      <div class="profile-card">
        <div class="avatar-wrap">
          <div class="avatar">👤</div>
        </div>
        <div class="profile-info">
          <h2 class="user-name">{{ user.name }}</h2>
          <p class="user-days">已加入健康管理 {{ user.days }} 天</p>
          <button class="btn-edit">编辑资料</button>
        </div>
      </div>
    </section>

    <section class="health-section">
      <div class="health-card">
        <div class="card-header">
          <h2 class="card-title">
            <span class="card-icon">📋</span>
            健康档案
          </h2>
          <span class="score-badge">评分{{ health.score ?? 85 }}</span>
        </div>
        <div class="health-grid">
          <div class="grid-item">
            <span class="label">当前体质</span>
            <span class="value bold">{{ health.constitution ?? '' }}</span>
          </div>
          <div class="grid-item">
            <span class="label">主要症状</span>
            <span class="value bold">{{ health.symptoms ?? '' }}</span>
          </div>
          <div class="grid-item">
            <span class="label">身体数据</span>
            <span class="value">{{ health.body ?? '' }}</span>
          </div>
          <div class="grid-item">
            <span class="label">BMI指数</span>
            <span class="value">{{ health.bmi ?? '' }}</span>
          </div>
          <div class="grid-item">
            <span class="label">昨晚睡眠</span>
            <span class="value">{{ health.sleep ?? '' }}</span>
          </div>
          <div class="grid-item">
            <span class="label">今日饮水</span>
            <span class="value">{{ health.water ?? '' }}</span>
          </div>
          <div class="grid-item">
            <span class="label">今日步数</span>
            <span class="value bold">{{ health.steps ?? '' }}</span>
          </div>
          <div class="grid-item">
            <span class="label">静息心率</span>
            <span class="value">{{ health.heartRate ?? '' }}</span>
          </div>
        </div>
        <div class="expert-box">
          <h3 class="expert-title">专家建议</h3>
          <p class="expert-text">{{ expertAdvice }}</p>
          <a class="expert-link" href="javascript:;">查看详细报告</a>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
.page-profile {
  background: var(--bg);
}
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 0 20px;
}
.page-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-h);
  margin: 0;
}
.header-icon {
  font-size: 22px;
}
.profile-section {
  margin-bottom: 20px;
}
.profile-card {
  display: flex;
  align-items: center;
  gap: 16px;
  background: var(--bg-card);
  border-radius: var(--radius);
  padding: 20px;
  box-shadow: var(--shadow);
}
.avatar-wrap {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  background: #fff8e7;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.avatar {
  font-size: 40px;
}
.profile-info {
  flex: 1;
  min-width: 0;
}
.user-name {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-h);
  margin: 0 0 6px;
}
.user-days {
  font-size: 13px;
  color: var(--text-muted);
  margin: 0 0 12px;
}
.btn-edit {
  padding: 6px 16px;
  border: none;
  border-radius: var(--radius-sm);
  background: var(--primary-light);
  color: var(--primary-dark);
  font-size: 14px;
  cursor: pointer;
}
.health-card {
  background: var(--bg-card);
  border-radius: var(--radius);
  padding: 20px;
  box-shadow: var(--shadow);
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
.card-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-h);
  margin: 0;
  display: flex;
  align-items: center;
  gap: 6px;
}
.card-icon {
  font-size: 18px;
}
.score-badge {
  font-size: 14px;
  font-weight: 600;
  color: var(--primary-dark);
  background: var(--primary-light);
  padding: 4px 12px;
  border-radius: 20px;
}
.health-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px 16px;
  margin-bottom: 16px;
}
.grid-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.grid-item .label {
  font-size: 12px;
  color: var(--text-muted);
}
.grid-item .value {
  font-size: 14px;
  color: var(--text-h);
}
.grid-item .value.bold {
  font-weight: 600;
}
.expert-box {
  border-left: 4px solid var(--primary);
  padding-left: 12px;
  background: var(--primary-light);
  padding: 12px 12px 12px 16px;
  border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
}
.expert-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--primary-dark);
  margin: 0 0 6px;
}
.expert-text {
  font-size: 13px;
  color: var(--text);
  line-height: 1.5;
  margin: 0 0 8px;
}
.expert-link {
  font-size: 14px;
  color: var(--primary);
  text-decoration: none;
}
</style>
