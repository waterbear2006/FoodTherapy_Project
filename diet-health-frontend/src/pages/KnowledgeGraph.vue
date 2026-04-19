<script setup>
import { nextTick, onBeforeUnmount, onMounted, ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import * as echarts from 'echarts'
import { getIngredientList } from '@/api/mock'

const router = useRouter()
const chartRef = ref(null)
const loading = ref(false)
const relationMode = ref('sheng')
const activeNode = ref(null)
const ingredientDetails = ref({})
const dataSourceText = ref('数据源：后端接口 /api/search/ingredients（CSV + 内存检索结构）')

// 答题模式相关
const quizMode = ref(false)
const quizIngredients = ref([])
const matchedPairs = ref([])
const wrongTags = ref([])
const quizComplete = ref(false)
const quizScore = ref(0)
const draggingIngredient = ref(null)
const dragOffset = ref({ x: 0, y: 0 })
const draggedElement = ref(null)

let chartInstance = null

// 五行渐变色和发光效果
const elementGradientColorMap = {
  木: new echarts.graphic.LinearGradient(0, 0, 1, 1, [
    { offset: 0, color: '#a8e063' }, // 浅绿
    { offset: 1, color: '#56ab2f' }  // 深绿
  ]),
  火: new echarts.graphic.LinearGradient(0, 0, 1, 1, [
    { offset: 0, color: '#ff7e5f' }, // 橙红
    { offset: 1, color: '#feb47b' }  // 浅橙
  ]),
  土: new echarts.graphic.LinearGradient(0, 0, 1, 1, [
    { offset: 0, color: '#f7d794' }, // 浅黄
    { offset: 1, color: '#e6b34b' }  // 金棕
  ]),
  金: new echarts.graphic.LinearGradient(0, 0, 1, 1, [
    { offset: 0, color: '#e0e0e0' }, // 浅灰
    { offset: 1, color: '#bdbdbd' }  // 中灰
  ]),
  水: new echarts.graphic.LinearGradient(0, 0, 1, 1, [
    { offset: 0, color: '#4facfe' }, // 浅蓝
    { offset: 1, color: '#00f2fe' }  // 青色
  ])
}

// 五脏莫兰迪色系
const organMorandiColorMap = {
  肝: '#9DC8C8', // 莫兰迪绿
  心: '#E0BBE4', // 莫兰迪粉
  脾: '#FEE1C7', // 莫兰迪黄
  肺: '#C9CCD5', // 莫兰迪灰
  肾: '#A2B9BC'  // 莫兰迪蓝
}

const organEmojiMap = {
  肝: '🌿',
  心: '❤️',
  脾: '🌾',
  肺: '🫁',
  肾: '💧'
}

const elementColorMap = {
  木: '#2E8B57',
  火: '#D94A38',
  土: '#C9A227',
  金: '#F0F0F0',
  水: '#2F2F2F'
}

const elementToOrgan = {
  木: '肝',
  火: '心',
  土: '脾',
  金: '肺',
  水: '肾'
}

const ingredientToOrgan = {
  // 脾（土）
  山药: '脾',
  莲子: '脾',
  薏米: '脾',
  红枣: '脾',
  茯苓: '脾',
  白术: '脾',
  扁豆: '脾',
  小米: '脾',
  南瓜: '脾',
  糯米: '脾',
  // 肝（木）
  枸杞: '肝',
  菊花: '肝',
  决明子: '肝',
  桑葚: '肝',
  菠菜: '肝',
  芹菜: '肝',
  猪肝: '肝',
  当归: '肝',
  白芍: '肝',
  柴胡: '肝',
  // 肺（金）
  黄芪: '肺',
  百合: '肺',
  银耳: '肺',
  梨: '肺',
  白萝卜: '肺',
  杏仁: '肺',
  麦冬: '肺',
  沙参: '肺',
  川贝: '肺',
  蜂蜜: '肺',
  // 肾（水）
  黑豆: '肾',
  黑芝麻: '肾',
  核桃: '肾',
  枸杞子: '肾',
  杜仲: '肾',
  熟地黄: '肾',
  山药: '肾',
  栗子: '肾',
  海参: '肾',
  韭菜: '肾',
  // 心（火）
  桂圆: '心',
  莲子心: '心',
  酸枣仁: '心',
  丹参: '心',
  远志: '心',
  柏子仁: '心',
  小麦: '心',
  百合: '心',
  龙眼肉: '心',
  朱砂: '心'
}

const generationPairs = [['木', '火'], ['火', '土'], ['土', '金'], ['金', '水'], ['水', '木']]
const controlPairs = [['木', '土'], ['土', '水'], ['水', '火'], ['火', '金'], ['金', '木']]
const categories = [{ name: '五行' }, { name: '五脏' }, { name: '食材' }]
const elementFixedPosition = {
  木: { x: 240, y: 90 },
  火: { x: 330, y: 180 },
  土: { x: 275, y: 300 },
  金: { x: 145, y: 300 },
  水: { x: 90, y: 180 }
}

function escapeHtml(value = '') {
  return String(value)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#39;')
}

function buildNodes(ingredients) {
  const elementNodes = Object.keys(elementToOrgan).map((name) => ({
    id: `element:${name}`,
    name,
    category: 0,
    symbolSize: 76,
    fixed: true,
    x: elementFixedPosition[name].x,
    y: elementFixedPosition[name].y,
    value: 120,
    nodeType: '五行',
    meridian: '-',
    efficacy: `${name}行核心节点`,
    suitable: '全部体质',
    itemStyle: {
      color: elementGradientColorMap[name],
      shadowBlur: 10,
      shadowColor: 'rgba(0, 0, 0, 0.3)',
      shadowOffsetX: 0,
      shadowOffsetY: 0
    }
  }))
  const organNodes = Object.values(elementToOrgan).map((name) => ({
    id: `organ:${name}`,
    name,
    category: 1,
    symbolSize: 48,
    value: 70,
    nodeType: '五脏',
    meridian: `${name}经`,
    efficacy: `与${name}相关调理`,
    suitable: '相关体质人群',
    itemStyle: { color: organMorandiColorMap[name] }
  }))
  const ingredientNodes = ingredients.map((name) => ({
    id: `ingredient:${name}`,
    name,
    category: 2,
    symbolSize: 34,
    symbol: 'diamond',
    value: 40,
    nodeType: '食材',
    meridian: ingredientToOrgan[name] ? `${ingredientToOrgan[name]}经` : '未知',
    efficacy: ingredientDetails.value[name]?.effect || '暂无功效描述',
    suitable: ingredientDetails.value[name]?.suitable || '暂无适宜体质信息',
    itemStyle: { color: '#6CA6CD' }
  }))
  return [...elementNodes, ...organNodes, ...ingredientNodes]
}

function buildLinks(ingredients) {
  const linksA = Object.entries(elementToOrgan).map(([element, organ]) => ({
    source: `element:${element}`,
    target: `organ:${organ}`,
    label: { show: true, formatter: '对应', fontSize: 10 },
    lineStyle: { color: '#9CB7A6', width: 2.2 }
  }))
  const linksB = ingredients
    .filter((name) => ingredientToOrgan[name])
    .map((name) => ({
      source: `ingredient:${name}`,
      target: `organ:${ingredientToOrgan[name]}`,
      label: { show: true, formatter: '归经', fontSize: 10 },
      lineStyle: { color: '#82AEE2', width: 1.8, type: 'dashed' }
    }))

  const relationText = relationMode.value === 'sheng' ? '相生' : '相克'
  const pairs = relationMode.value === 'sheng' ? generationPairs : controlPairs
  const linksC = pairs.map(([source, target]) => ({
    source: `element:${source}`,
    target: `element:${target}`,
    label: { show: true, formatter: relationText, fontSize: 10 },
    lineStyle: {
      color: relationMode.value === 'sheng' ? '#5E9F6F' : '#D07B6A',
      width: 2.6,
      curveness: 0.3
    }
  }))
  return [...linksA, ...linksB, ...linksC]
}

function buildOption(nodes, links) {
  return {
    title: { text: '五行食疗知识图谱', left: 'center', top: 6, textStyle: { fontSize: 16 } },
    tooltip: {
      trigger: 'item',
      backgroundColor: 'transparent',
      borderWidth: 0,
      padding: 0,
      extraCssText: 'box-shadow:none;',
      formatter: (params) => {
        if (params.dataType !== 'node') return ''
        const node = params.data || {}
        if (node.category !== 2) return `${node.name}`
        const tagColor = '#4f8aa9'
        return `
          <div style="
            min-width:220px;
            max-width:280px;
            background:linear-gradient(145deg,#ffffff 0%,#f4faf8 100%);
            border:1px solid #d9e8e2;
            border-radius:12px;
            box-shadow:0 8px 24px rgba(46,75,67,.18);
            padding:12px 14px;
            color:#2d2d2d;
          ">
            <div style="font-size:18px;font-weight:800;line-height:1.2;margin-bottom:8px;">
              ${escapeHtml(node.name)}
            </div>
            <div style="display:inline-block;background:${tagColor};color:#fff;border-radius:999px;padding:3px 10px;font-size:12px;margin-bottom:10px;">
              ${escapeHtml(node.nodeType || '食材')}
            </div>
            <div style="font-size:13px;line-height:1.6;">
              <div><strong>归经：</strong>${escapeHtml(node.meridian || '-')}</div>
              <div><strong>功效：</strong>${escapeHtml(node.efficacy || '暂无')}</div>
              <div><strong>适宜体质：</strong>${escapeHtml(node.suitable || '暂无')}</div>
            </div>
          </div>
        `
      }
    },
    legend: [{ bottom: 6, data: ['五行', '五脏', '食材'] }],
    series: [
      {
        type: 'graph',
        layout: 'force',
        data: nodes,
        links,
        categories,
        roam: true,
        draggable: true,
        label: {
          show: true,
          position: 'right',
          color: '#2d2d2d'
        },
        force: {
          repulsion: 340,
          edgeLength: [90, 170],
          gravity: 0.16,
          friction: 0.18
        },
        lineStyle: {
          opacity: 0.95,
          curveness: 0.3
        },
        emphasis: {
          focus: 'adjacency',
          lineStyle: { width: 4 }
        }
      }
    ]
  }
}

async function getIngredientSeed() {
  const list = await getIngredientList('全部', '')
  const picked = []
  for (const item of list) {
    ingredientDetails.value[item.name] = {
      effect: item.effect || '暂无功效描述',
      suitable: item.suitable || '暂无适宜人群信息'
    }
    if (ingredientToOrgan[item.name] && !picked.includes(item.name)) picked.push(item.name)
    if (picked.length >= 10) break
  }
  return picked.length > 0 ? picked : Object.keys(ingredientToOrgan).slice(0, 8)
}

function bindClickEvent() {
  chartInstance.off('click')
  chartInstance.on('click', (params) => {
    if (params.dataType !== 'node') return
    const node = params.data
    if (node.category === 2) {
      const detail = ingredientDetails.value[node.name] || {}
      activeNode.value = {
        name: node.name,
        type: '食材',
        desc: `归经：${ingredientToOrgan[node.name] || '未知'}；功效：${detail.effect || '暂无'}；适宜：${detail.suitable || '暂无'}`
      }
      return
    }
    if (node.category === 1) {
      activeNode.value = {
        name: node.name,
        type: '五脏',
        desc: `五脏节点：${node.name}。可查看与其关联的五行与食材归经关系。`
      }
      return
    }
    activeNode.value = {
      name: node.name,
      type: '五行',
      desc: `当前展示：${relationMode.value === 'sheng' ? '相生' : '相克'}关系。`
    }
  })
}

async function renderGraph() {
  loading.value = true
  try {
    const ingredients = await getIngredientSeed()
    const nodes = buildNodes(ingredients)
    const links = buildLinks(ingredients)
    if (!chartInstance && chartRef.value) {
      chartInstance = echarts.init(chartRef.value)
    }
    chartInstance.setOption(buildOption(nodes, links), true)
    bindClickEvent()
  } finally {
    loading.value = false
  }
}

async function changeMode(mode) {
  if (relationMode.value === mode) return
  relationMode.value = mode
  await renderGraph()
}

// ===== 答题模式功能 =====

// 开始答题模式
function startQuizMode() {
  quizMode.value = true
  quizComplete.value = false
  matchedPairs.value = []
  wrongTags.value = []
  quizScore.value = 0
  
  // 随机选择10个食材
  const allIngredients = Object.keys(ingredientToOrgan)
  const shuffled = [...allIngredients].sort(() => Math.random() - 0.5)
  quizIngredients.value = shuffled.slice(0, 10)
  
  // 隐藏图表中的食材节点
  if (chartInstance) {
    const option = chartInstance.getOption()
    const series = option.series[0]
    if (series && series.data) {
      series.data.forEach(node => {
        if (node.category === 2) {
          node.symbolSize = 0
          node.label = { show: false }
        }
      })
      chartInstance.setOption({ series: [series] })
    }
  }
}

// 退出答题模式
function exitQuizMode() {
  quizMode.value = false
  quizComplete.value = false
  matchedPairs.value = []
  wrongTags.value = []
  
  // 恢复图表
  renderGraph()
}

// 开始拖拽食材
function startDrag(ingredient, event) {
  draggingIngredient.value = ingredient
  event.dataTransfer.setData('text/plain', ingredient)
  event.dataTransfer.effectAllowed = 'move'
}

// 处理放置
function handleDrop(event, organ) {
  event.preventDefault()
  const ingredient = event.dataTransfer.getData('text/plain')
  if (!ingredient) return
  
  checkMatch(ingredient, organ, event.currentTarget)
}

// 检查匹配
function checkMatch(ingredient, organ, organCard) {
  const correctOrgan = ingredientToOrgan[ingredient]
  
  if (correctOrgan === organ) {
    // 匹配成功
    matchedPairs.value.push({ ingredient, organ })
    quizScore.value += 10
    
    // 从列表中移除该食材
    quizIngredients.value = quizIngredients.value.filter(i => i !== ingredient)
    
    // 在器官卡片上显示已匹配的食材
    const matchedList = organCard.querySelector('.matched-list')
    if (matchedList) {
      const tag = document.createElement('span')
      tag.className = 'matched-tag'
      tag.textContent = ingredient
      matchedList.appendChild(tag)
    }
    
    // 检查是否全部完成
    if (quizIngredients.value.length === 0) {
      quizComplete.value = true
    }
  } else {
    // 匹配失败
    wrongTags.value.push(ingredient)
    setTimeout(() => {
      wrongTags.value = wrongTags.value.filter(i => i !== ingredient)
    }, 1500)
  }
}

function handleResize() {
  if (chartInstance) chartInstance.resize()
}

onMounted(async () => {
  await nextTick()
  await renderGraph()
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  if (chartInstance) {
    chartInstance.dispose()
    chartInstance = null
  }
})
</script>

<template>
  <div class="page-graph app-page">
    <header class="page-header">
      <button class="back-btn" type="button" @click="router.back()">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M19 12H5M12 19l-7-7 7-7"/>
        </svg>
      </button>
      <h1 class="page-title">五行食疗知识图谱</h1>
      <span class="header-placeholder"></span>
    </header>

    <section class="toolbar">
      <button :class="['mode-btn', relationMode === 'sheng' ? 'active' : '']" @click="changeMode('sheng')" :disabled="quizMode">
        显示相生关系
      </button>
      <button :class="['mode-btn', relationMode === 'ke' ? 'active' : '']" @click="changeMode('ke')" :disabled="quizMode">
        显示相克关系
      </button>
      <button :class="['mode-btn', 'quiz-btn', quizMode ? 'active' : '']" @click="quizMode ? exitQuizMode() : startQuizMode()">
        {{ quizMode ? '退出答题' : '答题模式' }}
      </button>
    </section>

    <section class="graph-card" :class="{ 'quiz-active': quizMode }">
      <div v-if="loading" class="loading-text">图谱加载中...</div>
      <div ref="chartRef" class="chart"></div>
      
      <!-- 答题模式：器官放置区域 -->
      <div v-if="quizMode" class="quiz-overlay">
        <div class="quiz-header">
          <h3 class="quiz-title"> 将食材拖放到对应的五脏器官</h3>
          <div class="quiz-progress">
            <span>进度：{{ matchedPairs.length }} / {{ matchedPairs.length + quizIngredients.length }}</span>
            <span>得分：{{ quizScore }}</span>
          </div>
        </div>
        
        <div class="organs-container">
          <div 
            v-for="organ in ['肝', '心', '脾', '肺', '肾']" 
            :key="organ"
            class="organ-drop-zone"
            :data-organ="organ"
            @dragover.prevent
            @drop="handleDrop($event, organ)"
          >
            <div class="organ-icon">{{ organEmojiMap[organ] }}</div>
            <div class="organ-name">{{ organ }}</div>
            <div class="organ-element">（{{ Object.keys(elementToOrgan).find(k => elementToOrgan[k] === organ) }}）</div>
            <div class="matched-list">
              <span 
                v-for="pair in matchedPairs.filter(p => p.organ === organ)" 
                :key="pair.ingredient"
                class="matched-tag"
              >
                {{ pair.ingredient }}
              </span>
            </div>
          </div>
        </div>
        
        <!-- 完成提示 -->
        <div v-if="quizComplete" class="quiz-complete">
          <div class="complete-icon">🎉</div>
          <h3>答题完成！</h3>
          <p>最终得分：{{ quizScore }} 分</p>
          <button class="btn-restart" @click="startQuizMode">再来一轮</button>
        </div>
      </div>
      
      <div v-if="activeNode && !quizMode" class="detail-panel">
        <div class="detail-title">{{ activeNode.name }}</div>
        <div class="detail-tag">{{ activeNode.type }}</div>
        <p class="detail-desc">{{ activeNode.desc }}</p>
      </div>
    </section>
    
    <!-- 答题模式：底部食材标签 -->
    <section v-if="quizMode" class="ingredient-tags-section">
      <h4 class="tags-title">拖动食材到上方对应的器官：</h4>
      <div class="ingredient-tags">
        <div
          v-for="ingredient in quizIngredients"
          :key="ingredient"
          class="ingredient-tag"
          :class="{ 'wrong': wrongTags.includes(ingredient) }"
          draggable="true"
          @dragstart="startDrag(ingredient, $event)"
        >
          {{ ingredient }}
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
.page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px; }
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
.header-placeholder { width: 40px; }
.page-title { font-size: 18px; margin: 0; }

