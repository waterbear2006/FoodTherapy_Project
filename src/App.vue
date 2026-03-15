<script setup>
import { ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Tabbar, TabbarItem } from 'vant'

const route = useRoute()
const router = useRouter()

const pathToName = {
  '/': 'home',
  '/ingredient': 'home',
  '/recommend': 'recommend',
  '/recipe': 'recipe',
  '/therapy': 'recipe',
  '/profile': 'profile'
}
const active = ref(pathToName[route.path] || 'home')
watch(() => route.path, (path) => {
  active.value = pathToName[path] || 'home'
}, { immediate: true })

function onSwitch(name) {
  const pathMap = { home: '/', recommend: '/recommend', recipe: '/recipe', profile: '/profile' }
  if (pathMap[name]) router.push(pathMap[name])
}
</script>

<template>
  <div class="app-wrap">
    <main class="app-main">
      <router-view v-slot="{ Component }">
        <component :is="Component" />
      </router-view>
    </main>
    <Tabbar v-model="active" @change="onSwitch" placeholder safe-area-inset-bottom>
      <TabbarItem name="home" icon="home-o">首页</TabbarItem>
      <TabbarItem name="recommend" icon="star-o">智能推荐</TabbarItem>
      <TabbarItem name="recipe" icon="notes-o">菜谱</TabbarItem>
      <TabbarItem name="profile" icon="user-o">我的</TabbarItem>
    </Tabbar>
  </div>
</template>

<style scoped>
.app-wrap {
  min-height: 100vh;
  padding-bottom: 50px;
  box-sizing: border-box;
}
.app-main {
  min-height: calc(100vh - 50px);
}
:deep(.van-tabbar) {
  --van-tabbar-item-active-color: var(--primary);
}
:deep(.van-tabbar-item__icon) {
  font-size: 22px;
}
</style>
