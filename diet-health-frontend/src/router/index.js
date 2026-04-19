import { createRouter, createWebHistory } from 'vue-router'
import Home from '../pages/Home.vue'
import Recommend from '../pages/Recommend.vue'
import Recipe from '../pages/Recipe.vue'
import Profile from '../pages/Profile.vue'
import Ingredient from '../pages/Ingredient.vue'
import Therapy from '../pages/Therapy.vue'
import ConstitutionTest from '../pages/ConstitutionTest.vue'
import SmartRecommend from '../pages/SmartRecommend.vue'
import KnowledgeGraph from '../pages/KnowledgeGraph.vue'
import CheckIn from '../pages/CheckIN.vue'

const routes = [
  { path: '/', component: Home },
  { path: '/recommend', component: Recommend },
  { path: '/recipe', component: Recipe },
  { path: '/profile', component: Profile },
  { path: '/ingredient', component: Ingredient },
  { path: '/therapy', component: Therapy },
  { path: '/constitution', component: ConstitutionTest },
  { path: '/smart-recommend', component: SmartRecommend },
  { path: '/knowledge-graph', component: KnowledgeGraph },
  { path: '/checkin', component: CheckIn }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
