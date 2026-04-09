<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getQuizQuestions, submitQuizAnswers, saveHealthArchive } from '@/api/mock'

const router = useRouter()

const questions = ref([])
// 默认选项（兜底）
const defaultOptions = [
  { text: '总是', score: 5 },
  { text: '经常', score: 4 },
  { text: '有时', score: 3 },
  { text: '很少', score: 2 },
  { text: '根本不', score: 1 }
]

const currentIndex = ref(0)
const answers = ref({})
const loading = ref(false)
const apiResult = ref(null)
const showReport = ref(false) // 显示报告弹窗
const showSubmitButton = ref(false) // 显示提交按钮

// 用户信息
const userInfo = ref({
  gender: '',
  age: null,
  height: null,
  weight: null
})
const showUserForm = ref(true) // 是否显示用户信息表单

const currentQuestion = computed(() => questions.value[currentIndex.value])
const progress = computed(() => {
  if (!questions.value.length) return 0
  return ((currentIndex.value + 1) / questions.value.length) * 100
})
const finished = computed(() => {
  return apiResult.value !== null && currentIndex.value >= questions.value.length
})
const hasQuestions = computed(() => questions.value.length > 0)

const result = computed(() => {
  if (!apiResult.value) return null
  
  // 后端返回格式：{ data: { constitutions: [...], description: '', is_combination: ... }, success: true }
  const apiData = apiResult.value.data || apiResult.value
  const { constitutions, is_combination, scores, description } = apiData
  
  if (!constitutions || !Array.isArray(constitutions) || constitutions.length === 0) {
    console.warn('⚠️ 体质数据为空，使用默认值')
    return null
  }
  
  const mainConstitutionRaw = constitutions[0]
  
  // 保持原始名称用于查找
  let mainConstitution = mainConstitutionRaw
  
  console.log('📊 体质结果:', {
    raw: mainConstitutionRaw,
    normalized: mainConstitution,
    is_combination,
    scores,
    description
  })
  
  // 根据体质类型返回对应的建议
  const constitutionInfo = {
    '气虚质': {
      feature: '容易疲劳、气短懒言，活动后乏力明显，面色偏白或少华。',
      diet: '宜常食健脾补气之品，如山药、黄芪、党参、红枣、小米等，饮食以温和清淡为主。',
      foods: ['山药', '黄芪', '红枣', '小米'],
      therapies: ['黄芪党参鸡汤', '山药红枣小米粥']
    },
    '湿热质': {
      feature: '面部油光、易生痤疮，口苦口干，身重困倦，大便黏滞不畅。',
      diet: '宜清热利湿，多食绿豆、冬瓜、丝瓜、芹菜等，少食辛辣油腻。',
      foods: ['绿豆', '冬瓜', '丝瓜', '芹菜'],
      therapies: ['绿豆薏米粥', '冬瓜排骨汤']
    },
    '阳虚质': {
      feature: '畏寒怕冷，手脚冰凉，喜热饮食，精神不振。',
      diet: '宜温补脾肾，多食羊肉、韭菜、桂圆、生姜等温热食物。',
      foods: ['羊肉', '韭菜', '桂圆', '生姜'],
      therapies: ['当归生姜羊肉汤', '韭菜炒虾仁']
    },
    '阴虚质': {
      feature: '手足心热，口燥咽干，鼻微干，喜冷饮，大便干燥。',
      diet: '宜滋阴润燥，多食银耳、百合、梨、蜂蜜等滋润食物。',
      foods: ['银耳', '百合', '梨', '蜂蜜'],
      therapies: ['银耳莲子羹', '百合雪梨汤']
    },
    '痰湿质': {
      feature: '腹部肥满松软，面部皮肤油脂较多，多汗且黏，胸闷痰多。',
      diet: '宜健脾祛湿，多食薏米、赤小豆、陈皮、白萝卜等。',
      foods: ['薏米', '赤小豆', '陈皮', '白萝卜'],
      therapies: ['薏米赤小豆粥', '陈皮排骨汤']
    },
    '血瘀质': {
      feature: '肤色晦暗，唇色暗红，易出现瘀斑，女性痛经。',
      diet: '宜活血化瘀，多食山楂、黑木耳、洋葱、红糖等。',
      foods: ['山楂', '黑木耳', '洋葱', '红糖'],
      therapies: ['山楂红糖水', '木耳炒肉片']
    },
    '气郁质': {
      feature: '情绪低落，焦虑不安，胸闷胁胀，失眠多梦。',
      diet: '宜疏肝解郁，多食玫瑰花、佛手、柑橘、芹菜等。',
      foods: ['玫瑰花', '佛手', '柑橘', '芹菜'],
      therapies: ['玫瑰花茶', '佛手粥']
    },
    '特禀质': {
      feature: '易过敏，对季节变化适应能力差，易患哮喘、荨麻疹等。',
      diet: '宜益气固表，多食灵芝、蜂蜜、胡萝卜、金针菇等。',
      foods: ['灵芝', '蜂蜜', '胡萝卜', '金针菇'],
      therapies: ['灵芝红枣茶', '蜂蜜蒸南瓜']
    },
    '平和质': {
      feature: '体态适中，面色红润，精力充沛，耐受冷热，较少出现不适。',
      diet: '饮食宜均衡多样，谷类、蔬菜、水果、适量肉类合理搭配，少油少盐。',
      foods: ['燕麦', '莲子', '绿叶蔬菜'],
      therapies: ['莲子百合银耳羹', '清润蔬菜汤']
    }
  }
  
  const info = constitutionInfo[mainConstitution] || constitutionInfo['平和质']
  return {
    type: mainConstitution,
    is_combination,
    scores,
    ...info
  }
})

