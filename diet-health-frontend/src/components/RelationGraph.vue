<script setup>
import { ref, onMounted, watch, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import axios from 'axios'
import { showToast } from 'vant'

const props = defineProps({
  centerNode: {
    type: String,
    required: true
  },
  height: {
    type: String,
    default: '560px'
  }
})

const emit = defineEmits(['nodeClick'])

const chartRef = ref(null)
let chartInstance = null
const loading = ref(false)

// 详情弹窗与浮层状态
const showDetail = ref(false)
const showEdgeRole = ref(false)
const selectedNode = ref({ name: '', categoryName: '', summary: '', role: '', metadata: {} })
const selectedEdge = ref({ source: '', target: '', role: '', roleName: '', desc: '' })

// 维护全局节点和连线
const allNodes = ref([])
const allLinks = ref([])
const categories = ref([])

// Apple Color Hierarchy
const roleColors = {
  "Jun": "rgba(201, 72, 72, 0.9)",   // 君 - 胭脂红
  "Chen": "rgba(142, 151, 117, 0.8)", // 臣 - 鼠尾草绿
  "Zuo": "rgba(220, 220, 220, 0.7)",  // 佐 - 极简灰
  "Shi": "rgba(220, 220, 220, 0.6)",  // 使 - 极简灰
  "default": "rgba(70, 130, 180, 0.8)" // 其他 (体质/功效)
}

const getRoleCN = (role) => {
  const map = { "Jun": "君", "Chen": "臣", "Zuo": "佐", "Shi": "使" }
  return map[role] || ""
}

const getRoleFullCN = (role) => {
  const map = { "Jun": "君药 (Monarch)", "Chen": "臣药 (Minister)", "Zuo": "佐药 (Assistant)", "Shi": "使药 (Envoy)" }
  return map[role] || "配伍成分"
}

const getRoleDescription = (role) => {
  const map = {
    "Jun": "主病之谓君。在方剂中针对主病或主证起主要治疗作用，是核心力量。",
    "Chen": "佐君之谓臣。辅助君药加强治疗作用，或兼治兼证。",
    "Zuo": "应臣之谓佐。协助君臣药治兼证，或抑制、调和主药的偏性、毒性。",
    "Shi": "引经之谓使。引导药物到达病所，或调和诸药药性。"
  }
  return map[role] || "该药参与方剂配伍，协同增强整体疗效。"
}

const loadGraphData = async (nodeName, isIncremental = false) => {
  loading.value = true
  try {
    const response = await axios.get(`http://127.0.0.1:8001/api/graph/detail?name=${encodeURIComponent(nodeName)}&depth=1`)
    const { nodes, links, categories: cats } = response.data
    
    categories.value = cats

    if (!isIncremental) {
      allNodes.value = nodes
      allLinks.value = links
    } else {
      const existingIds = new Set(allNodes.value.map(n => n.id))
      nodes.forEach(node => {
        if (!existingIds.has(node.id)) allNodes.value.push(node)
      })
      const existingLinks = new Set(allLinks.value.map(l => `${l.source}-${l.target}`))
      links.forEach(link => {
        const key = `${link.source}-${link.target}`
        if (!existingLinks.has(key)) allLinks.value.push(link)
      })
    }
    
    updateChart()
  } catch (error) {
    console.error('Apple Intelligence Offline:', error)
    showToast('知识库连接中断')
  } finally {
    loading.value = false
  }
}

const updateChart = () => {
  if (!chartInstance) return

  const nodes = allNodes.value.map(node => {
    const role = node.role
    let size = 30
    let color = roleColors.default
    
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
        show: true, 
        position: 'bottom',
        distance: 14,
        color: isCenterOrJun ? '#1D1D1F' : 'transparent',
        backgroundColor: isCenterOrJun ? 'rgba(255,255,255,0.85)' : 'transparent',
        shadowColor: isCenterOrJun ? 'rgba(0,0,0,0.05)' : 'transparent',
        fontSize: role === 'Jun' ? 14 : 12,
        fontWeight: '700',
        padding: [4, 10],
        borderRadius: 8,
        shadowBlur: 10
      },
      emphasis: {
        label: {
          show: true,
          color: '#1D1D1F',
          backgroundColor: 'rgba(255,255,255,0.95)',
          shadowColor: 'rgba(0,0,0,0.1)',
          shadowBlur: 15
        }
      }
    }
})

  const links = allLinks.value.map(link => {
    const roleCN = getRoleCN(link.role)
    let width = 1.2, color = '#D1D1D6', type = 'dashed'
    if (link.role === 'Jun') { width = 3; color = roleColors.Jun; type = 'solid' }
    else if (link.role === 'Chen') { width = 2; color = '#48484A'; type = 'solid' }
    
    return {
      ...link,
      lineStyle: { width, color, type, curveness: 0.2 },
      label: {
        show: !!roleCN,
        formatter: roleCN,
        fontSize: 10,
        color: '#8E8E93',
        backgroundColor: '#F2F2F7',
        padding: [2, 4],
        borderRadius: 2
      },
      emphasis: { lineStyle: { width: width + 2, color: '#007AFF' } }
    }
  })

  const option = {
    backgroundColor: '#F5F5F7',
    series: [{
      type: 'graph',
      layout: 'force',
      data: nodes,
      links: links,
      categories: categories.value,
      roam: true,
      scaleLimit: { min: 0.4, max: 5 },
      draggable: true,
      force: {
        repulsion: 2500,
        gravity: 0.03,
        friction: 0.8,
        edgeLength: [40, 100]
      },
      emphasis: {
        focus: 'adjacency',
        label: {
          show: true, // 确保悬浮时全量显名
          fontSize: 15,
          fontWeight: '700',
          color: '#1D1D1F',
          backgroundColor: 'rgba(255,255,255,0.95)',
          padding: [6, 12],
          borderRadius: 10,
          shadowBlur: 15,
          shadowColor: 'rgba(0,0,0,0.15)'
        }
      },
      lineStyle: { curveness: 0.2 }
    }]
  }

  chartInstance.setOption(option)
}

