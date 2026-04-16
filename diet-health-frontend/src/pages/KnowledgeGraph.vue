<script setup>
import { nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
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

let chartInstance = null

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
  山药: '脾',
  枸杞: '肝',
  黄芪: '肺',
  百合: '肺',
  莲子: '脾',
  黑豆: '肾',
  桂圆: '心',
  薏米: '脾',
  银耳: '肺',
  红枣: '脾'
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
    itemStyle: { color: elementColorMap[name], borderColor: '#777', borderWidth: 1 }
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
    itemStyle: { color: '#7D9D8A' }
  }))
  const ingredientNodes = ingredients.map((name) => ({
    id: `ingredient:${name}`,
    name,
    category: 2,
    symbolSize: 34,
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
      <button :class="['mode-btn', relationMode === 'sheng' ? 'active' : '']" @click="changeMode('sheng')">
        显示相生关系
      </button>
      <button :class="['mode-btn', relationMode === 'ke' ? 'active' : '']" @click="changeMode('ke')">
        显示相克关系
      </button>
    </section>

    <section class="graph-card">
      <div v-if="loading" class="loading-text">图谱加载中...</div>
      <div ref="chartRef" class="chart"></div>
      <div v-if="activeNode" class="detail-panel">
        <div class="detail-title">{{ activeNode.name }}</div>
        <div class="detail-tag">{{ activeNode.type }}</div>
        <p class="detail-desc">{{ activeNode.desc }}</p>
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
</style>