async function loadQuestions() {
  loading.value = true
  try {
    const list = await getQuizQuestions()
    console.log('✅ 加载到的题目:', list)
    questions.value = list
  } catch (err) {
    console.error('❌ 加载题目失败:', err)
    questions.value = []
  } finally {
    loading.value = false
    console.log('📊 加载状态:', {
      loading: loading.value,
      questionsLength: questions.value.length,
      hasQuestions: questions.value.length > 0
    })
  }
}

function choose(score) {
  const questionId = String(currentQuestion.value.id)
  answers.value[questionId] = score
  
  if (currentIndex.value < questions.value.length - 1) {
    currentIndex.value += 1
  } else {
    // 最后一题，显示提交按钮
    showSubmitButton.value = true
  }
}

function previous() {
  if (currentIndex.value > 0) {
    currentIndex.value -= 1
  }
}

async function submitAnswers() {
  loading.value = true
  try {
    console.log('📤 开始提交答案...')
    const result = await submitQuizAnswers(answers.value)
    console.log('✅ 答案提交成功，设置 apiResult')
    apiResult.value = result
    currentIndex.value = questions.value.length
    showSubmitButton.value = false // 隐藏提交按钮
    // 注意：finished 是计算属性，不需要手动赋值
    console.log('📊 当前状态:', {
      apiResult: apiResult.value,
      currentIndex: currentIndex.value,
      questionsLength: questions.value.length,
      finished: finished.value
    })
    // 保存结果到健康档案
    saveToHealthArchive()
  } catch (err) {
    console.error('❌ 提交答案失败:', err)
    alert('提交失败，请重试')
  } finally {
    loading.value = false
  }
}

// 保存测试结果到健康档案并生成报告
async function saveToHealthArchive() {
  console.log('💾 开始保存测试数据...')
  console.log('🔍 result.value:', result.value)
  console.log('🔍 apiResult.value:', apiResult.value)
  
  if (!result.value) {
    console.error('❌ result.value 为空，无法保存')
    return
  }
  
  const record = {
    id: Date.now(),
    date: new Date().toISOString().split('T')[0],
    timestamp: new Date().toISOString(),
    type: 'constitution',
    title: '体质测试报告',
    content: `您的体质类型为：${result.value.type}${result.value.is_combination ? '（兼夹体质）' : ''}`,
    details: {
      constitution: result.value.type, // 这个字段会被 Profile.vue 读取
      isCombination: result.value.is_combination,
      scores: result.value.scores,
      feature: result.value.feature,
      diet: result.value.diet,
      foods: result.value.foods,
      therapies: result.value.therapies,
      description: result.value.description,
      userInfo: { 
        gender: userInfo.value.gender,
        age: userInfo.value.age,
        height: userInfo.value.height,
        weight: userInfo.value.weight
      }
    }
  }
  
  console.log('📦 准备保存的体质数据:', record)
  
  // 保存到 localStorage
  const existing = JSON.parse(localStorage.getItem('healthArchive') || '[]')
  existing.unshift(record)
  localStorage.setItem('healthArchive', JSON.stringify(existing))
  console.log('✅ 已保存到 localStorage')
  console.log('📋 完整的 healthArchive:', JSON.parse(localStorage.getItem('healthArchive') || '[]'))
  
  // 调用后端 API 保存健康档案
  try {
    await saveHealthArchive({
      user_id: localStorage.getItem('user_id') || 'temp_user',
      constitution: result.value.type,
      score: Math.round(result.value.score || 85),
      symptoms: result.value.feature,
      height: userInfo.value.height,
      weight: userInfo.value.weight,
      age: userInfo.value.age,
      gender: userInfo.value.gender,
      sleep: '',
      water: '',
      steps: '',
      heartRate: '',
      lastUpdated: new Date().toISOString()
    })
    console.log('✅ 已同步到后端健康档案')
  } catch (err) {
    console.error('❌ 同步后端失败:', err)
  }
  
  // 延迟一点显示报告，让用户感觉到保存的过程
  setTimeout(() => {
    showReport.value = true
    console.log('🎉 报告已显示，showReport:', showReport.value)
  }, 300)
}