const initChart = () => {
  if (chartRef.value) {
    chartInstance = echarts.init(chartRef.value)
    chartInstance.on('click', (params) => {
      if (params.dataType === 'node') {
        const node = params.data
        selectedNode.value = {
          name: node.name,
          categoryName: categories.value[node.category]?.name || '医疗',
          summary: node.summary,
          role: node.role,
          metadata: node.metadata || {}
        }
        showDetail.value = true
        emit('nodeClick', node)
        loadGraphData(node.name, true)
      } else if (params.dataType === 'edge') {
        const link = params.data
        selectedEdge.value = {
          source: link.source,
          target: link.target,
          role: link.role,
          roleName: getRoleFullCN(link.role),
          desc: getRoleDescription(link.role)
        }
        showEdgeRole.value = true
      }
    })
  }
}

watch(() => props.centerNode, (val) => val && loadGraphData(val, false))

onMounted(() => {
  initChart()
  if (props.centerNode) loadGraphData(props.centerNode, false)
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  if (chartInstance) chartInstance.dispose()
})

const handleResize = () => chartInstance?.resize()
</script>

<template>
  <div class="apple-hier-wrapper">
    <div class="hier-container">
      <div v-if="loading" class="hier-loading">
        <van-loading size="22px" color="#C94848" />
      </div>
      <div ref="chartRef" :style="{ width: '100%', height: props.height }"></div>
      
      <div class="hier-legend">
        <div class="legend-item"><span class="dot jun"></span>君药</div>
        <div class="legend-item"><span class="dot chen"></span>臣药</div>
        <div class="legend-item"><span class="dot zuo"></span>佐/使药</div>
      </div>
    </div>

    <!-- Apple Hierarchical Detail Sheet -->
    <van-popup
      v-model:show="showDetail"
      position="bottom"
      round
      class="apple-hier-popup"
    >
      <div class="hier-sheet-content">
        <div class="sheet-handle"></div>
        
        <div class="hier-header">
          <div class="role-badge" v-if="selectedNode.role">
            {{ getRoleFullCN(selectedNode.role) }}
          </div>
          <div class="header-main">
            <h2 v-if="selectedNode.role === 'Jun'">该方之君药：{{ selectedNode.name }}</h2>
            <h2 v-else-if="selectedNode.role">配伍角色：{{ getRoleCN(selectedNode.role) }} ({{ selectedNode.name }})</h2>
            <h2 v-else>{{ selectedNode.name }}</h2>
            <span class="type-badge">{{ selectedNode.categoryName }}</span>
          </div>
        </div>

        <div class="hier-body">
          <div v-if="selectedNode.metadata?.ancient_quote" class="medical-quote">
            <van-icon name="guide-o" class="quote-icon" />
            <p>“{{ selectedNode.metadata.ancient_quote }}”</p>
          </div>
          
          <div class="info-grid">
            <div class="info-item">
              <label>配伍职能</label>
              <p class="role-highlight" v-if="selectedNode.role">{{ getRoleDescription(selectedNode.role) }}</p>
              <p v-else>对方剂起基础支撑作用。</p>
            </div>
            <div v-if="selectedNode.metadata?.tag" class="info-item">
              <label>药性标签</label>
              <div class="tag-cloud">
                <span v-for="tag in selectedNode.metadata.tag.split('、')" :key="tag" class="small-tag">{{ tag }}</span>
              </div>
            </div>
          </div>
          
          <div class="summary-box">
            <label>疗法纲要</label>
            <p>{{ selectedNode.summary || '资料整理中...' }}</p>
          </div>
        </div>
      </div>
    </van-popup>

    <!-- Role Context Floating Layer -->
    <van-popup
      v-model:show="showEdgeRole"
      position="bottom"
      round
      class="apple-hier-popup role-sheet"
    >
      <div class="hier-sheet-content">
        <div class="sheet-handle"></div>
        <div class="hier-role-card">
          <div class="role-visual">
            <span class="name">{{ selectedEdge.source }}</span>
            <div class="connector">
              <span class="role-text">{{ getRoleCN(selectedEdge.role) }}</span>
              <div class="line" :class="selectedEdge.role"></div>
            </div>
            <span class="name">{{ selectedEdge.target }}</span>
          </div>
          <h3 class="role-title">{{ selectedEdge.roleName }}</h3>
          <p class="role-desc">{{ selectedEdge.desc }}</p>
        </div>
      </div>
    </van-popup>
  </div>
