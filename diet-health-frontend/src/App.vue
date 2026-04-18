<script setup>
import { ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Tabbar, TabbarItem } from 'vant'

const route = useRoute()
const router = useRouter()

const pathToName = {
  '/': 'home',
  '/ingredient': 'ingredient',
  '/therapy': 'therapy',
  '/recommend': '',
  '/recipe': '',
  '/constitution': '',
  '/smart-recommend': '',
  '/profile': 'profile'
}
const active = ref(pathToName[route.path] || 'home')
watch(() => route.path, (path) => {
  active.value = pathToName[path] || 'home'
}, { immediate: true })

function onSwitch(name) {
  const pathMap = { home: '/', ingredient: '/ingredient', therapy: '/therapy', profile: '/profile' }
  if (pathMap[name]) router.push(pathMap[name])
}
</script>

<template>
  <div class="app-wrap">
    <main class="app-main">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <keep-alive>
            <component :is="Component" />
          </keep-alive>
        </transition>
      </router-view>
    </main>
    <Tabbar v-model="active" @change="onSwitch" placeholder safe-area-inset-bottom>
      <TabbarItem name="home">
        <template #icon="{ active }">
          <svg :class="['tabbar-icon', active ? 'active' : '']" viewBox="0 0 64 64" fill="currentColor">
            <!-- 中式塔楼 -->
            <path d="M32 4L8 16v4h48V16L32 4z" opacity="0.9"/>
            <path d="M12 24v4h40V24H12z" opacity="0.8"/>
            <path d="M16 32v4h32V32H16z" opacity="0.7"/>
            <rect x="24" y="40" width="16" height="20" opacity="0.9"/>
          </svg>
        </template>
        首页
      </TabbarItem>
      <TabbarItem name="ingredient">
        <template #icon="{ active }">
          <svg :class="['tabbar-icon', active ? 'active' : '']" viewBox="0 0 64 64" fill="currentColor">
            <!-- 中草药叶子 -->
            <path d="M32 8c-2 8-12 16-12 28 0 8 6 14 12 20 6-6 12-12 12-20 0-12-10-20-12-28z" opacity="0.9"/>
            <path d="M32 8v48" stroke="currentColor" stroke-width="2" fill="none"/>
            <path d="M32 20c-4 4-8 6-8 12" stroke="currentColor" stroke-width="2" fill="none" opacity="0.6"/>
            <path d="M32 28c4 4 8 6 8 12" stroke="currentColor" stroke-width="2" fill="none" opacity="0.6"/>
          </svg>
        </template>
        食材
      </TabbarItem>
      <TabbarItem name="therapy">
        <template #icon="{ active }">
          <svg :class="['tabbar-icon', active ? 'active' : '']" viewBox="0 0 64 64" fill="currentColor">
            <!-- 中式药膳鼎 -->
            <path d="M16 20h32v24H16z" opacity="0.9"/>
            <path d="M20 44v8h8v-8H20zm16 0v8h8v-8H36z" opacity="0.7"/>
            <path d="M12 24h4v16h-4zm36 0h4v16h-4z" opacity="0.8"/>
            <circle cx="32" cy="32" r="6" opacity="0.6"/>
          </svg>
        </template>
        食疗
      </TabbarItem>
      <TabbarItem name="profile">
        <template #icon="{ active }">
          <svg :class="['tabbar-icon', active ? 'active' : '']" viewBox="0 0 64 64" fill="currentColor">
            <!-- 中式人物轮廓 -->
            <circle cx="32" cy="20" r="10" opacity="0.9"/>
            <path d="M16 56V44c0-8 8-12 16-12s16 4 16 12v12H16z" opacity="0.8"/>
            <path d="M32 32v24" stroke="currentColor" stroke-width="2" opacity="0.5"/>
          </svg>
        </template>
        我的
      </TabbarItem>
    </Tabbar>
  </div>
</template>

<style scoped>
.app-wrap {
  min-height: 100vh;
  padding-bottom: 50px;
  box-sizing: border-box;
  background: var(--bg);
}
.app-main {
  min-height: calc(100vh - 50px);
}
:deep(.van-tabbar) {
  --van-tabbar-item-active-color: var(--primary);
  background: rgba(255, 255, 255, 0.98);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  box-shadow: 0 -6px 32px rgba(125, 157, 138, 0.12);
  border-top: none;
  padding-bottom: env(safe-area-inset-bottom);
}
:deep(.van-tabbar-item) {
  padding: 14px 0 10px;
  min-height: auto;
}
:deep(.tabbar-icon) {
  width: 28px;
  height: 28px;
  color: var(--text-muted);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
:deep(.tabbar-icon.active) {
  color: var(--primary);
  transform: translateY(-2px);
  filter: drop-shadow(0 2px 4px rgba(125, 157, 138, 0.3));
}
:deep(.van-tabbar-item__text) {
  font-size: 11px;
  margin-top: 6px;
  color: var(--text-muted);
  font-weight: 500;
  letter-spacing: 0.5px;
}

/* 页面转场动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.25s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