// 计算 BMI
function calculateBMI() {
  if (!userInfo.value.height || !userInfo.value.weight) return '-'
  const heightInM = userInfo.value.height / 100
  const bmi = (userInfo.value.weight / (heightInM * heightInM)).toFixed(1)
  return bmi
}

// 保存并关闭
function saveAndClose() {
  alert('报告已保存到健康档案！\n您可以在主页查看完整记录。')
  showReport.value = false
  router.push('/') // 跳转到主页
}

// 下载报告
function downloadReport() {
  alert('报告下载功能开发中...\n当前数据已自动保存到健康档案。')
}

// 开始测试（填写完用户信息后）
function startTest() {
  // 验证用户信息
  if (!userInfo.value.gender || !userInfo.value.age || !userInfo.value.height || !userInfo.value.weight) {
    alert('请填写完整的个人信息')
    return
  }
  if (userInfo.value.age < 1 || userInfo.value.age > 120) {
    alert('请输入有效的年龄（1-120岁）')
    return
  }
  if (userInfo.value.height < 50 || userInfo.value.height > 250) {
    alert('请输入有效的身高（50-250cm）')
    return
  }
  if (userInfo.value.weight < 20 || userInfo.value.weight > 300) {
    alert('请输入有效的体重（20-300kg）')
    return
  }
  showUserForm.value = false
}


// 雷达图背景网格计算
const radarGrids = [20, 40, 60, 80, 100].map(level => {
  const angleStep = (Math.PI * 2) / 9
  return Array.from({ length: 9 }).map((_, i) => {
    const r = (level / 100) * 100
    const x = 150 + Math.cos(angleStep * i - Math.PI / 2) * r
    const y = 150 + Math.sin(angleStep * i - Math.PI / 2) * r
    return `${x},${y}`
  }).join(' ')
})

const radarPoints = computed(() => {
  if (!result.value || !result.value.scores) return ''
  const scores = result.value.scores
  const categories = ['平和质', '气虚质', '阳虚质', '阴虚质', '痰湿质', '湿热质', '血瘀质', '气郁质', '特禀质']
  const angleStep = (Math.PI * 2) / 9
  
  return categories.map((cat, i) => {
    // 获取转化分，如果没有则默认为8（为了图形饱满感，且保证转化分显示比例）
    const score = Math.max(scores[cat] || 0, 8)
    const r = (score / 100) * 100
    const x = 150 + Math.cos(angleStep * i - Math.PI / 2) * r
    const y = 150 + Math.sin(angleStep * i - Math.PI / 2) * r
    return `${x},${y}`
  }).join(' ')
})

const radarLabels = computed(() => {
  const categories = ['平和', '气虚', '阳虚', '阴虚', '痰湿', '湿热', '血瘀', '气郁', '特禀']
  const angleStep = (Math.PI * 2) / 9
  return categories.map((name, i) => {
    // 标签位置略微偏离中心
    const x = 150 + Math.cos(angleStep * i - Math.PI / 2) * 125
    const y = 150 + Math.sin(angleStep * i - Math.PI / 2) * 125
    return { name, x, y }
  })
})

const restart = () => {
  currentIndex.value = 0
  answers.value = {}
  apiResult.value = null
}

onMounted(() => {
  loadQuestions()
  
  // 检查是否是从主页"查看详细报告"跳转过来的
  const routeQuery = router.currentRoute.value.query
  if (routeQuery.view === 'result') {
    console.log('🔍 检测到查看模式，尝试加载历史测试结果')
    
    // 从 localStorage 加载最近的体质测试记录
    const records = JSON.parse(localStorage.getItem('healthArchive') || '[]')
    const constitutionRecord = records.find(r => r.type === 'constitution')
    
    if (constitutionRecord && constitutionRecord.details) {
      console.log('📝 找到历史记录:', constitutionRecord)
      
      // 模拟 apiResult，触发结果显示
      apiResult.value = {
        data: {
          constitutions: [constitutionRecord.details.constitution],
          description: `您的主体质是 ${constitutionRecord.details.constitution}`,
          is_combination: constitutionRecord.details.isCombination || false,
          scores: constitutionRecord.details.scores || {}
        }
      }
      
      // 恢复用户信息
      if (constitutionRecord.details.userInfo) {
        userInfo.value = { ...constitutionRecord.details.userInfo }
      }
      
      // 延迟一点显示报告，模拟刚做完题的效果
      setTimeout(() => {
        showReport.value = true
        console.log('🎉 已加载历史测试结果并显示报告')
      }, 500)
    } else {
      console.log('⚠️ 未找到历史记录')
      alert('您还没有完成过体质测试哦~')
      router.push('/') // 跳转到主页
    }
  }
})
</script>