.toolbar { display: flex; gap: 8px; margin-bottom: 10px; }
.mode-btn {
  flex: 1;
  border: 1px solid var(--border);
  border-radius: 10px;
  background: #fff;
  padding: 10px;
  font-size: 13px;
}
.mode-btn.active {
  border-color: var(--primary);
  background: var(--primary-light);
  color: var(--primary-dark);
  font-weight: 600;
}

.graph-card {
  position: relative;
  border: 1px solid var(--border);
  border-radius: 14px;
  background: #fff;
  overflow: hidden;
}

.chart { width: 100%; height: 620px; }
.loading-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: var(--text-muted);
  font-size: 13px;
  z-index: 2;
}

.detail-panel {
  position: absolute;
  right: 12px;
  top: 12px;
  width: 220px;
  background: rgba(255, 255, 255, 0.97);
  border: 1px solid var(--border);
  border-radius: 10px;
  box-shadow: var(--shadow);
  padding: 10px;
}
.detail-title { font-size: 15px; font-weight: 700; color: var(--text-h); }
.detail-tag { font-size: 12px; color: var(--primary-dark); margin: 4px 0 6px; }
.detail-desc { font-size: 12px; line-height: 1.5; color: var(--text-secondary); margin: 0; }

/* 答题模式样式 */
.quiz-btn {
  background: linear-gradient(135deg, rgba(144, 180, 148, 0.85) 0%, rgba(118, 156, 122, 0.85) 100%);
  color: #fff;
  border-color: transparent;
}

