"""
[Business Engine] 智能推荐调度引擎 (AI 增强版)
职责：根据用户体质、当前节气和季节，生成个性化的食疗推荐方案。
实施功能：
- 获取当前节气和季节
- 根据体质、节气和季节生成推荐
- 根据年龄和性别调整推荐
- 调用 AI 生成推荐理由
- 组装并返回推荐结果
- 支持默认推荐理由，当 AI API 不可用时使用
"""
import os
import json
import asyncio
from typing import Optional, List
from datetime import datetime
from openai import AsyncOpenAI
from dotenv import load_dotenv
from models.recommendation import RecommendationItem

load_dotenv() # 加载 .env 里的 API_KEY

class RecommendEngine:
    def __init__(self):
        # 自动读取环境变量中的 API_KEY
        api_key = os.getenv("AI_API_KEY")
        if api_key:
            self.client = AsyncOpenAI(
                api_key=api_key,
                base_url=os.getenv("AI_BASE_URL", "https://api.openai.com/v1")
            )
        else:
            self.client = None
            print("⚠️ [RecommendEngine] 警告：未设置 AI_API_KEY 环境变量，将使用默认推荐理由")
        
        # 智能推荐理由本地缓存
        self._ai_cache = {}
        
        # 24节气列表
        self.solar_terms = [
            {"name": "立春", "start_date": "02-03", "end_date": "02-17"},
            {"name": "雨水", "start_date": "02-18", "end_date": "03-04"},
            {"name": "惊蛰", "start_date": "03-05", "end_date": "03-19"},
            {"name": "春分", "start_date": "03-20", "end_date": "04-03"},
            {"name": "清明", "start_date": "04-04", "end_date": "04-18"},
            {"name": "谷雨", "start_date": "04-19", "end_date": "05-04"},
            {"name": "立夏", "start_date": "05-05", "end_date": "05-19"},
            {"name": "小满", "start_date": "05-20", "end_date": "06-04"},
            {"name": "芒种", "start_date": "06-05", "end_date": "06-20"},
            {"name": "夏至", "start_date": "06-21", "end_date": "07-06"},
            {"name": "小暑", "start_date": "07-07", "end_date": "07-22"},
            {"name": "大暑", "start_date": "07-23", "end_date": "08-06"},
            {"name": "立秋", "start_date": "08-07", "end_date": "08-22"},
            {"name": "处暑", "start_date": "08-23", "end_date": "09-06"},
            {"name": "白露", "start_date": "09-07", "end_date": "09-22"},
            {"name": "秋分", "start_date": "09-23", "end_date": "10-07"},
            {"name": "寒露", "start_date": "10-08", "end_date": "10-22"},
            {"name": "霜降", "start_date": "10-23", "end_date": "11-06"},
            {"name": "立冬", "start_date": "11-07", "end_date": "11-21"},
            {"name": "小雪", "start_date": "11-22", "end_date": "12-06"},
            {"name": "大雪", "start_date": "12-07", "end_date": "12-21"},
            {"name": "冬至", "start_date": "12-22", "end_date": "01-04"},
            {"name": "小寒", "start_date": "01-05", "end_date": "01-19"},
            {"name": "大寒", "start_date": "01-20", "end_date": "02-02"}
        ]
        
        # 节气与季节的对应关系
        self.season_map = {
            "春季": ["立春", "雨水", "惊蛰", "春分", "清明", "谷雨"],
            "夏季": ["立夏", "小满", "芒种", "夏至", "小暑", "大暑"],
            "秋季": ["立秋", "处暑", "白露", "秋分", "寒露", "霜降"],
            "冬季": ["立冬", "小雪", "大雪", "冬至", "小寒", "大寒"]
        }
        
        # 体质与节气的推荐规则
        self.recommendation_rules = {
            "湿热体质": {
                "春季": {"therapies": ["针灸排毒", "中药熏蒸"], "recipes": ["清解绿豆汤", "凉拌苦瓜"], "ingredients": ["薏苡仁", "菊花"]},
                "夏季": {"therapies": ["针灸排毒", "中药熏蒸", "刮痧"], "recipes": ["清解绿豆汤", "凉拌苦瓜", "冬瓜薏米汤"], "ingredients": ["薏苡仁", "菊花", "绿豆"]},
                "秋季": {"therapies": ["针灸排毒"], "recipes": ["清解绿豆汤"], "ingredients": ["薏苡仁"]},
                "冬季": {"therapies": ["针灸排毒"], "recipes": ["清解绿豆汤"], "ingredients": ["薏苡仁"]}
            },
            "气虚体质": {
                "春季": {"therapies": ["艾灸", "推拿", "穴位按摩"], "recipes": ["黄芪鸡汤", "党参粥"], "ingredients": ["黄芪", "党参", "大枣"]},
                "夏季": {"therapies": ["艾灸", "推拿"], "recipes": ["黄芪鸡汤", "党参粥"], "ingredients": ["黄芪", "党参"]},
                "秋季": {"therapies": ["艾灸", "推拿"], "recipes": ["黄芪鸡汤"], "ingredients": ["黄芪", "大枣"]},
                "冬季": {"therapies": ["艾灸", "中药热敷"], "recipes": ["黄芪鸡汤", "当归生姜汤"], "ingredients": ["黄芪", "大枣"]}
            },
            "阳虚体质": {
                "春季": {"therapies": ["艾灸", "中药热敷"], "recipes": ["生姜羊肉汤"], "ingredients": ["生姜", "羊肉"]},
                "夏季": {"therapies": ["艾灸"], "recipes": ["生姜羊肉汤"], "ingredients": ["生姜", "羊肉"]},
                "秋季": {"therapies": ["艾灸", "中药热敷"], "recipes": ["生姜羊肉汤"], "ingredients": ["生姜", "羊肉"]},
                "冬季": {"therapies": ["艾灸", "中药热敷", "火龙灸"], "recipes": ["生姜羊肉汤", "当归生姜汤"], "ingredients": ["生姜", "羊肉"]}
            },
            "阴虚体质": {
                "春季": {"therapies": ["针灸", "推拿"], "recipes": ["银耳百合汤", "枸杞粥"], "ingredients": ["银耳", "百合"]},
                "夏季": {"therapies": ["针灸", "推拿"], "recipes": ["银耳百合汤", "西瓜汁"], "ingredients": ["银耳", "百合"]},
                "秋季": {"therapies": ["针灸", "推拿"], "recipes": ["银耳百合汤", "梨汤"], "ingredients": ["银耳", "梨"]},
                "冬季": {"therapies": ["针灸"], "recipes": ["银耳百合汤"], "ingredients": ["银耳"]}
            },
            "痰湿体质": {
                "春季": {"therapies": ["针灸", "推拿", "刮痧"], "recipes": ["薏米粥", "茯苓粥"], "ingredients": ["薏米", "茯苓"]},
                "夏季": {"therapies": ["针灸", "推拿", "刮痧"], "recipes": ["薏米粥", "冬瓜汤"], "ingredients": ["薏米", "冬瓜"]},
                "秋季": {"therapies": ["针灸", "推拿"], "recipes": ["薏米粥"], "ingredients": ["薏米"]},
                "冬季": {"therapies": ["针灸"], "recipes": ["薏米粥"], "ingredients": ["薏米"]}
            },
            "血瘀体质": {
                "春季": {"therapies": ["针灸", "推拿", "拔罐"], "recipes": ["当归汤", "桃仁粥"], "ingredients": ["当归", "桃仁"]},
                "夏季": {"therapies": ["针灸", "推拿"], "recipes": ["当归汤", "桃仁粥"], "ingredients": ["当归", "桃仁"]},
                "秋季": {"therapies": ["针灸", "推拿", "拔罐"], "recipes": ["当归汤", "桃仁粥"], "ingredients": ["当归", "桃仁"]},
                "冬季": {"therapies": ["针灸", "推拿", "中药热敷"], "recipes": ["生姜当归汤"], "ingredients": ["当归", "生姜"]}
            },
            "气郁体质": {
                "春季": {"therapies": ["针灸", "推拿", "心理疏导"], "recipes": ["玫瑰花茶", "合欢粥"], "ingredients": ["玫瑰花", "合欢花"]},
                "夏季": {"therapies": ["针灸", "推拿"], "recipes": ["玫瑰花茶"], "ingredients": ["玫瑰花"]},
                "秋季": {"therapies": ["针灸", "推拿", "心理疏导"], "recipes": ["玫瑰花茶", "百合粥"], "ingredients": ["玫瑰花", "百合"]},
                "冬季": {"therapies": ["针灸", "推拿"], "recipes": ["玫瑰花茶"], "ingredients": ["玫瑰花"]}
            },
            "特禀体质": {
                "春季": {"therapies": ["针灸", "推拿"], "recipes": ["黄芪粥", "防风粥"], "ingredients": ["黄芪", "防风"]},
                "夏季": {"therapies": ["针灸", "推拿"], "recipes": ["黄芪粥"], "ingredients": ["黄芪"]},
                "秋季": {"therapies": ["针灸", "推拿"], "recipes": ["黄芪粥", "百合粥"], "ingredients": ["黄芪", "百合"]},
                "冬季": {"therapies": ["针灸", "推拿"], "recipes": ["黄芪粥"], "ingredients": ["黄芪"]}
            },
            "平和体质": {
                "春季": {"therapies": ["针灸", "推拿"], "recipes": ["营养粥", "养生汤"], "ingredients": ["枸杞", "红枣"]},
                "夏季": {"therapies": ["针灸"], "recipes": ["营养粥", "绿豆汤"], "ingredients": ["枸杞", "绿豆"]},
                "秋季": {"therapies": ["针灸", "推拿"], "recipes": ["营养粥", "梨汤"], "ingredients": ["枸杞", "梨"]},
                "冬季": {"therapies": ["针灸", "推拿"], "recipes": ["营养粥"], "ingredients": ["枸杞", "红枣"]}
            }
        }
        
        # 专业中医知识库
        self.tcm_knowledge_base = {
            "艾灸": "通过燃烧艾叶产生的温热刺激作用于足三里、气海等穴位，具有温补元气、通经活络、升阳举陷之效，能显著改善神疲乏力之态。",
            "推拿": "以揉、按、推等手法作用于经络，旨在疏通气机、调理脏腑，对缓解周身酸楚、增强机体运化能力具有传统疗效。",
            "穴位按摩": "针对气海、太白等补益要穴进行按揉，旨在激发生物气血，调理脏腑机能，通过经络传导达到增智益神、强健体魄的目的。",
            "针灸": "针刺特定腧穴以调理经络气血，对阳虚补火、阴虚滋润具有精准辨证作用，是中医内病外治的核心手段。",
            "中药热敷": "利用药性与热力的双重作用渗透肌肤，温经散寒，尤其适合改善虚冷体质，促进局部气血巡行。",
            "黄芪鸡汤": "选取上等黄芪与老母鸡炖煮，补气固表、脱毒排脓。黄芪为补气之要药，与鸡肉相伍，能极大增强机体正气。",
            "生姜羊肉汤": "温中散寒、补肾壮阳。羊肉性温热，配以生姜之辛温，对阳虚怕冷者具有显著的食疗改善作用。",
            "银耳百合汤": "滋阴润肺、宁心安神。银耳素有‘平民燕窝’之称，与百合共奏清心降火、润燥之功，最为阴虚者所宜。"
        }

    def get_current_solar_term(self):
        """获取当前的节气"""
        today = datetime.now()
        today_str = today.strftime("%m-%d")
        for term in self.solar_terms:
            if term["start_date"] > term["end_date"]: # 跨年
                if today_str >= term["start_date"] or today_str <= term["end_date"]:
                    return term["name"]
            elif term["start_date"] <= today_str <= term["end_date"]:
                return term["name"]
        return "立春"
    
    def get_season_by_solar_term(self, solar_term):
        """根据节气获取季节"""
        for season, terms in self.season_map.items():
            if solar_term in terms:
                return season
        return "春季"

    async def generate_recipe_details(self, recipe_name: str, ingredients: List[str]) -> dict:
        """为没有具体做法的菜谱生成详细的介绍和做法步骤"""
        if not self.client:
            return {
                "introduction": f"{recipe_name} 是一道结合中医食疗理念的养生佳肴，搭配适当食材，助您调理身体。",
                "steps": ["将所有食材洗净备用。", "结合常规健康烹饪方法进行处理。", "出锅前调味即可。"]
            }
        prompt = f"菜谱名称: {recipe_name}\n主要食材: {', '.join(ingredients)}\n请返回JSON格式：{{\"introduction\": \"100字介绍\", \"steps\": [\"步骤1\", \"步骤2\"]}}"
        try:
            response = await self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
        except Exception:
            return {"introduction": "暂无介绍", "steps": ["具体步骤请咨询营养师"]}

    async def _get_ai_reasons(self, constitution: str, solar_term: str, season: str, items: list, weather_data: Optional[dict] = None) -> dict:
        """批量生成推荐理由 (带缓存与名医兜底)"""
        cache_key = (constitution, solar_term, str(weather_data), tuple(sorted(items)))
        if cache_key in self._ai_cache:
            return self._ai_cache[cache_key]

        if not self.client:
            return self._get_fallback_reasons(constitution, solar_term, items)

        weather_str = ""
        if weather_data:
            temperature = weather_data.get("temperature")
            humidity = weather_data.get("humidity")
            city = weather_data.get("city", "")
            if temperature is not None and humidity is not None:
                weather_str = f", 当前天气: {city}气温{temperature}℃ 湿度{humidity}%"

        prompt = f"体质: {constitution}, 节气: {solar_term}{weather_str}\n项目: {items}\n为每个项目写50字专业中医理由(如有天气请结合)，返回JSON: {{\"项目名\": \"理由\"}}"
        try:
            import time
            start = time.time()
            response = await asyncio.wait_for(
                self.client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[{"role": "user", "content": prompt}],
                    response_format={"type": "json_object"}
                ),
                timeout=5.0
            )
            reasons = json.loads(response.choices[0].message.content)
            self._ai_cache[cache_key] = reasons
            print(f"📖 [AI Debug] 成功获取理由 (耗时 {time.time()-start:.1f}s)")
            return reasons
        except Exception as e:
            print(f"⚠️ [AI Debug] 启动名医兜底: {e}")
            return self._get_fallback_reasons(constitution, solar_term, items)

    def _get_fallback_reasons(self, constitution: str, solar_term: str, items: list) -> dict:
        """名医兜底逻辑"""
        reasons = {}
        from core.preloader import ingredient_db
        for item in items:
            s_item = str(item)
            if s_item in self.tcm_knowledge_base:
                reasons[s_item] = f"{self.tcm_knowledge_base[s_item]} (《饮食须知》合『{solar_term}』时令推荐)"
            else:
                effect_str = ""
                # 首先在主食材库中查找
                for ing in ingredient_db.values():
                    if ing.get("name") == s_item:
                        effect_str = ing.get("effect", "")
                        break
                # 如果没找到，在菜谱库中查找 tag 或 effect
                if not effect_str:
                    from api.therapy import therapy_service
                    for recipe in therapy_service.recipes:
                        if recipe.name == s_item:
                            tags = recipe.effect
                            if tags:
                                effect_str = "、".join(tags) if isinstance(tags, list) else str(tags)
                            break
                            
                if effect_str:
                    reasons[s_item] = f"{effect_str} (依《本草纲目》合『{solar_term}』时令推荐)"
                else:
                    reasons[s_item] = f"对症调理{constitution} (中医典籍合『{solar_term}』时令推荐)"
        return reasons

    async def get_smart_recommendations(self, user_id: str, constitution: str, age: Optional[int] = None, gender: Optional[str] = None, weather_data: Optional[dict] = None):
        """主推荐调度逻辑"""
        import time
        start_t = time.time()
        import random
        from api.therapy import therapy_service
        from core.preloader import ingredient_db

        solar_term = self.get_current_solar_term()
        season = self.get_season_by_solar_term(solar_term)
        
        # 挑选项目
        matched_recipes = therapy_service.query(constitution=constitution) or therapy_service.query()
        selected_recipes = random.sample(matched_recipes, min(3, len(matched_recipes)))

        matched_ingredients = [v for k, v in ingredient_db.items() if constitution in str(v.get('suitable', ''))] or list(ingredient_db.values())
        selected_ingredients = random.sample(matched_ingredients, min(3, len(matched_ingredients)))
        
        rule_key = constitution if "体质" in constitution else constitution + "体质"
        therapies_str = self.recommendation_rules.get(rule_key, {}).get(season, {}).get("therapies", ["艾灸", "推拿"])
        
        items_for_ai = therapies_str + [r.name for r in selected_recipes] + [i.get('name', '') for i in selected_ingredients]
        reasons_map = await self._get_ai_reasons(constitution, solar_term, season, items_for_ai, weather_data=weather_data)

        return {
            "constitution": constitution,
            "solar_term": solar_term,
            "season": season,
            "weather": weather_data,
            "summary": f"针对{constitution}，{solar_term}期间的专属方案。",
            "therapies": [RecommendationItem(title=t, reason=reasons_map.get(t)) for t in therapies_str],
            "recipes": [RecommendationItem(id=r.id, title=r.name, reason=reasons_map.get(r.name), image=getattr(r, 'images', '')) for r in selected_recipes],
            "ingredients": [RecommendationItem(id=i.get('id', 0), title=i.get('name', ''), reason=reasons_map.get(i.get('name', '')), image=i.get('images', '')) for i in selected_ingredients]
        }