<template>
  <div class="page-constitution app-page">
    <header class="page-header">
      <button class="back-btn" type="button" @click="router.back()">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M19 12H5M12 19l-7-7 7-7"/>
        </svg>
      </button>
      <h1 class="page-title">体质测试</h1>
      <span class="header-placeholder"></span>
    </header>

    <!-- 加载状态 -->
    <section v-if="loading" class="block">
      <div class="card">
        <p class="hint" style="text-align: center;">加载中...</p>
      </div>
    </section>

    <!-- 无题目状态 -->
    <section v-else-if="!hasQuestions && !finished" class="block">
      <div class="card">
        <p class="hint" style="text-align: center;">暂无题目</p>
      </div>
    </section>

    <!-- 用户信息收集表单 -->
    <section v-else-if="showUserForm" class="block">
      <div class="card">
        <div class="card-head">
          <span class="card-subtitle">基本信息</span>
        </div>
        <p class="form-desc">请填写您的基本信息，以便为您提供更准确的体质分析</p>
        
        <div class="form-group">
          <label>性别</label>
          <div class="gender-options">
            <button 
              type="button"
              class="gender-btn"
              :class="{ selected: userInfo.gender === '男' }"
              @click="userInfo.gender = '男'"
            >
              <span class="gender-icon">♂</span>
              男
            </button>
            <button 
              type="button"
              class="gender-btn"
              :class="{ selected: userInfo.gender === '女' }"
              @click="userInfo.gender = '女'"
            >
              <span class="gender-icon">♀</span>
              女
            </button>
          </div>
        </div>

        <div class="form-group">
          <label>年龄（岁）</label>
          <input 
            v-model.number="userInfo.age" 
            type="number" 
            placeholder="请输入年龄"
            class="form-input"
            min="1"
            max="120"
          />
        </div>

        <div class="form-row">
          <div class="form-group">
            <label>身高（cm）</label>
            <input 
              v-model.number="userInfo.height" 
              type="number" 
              placeholder="请输入身高"
              class="form-input"
              min="50"
              max="250"
            />
          </div>
          <div class="form-group">
            <label>体重（kg）</label>
            <input 
              v-model.number="userInfo.weight" 
              type="number" 
              placeholder="请输入体重"
              class="form-input"
              min="20"
              max="300"
            />
          </div>
        </div>

        <button class="btn-primary" type="button" @click="startTest">
          开始测试
        </button>
      </div>
    </section>

    <!-- 测试阶段 -->
    <section v-else-if="!finished" class="block">
      <div class="card">
        <div class="card-head">
          <span class="card-subtitle">中医九种体质参考问卷（简版）</span>
          <span class="card-step">第 {{ currentIndex + 1 }} 题 / 共 {{ questions.length }} 题</span>
        </div>
        <div class="progress-wrap">
          <div class="progress-bar">
            <div class="progress-inner" :style="{ width: progress + '%' }" />
          </div>
        </div>
        <p class="question-text">
          {{ currentQuestion?.question }}
        </p>
        <div class="option-list">
          <button
            v-for="opt in (currentQuestion?.options || defaultOptions)"
            :key="opt.text"
            type="button"
            class="option-btn"
            :class="{ selected: answers[String(currentQuestion?.id)] === opt.score }"
            @click="choose(opt.score)"
          >
            {{ opt.text }}
          </button>
        </div>
        
        <!-- 提交按钮 - 只在最后一题完成且未提交时显示 -->
        <div v-if="showSubmitButton && !apiResult" class="submit-section">
          <button 
            class="btn-submit" 
            type="button" 
            @click="submitAnswers"
            :disabled="loading"
          >
            {{ loading ? '提交中...' : '✅ 提交并查看报告' }}
          </button>
        </div>
        
        <div class="action-row">
          <button
            v-if="currentIndex > 0"
            class="btn-secondary"
            type="button"
            @click="previous"
          >
            上一题
          </button>
          <span class="hint">请根据最近一段时间的整体感觉作答。</span>
        </div>
      </div>
    </section>

    <!-- 结果阶段 -->
    <section v-else-if="result" class="block">
      <div class="card">
        <div class="result-badge">测试结果</div>
        <h2 class="result-type">{{ result.type }}{{ result.is_combination ? '（兼夹体质）' : '' }}</h2>
        <p class="result-desc">
          {{ result.feature }}
        </p>

        <div class="result-section">
          <h3>饮食建议</h3>
          <p class="result-text">
            {{ result.diet }}
          </p>
        </div>

        <div class="result-section">
          <h3>推荐食材</h3>
          <div class="chips">
            <span
              v-for="food in result.foods"
              :key="food"
              class="chip"
            >
              {{ food }}
            </span>
          </div>
        </div>

        <div class="result-section">
          <h3>推荐食疗方案</h3>
          <ul class="therapy-list">
            <li
              v-for="name in result.therapies"
              :key="name"
            >
              {{ name }}
            </li>
          </ul>
        </div>

        <div class="result-actions">
          <button class="btn-primary" type="button" @click="showReport = true">
            📄 查看详细报告
          </button>
          <button class="btn-secondary" type="button" @click="restart">
            🔄 重新测试
          </button>
        </div>
      </div>
    </section>

    <!-- 详细报告弹窗 -->
    <div v-if="showReport && result" class="report-modal" @click.self="showReport = false">
      <div class="report-content">
        <button class="report-close" @click="showReport = false">×</button>
        
        <div class="report-header">
          <h2 class="report-title">📋 体质测试报告</h2>
          <div class="report-date">{{ new Date().toLocaleDateString('zh-CN') }}</div>
        </div>

        <div class="report-main">
          <!-- 体质类型卡片 -->
          <div class="constitution-card">
            <div class="constitution-icon">🌿</div>
            <div class="constitution-info">
              <h3 class="constitution-name">{{ result.type }}</h3>
              <p class="constitution-desc">{{ result.description }}</p>
            </div>
          </div>

          <!-- 体质特征 -->
          <section class="report-section">
            <h4 class="section-title">
              <span class="title-icon">✨</span>
              体质特征
            </h4>
            <p class="section-content highlight">{{ result.feature }}</p>
          </section>

          <!-- 饮食建议 -->
          <section class="report-section">
            <h4 class="section-title">
              <span class="title-icon">🍲</span>
              饮食调理建议
            </h4>
            <p class="section-content">{{ result.diet }}</p>
          </section>

          <!-- 推荐食材 -->
          <section class="report-section">
            <h4 class="section-title">
              <span class="title-icon">🥬</span>
              推荐食材
            </h4>
            <div class="food-tags">
              <span 
                v-for="(food, index) in result.foods" 
                :key="index"
                class="food-tag"
              >
                {{ food }}
              </span>
            </div>
          </section>

          <!-- 推荐食疗方 -->
          <section class="report-section">
            <h4 class="section-title">
              <span class="title-icon">👨‍🍳</span>
              推荐食疗方案
            </h4>
            <div class="therapy-cards">
              <div 
                v-for="(therapy, index) in result.therapies" 
                :key="index"
                class="therapy-item"
              >
                <span class="therapy-icon">✓</span>
                <span class="therapy-name">{{ therapy }}</span>
              </div>
            </div>
          </section>

          <!-- 九维体质得分雷达图 -->
          <section v-if="result.scores" class="report-section radar-report">
            <h4 class="section-title">
              <span class="title-icon">📊</span>
              体质辨识指标
            </h4>
            
            <div class="radar-chart-container">
              <svg viewBox="0 0 300 300" class="radar-svg">
                <!-- 背景多边形网格 -->
                <polygon 
                  v-for="(grid, i) in radarGrids" 
                  :key="'grid-'+i"
                  :points="grid"
                  class="radar-grid-line"
                  fill="none"
                  stroke="#e8e8e8"
                  stroke-width="1"
                />
                
                <!-- 轴线 -->
                <line 
                  v-for="(label, i) in radarLabels" 
                  :key="'axis-'+i"
                  x1="150" y1="150" 
                  :x2="150 + Math.cos((Math.PI * 2 / 9) * i - Math.PI / 2) * 100" 
                  :y2="150 + Math.sin((Math.PI * 2 / 9) * i - Math.PI / 2) * 100"
                  stroke="#e8e8e8"
                  stroke-width="1"
                  stroke-dasharray="2,2"
                />
                
                <!-- 得分区域 -->
                <polygon 
                  :points="radarPoints" 
                  class="radar-area" 
                />

                <!-- 各维度标签 -->
                <text 
                  v-for="(label, i) in radarLabels" 
                  :key="'label-'+i"
                  :x="label.x" 
                  :y="label.y" 
                  text-anchor="middle"
                  dominant-baseline="middle"
                  class="radar-label-text"
                >
                  {{ label.name }}
                </text>
              </svg>
            </div>

            <!-- 数据明细 -->
            <div class="scores-grid-mini">
              <div 
                v-for="(score, key) in result.scores" 
                :key="key"
                class="score-mini-item"
                :class="{ 'high': score >= 40 }"
              >
                <div class="mini-label">{{ key.replace('体质', '') }}</div>
                <div class="mini-value">{{ Math.round(score) }}分</div>
              </div>
            </div>
          </section>

          <!-- 用户基本信息 -->
          <section class="report-section">
            <h4 class="section-title">
              <span class="title-icon">👤</span>
              基本信息
            </h4>
            <div class="user-info-grid">
              <div class="info-row">
                <span class="info-label">性别：</span>
                <span class="info-value">{{ userInfo.gender || '-' }}</span>
              </div>
              <div class="info-row">
                <span class="info-label">年龄：</span>
                <span class="info-value">{{ userInfo.age || '-' }}岁</span>
              </div>
              <div class="info-row">
                <span class="info-label">身高：</span>
                <span class="info-value">{{ userInfo.height || '-' }}cm</span>
              </div>
              <div class="info-row">
                <span class="info-label">体重：</span>
                <span class="info-value">{{ userInfo.weight || '-' }}kg</span>
              </div>
              <div class="info-row">
                <span class="info-label">BMI：</span>
                <span class="info-value">{{ calculateBMI() }}</span>
              </div>
            </div>
          </section>
        </div>

        <div class="report-footer">
          <button class="btn-save" @click="saveAndClose">
            ✓ 已保存到健康档案
          </button>
          <button class="btn-download" @click="downloadReport">
            📥 下载报告
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.page-constitution {
  background: var(--bg);
}

