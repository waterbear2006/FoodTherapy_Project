<script setup>
import { computed, watch } from 'vue'
import RelationGraph from './RelationGraph.vue' // 引入你的图谱组件

const props = defineProps({
  therapy: { type: Object, default: null },
  visible: { type: Boolean, default: false }
})

watch(() => props.therapy, (newVal) => {
  console.log('🔍 TherapyDetailModal 收到的数据:', newVal)
}, { immediate: true, deep: true })

watch(() => props.visible, (newVal) => {
  console.log('👁️ Modal visible:', newVal)
}, { immediate: true })

const emit = defineEmits(['close'])

const imageUrl = computed(() => {
  if (!props.therapy?.images) return ''
  const imageName = props.therapy.images.trim()
  return `/data/Caipuimages/${imageName}`
})

const effectTags = computed(() => {
  if (!props.therapy?.effect) return []
  return Array.isArray(props.therapy.effect) ? props.therapy.effect : props.therapy.effect.split('、')
})

const suitableTags = computed(() => {
  if (!props.therapy?.suitable) return []
  return Array.isArray(props.therapy.suitable) ? props.therapy.suitable : props.therapy.suitable.split('、')
})

const stepsList = computed(() => {
  if (!props.therapy?.steps) return []
  if (Array.isArray(props.therapy.steps)) return props.therapy.steps
  const steps = props.therapy.steps
  let parts = steps.split(/[;\n；]/).filter(s => s.trim())
  let finalSteps = []
  parts.forEach(part => {
    const subParts = part.split(/(?=\d+[.、\s])/).filter(s => s.trim())
    finalSteps.push(...subParts)
  })
  return finalSteps.map(s => s.replace(/^\d+[.、\s]*/, '').trim()).filter(s => s)
})

// RAG 古籍专属正则渲染引擎
const formatAncientText = (text) => {
  if (!text) return ''
  return text.replace(/(《.*?》)/g, '<strong style="color: #8b0000; font-weight: bold;">$1</strong>')
}

function handleClose() {
  emit('close')
}
</script>

<template>
  <transition name="slide-up">
    <div v-if="visible" class="therapy-detail-modal" @click.self="handleClose">
      <div class="modal-content glass-card ink-wash-fade-in">
        <button class="close-btn" @click="handleClose">×</button>
        
        <div class="image-section">
          <img v-if="imageUrl" :src="imageUrl" :alt="therapy?.name" class="detail-image" @error="$event.target.style.display='none'" />
          <div v-else class="image-placeholder">🍲</div>
        </div>

        <div class="info-section">
          <h2 class="therapy-name">{{ therapy?.name }}</h2>
          <div v-if="therapy?.suitable && suitableTags.length > 0" class="suitable-tags">
            <span v-for="(tag, index) in suitableTags" :key="index" class="tag">{{ tag }}</span>
          </div>
        </div>

        <!-- RAG 古籍考证：宣纸感区块 -->
        <section v-if="therapy?.reason || therapy?.ancient_quote" class="detail-block">
          <h3 class="block-title">
            <span class="icon">📜</span>
            医典引证
          </h3>
          <div class="rice-paper-block" v-html="formatAncientText(therapy.reason || therapy.ancient_quote)"></div>
        </section>

        <section class="detail-block">
          <h3 class="block-title"><span class="icon">✨</span> 主要功效</h3>
          <p class="block-content">{{ therapy?.effect ? (Array.isArray(therapy.effect) ? therapy.effect.join('、') : therapy.effect) : '暂无信息' }}</p>
        </section>

        <section v-if="therapy?.ingredients" class="detail-block">
          <h3 class="block-title"><span class="icon">🥬</span> 所需食材</h3>
          <div class="ingredients-list">
            <span v-for="(ingredient, index) in (Array.isArray(therapy.ingredients) ? therapy.ingredients : therapy.ingredients.split('、'))" :key="index" class="ingredient-item">
              {{ ingredient }}
            </span>
          </div>
        </section>

        <section v-if="therapy?.steps && stepsList.length > 0" class="detail-block">
          <h3 class="block-title"><span class="icon">👨‍🍳</span> 制作步骤</h3>
          <div class="steps-list">
            <div v-for="(step, index) in stepsList" :key="index" class="step-item">
              <span class="step-number">{{ index + 1 }}</span>
              <span class="step-text">{{ step }}</span>
            </div>
          </div>
        </section>

        <section v-if="therapy?.taboo" class="detail-block warning">
          <h3 class="block-title"><span class="icon">⚠️</span> 食用禁忌</h3>
          <p class="warning-text">{{ therapy.taboo }}</p>
        </section>

        <!-- 知识图谱置于最底部 -->
        <section v-if="therapy?.name" class="detail-block graph-section">
          <h3 class="block-title"><span class="icon">🕸️</span> 药食配伍图谱</h3>
          <div class="graph-container">
            <RelationGraph :centerNode="therapy.name" />
          </div>
        </section>
      </div>
    </div>
  </transition>
