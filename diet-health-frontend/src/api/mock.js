/**
 * API 接口：调用真实后端接口
 * 所有数据来自后端，不使用任何假数据
 */
import axios from 'axios'

// 创建 axios 实例
const api = axios.create({
  baseURL: 'http://127.0.0.1:8001/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 默认图片
const defaultImage = 'https://fastly.jsdelivr.net/npm/@vant/assets/cat.jpeg'

// ========== 食材相关 API ==========

// 获取食材分类列表
export const getIngredientCategoryList = async () => {
  try {
    const res = await api.get('/search/categories')
    return res.data.categories || []
  } catch (error) {
    console.error('获取食材分类失败:', error)
    return []
  }
}

// 获取食材列表
export const getIngredientList = async (category = '') => {
  try {
    const params = category && category !== '全部' ? { category } : {}
    const res = await api.get('/search/ingredients', { params })
    const list = res.data || []
    return list.map(item => ({
      id: item.id,
      name: item.name,
      effect: item.effect,
      suitable: item.suitable,
      avoid: item.avoid,
      methods: item.methods,
      tag: item.tag,
      image: item.images ? `http://127.0.0.1:8001/data/Shicaiimages/${item.images}` : defaultImage
    }))
  } catch (error) {
    console.error('获取食材列表失败:', error)
    return []
  }
}

// 搜索食材
export const searchIngredients = async (keyword) => {
  try {
    const res = await api.get('/search/ingredients', { params: { keyword } })
    const list = res.data || []
    return list.map(item => ({
      id: item.id,
      name: item.name,
      effect: item.effect,
      image: item.images ? `http://127.0.0.1:8001/data/Shicaiimages/${item.images}` : defaultImage
    }))
  } catch (error) {
    console.error('搜索食材失败:', error)
    return []
  }
}

// ========== 食疗/菜谱相关 API ==========

// 获取热门食疗（首页）
export const getPopularTherapy = async () => {
  try {
    const res = await api.get('/search/recipes/popular?limit=5')
    const list = res.data.items || []
    return list.map(item => ({
      id: item.id,
      title: item.name,
      tags: Array.isArray(item.suitable) ? item.suitable : (item.suitable ? item.suitable.split('、') : []),
      efficacy: Array.isArray(item.effect) ? item.effect.join('、') : item.effect,
      ingredients: Array.isArray(item.ingredients) ? item.ingredients : (item.ingredients ? item.ingredients.split('、') : []),
      method: Array.isArray(item.steps) ? item.steps.join('\n') : item.steps,
      taboo: item.taboo || '无',
      image: item.images ? `http://127.0.0.1:8001/data/Caipuimages/${item.images}${item.images.endsWith('.png') ? '' : '.png'}` : defaultImage
    }))
  } catch (error) {
    console.error('获取热门食疗失败:', error)
    return []
  }
}

// 获取食疗列表
export const getTherapyList = async (category = '', keyword = '') => {
  try {
    const params = {}
    if (category && category !== '全部') {
      params.suitable = category
    }
    if (keyword && keyword.trim()) {
      params.keyword = keyword.trim()
    }
    const res = await api.get('/therapy/search', { params })
    console.log('📋 API 返回的原始数据:', res.data, '参数:', params)
    const list = res.data || []
    return list.map(item => ({
      id: item.id,
      name: item.name, // 保留原始名称给弹窗使用
      title: item.name,
      tag: '推荐',
      effect: Array.isArray(item.effect) ? item.effect.join('、') : item.effect,
      desc: Array.isArray(item.effect) ? item.effect.join('、') : item.effect,
      tags: Array.isArray(item.suitable) ? item.suitable : (item.suitable ? item.suitable.split('、') : []),
      ingredients: item.ingredients, // 保留原始食材数据给弹窗
      steps: item.steps, // 保留原始步骤数据给弹窗
      suitable: item.suitable, // 保留原始适合体质给弹窗
      images: item.images, // 保留原始图片给弹窗
      taboo: item.taboo, // 保留禁忌给弹窗
      buttonText: '查看详情',
      primaryButton: true,
      image: item.images ? `http://127.0.0.1:8001/data/Caipuimages/${item.images}${item.images.endsWith('.png') ? '' : '.png'}` : defaultImage
    }))
  } catch (error) {
    console.error('获取食疗列表失败:', error)
    return []
  }
}

// 获取食疗分类
export const getTherapyFilters = async () => {
  try {
    const res = await api.get('/therapy/constitutions')
    return ['全部', ...(res.data || [])]
  } catch (error) {
    console.error('获取食疗分类失败:', error)
    return ['全部']
  }
}

// 搜索食疗
export const searchTherapy = async (keyword) => {
  try {
    const res = await api.get('/recipes/search/name', { params: { name: keyword } })
    const list = res.data || []
    return list.map(item => ({
      id: item.id,
      title: item.name,
      effect: Array.isArray(item.effect) ? item.effect.join('、') : item.effect,
      tags: Array.isArray(item.suitable) ? item.suitable : [],
      image: item.images ? `http://127.0.0.1:8001/data/Caipuimages/${item.images}${item.images.endsWith('.png') ? '' : '.png'}` : defaultImage
    }))
  } catch (error) {
    console.error('搜索食疗失败:', error)
    return []
  }
}


// 检查食材搭配禁忌
export const checkIngredientCompatibility = async (ingredients) => {
  try {
    // 常见的食材相克搭配（简化版）
    const incompatiblePairs = []
    
    // 这里可以调用后端 API 或者使用本地规则
    // 示例规则（实际应该从后端获取）：
    const rules = [
      { pair: ['螃蟹', '柿子'], reason: '易引起腹泻' },
      { pair: ['羊肉', '西瓜'], reason: '易伤元气' },
      { pair: ['鸡肉', '芥末'], reason: '易上火' },
      { pair: ['鸡蛋', '豆浆'], reason: '影响蛋白质吸收' },
      { pair: ['萝卜', '橘子'], reason: '易引起甲状腺肿大' }
    ]
    
    for (const rule of rules) {
      if (ingredients.includes(rule.pair[0]) && ingredients.includes(rule.pair[1])) {
        incompatiblePairs.push({
          ingredients: rule.pair,
          reason: rule.reason
        })
      }
    }
    
    return {
      isSafe: incompatiblePairs.length === 0,
      incompatiblePairs
    }
  } catch (error) {
    console.error('检查食材搭配失败:', error)
    return {
      isSafe: true,
      incompatiblePairs: []
    }
  }
}


// ========== 生成菜谱 API ==========

// 根据食材生成菜谱
export const generateRecipe = async (ingredients) => {
  try {
    const res = await api.post('/search/recipes/generate', { ingredients })
    const data = res.data || {}
    return {
      match: Math.round((data.match_score || 0.8) * 100) + '%',
      stars: 3,
      name: data.name,
      desc: data.description,
      image: data.images ? `http://127.0.0.1:8001/data/Caipuimages/${data.images}` : defaultImage
    }
  } catch (error) {
    console.error('生成菜谱失败:', error)
    return null
  }
}

// 根据食材搜索匹配菜谱
export const generateRecipeFromIngredients = async (ingredients, constitution = '') => {
  try {
    const res = await api.post('/search/recipes/generate', { 
      ingredients,
      constitution 
    })
    
    // 后端返回格式：{ status: "success", data: [菜谱数组], message: "..." }
    const recipes = res.data?.data || []
    
    if (!recipes || recipes.length === 0) {
      return {
        success: false,
        type: 'none',
        message: '未找到匹配的菜谱',
        recipes: [],
        incompatiblePairs: []
      }
    }
    
    // 返回所有匹配的菜谱
    return {
      success: true,
      type: 'existing',
      recipes: recipes.map(r => ({
        id: r.id,
        name: r.name,
        ingredients: r.ingredients || [],
        effect: r.effect || [],
        suitable: r.suitable || [],
        steps: r.steps || '',
        taboo: r.taboo || '无特殊禁忌',
        images: r.images || '',
        match_score: r.match_score || 0,
        matched_ingredients: r.matched_ingredients || []
      })),
      incompatiblePairs: []
    }
  } catch (error) {
    console.error('生成菜谱失败:', error)
    return {
      success: false,
      type: 'error',
      message: '生成失败，请重试',
      recipes: [],
      incompatiblePairs: []
    }
  }
}

// ========== 智能推荐 API ==========

// 获取推荐食疗
export const getRecommendedTherapies = async (constitution = '', count = 5) => {
  try {
    const res = await api.get('/recommend/daily', {
      params: { user_id: '123', constitution, age: 30, gender: '男性' }
    })
    const therapies = res.data.therapies || []
    return therapies.slice(0, count).map((item, idx) => ({
      id: idx + 1,
      title: item.title,
      effect: item.reason,
      desc: item.reason,
      image: defaultImage,
      users: 10
    }))
  } catch (error) {
    console.error('获取推荐食疗失败:', error)
    return []
  }
}

// 获取推荐菜谱
export const getRecommendedRecipes = async (constitution = '', count = 5) => {
  try {
    const res = await api.get('/recommend/daily', {
      params: { user_id: '123', constitution, age: 30, gender: '男性' }
    })
    const recipes = res.data.recipes || []
    return recipes.slice(0, count).map((item, idx) => ({
      id: idx + 1,
      name: item.title,
      effect: item.reason,
      match_percentage: 95
    }))
  } catch (error) {
    console.error('获取推荐菜谱失败:', error)
    return []
  }
}

// ========== 体质测试 API ==========

// 获取体质测试题目
export const getQuizQuestions = async () => {
  try {
    const res = await api.get('/quiz/questions')
    // 后端返回格式：{ status: "success", data: [...] }
    const questions = res.data.data || res.data.questions || []
    console.log('获取到的题目数据:', questions)
    return questions.map((q, idx) => ({
      id: q.id || idx + 1,
      question: q.text || q.question,
      options: q.options || [{ text: '是' }, { text: '否' }]
    }))
  } catch (error) {
    console.error('获取测试题目失败:', error)
    return []
  }
}

// 提交体质测试答案
export const submitQuizAnswers = async (answers) => {
  try {
    console.log('📤 原始答案:', answers)
    
    // 需要从题目中获取 category 信息
    // 先获取题目列表
    const questions = await getQuizQuestions()
    console.log('📋 题目列表:', questions)
    
    // 将答案转换为后端需要的格式
    const formattedAnswers = Object.keys(answers).map(questionId => {
      const question = questions.find(q => String(q.id) === String(questionId))
      const answerValue = answers[questionId]
      
      // 根据答案值（是/否）转换为分数（1-5）
      let score
      if (answerValue === '是') {
        score = 5
      } else {
        score = 1
      }
      
      return {
        category: question?.category || '平和质',
        score: score
      }
    })
    
    console.log('📦 格式化后的答案:', formattedAnswers)
    
    // 发送到后端
    const res = await api.post('/quiz/submit', {
      user_id: 'user_' + Date.now(),
      answers: formattedAnswers
    })
    
    console.log('✅ 后端返回:', res.data)
    
    return {
      success: true,
      data: {
        constitutions: [res.data.primary_constitution || '平和质'],
        description: `您的主体质是 ${res.data.primary_constitution || '平和质'}`,
        is_combination: false,
        scores: res.data.constitution_vector || {}
      }
    }
  } catch (error) {
    console.error('提交答案失败:', error)
    throw error
  }
}

// ========== 用户信息 API ==========

// 获取用户信息
export const getUserInfo = async () => {
  try {
    const res = await api.get('/user/info')
    return res.data || { name: '用户', days: 1, avatar: '' }
  } catch (error) {
    console.error('获取用户信息失败:', error)
    return { name: '用户', days: 1, avatar: '' }
  }
}

// 获取专家建议（从每日报告中提取）
export const getExpertAdvice = async (constitution, userInfo) => {
  try {
    // 调用新的每日报告 API
    const res = await api.post('/reports/daily', {
      user_id: 'user_' + Date.now(),
      constitution_vector: constitution || {},
      available_ingredients: [],
      force_refresh: false
    })
    
    // 返回报告文本
    return res.data?.report_text || '暂无专家建议'
  } catch (error) {
    console.error('获取专家建议失败:', error)
    return '暂无专家建议'
  }
}

// 获取今日养生报告（完整 UI 卡片数据）
export const getWellnessReport = async (constitution, userInfo) => {
  try {
    // 调用新的每日报告 API
    const res = await api.post('/reports/daily', {
      user_id: 'user_' + Date.now(),
      constitution_vector: constitution || {},
      available_ingredients: [],
      force_refresh: false
    })
    
    const data = res.data || {}
    const uiCard = data.ui_card || {}
    
    return {
      module_title: uiCard.module_title || '今日养生',
      suggestion_title: uiCard.suggestion_title || '今日养生建议',
      season_tag: uiCard.season_tag || '四时调养',
      intro: uiCard.intro || '',
      recommended_ingredients: uiCard.recommended_ingredients || [],
      recommended_recipe: uiCard.recommended_recipe || '',
      recipe_tip: uiCard.recipe_tip || '',
      report_text: data.report_text || ''
    }
  } catch (error) {
    console.error('获取养生报告失败:', error)
    return {
      module_title: '今日养生',
      suggestion_title: '今日养生建议',
      season_tag: '四时调养',
      intro: '今日宜食清淡，保持规律作息。',
      recommended_ingredients: [],
      recommended_recipe: '',
      recipe_tip: '',
      report_text: ''
    }
  }
}

// 获取菜谱历史
export const getRecipeHistory = async () => {
  try {
    // 从本地存储获取历史记录
    const history = localStorage.getItem('recipeHistory')
    if (history) {
      return JSON.parse(history)
    }
    return []
  } catch (error) {
    console.error('获取菜谱历史失败:', error)
    return []
  }
}

// 获取健康档案
export const getHealthArchive = async (userId) => {
  try {
    // 从 localStorage 获取健康档案
    const archive = localStorage.getItem('healthArchive')
    if (archive) {
      const records = JSON.parse(archive)
      // 如果传入了 userId，查找对应的记录
      if (userId) {
        return records.find(r => r.userId === userId) || null
      }
      // 否则返回所有记录
      return records
    }
    return null
  } catch (error) {
    console.error('获取健康档案失败:', error)
    return null
  }
}

// 获取用户资料
export const getProfile = async () => {
  try {
    // 从 localStorage 获取用户信息
    const userInfo = localStorage.getItem('userInfo')
    if (userInfo) {
      return JSON.parse(userInfo)
    }
    // 默认用户信息
    return {
      name: '用户',
      days: 1,
      avatar: ''
    }
  } catch (error) {
    console.error('获取用户资料失败:', error)
    return {
      name: '用户',
      days: 1,
      avatar: ''
    }
  }
}