/* 页面头部毛玻璃效果 */
.page-header {
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  background: rgba(250, 249, 247, 0.95);
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  background: transparent;
  position: sticky;
  top: 0;
  z-index: 100;
}

.back-btn {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  border: none;
  background: #ffffff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #333;
}

.back-btn:active {
  transform: scale(0.95);
  background: #f8f9fa;
}

.back-btn svg {
  width: 22px;
  height: 22px;
}

.page-title {
  font-size: 20px;
  font-weight: 700;
  color: #1a1a1a;
  margin: 0;
  letter-spacing: -0.3px;
}

.header-placeholder {
  width: 40px;
}

.block {
  margin-bottom: 24px;
}

.card {
  background: var(--bg-card);
  border-radius: 16px;
  padding: 18px 16px 16px;
  box-shadow: var(--shadow);
}

.card-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.card-subtitle {
  font-size: 12px;
  color: var(--text-muted);
}

.card-step {
  font-size: 12px;
  color: var(--primary-dark);
}

.progress-wrap {
  margin-bottom: 12px;
}

.progress-bar {
  width: 100%;
  height: 6px;
  border-radius: 999px;
  background: #f0f0f0;
  overflow: hidden;
}

.progress-inner {
  height: 100%;
  background: linear-gradient(90deg, var(--primary), #f2994a);
}

.question-text {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-h);
  margin: 12px 0 18px;
  letter-spacing: -0.3px;
  line-height: 1.4;
}

