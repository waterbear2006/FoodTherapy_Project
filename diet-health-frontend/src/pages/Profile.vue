<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { getProfile, getExpertAdvice } from '../api/mock'

const router = useRouter()
const user = ref({ name: '', days: 0, avatar: '' })
const expertAdvice = ref('')

// 从 localStorage 获取健康档案记录
const healthRecords = ref([])

// 获取最新的体质测试结果
const latestConstitution = computed(() => {
  const constitutionRecord = healthRecords.value.find(r => r.type === 'constitution')
  const result = constitutionRecord?.details?.constitution || '未测试'
  console.log('🔍 Profile - 当前体质:', result)
  return result
})

// 获取最新的用户信息（身高体重等）
const latestUserInfo = computed(() => {
  const constitutionRecord = healthRecords.value.find(r => r.type === 'constitution')
  const info = constitutionRecord?.details?.userInfo || null
  console.log('🔍 Profile - 用户信息:', info)
  return info
})

// 获取体质特征（主要症状）
const constitutionFeature = computed(() => {
  const constitutionRecord = healthRecords.value.find(r => r.type === 'constitution')
  let feature = constitutionRecord?.details?.feature || ''
  
  if (!feature && latestConstitution.value !== '未测试') {
    const fallbackFeatures = {
      '气虚质': '容易疲劳、气短懒言，活动后乏力明显，面色偏白或少华。',
      '湿热质': '面部油光、易生痤疮，口苦口干，身重困倦，大便黏滞不畅。',
      '阳虚质': '畏寒怕冷，手脚冰凉，喜热饮食，精神不振。',
      '阴虚质': '手足心热，口燥咽干，鼻微干，喜冷饮，大便干燥。',
      '痰湿质': '腹部肥满松软，面部皮肤油脂较多，多汗且黏，胸闷痰多。',
      '血瘀质': '肤色晦暗，唇色暗红，易出现瘀斑，女性痛经。',
      '气郁质': '情绪低落，焦虑不安，胸闷胁胀，失眠多梦。',
      '特禀质': '易过敏，对季节变化适应能力差，易患哮喘、荨麻疹等。',
      '平和质': '体态适中，面色红润，精力充沛，耐受冷热，较少出现不适。'
    }
    feature = fallbackFeatures[latestConstitution.value] || '暂无特征数据'
  }
  
  console.log('🔍 Profile - 体质特征:', feature)
  return feature
})

// 计算 BMI
const bmi = computed(() => {
  const info = latestUserInfo.value
  if (!info || !info.height || !info.weight) return ''
  const heightInM = info.height / 100
  const bmiValue = (info.weight / (heightInM * heightInM)).toFixed(1)
  return bmiValue
})

// 健康数据
const health = computed(() => {
  const info = latestUserInfo.value
  return {
    constitution: latestConstitution.value,
    symptoms: constitutionFeature.value, // 使用体质特征作为主要症状
    body: info ? `${info.height}cm / ${info.weight}kg` : '',
    bmi: bmi.value
  }
})

onMounted(async () => {
  // 从 localStorage 加载健康档案
  const records = JSON.parse(localStorage.getItem('healthArchive') || '[]')
  healthRecords.value = Array.isArray(records) ? records : []
  
  console.log('📋 Profile 页面加载的健康档案:', records)
  
  const constitutionRecord = healthRecords.value.find(r => r.type === 'constitution')
  
  // 获取用户资料
  const profile = await getProfile()
  user.value = profile
  
  // 根据体质获取专家建议
  if (constitutionRecord?.details) {
    const constitution = constitutionRecord.details.constitution || '平和质'
    const userInfo = constitutionRecord.details.userInfo || {}
    
    // 调用后端 API 获取专家建议
    const advice = await getExpertAdvice(
      { [constitution]: constitutionRecord.details.scores?.[constitution] || 80 },
      userInfo
    )
    expertAdvice.value = advice
  } else {
    // 如果没有体质记录，显示默认建议
    expertAdvice.value = '您还没有进行体质测试，建议先完成体质测试以获取个性化养生建议。'
  }
})

// 查看详细报告（跳转到体质测试页面）
function viewDetailedReport() {
  const hasConstitutionTest = healthRecords.value.some(r => r.type === 'constitution')
  
  if (!hasConstitutionTest) {
    alert('您还没有进行体质测试哦~\n请先完成体质测试后查看报告。')
    router.push('/constitution') // 跳转到体质测试页面
  } else {
    // 如果已经测试过，跳转到体质测试页面并通过 query 参数标记查看模式
    router.push({ 
      path: '/constitution',
      query: { view: 'result' } // 标记为查看模式，不是做题模式
    })
  }
}
</script>

<template>
  <div class="page-profile app-page">
    <header class="page-header">
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
            <span class="label">BMI 指数</span>
            <span class="value">{{ health.bmi ?? '' }}</span>
          </div>
        </div>
        <div class="expert-box">
          <h3 class="expert-title">专家建议</h3>
          <p class="expert-text">{{ expertAdvice }}</p>
          <a class="expert-link" @click="viewDetailedReport" style="cursor: pointer;">查看详细报告</a>
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
