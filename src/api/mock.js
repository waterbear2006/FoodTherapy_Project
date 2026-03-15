/**
 * 模拟接口：用延迟模拟网络请求，返回与 UI 一致的模拟数据
 */

const delay = (ms = 300) => new Promise((r) => setTimeout(r, ms))

const defaultImage = 'https://fastly.jsdelivr.net/npm/@vant/assets/cat.jpeg'

// 今日养生报告
export async function getWellnessReport() {
  await delay()
  return {
    score: 88,
    change: '+2%',
    advice: '今日宜食山药芡实粥，健脾益气，建议少食生冷，适度散步。',
    detailLink: '#'
  }
}

// 食材分类
export async function getIngredientCategories() {
  await delay()
  return [
    { id: '1', icon: 'leaf', label: '补益类' },
    { id: '2', icon: 'water', label: '清热类' },
    { id: '3', icon: 'wind', label: '理气类' },
    { id: '4', icon: 'all', label: '全部' }
  ]
}

// 热门食疗（首页）
export async function getPopularTherapy() {
  await delay()
  return [
    {
      id: 1,
      title: '五指毛桃祛湿汤',
      tag: '推荐',
      desc: '健脾化湿，舒筋活络，适合春夏季节。',
      time: '45分钟',
      calorie: '180千卡',
      image: defaultImage
    },
    {
      id: 2,
      title: '百合莲子清心粥',
      tag: '应季',
      desc: '养阴润肺、清心安神、缓解夏季燥热。',
      time: '30分钟',
      calorie: '120千卡',
      image: defaultImage
    }
  ]
}

// AI 菜谱 - 根据食材生成推荐
export async function generateRecipe(ingredients) {
  await delay(600)
  return {
    match: '98%',
    stars: 3,
    name: '浓汁番茄炒蛋',
    desc: '经典国民菜，采用独家浓缩汤汁做法，让每一块鸡蛋都吸饱番茄的鲜甜。',
    image: defaultImage
  }
}

// AI 菜谱 - 历史生成列表
export async function getRecipeHistory() {
  await delay()
  return [
    { id: 1, name: '家常青椒肉丝', time: '两周前生成', difficulty: '简单', tags: ['青椒', '里脊肉'], image: '' },
    { id: 2, name: '轻食减脂沙拉', time: '上个月生成', difficulty: '极简', tags: ['生菜', '鸡胸肉'], image: '' }
  ]
}

// 智能推荐 - 体质标签
export async function getConstitutionTags() {
  await delay()
  return [
    { id: '1', label: '气虚体质', icon: '✓', active: true },
    { id: '2', label: '补气养血', icon: '🌿' },
    { id: '3', label: '温和调', icon: '🌡' }
  ]
}

// 智能推荐 - 针对性食疗方案
export async function getRecommendTherapyList() {
  await delay()
  return [
    {
      id: 1,
      name: '党参山药鸡汤',
      match: '98%',
      effect: '补中益气，健脾益肺',
      desc: '党参具有明显的补气效果，配合山药可增强脾胃运化，适合气虚导致的精神疲惫。',
      image: defaultImage,
      users: 12
    },
    {
      id: 2,
      name: '黄芪红枣小米粥',
      match: '92%',
      effect: '益气固表，养血安神',
      desc: '黄芪是补气之王，红枣补血，小米粥性平补中，作为早餐调理效果极佳。',
      image: defaultImage,
      time: '20分钟',
      calorie: '180千卡'
    }
  ]
}

// 智能推荐 - 今日调理建议
export async function getTodayAdvice() {
  await delay()
  return '气虚体质应注意防寒保暖，晨起可适度进行八段锦锻炼，避免过度劳累伤气。'
}

// 我的 - 用户资料
export async function getProfile() {
  await delay()
  return {
    name: '草本健康家',
    days: 128,
    avatar: ''
  }
}

// 我的 - 健康档案
export async function getHealthArchive() {
  await delay()
  return {
    score: 85,
    constitution: '气虚质',
    symptoms: '易疲劳、畏寒',
    body: '175cm | 70kg | 男',
    bmi: '22.8 (正常)',
    sleep: '7h 20m (良好)',
    water: '1200ml / 2000ml',
    steps: '8,432步',
    heartRate: '68次/分'
  }
}

// 我的 - 专家建议
export async function getExpertAdvice() {
  await delay()
  return '适宜补气养血，日常饮食应避开辛辣油腻，建议多饮党参红枣茶。'
}

// 食材百科 - 分类
export async function getIngredientCategoryList() {
  await delay()
  return ['全部', '补气', '补血', '清热', '养胃']
}

// 食材百科 - 列表（支持分类 keyword）
export async function getIngredientList(category = '全部', keyword = '') {
  await delay()
  const list = [
    { id: 1, name: '红枣', effect: '补气养血', image: defaultImage },
    { id: 2, name: '枸杞', effect: '滋补肝肾', image: defaultImage },
    { id: 3, name: '山药', effect: '健脾益胃', image: defaultImage },
    { id: 4, name: '莲子', effect: '养心安神', image: defaultImage },
    { id: 5, name: '百合', effect: '润肺止咳', image: defaultImage },
    { id: 6, name: '银耳', effect: '滋阴润肺', image: defaultImage }
  ]
  if (category !== '全部') {
    return list.filter((i) => i.effect.includes(category) || i.name.includes(keyword))
  }
  if (keyword) {
    return list.filter((i) => i.name.includes(keyword) || i.effect.includes(keyword))
  }
  return list
}

// 食疗方案 - 筛选条件
export async function getTherapyFilters() {
  await delay()
  return ['全部', '体质', '症状', '季节']
}

// 食疗方案 - 列表
export async function getTherapyList(filter = '全部', keyword = '') {
  await delay()
  return [
    {
      id: 1,
      title: '山药枸杞粥',
      tag: '推荐',
      desc: '补益脾胃，滋养肝肾。山药健脾益气，枸杞子滋补肝肾，明目驻颜。',
      tags: ['脾胃虚弱', '肝肾阴亏'],
      buttonText: '查看详情',
      primaryButton: true,
      image: defaultImage
    },
    {
      id: 2,
      title: '黄芪鸡汤',
      effect: '益气补虚，增强免疫力',
      tags: ['气血体虚', '冬季养生'],
      buttonText: '了解配方',
      primaryButton: false,
      image: defaultImage
    },
    {
      id: 3,
      title: '莲子百合汤',
      effect: '养心安神，润肺止咳',
      tags: ['心火旺盛', '秋季滋润'],
      buttonText: '了解配方',
      primaryButton: false,
      image: defaultImage
    },
    {
      id: 4,
      title: '生姜红枣茶',
      effect: '驱寒暖胃，补血养颜',
      tags: ['阳虚体寒', '女性虚弱'],
      buttonText: '了解配方',
      primaryButton: false,
      image: defaultImage
    }
  ]
}
