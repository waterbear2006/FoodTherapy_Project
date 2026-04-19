<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// 打卡项目列表
const checkInItems = ref([
  { id: 'water', name: '晨起一杯水', icon: '🥤' },
  { id: 'teeth', name: '晨起叩齿', icon: '🦷' },
  { id: 'meals', name: '三餐规律', icon: '🍽️' },
  { id: 'sleep', name: '23点前睡', icon: '🌙' },
  { id: 'steps', name: '每天6000步', icon: '👟' },
  { id: 'sun', name: '晒太阳', icon: '☀️' },
  { id: 'mood', name: '心情舒畅', icon: '😊' },
  { id: 'footbath', name: '睡前泡脚', icon: '🦶' },
  { id: 'tiptoe', name: '垫脚100次', icon: '🦵' },
  { id: 'nap', name: '午睡', icon: '😴' },
  { id: 'massage', name: '睡前揉腹', icon: '🤲' },
  { id: 'kegel', name: '提肛收腹', icon: '🫃' }
])

// 已打卡的项目
const checkedItems = ref(new Set())

// 获取今天的日期字符串
function getTodayKey() {
  const today = new Date()
  return `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`
}

// 加载今日打卡状态
function loadCheckInStatus() {
  const todayKey = getTodayKey()
  const saved = localStorage.getItem(`checkin_${todayKey}`)
  if (saved) {
    try {
      const items = JSON.parse(saved)
      checkedItems.value = new Set(items)
    } catch (e) {
      checkedItems.value = new Set()
    }
  }
}

// 保存打卡状态
function saveCheckInStatus() {
  const todayKey = getTodayKey()
  localStorage.setItem(`checkin_${todayKey}`, JSON.stringify([...checkedItems.value]))
}

// 切换打卡状态
function toggleCheckIn(itemId) {
  if (checkedItems.value.has(itemId)) {
    checkedItems.value.delete(itemId)
  } else {
    checkedItems.value.add(itemId)
  }
  saveCheckInStatus()
}

// 计算已打卡数量
const checkedCount = computed(() => checkedItems.value.size)

// 计算总项目数
const totalCount = computed(() => checkInItems.value.length)

// 计算打卡进度百分比
const progressPercent = computed(() => {
  if (totalCount.value === 0) return 0
  return Math.round((checkedCount.value / totalCount.value) * 100)
})

onMounted(() => {
  loadCheckInStatus()
})
</script>

<template>
  <div class="page-checkin app-page">
    <header class="page-header">
      <button class="back-btn" type="button" @click="router.back()">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M19 12H5M12 19l-7-7 7-7"/>
        </svg>
      </button>
      <h1 class="page-title">每日打卡</h1>
      <span class="header-placeholder"></span>
    </header>

    <!-- 打卡进度 -->
    <section class="progress-section">
      <div class="progress-card">
        <div class="progress-info">
          <span class="progress-text">今日已打卡 {{ checkedCount }}/{{ totalCount }}</span>
          <span class="progress-percent">{{ progressPercent }}%</span>
        </div>
        <div class="progress-bar">
          <div class="progress-fill" :style="{ width: `${progressPercent}%` }"></div>
        </div>
      </div>
    </section>

    <!-- 打卡项目网格 -->
    <section class="checkin-grid-section">
      <div class="checkin-grid">
        <div
          v-for="item in checkInItems"
          :key="item.id"
          class="checkin-item"
          :class="{ 'checked': checkedItems.has(item.id) }"
          @click="toggleCheckIn(item.id)"
        >
          <div class="item-icon-wrap">
            <span class="item-icon">{{ item.icon }}</span>
            <span v-if="checkedItems.has(item.id)" class="check-mark">✓</span>
          </div>
          <span class="item-name">{{ item.name }}</span>
          <span class="item-status" :class="{ 'done': checkedItems.has(item.id) }">
            {{ checkedItems.has(item.id) ? '今日已打卡' : '今日未打卡' }}
          </span>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
.page-checkin {
  background: var(--bg);
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  background: transparent;
}

.back-btn {
  border: 1px solid var(--border);
  border-radius: 10px;
  width: 40px;
  height: 40px;
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
}

.back-btn:active {
  transform: scale(0.95);
  background: #f5f5f5;
}

.header-placeholder {
  width: 40px;
}

.page-title {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-h);
  margin: 0;
}

/* 进度区域 */
.progress-section {
  padding: 0 16px;
  margin-bottom: 20px;
}

.progress-card {
  background: linear-gradient(135deg, rgba(144, 180, 148, 0.85) 0%, rgba(118, 156, 122, 0.85) 100%);
  border-radius: 16px;
  padding: 16px 20px;
  box-shadow: 0 4px 16px rgba(118, 156, 122, 0.25);
}

.progress-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.progress-text {
  font-size: 14px;
  font-weight: 600;
  color: #fff;
}

.progress-percent {
  font-size: 16px;
  font-weight: 700;
  color: #fff;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 999px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: #fff;
  border-radius: 999px;
  transition: width 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

/* 打卡网格 */
.checkin-grid-section {
  padding: 0 16px;
}

.checkin-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.checkin-item {
  background: #fff;
  border-radius: 16px;
  padding: 16px 10px 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 2px solid transparent;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  position: relative;
}

.checkin-item:active {
  transform: scale(0.96);
}

.checkin-item.checked {
  border-color: #4caf50;
  background: linear-gradient(135deg, #f0fff0 0%, #e8f5e9 100%);
  box-shadow: 0 4px 12px rgba(76, 175, 80, 0.2);
}

.item-icon-wrap {
  position: relative;
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.item-icon {
  font-size: 32px;
  line-height: 1;
}

.check-mark {
  position: absolute;
  bottom: -2px;
  right: -2px;
  width: 18px;
  height: 18px;
  background: #4caf50;
  color: #fff;
  border-radius: 50%;
  font-size: 11px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid #fff;
  animation: popIn 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes popIn {
  0% {
    transform: scale(0);
    opacity: 0;
  }
  100% {
    transform: scale(1);
    opacity: 1;
  }
}

.item-name {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-h);
  text-align: center;
  line-height: 1.3;
}

.item-status {
  font-size: 10px;
  color: var(--text-muted);
  font-weight: 400;
}

.item-status.done {
  color: #4caf50;
  font-weight: 600;
}
</style>