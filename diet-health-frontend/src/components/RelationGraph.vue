<script setup>
import { ref, onMounted, watch, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import axios from 'axios'
import { showToast } from 'vant'

const props = defineProps({
  centerNode: { type: String, required: true },
  height: { type: String, default: '560px' }
})

const emit = defineEmits(['nodeClick'])

const chartRef = ref(null)
let chartInstance = null
const loading = ref(false)

// 【单例模式】核心状态：只有一个弹窗，一个数据源
const showPopup = ref(false)
const popupData = ref(null) // { type: 'node'|'edge', data: any }

// 全局节点和连线缓存
const allNodes = ref([])
const allLinks = ref([])
const categories = ref([])

// Apple Color Hierarchy
const roleColors = {
  "Jun": "rgba(201, 72, 72, 0.9)",
  "Chen": "rgba(142, 151, 117, 0.8)",
  "Zuo": "rgba(220, 220, 220, 0.7)",
  "Shi": "rgba(220, 220, 220, 0.6)",
  "default": "rgba(70, 130, 180, 0.8)"
}

const getRoleCN = (role) => {
  const map = { "Jun": "君", "Chen": "臣", "Zuo": "佐", "Shi": "使" }
  return map[role] || ""
}

const getRoleFullCN = (role) => {
  const map = { "Jun": "君药 (Monarch)", "Chen": "臣药 (Minister)", "Zuo": "佐药 (Assistant)", "Shi": "使药 (Envoy)" }
  return map[role] || "配伍成分"
}

const loadGraphData = async (nodeName, isIncremental = false) => {
  loading.value = true
  try {
    const response = await axios.get(`/api/graph/detail?name=${encodeURIComponent(nodeName)}&depth=1`)
    const { nodes, links, categories: cats } = response.data
    categories.value = cats

    if (!isIncremental) {
      allNodes.value = nodes
      allLinks.value = links
    } else {
      const existingIds = new Set(allNodes.value.map(n => n.id))
      nodes.forEach(node => { if (!existingIds.has(node.id)) allNodes.value.push(node) })
      const existingLinks = new Set(allLinks.value.map(l => `${l.source}-${l.target}`))
      links.forEach(link => {
        const key = `${link.source}-${link.target}`
        if (!existingLinks.has(key)) allLinks.value.push(link)
      })
    }
    updateChart()
  } catch (error) {
    console.error('Graph Error:', error)
    showToast('知识库连接中断')
  } finally {
    loading.value = false
  }
}

const updateChart = () => {
  if (!chartInstance) return
  const nodes = allNodes.value.map(node => {
    const role = node.role
    let size = 30, color = roleColors.default
    if (role === 'Jun') { size = 70; color = roleColors.Jun }
    else if (role === 'Chen') { size = 45; color = roleColors.Chen }
    else if (role === 'Zuo' || role === 'Shi') { size = 25; color = roleColors.Zuo }
    else if (node.id === props.centerNode) { size = 50; color = roleColors.Jun }

    const isCenterOrJun = role === 'Jun' || node.id === props.centerNode
    return {
      ...node,
      symbolSize: size,
      draggable: true,
      itemStyle: {
        color: color,
        borderColor: role === 'Jun' ? 'rgba(251, 235, 235, 0.8)' : '#fff', 
        borderWidth: role === 'Jun' ? 8 : 1.5,
        shadowBlur: role === 'Jun' ? 40 : 15,
        shadowColor: role === 'Jun' ? 'rgba(201, 72, 72, 0.3)' : 'rgba(0,0,0,0.1)',
        cursor: 'pointer'
      },
      label: {
        show: true, position: 'bottom', distance: 14,
        color: isCenterOrJun ? '#1D1D1F' : 'transparent',
        backgroundColor: isCenterOrJun ? 'rgba(255,255,255,0.85)' : 'transparent',
        fontSize: role === 'Jun' ? 14 : 12, fontWeight: '700', padding: [4, 10], borderRadius: 8
      }
    }
  })

  const links = allLinks.value.map(link => {
    const roleCN = getRoleCN(link.role)
    return {
      ...link,
      lineStyle: { width: link.role === 'Jun' ? 3 : 1.2, color: link.role === 'Jun' ? roleColors.Jun : '#D1D1D6', type: link.role === 'Jun' ? 'solid' : 'dashed', curveness: 0.2 },
      label: { show: !!roleCN, formatter: roleCN, fontSize: 10, color: '#8E8E93', backgroundColor: '#F2F2F7', padding: [2, 4], borderRadius: 2 }
    }
  })

  chartInstance.setOption({
    backgroundColor: '#F5F5F7',
    series: [{
      type: 'graph', layout: 'force', data: nodes, links: links, categories: categories.value,
      roam: true, draggable: true,
      force: { repulsion: 2500, gravity: 0.03, edgeLength: [40, 100] },
      emphasis: { focus: 'adjacency', label: { show: true, fontSize: 15, fontWeight: '700', color: '#1D1D1F', backgroundColor: 'rgba(255,255,255,0.95)', padding: [6, 12], borderRadius: 10 } }
    }]
  })
}

const initChart = () => {
  if (chartRef.value) {
    chartInstance = echarts.init(chartRef.value)
    chartInstance.on('click', async (params) => {
      // 【强制隔离】阻止逻辑冒泡，确保单次触发
      if (!params || !params.data || !params.dataType) return

      if (params.dataType === 'node') {
        const node = params.data
        const categoryId = node.category // 0:食材, 1:菜谱, 2+:分类
        
        let apiUrl = ''
        if (categoryId === 0) apiUrl = `/api/ingredients/detail/${encodeURIComponent(node.name)}`
        else if (categoryId === 1) apiUrl = `/api/recipes/detail/${encodeURIComponent(node.name)}`
        else apiUrl = `/api/categories/${encodeURIComponent(node.name)}`

        try {
          const response = await axios.get(apiUrl)
          const stdData = response.data
          
          popupData.value = {
            type: 'node',
            id: node.id || node.name,
            name: stdData.name,
            summary: stdData.summary,
            role: node.role,
            categoryName: categories.value[categoryId]?.name || '医疗',
            ancient_quote: stdData.ancient_quote
          }
          showPopup.value = true
          loadGraphData(node.name, true)
        } catch (error) {
          console.error('Fetch detail failed:', error)
          // 回退机制：使用图谱原始数据
          popupData.value = {
            type: 'node',
            id: node.id || node.name,
            name: node.name,
            summary: node.summary || '资料整理中...',
            role: node.role,
            categoryName: categories.value[categoryId]?.name || '医疗',
            ancient_quote: ''
          }
          showPopup.value = true
        }
      } else if (params.dataType === 'edge') {
        popupData.value = {
          type: 'edge',
          id: params.data.source + '-' + params.data.target,
          source: params.data.source,
          target: params.data.target,
          roleName: getRoleFullCN(params.data.role),
          summary: params.data.desc || '配伍关联'
        }
        showPopup.value = true
      }
    })
  }
}

const handleResize = () => chartInstance?.resize()
const handleKeyDown = (e) => { if (e.key === 'Escape') showPopup.value = false }

onMounted(() => {
  initChart()
  if (props.centerNode) loadGraphData(props.centerNode, false)
  window.addEventListener('resize', handleResize)
  window.addEventListener('keydown', handleKeyDown)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  window.removeEventListener('keydown', handleKeyDown)
  
  // 【物理清场】彻底强制拔掉 body 下任何可能的 Residue
  document.querySelectorAll('.van-popup').forEach(el => el.remove())
  document.querySelectorAll('.van-overlay').forEach(el => el.remove())
  
  if (chartInstance) chartInstance.dispose()
})
</script>

<template>
  <div class="apple-hier-wrapper">
    <div class="hier-container">
      <div v-if="loading" class="hier-loading"><van-loading size="22px" color="#C94848" /></div>
      <div ref="chartRef" :style="{ width: '100%', height: props.height }"></div>
      <div class="hier-legend">
        <div class="legend-item"><span class="dot jun"></span>君药</div>
        <div class="legend-item"><span class="dot chen"></span>臣药</div>
        <div class="legend-item"><span class="dot zuo"></span>佐/使药</div>
      </div>
    </div>

    <!-- 【单例重构】唯一的弹窗，强制 v-if 销毁与 Key 刷新 -->
    <van-popup
      v-if="showPopup"
      v-model:show="showPopup"
      :key="popupData?.id"
      teleport="body"
      class="singleton-node-capsule"
      :overlay-style="{ zIndex: 10010 }"
      @click-overlay="showPopup = false"
    >
      <div class="capsule-content" @click.stop>
        <button class="capsule-close" @click="showPopup = false">✕</button>
        
        <div v-if="popupData?.type === 'node'" class="node-layout">
          <div class="capsule-header">
            <span class="capsule-badge" v-if="popupData.role">{{ getRoleCN(popupData.role) }}</span>
            <h2 class="capsule-title">{{ popupData.name }}</h2>
          </div>
          
          <div class="capsule-body">
            <div v-if="popupData.ancient_quote" class="capsule-quote">
              <p>“{{ popupData.ancient_quote }}”</p>
            </div>
            <div class="capsule-summary">
              <label>功效简述</label>
              <p>{{ popupData.summary || '资料整理中...' }}</p>
            </div>
          </div>
        </div>

        <div v-else class="edge-layout">
          <div class="capsule-header">
            <h2 class="capsule-title">{{ popupData.roleName }}</h2>
          </div>
          <div class="capsule-body">
            <p class="edge-rel">{{ popupData.source }} → {{ popupData.target }}</p>
            <p class="edge-desc">{{ popupData.summary }}</p>
          </div>
        </div>
      </div>
    </van-popup>
  </div>
</template>

<style scoped>
.apple-hier-wrapper { margin: 24px 0; font-family: -apple-system, BlinkMacSystemFont, sans-serif; }
.hier-container { position: relative; background: #F5F5F7; border-radius: 32px; overflow: hidden; border: 1px solid rgba(0,0,0,0.06); }
.hier-loading { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); z-index: 10; }
.hier-legend { position: absolute; top: 20px; right: 20px; background: rgba(255,255,255,0.7); backdrop-filter: blur(10px); padding: 8px 12px; border-radius: 14px; display: flex; flex-direction: column; gap: 6px; }
.legend-item { font-size: 11px; font-weight: 600; color: #8E8E93; display: flex; align-items: center; gap: 6px; }
.dot { width: 8px; height: 8px; border-radius: 50%; }
.dot.jun { background: #C94848; }
.dot.chen { background: #8E9775; }
.dot.zuo { background: #D1D1D6; }

/* 唯一的悬浮胶囊样式 (物理隔离) */
.singleton-node-capsule {
  position: fixed !important;
  bottom: 24px !important;
  left: 16px !important;
  right: 16px !important;
  top: auto !important;
  width: calc(100% - 32px) !important;
  max-width: 440px !important;
  margin: 0 auto !important;
  max-height: 45vh !important;
  border-radius: 28px !important;
  background: rgba(255, 255, 255, 0.92) !important;
  backdrop-filter: blur(20px) saturate(180%) !important;
  box-shadow: 0 20px 50px rgba(0,0,0,0.15) !important;
  border: 1px solid rgba(255,255,255,0.4) !important;
  overflow: hidden !important;
  z-index: 10010 !important;
  transition: all 0.3s cubic-bezier(0.32, 1, 0.23, 1) !important;
}

.capsule-content { padding: 18px 24px 24px; position: relative; }
.capsule-close { 
  position: absolute; top: 16px; right: 16px; width: 28px; height: 28px; 
  border-radius: 50%; background: rgba(0,0,0,0.06); border: none; 
  font-size: 12px; color: #8E8E93; cursor: pointer; display: flex; 
  align-items: center; justify-content: center; z-index: 20; 
}

.capsule-header { display: flex; align-items: center; gap: 10px; margin-bottom: 14px; }
.capsule-badge { background: #C94848; color: #fff; font-size: 10px; font-weight: 800; padding: 2px 8px; border-radius: 20px; }
.capsule-title { font-size: 19px; font-weight: 800; color: #1D1D1F; margin: 0; }

.capsule-quote { background: rgba(0,0,0,0.04); padding: 12px 14px; border-radius: 12px; margin-bottom: 14px; border-left: 3px solid #C94848; }
.capsule-quote p { font-size: 13.5px; line-height: 1.5; color: #2C2C2E; font-style: italic; margin: 0; }

.capsule-summary label { font-size: 10px; font-weight: 700; color: #8E8E93; text-transform: uppercase; letter-spacing: 0.5px; display: block; margin-bottom: 6px; }
.capsule-summary p { font-size: 14px; line-height: 1.5; color: #48484A; margin: 0; }

.edge-rel { font-size: 13px; font-weight: 700; color: #8E8E93; margin-bottom: 8px; }
.edge-desc { font-size: 15px; color: #1D1D1F; line-height: 1.6; font-weight: 500; }
</style>