</template>

<style scoped>
.apple-hier-wrapper {
  margin: 24px 0;
  font-family: -apple-system, system-ui, BlinkMacSystemFont, "SF Pro Text", "Helvetica Neue", sans-serif;
}

.hier-container {
  position: relative;
  background-color: #F5F5F7;
  border-radius: 32px;
  overflow: hidden;
  border: 1px solid rgba(0,0,0,0.06);
  box-shadow: 0 10px 30px rgba(0,0,0,0.03);
}

.hier-loading {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 10;
}

.hier-legend {
  position: absolute;
  top: 24px;
  right: 24px;
  background: rgba(255,255,255,0.6);
  backdrop-filter: blur(10px);
  padding: 10px 16px;
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  border: 1px solid rgba(0,0,0,0.03);
}

.legend-item {
  font-size: 11px;
  font-weight: 600;
  color: #8E8E93;
  display: flex;
  align-items: center;
  gap: 8px;
}

.dot { width: 8px; height: 8px; border-radius: 50%; }
.dot.jun { background: #C94848; }
.dot.chen { background: #8E9775; }
.dot.zuo { background: #D1D1D6; }

/* Apple Hier Popup */
.apple-hier-popup {
  background: rgba(255, 255, 255, 0.9) !important;
  backdrop-filter: blur(28px) saturate(200%);
  border-radius: 40px 40px 0 0 !important;
  border-top: 1px solid rgba(255,255,255,0.5);
}

.hier-sheet-content {
  padding: 12px 28px 48px;
}

.sheet-handle {
  width: 44px;
  height: 5px;
  background-color: rgba(0,0,0,0.12);
  border-radius: 2.5px;
  margin: 0 auto 28px;
}

.role-badge {
  display: inline-block;
  background: #C94848;
  color: #fff;
  font-size: 10px;
  font-weight: 800;
  padding: 3px 10px;
  border-radius: 20px;
  margin-bottom: 12px;
  letter-spacing: 0.5px;
}

.hier-header h2 {
  font-size: 36px;
  font-weight: 800;
  color: #1D1D1F;
  margin: 0;
}

.type-badge {
  background: rgba(0, 122, 255, 0.08);
  color: #007AFF;
  padding: 4px 12px;
  border-radius: 10px;
  font-size: 13px;
  font-weight: 600;
  margin-top: 8px;
  display: inline-block;
}

.hier-body {
  margin-top: 32px;
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.medical-quote {
  background: rgba(0,0,0,0.03);
  padding: 20px;
  border-radius: 20px;
  display: flex;
  gap: 16px;
}

.quote-icon { font-size: 24px; color: #C94848; margin-top: 4px; }

.medical-quote p {
  font-size: 16px;
  line-height: 1.6;
  color: #1D1D1F;
  font-weight: 500;
  font-family: inherit;
}

.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

.info-item label {
  font-size: 11px;
  font-weight: 700;
  color: #8E8E93;
  text-transform: uppercase;
  margin-bottom: 10px;
  display: block;
}

.role-highlight { color: #C94848; font-weight: 600; line-height: 1.5; }

.tag-cloud { display: flex; gap: 6px; flex-wrap: wrap; }

.small-tag {
  background: rgba(0,0,0,0.05);
  padding: 4px 10px;
  border-radius: 8px;
  font-size: 12px;
  color: #48484A;
}

.summary-box label {
  font-size: 11px;
  font-weight: 700;
  color: #8E8E93;
  text-transform: uppercase;
  margin-bottom: 10px;
  display: block;
}

.summary-box p {
  font-size: 18px;
  line-height: 1.6;
  color: #424245;
}

/* Role Context Card */
.hier-role-card { text-align: center; }

.role-visual {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 24px;
  margin-bottom: 32px;
}

.role-visual .name { font-size: 20px; font-weight: 700; color: #1D1D1F; }

.connector {
  position: relative;
  width: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.role-text {
  position: absolute;
  top: -20px;
  font-size: 12px;
  font-weight: 800;
  color: #C94848;
}

.connector .line {
  width: 100%;
  height: 2px;
  background: #D1D1D6;
}

.connector .line.Jun { background: #C94848; height: 3px; }

.role-title { font-size: 26px; font-weight: 800; color: #1D1D1F; margin-bottom: 16px; }

.role-desc { font-size: 17px; line-height: 1.7; color: #48484A; max-width: 320px; margin: 0 auto; }
</style>
