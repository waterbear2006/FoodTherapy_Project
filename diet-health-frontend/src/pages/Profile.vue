<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { getExpertAdvice, getProfile } from '../api/mock'

const router = useRouter()
const user = ref({ name: '', days: 0, avatar: '' })
const expertAdvice = ref('')
const healthRecords = ref([])

const constitutionOrder = ['平和质', '气虚质', '阳虚质', '阴虚质', '痰湿质', '湿热质', '血瘀质', '气郁质', '特禀质']

const constitutionRecord = computed(() => healthRecords.value.find((r) => r.type === 'constitution') || null)

const latestConstitution = computed(() => constitutionRecord.value?.details?.constitution || '未测试')

const latestUserInfo = computed(() => constitutionRecord.value?.details?.userInfo || null)

const constitutionScores = computed(() => {
  try {
    const records = JSON.parse(localStorage.getItem('healthArchive') || '[]')
    const record = records.find(r => r && r.type === 'constitution')
    
    if (!record || !record.details) {
      return constitutionOrder.map(() => 45)
    }
    
    const scores = record.details.scores || record.details.constitution_vector || {}
    
    const result = constitutionOrder.map((name) => {
      const scoreValue = scores[name]
      const score = Number(scoreValue) || 0
      return score
    })
    
    return result
  } catch (error) {
    console.error('❌ Profile: constitutionScores 计算失败:', error)
    return constitutionOrder.map(() => 45)
  }
})

const healthScore = computed(() => Math.round(Math.max(...constitutionScores.value)))

const constitutionFeature = computed(() => {
  const feature = constitutionRecord.value?.details?.feature || ''
  if (feature) return feature
  const fallbackFeatures = {
    气虚质: '容易疲劳、气短懒言，活动后乏力明显。',
    湿热质: '面部油光、口苦口干、身重困倦。',
    阳虚质: '畏寒怕冷，手脚偏凉，喜温热饮食。',
    阴虚质: '手足心热，口燥咽干，易烦躁失眠。',
    痰湿质: '腹部肥满松软，胸闷痰多，困倦较重。',
    血瘀质: '肤色晦暗，易有瘀斑，局部刺痛。',
    气郁质: '情绪低落，胸闷胁胀，睡眠质量受影响。',
    特禀质: '易过敏，对外界环境变化较敏感。',
    平和质: '体态适中，面色红润，精力充沛。'
  }
  return fallbackFeatures[latestConstitution.value] || '暂无特征数据'
})

const bmiValue = computed(() => {
  const info = latestUserInfo.value
  if (!info?.height || !info?.weight) return null
  const h = Number(info.height) / 100
  if (!h) return null
  return Number((Number(info.weight) / (h * h)).toFixed(1))
})

const bmiPercent = computed(() => {
  if (bmiValue.value === null) return 0
  const min = 15
  const max = 35
  const normalized = ((bmiValue.value - min) / (max - min)) * 100
  return Math.min(100, Math.max(0, normalized))
})

const bmiLevel = computed(() => {
  if (bmiValue.value === null) return '暂无数据'
  if (bmiValue.value < 18.5) return '偏瘦'
  if (bmiValue.value < 24) return '正常'
  if (bmiValue.value < 28) return '超重'
  return '肥胖风险'
})

const bodyInfo = computed(() => {
  const info = latestUserInfo.value
  return info ? `${info.height}cm / ${info.weight}kg` : '未填写'
})

async function loadProfileData() {
  try {
    const records = JSON.parse(localStorage.getItem('healthArchive') || '[]')
    console.log('📥 Profile: loadProfileData 加载的 records:', records)
    healthRecords.value = Array.isArray(records) ? records : []
    console.log('✅ Profile: healthRecords 已设置，长度:', healthRecords.value.length)
    
    user.value = await getProfile()

    if (constitutionRecord.value?.details) {
      const constitution = constitutionRecord.value.details.constitution || '平和质'
      const userInfo = constitutionRecord.value.details.userInfo || {}
      const scoreValue = constitutionRecord.value.details.scores?.[constitution] || 80
      console.log(' Profile: 获取专家建议，体质:', constitution, '分数:', scoreValue)
      expertAdvice.value = await getExpertAdvice(
        { [constitution]: scoreValue },
        userInfo
      )
    } else {
      console.log('⚠️ Profile: 没有找到体质记录')
      expertAdvice.value = '您还没有进行体质测试，建议先完成体质测试以获取个性化养生建议。'
    }
  } catch (error) {
    console.error('❌ Profile: loadProfileData 失败:', error)
  }
}

function viewDetailedReport() {
  if (!constitutionRecord.value) {
    alert('您还没有进行体质测试哦，请先完成体质测试。')
    router.push('/constitution')
    return
  }
  router.push({ path: '/constitution', query: { view: 'result' } })
}

onMounted(async () => {
  await loadProfileData()
})
</script>