.quiz-btn.active {
  background: linear-gradient(135deg, rgba(118, 156, 122, 0.85) 0%, rgba(144, 180, 148, 0.85) 100%);
  box-shadow: 0 4px 15px rgba(118, 156, 122, 0.35);
  color: #fff;
}

.graph-card.quiz-active {
  min-height: 500px;
}

.quiz-overlay {
  position: absolute;
  inset: 0;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
  z-index: 10;
  padding: 20px;
  overflow-y: auto;
}

.quiz-header {
  text-align: center;
  margin-bottom: 20px;
}

.quiz-title {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-h);
  margin: 0 0 10px;
}

.quiz-progress {
  display: flex;
  justify-content: center;
  gap: 20px;
  font-size: 14px;
  color: var(--text-muted);
}

.quiz-progress span {
  background: var(--primary-light);
  padding: 4px 12px;
  border-radius: 999px;
  font-weight: 600;
  color: var(--primary-dark);
}

.organs-container {
  display: flex;
  justify-content: center;
  gap: 16px;
  flex-wrap: wrap;
  margin-bottom: 20px;
}

.organ-drop-zone {
  width: 120px;
  min-height: 140px;
  border: 2px dashed #d0d8d0;
  border-radius: 16px;
  background: #f8faf8;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 12px 8px;
  transition: all 0.3s ease;
  cursor: pointer;
}