.option-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 10px;
}

.option-btn {
  width: 100%;
  padding: 20px 22px;
  border-radius: var(--radius);
  border: 1px solid var(--border);
  background: var(--bg-card);
  font-size: 15px;
  color: var(--text-h);
  text-align: left;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
  position: relative;
  overflow: hidden;
  box-shadow: var(--shadow-sm);
}

.option-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, var(--primary-light) 0%, var(--bg-subtle) 100%);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.option-btn:active::before {
  opacity: 1;
}

.option-btn:active {
  transform: scale(0.98);
  border-color: var(--primary);
}

.option-btn.selected {
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
  border-color: transparent;
  color: #fff;
  font-weight: 600;
  box-shadow: 0 6px 20px rgba(125, 157, 138, 0.35), 0 0 0 4px var(--primary-light);
  transform: translateY(-2px);
}

.option-btn.selected::after {
  content: '✓';
  position: absolute;
  right: 16px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 18px;
  font-weight: bold;
  color: #fff;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.15);
}

.action-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 10px;
}

.btn-secondary {
  padding: 10px 20px;
  border-radius: var(--radius);
  border: 2px solid var(--border);
  background: var(--bg-card);
  font-size: 14px;
  font-weight: 500;
  color: var(--text-h);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.04);
}

.btn-secondary:active {
  transform: scale(0.98);
  background: var(--bg-subtle);
  border-color: var(--primary);
}

