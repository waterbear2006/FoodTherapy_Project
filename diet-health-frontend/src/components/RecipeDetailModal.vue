<script setup>
import { computed } from 'vue'
import RelationGraph from './RelationGraph.vue'

const props = defineProps({
  recipe: { type: Object, default: null },
  visible: { type: Boolean, default: false }
})

const emit = defineEmits(['close'])

const imageUrl = computed(() => {
  if (!props.recipe?.images) return ''
  const imageName = props.recipe.images.trim()
  return `http://127.0.0.1:8001/data/Caipuimages/${imageName}`
})

const suitableTags = computed(() => {
  if (!props.recipe?.suitable) return []
  return Array.isArray(props.recipe.suitable) ? props.recipe.suitable : props.recipe.suitable.split('、')
})

const stepsList = computed(() => {
  if (!props.recipe?.steps) return []
  if (Array.isArray(props.recipe.steps)) return props.recipe.steps
  const steps = props.recipe.steps
  let parts = steps.split(/[;\n；]/).filter(s => s.trim())
  let finalSteps = []
  parts.forEach(part => {
    const subParts = part.split(/(?=\d+[.、\s])/).filter(s => s.trim())
    finalSteps.push(...subParts)
  })
  return finalSteps.map(s => s.replace(/^\d+[.、\s]*/, '').trim()).filter(s => s)
})

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
    <div v-if="visible" class="recipe-detail-modal" @click.self="handleClose">
      <div class="modal-content glass-card ink-wash-fade-in">
        <button class="close-btn" @click="handleClose">×</button>
        
        <div class="image-section">
          <img v-if="imageUrl" :src="imageUrl" :alt="recipe?.name" class="detail-image" @error="$event.target.style.display='none'" />
          <div v-else class="image-placeholder">🍳</div>
          <div v-if="recipe?.match_score" class="match-badge">
            匹配度 {{ Math.round(recipe.match_score * 100) }}%
          </div>
        </div>

        <div class="info-section">
          <h2 class="recipe-name">{{ recipe?.name }}</h2>
          <div v-if="suitableTags.length > 0" class="suitable-tags">
            <span v-for="(tag, index) in suitableTags" :key="index" class="tag">{{ tag }}</span>
          </div>
        </div>

        <section v-if="recipe?.effect" class="detail-block">
          <h3 class="block-title"><span class="icon">✨</span> 主要功效</h3>
          <p class="block-content">{{ recipe.effect }}</p>
        </section>

        <section v-if="recipe?.ingredients" class="detail-block">
          <h3 class="block-title"><span class="icon">🥬</span> 所需食材</h3>
          <div class="ingredients-list">
            <span v-for="(ingredient, index) in (Array.isArray(recipe.ingredients) ? recipe.ingredients : recipe.ingredients.split('、'))" :key="index" class="ingredient-item">
              {{ ingredient }}
            </span>
          </div>
        </section>

        <section v-if="stepsList.length > 0" class="detail-block">
          <h3 class="block-title"><span class="icon">👨‍🍳</span> 制作步骤</h3>
          <div class="steps-list">
            <div v-for="(step, index) in stepsList" :key="index" class="step-item">
              <span class="step-number">{{ index + 1 }}</span>
              <span class="step-text">{{ step }}</span>
            </div>
          </div>
        </section>

        <section v-if="recipe?.taboo" class="detail-block warning">
          <h3 class="block-title"><span class="icon">⚠️</span> 食用禁忌</h3>
          <p class="warning-text">{{ recipe.taboo }}</p>
        </section>

        <section v-if="recipe?.name" class="detail-block graph-section">
          <h3 class="block-title"><span class="icon">🕸️</span> 药食配伍图谱</h3>
          <div class="graph-container">
            <RelationGraph :centerNode="recipe.name" />
          </div>
        </section>
      </div>
    </div>
  </transition>
</template>

<style scoped>
.recipe-detail-modal {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  display: flex; align-items: center; justify-content: center;
  z-index: 100; padding: 16px; 
}

.modal-content {
  width: 100%; max-width: 440px; max-height: 85vh;
  overflow-y: auto; position: relative;
  border-radius: var(--radius-xl);
  padding-bottom: 24px;
}

.close-btn {
  position: absolute; top: 16px; right: 16px;
  width: 30px; height: 30px; border-radius: 50%;
  background: rgba(0, 0, 0, 0.1);
  border: none;
  font-size: 20px; color: white; cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  z-index: 100;
  text-shadow: 0 1px 2px rgba(0,0,0,0.5);
}

.image-section { width: 100%; height: 240px; position: relative; overflow: hidden; background: white;}
.detail-image { width: 100%; height: 100%; object-fit: cover; }
.image-placeholder { width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; font-size: 64px; background: var(--primary-light); }

.match-badge {
  position: absolute; bottom: 12px; right: 12px;
  background: rgba(26, 163, 157, 0.9);
  color: white; padding: 4px 12px; border-radius: 99px;
  font-size: 12px; font-weight: 700;
  backdrop-filter: blur(4px);
}

.info-section, .detail-block { padding: 20px; }
.recipe-name { font-size: 24px; font-weight: 700; color: var(--text); margin: 0 0 12px; }
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

.detail-block.warning { background: rgba(255, 59, 48, 0.03); margin: 12px; border-radius: var(--radius); }
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