<template>
  <div class="page-profile app-page">
    <section class="profile-section">
      <div class="profile-card">
        <div class="avatar-wrap">
          <div class="avatar">👤</div>
        </div>
        <div class="profile-info">
          <h2 class="user-name">{{ user.name || '用户' }}</h2>
          <p class="user-days">已加入健康管理 {{ user.days || 1 }} 天</p>
          <div class="profile-actions">
            <button class="btn-edit">编辑资料</button>
          </div>
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
          <span class="score-badge">评分 {{ healthScore }}</span>
        </div>

        <div class="metrics-grid">
          <div class="metric neumorph">
            <span class="label">当前体质</span>
            <span class="value bold">{{ latestConstitution }}</span>
          </div>
          <div class="metric neumorph">
            <span class="label">主要症状</span>
            <span class="value">{{ constitutionFeature }}</span>
          </div>
          <div class="metric neumorph">
            <span class="label">身体数据</span>
            <span class="value">{{ bodyInfo }}</span>
          </div>
          <div class="metric neumorph">
            <span class="label">BMI 指数</span>
            <span class="value bold">{{ bmiValue ?? '-' }}（{{ bmiLevel }}）</span>
            <div class="bmi-bar">
              <div class="zone thin"></div>
              <div class="zone normal"></div>
              <div class="zone risk"></div>
              <div class="bmi-pointer" :style="{ left: `${bmiPercent}%` }"></div>
            </div>
          </div>
        </div>

        <div class="expert-box">
          <h3 class="expert-title">专家建议</h3>
          <p class="expert-text">{{ expertAdvice }}</p>
          <a class="expert-link" @click="viewDetailedReport">查看详细报告</a>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
.page-profile {
  background: var(--bg);
}

.profile-section {
  margin-bottom: 20px;
}

.profile-card {
  display: flex;
  align-items: center;
  gap: 16px;
  border-radius: var(--radius-lg);
  padding: 20px;
  box-shadow: var(--shadow);
  background: linear-gradient(155deg, #f2f7f2 0%, #ffffff 56%, #ffffff 100%);
  position: relative;
  overflow: hidden;
}

.profile-card::after {
  content: '';
  position: absolute;
  right: -16px;
  top: -20px;
  width: 160px;
  height: 160px;
  background: radial-gradient(circle, rgba(125, 157, 138, 0.1) 0%, transparent 70%);
  pointer-events: none;
}

.avatar-wrap {
  width: 74px;
  height: 74px;
  border-radius: 50%;
  background: #fffaf1;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: inset 4px 4px 10px rgba(204, 198, 187, 0.25), inset -4px -4px 10px rgba(255, 255, 255, 0.8);
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
  font-weight: 700;
  color: var(--text-h);
  margin: 0 0 6px;
}

.user-days {
  font-size: 13px;
  color: var(--text-muted);
  margin: 0 0 12px;
}

.profile-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.btn-edit,
.btn-export,
.btn-import {
  padding: 7px 12px;
  border-radius: var(--radius-sm);
  font-size: 13px;
  cursor: pointer;
  border: none;
}

.btn-edit {
  background: var(--primary-light);
  color: var(--primary-dark);
}

.btn-export {
  background: #e8f2ec;
  color: #4a6e5b;
}

.btn-import {
  background: #f5efe6;
  color: #7d6446;
}

.health-card {
  background: #ffffff;
  border-radius: var(--radius-lg);
  padding: 20px;
  box-shadow: var(--shadow);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.card-title {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-h);
  margin: 0;
  display: flex;
  align-items: center;
  gap: 6px;
}

.score-badge {
  font-size: 14px;
  font-weight: 600;
  color: var(--primary-dark);
  background: var(--primary-light);
  padding: 5px 12px;
  border-radius: 999px;
}

.metrics-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-bottom: 14px;
}

.metric {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 12px;
  border-radius: 14px;
}

.neumorph {
  background: #f6f8f6;
  box-shadow: inset 4px 4px 8px rgba(207, 214, 207, 0.45), inset -4px -4px 8px rgba(255, 255, 255, 0.9);
}

.label {
  font-size: 12px;
  color: var(--text-muted);
}

.value {
  font-size: 13px;
  color: var(--text-h);
  line-height: 1.5;
}

.value.bold {
  font-weight: 700;
}

.bmi-bar {
  position: relative;
  display: flex;
  height: 8px;
  border-radius: 999px;
  overflow: hidden;
  margin-top: 2px;
}

.zone {
  flex: 1;
}

.zone.thin {
  background: #9bc5f5;
}

.zone.normal {
  background: #82caa6;
}

.zone.risk {
  background: #f2c46f;
}

.bmi-pointer {
  position: absolute;
  top: -4px;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #3f5f52;
  border: 2px solid #ffffff;
  transform: translateX(-50%);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.18);
}

.expert-box {
  border-left: 4px solid var(--primary);
  background: var(--primary-light);
  padding: 12px 12px 12px 16px;
  border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
}

.expert-title {
  font-size: 14px;
  font-weight: 700;
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
  cursor: pointer;
}
</style>