.hint {
  font-size: 12px;
  color: var(--text-muted);
  margin: 0;
}

.result-badge {
  display: inline-flex;
  padding: 4px 10px;
  border-radius: 999px;
  background: rgba(180, 64, 64, 0.08);
  color: #b44040;
  font-size: 12px;
  margin-bottom: 8px;
}

.result-type {
  margin: 0 0 6px;
  font-size: 20px;
  font-weight: 600;
  color: var(--text-h);
}

.result-desc {
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.6;
  margin: 0 0 12px;
}

.result-section {
  margin-bottom: 12px;
}

.result-section h3 {
  margin: 0 0 6px;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-h);
}

.result-text {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.6;
  margin: 0;
}

.chips {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.chip {
  padding: 4px 10px;
  border-radius: 999px;
  background: var(--primary-light);
  color: var(--primary-dark);
  font-size: 12px;
}

.therapy-list {
  margin: 0;
  padding-left: 18px;
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.6;
}

.btn-primary {
  margin-top: 8px;
  width: 100%;
  height: 48px;
  border-radius: 12px;
  border: none;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  font-size: 16px;
  font-weight: 600;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
  transition: all 0.2s ease;
}

.btn-primary:active {
  transform: scale(0.98);
}

/* 用户信息表单样式 */
.form-desc {
  font-size: 14px;
  color: var(--text-secondary);
  margin: 0 0 16px;
  line-height: 1.5;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-h);
  margin-bottom: 8px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.form-input {
  width: 100%;
  padding: 12px 16px;
  border: 2px solid #e4e4e4;
  border-radius: 12px;
  font-size: 15px;
  color: var(--text-h);
  background: #fff;
  transition: all 0.2s ease;
  box-sizing: border-box;
}

.form-input:focus {
  outline: none;
  border-color: #667eea;
}

.form-input::placeholder {
  color: #999;
}

.gender-options {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.gender-btn {
  padding: 14px 16px;
  border: 2px solid #e4e4e4;
  border-radius: 12px;
  background: #fff;
  font-size: 15px;
  color: var(--text-h);
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

.gender-btn:active {
  transform: scale(0.98);
}

.gender-btn.selected {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-color: transparent;
  color: #fff;
  font-weight: 600;
}

.gender-icon {
  font-size: 18px;
}

/* 报告弹窗样式 */
.report-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  padding: 20px;
  overflow-y: auto;
  backdrop-filter: blur(4px);
}

.report-content {
  background: #ffffff;
  border-radius: 20px;
  width: 100%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
  position: relative;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  animation: slideUp 0.3s ease;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.report-close {
  position: absolute;
  top: 16px;
  right: 16px;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.95);
  border: none;
  font-size: 28px;
  color: #666;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  z-index: 10;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.report-close:hover {
  background: #f5f5f5;
  color: #333;
  transform: rotate(90deg);
}

.report-header {
  padding: 24px 24px 20px;
  border-bottom: 2px solid #f0f0f0;
  background: linear-gradient(135deg, rgba(26, 163, 157, 0.05) 0%, rgba(39, 179, 168, 0.05) 100%);
  border-radius: 20px 20px 0 0;
}

.report-title {
  font-size: 24px;
  font-weight: 700;
  color: #1a1a1a;
  margin: 0 0 8px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.report-date {
  font-size: 13px;
  color: #999;
}

.report-main {
  padding: 24px;
}

/* 体质类型卡片 */
.constitution-card {
  display: flex;
  gap: 16px;
  padding: 20px;
  background: linear-gradient(135deg, rgba(26, 163, 157, 0.1) 0%, rgba(39, 179, 168, 0.1) 100%);
  border-radius: 16px;
  border: 2px solid rgba(26, 163, 157, 0.2);
  margin-bottom: 24px;
}

.constitution-icon {
  font-size: 48px;
  flex-shrink: 0;
}

.constitution-info {
  flex: 1;
}

.constitution-name {
  font-size: 22px;
  font-weight: 700;
  color: #1a1a1a;
  margin: 0 0 8px;
}

.constitution-desc {
  font-size: 14px;
  line-height: 1.6;
  color: #555;
  margin: 0;
}

/* 报告区块 */
.report-section {
  margin-bottom: 24px;
  padding-bottom: 24px;
  border-bottom: 1px solid #f0f0f0;
}

.report-section:last-child {
  border-bottom: none;
  margin-bottom: 0;
  padding-bottom: 0;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 700;
  color: #1a1a1a;
  margin: 0 0 12px;
}

.title-icon {
  font-size: 20px;
}

.section-content {
  font-size: 14px;
  line-height: 1.7;
  color: #555;
  margin: 0;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 8px;
  border-left: 3px solid #1aa39d;
}

.section-content.highlight {
  background: linear-gradient(135deg, rgba(26, 163, 157, 0.08) 0%, rgba(39, 179, 168, 0.08) 100%);
  border-left-color: #27b3a8;
  font-weight: 500;
}

/* 食材标签 */
.food-tags {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
  gap: 10px;
}

.food-tag {
  padding: 10px 14px;
  background: linear-gradient(135deg, rgba(52, 199, 89, 0.1) 0%, rgba(48, 209, 88, 0.1) 100%);
  border-radius: 10px;
  font-size: 13px;
  font-weight: 600;
  color: #34c759;
  text-align: center;
  border: 1px solid rgba(52, 199, 89, 0.2);
  transition: all 0.2s ease;
}

.food-tag:active {
  transform: scale(0.96);
}

/* 食疗方案 */
.therapy-cards {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.therapy-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px;
  background: #f8f9fa;
  border-radius: 10px;
  border: 1px solid #e8e8e8;
}

.therapy-icon {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #1aa39d;
  font-size: 18px;
  font-weight: 700;
}

.therapy-name {
  font-size: 14px;
  font-weight: 600;
  color: #333;
}

/* 雷达图样式 */
.radar-chart-container {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px 0;
  margin: 0 auto;
  max-width: 320px;
}

.radar-svg {
  width: 100%;
  height: auto;
  overflow: visible;
}

.radar-grid-line {
  fill: none;
  stroke: #eee;
  stroke-width: 1;
}

.radar-axis {
  stroke: #eee;
  stroke-width: 1;
  stroke-dasharray: 2,2;
}

.radar-area {
  fill: rgba(26, 163, 157, 0.25);
  stroke: #1aa39d;
  stroke-width: 2.5;
  stroke-linejoin: round;
  transition: all 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}

.radar-label-text {
  font-size: 12px;
  font-weight: 600;
  fill: #666;
  text-shadow: 0 0 2px #fff;
}

/* 迷你得分网格 */
.scores-grid-mini {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
  margin-top: 20px;
}

.score-mini-item {
  padding: 10px 8px;
  background: #f8f9fa;
  border-radius: 10px;
  text-align: center;
  border: 1px solid #f0f0f0;
  transition: all 0.2s ease;
}

.score-mini-item.high {
  background: rgba(26, 163, 157, 0.05);
  border-color: rgba(26, 163, 157, 0.2);
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.03);
}

.mini-label {
  font-size: 11px;
  color: #999;
  margin-bottom: 4px;
}

.mini-value {
  font-size: 14px;
  font-weight: 700;
  color: #333;
}

.score-mini-item.high .mini-value {
  color: #1aa39d;
}

/* 用户信息网格 */
.user-info-grid {
  display: grid;
  gap: 12px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  padding: 10px 12px;
  background: #f8f9fa;
  border-radius: 8px;
}

.info-label {
  font-size: 13px;
  color: #666;
  font-weight: 500;
}

.info-value {
  font-size: 13px;
  color: #333;
  font-weight: 600;
}

/* 报告底部按钮 */
.report-footer {
  display: flex;
  gap: 12px;
  padding: 20px 24px 24px;
  border-top: 1px solid #f0f0f0;
  background: #f8f9fa;
  border-radius: 0 0 20px 20px;
}

.btn-save {
  flex: 1;
  height: 48px;
  border-radius: 12px;
  border: none;
  background: linear-gradient(135deg, #1aa39d 0%, #27b3a8 100%);
  color: #ffffff;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 4px 12px rgba(26, 163, 157, 0.3);
}

.btn-save:active {
  transform: scale(0.96);
  box-shadow: 0 2px 8px rgba(26, 163, 157, 0.4);
}

.btn-download {
  flex: 1;
  height: 48px;
  border-radius: 12px;
  border: 2px solid #1aa39d;
  background: #ffffff;
  color: #1aa39d;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-download:active {
  transform: scale(0.96);
  background: #f0fdfa;
}

/* 提交按钮样式 */
.submit-section {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 2px solid #f0f0f0;
}

.btn-submit {
  width: 100%;
  padding: 16px;
  border-radius: 12px;
  border: none;
  background: linear-gradient(135deg, #1aa39d 0%, #27b3a8 100%);
  color: #ffffff;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 6px 16px rgba(26, 163, 157, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.btn-submit:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(26, 163, 157, 0.4);
}

.btn-submit:active:not(:disabled) {
  transform: scale(0.98) translateY(0);
  box-shadow: 0 4px 12px rgba(26, 163, 157, 0.3);
}

.btn-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  background: linear-gradient(135deg, #999 0%, #bbb 100%);
}
</style>