</template>

<style scoped>
.therapy-detail-modal {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  display: flex; align-items: center; justify-content: center;
  z-index: 100; padding: 16px; 
}

/* Apple 极简毛玻璃卡片 */
/* Apple 极简毛玻璃卡片 */
.modal-content {
  width: 100%; max-width: 440px; max-height: 85vh;
  overflow-y: auto; position: relative;
  border-radius: var(--radius-xl);
  padding-bottom: 24px;
}

.close-btn {
  position: absolute; top: 16px; right: 16px;
  width: 30px; height: 30px; border-radius: 50%;
  background: rgba(0, 0, 0, 0.05);
  border: none;
  font-size: 20px; color: var(--text-secondary); cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  z-index: 100;
}

.image-section { width: 100%; height: 240px; position: relative; overflow: hidden; background: white;}
.detail-image { width: 100%; height: 100%; object-fit: cover; }
.image-placeholder { width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; font-size: 64px; background: var(--primary-light); }

.info-section, .detail-block {
  padding: 20px;
}

.therapy-name { font-size: 24px; font-weight: 700; color: var(--text); margin: 0 0 12px; }
.suitable-tags { display: flex; gap: 8px; flex-wrap: wrap; }
.tag { padding: 4px 12px; background: var(--primary-light); color: var(--primary); border-radius: 99px; font-size: 12px; font-weight: 600; }
.block-title { display: flex; align-items: center; gap: 8px; font-size: 16px; font-weight: 600; color: var(--text); margin: 0 0 14px; }
.block-content { font-size: 14px; line-height: 1.6; color: var(--text-secondary); margin: 0; }

.ingredients-list { display: flex; flex-wrap: wrap; gap: 8px; }
.ingredient-item { padding: 6px 14px; background: white; border: 1px solid var(--primary-light); border-radius: 10px; font-size: 13px; color: var(--primary); font-weight: 500; }

.steps-list { display: flex; flex-direction: column; gap: 10px; }
.step-item { display: flex; gap: 12px; align-items: flex-start; padding: 12px; background: rgba(255, 255, 255, 0.5); border-radius: 12px; border: 1px solid rgba(0, 0, 0, 0.03); }
.step-number { flex-shrink: 0; width: 22px; height: 22px; background: var(--primary); color: #fff; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: 700; }
.step-text { flex: 1; font-size: 14px; line-height: 1.6; color: var(--text-secondary); }

.detail-block.warning {
  background: rgba(255, 59, 48, 0.03);
  margin: 12px;
  border-radius: var(--radius);
}
.warning-text { font-size: 14px; color: #d32f2f; margin: 0; line-height: 1.6; }

.graph-container {
  height: 300px;
  background: rgba(255, 255, 255, 0.4);
  border-radius: var(--radius);
  overflow: hidden;
  border: 1px solid var(--border-glass);
}

.modal-content::-webkit-scrollbar { width: 4px; }
.modal-content::-webkit-scrollbar-thumb { background: rgba(0,0,0,0.1); border-radius: 10px; }
</style>