.organ-drop-zone:hover,
.organ-drop-zone.drag-over {
  border-color: var(--primary);
  background: var(--primary-light);
  transform: scale(1.05);
}

.organ-icon {
  font-size: 32px;
  margin-bottom: 6px;
}

.organ-name {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-h);
  margin-bottom: 2px;
}

.organ-element {
  font-size: 12px;
  color: var(--text-muted);
  margin-bottom: 8px;
}

.matched-list {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  justify-content: center;
  width: 100%;
}

.matched-tag {
  font-size: 11px;
  background: var(--primary);
  color: #fff;
  padding: 3px 8px;
  border-radius: 999px;
  font-weight: 500;
}

/* 完成提示 */
.quiz-complete {
  text-align: center;
  padding: 30px;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  border-radius: 16px;
  margin-top: 20px;
}

.complete-icon {
  font-size: 48px;
  margin-bottom: 10px;
}

.quiz-complete h3 {
  font-size: 20px;
  font-weight: 700;
  color: var(--text-h);
  margin: 0 0 8px;
}

.quiz-complete p {
  font-size: 16px;
  color: var(--text-muted);
  margin: 0 0 16px;
}

.btn-restart {
  background: var(--primary-dark);
  color: #fff;
  border: none;
  border-radius: 10px;
  padding: 10px 24px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-restart:hover {
  background: var(--primary);
  transform: scale(1.05);
}

/* 底部食材标签区域 */
.ingredient-tags-section {
  background: #fff;
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 16px;
  margin-top: 16px;
}

.tags-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-h);
  margin: 0 0 12px;
  text-align: center;
}

.ingredient-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: center;
}

.ingredient-tag {
  background: linear-gradient(135deg, rgba(144, 180, 148, 0.85) 0%, rgba(118, 156, 122, 0.85) 100%);
  color: #fff;
  padding: 8px 16px;
  border-radius: 999px;
  font-size: 14px;
  font-weight: 600;
  cursor: grab;
  user-select: none;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(118, 156, 122, 0.3);
}

.ingredient-tag:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(118, 156, 122, 0.4);
}

.ingredient-tag:active {
  cursor: grabbing;
  transform: scale(0.95);
}

.ingredient-tag.wrong {
  background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
  animation: shake 0.5s ease-in-out;
  box-shadow: 0 2px 8px rgba(255, 107, 107, 0.4);
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-5px); }
  75% { transform: translateX(5px); }
}
</style>
