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
        # 如果是 DeepSeek，base_url 换成 https://api.deepseek.com
        api_key = os.getenv("AI_API_KEY")
        if api_key:
            self.client = AsyncOpenAI(
                api_key=api_key,
                base_url=os.getenv("AI_BASE_URL", "https://api.openai.com/v1")
            )
        else:
            self.client = None
            print("⚠️ [RecommendEngine] 警告：未设置 AI_API_KEY 环境变量，将使用默认推荐理由")
        # 24节气列表及对应日期范围（考虑到每年的微小变化）
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
        
        # 体质与节气的推荐规则（更详细）
        self.recommendation_rules = {
            "湿热体质": {
                "春季": {
                    "therapies": ["针灸排毒", "中药熏蒸"],
                    "recipes": ["清解绿豆汤", "凉拌苦瓜"],
                    "ingredients": ["薏苡仁", "菊花"]
                },
                "夏季": {
                    "therapies": ["针灸排毒", "中药熏蒸", "刮痧"],
                    "recipes": ["清解绿豆汤", "凉拌苦瓜", "冬瓜薏米汤", "黄瓜汁"],
                    "ingredients": ["薏苡仁", "菊花", "绿豆", "冬瓜", "黄瓜"]
                },
                "秋季": {
                    "therapies": ["针灸排毒", "中药熏蒸"],
                    "recipes": ["清解绿豆汤", "凉拌苦瓜"],
                    "ingredients": ["薏苡仁", "菊花"]
                },
                "冬季": {
                    "therapies": ["针灸排毒"],
                    "recipes": ["清解绿豆汤"],
                    "ingredients": ["薏苡仁"]
                }
            },
            "气虚体质": {
                "春季": {
                    "therapies": ["艾灸", "推拿", "穴位按摩"],
                    "recipes": ["黄芪鸡汤", "党参粥", "大枣粥"],
                    "ingredients": ["黄芪", "党参", "大枣", "山药"]
                },
                "夏季": {
                    "therapies": ["艾灸", "推拿"],
                    "recipes": ["黄芪鸡汤", "党参粥"],
                    "ingredients": ["黄芪", "党参", "大枣"]
                },
                "秋季": {
                    "therapies": ["艾灸", "推拿"],
                    "recipes": ["黄芪鸡汤"],
                    "ingredients": ["黄芪", "大枣"]
                },
                "冬季": {
                    "therapies": ["艾灸", "中药热敷"],
                    "recipes": ["黄芪鸡汤", "当归生姜汤"],
                    "ingredients": ["黄芪", "大枣", "当归"]
                }
            },
            "阳虚体质": {
                "春季": {
                    "therapies": ["艾灸", "中药热敷"],
                    "recipes": ["生姜羊肉汤"],
                    "ingredients": ["生姜", "羊肉"]
                },
                "夏季": {
                    "therapies": ["艾灸"],
                    "recipes": ["生姜羊肉汤"],
                    "ingredients": ["生姜", "羊肉"]
                },
                "秋季": {
                    "therapies": ["艾灸", "中药热敷"],
                    "recipes": ["生姜羊肉汤"],
                    "ingredients": ["生姜", "羊肉"]
                },
                "冬季": {
                    "therapies": ["艾灸", "中药热敷", "火龙灸"],
                    "recipes": ["生姜羊肉汤", "当归生姜汤", "附子汤"],
                    "ingredients": ["生姜", "羊肉", "当归", "附子"]
                }
            },
            "阴虚体质": {
                "春季": {
                    "therapies": ["针灸", "推拿"],
                    "recipes": ["银耳百合汤", "枸杞粥"],
                    "ingredients": ["银耳", "百合", "枸杞"]
                },
                "夏季": {
                    "therapies": ["针灸", "推拿"],
                    "recipes": ["银耳百合汤", "枸杞粥", "西瓜汁"],
                    "ingredients": ["银耳", "百合", "枸杞", "西瓜"]
                },
                "秋季": {
                    "therapies": ["针灸", "推拿"],
                    "recipes": ["银耳百合汤", "枸杞粥", "梨汤"],
                    "ingredients": ["银耳", "百合", "枸杞", "梨"]
                },
                "冬季": {
                    "therapies": ["针灸"],
                    "recipes": ["银耳百合汤", "枸杞粥"],
                    "ingredients": ["银耳", "百合", "枸杞"]
                }
            },
            "痰湿体质": {
                "春季": {
                    "therapies": ["针灸", "推拿", "刮痧"],
                    "recipes": ["薏米粥", "茯苓粥"],
                    "ingredients": ["薏米", "茯苓", "陈皮"]
                },
                "夏季": {
                    "therapies": ["针灸", "推拿", "刮痧"],
                    "recipes": ["薏米粥", "茯苓粥", "冬瓜汤"],
                    "ingredients": ["薏米", "茯苓", "陈皮", "冬瓜"]
                },
                "秋季": {
                    "therapies": ["针灸", "推拿"],
                    "recipes": ["薏米粥", "茯苓粥"],
                    "ingredients": ["薏米", "茯苓", "陈皮"]
                },
                "冬季": {
                    "therapies": ["针灸"],
                    "recipes": ["薏米粥"],
                    "ingredients": ["薏米", "茯苓"]
                }
            },
            "血瘀体质": {
                "春季": {
                    "therapies": ["针灸", "推拿", "拔罐"],
                    "recipes": ["当归汤", "桃仁粥"],
                    "ingredients": ["当归", "桃仁", "红花"]
                },
                "夏季": {
                    "therapies": ["针灸", "推拿"],
                    "recipes": ["当归汤", "桃仁粥"],
                    "ingredients": ["当归", "桃仁", "红花"]
                },
                "秋季": {
                    "therapies": ["针灸", "推拿", "拔罐"],
                    "recipes": ["当归汤", "桃仁粥"],
                    "ingredients": ["当归", "桃仁", "红花"]
                },
                "冬季": {
                    "therapies": ["针灸", "推拿", "中药热敷"],
                    "recipes": ["当归汤", "桃仁粥", "生姜当归汤"],
                    "ingredients": ["当归", "桃仁", "红花", "生姜"]
                }
            },
            "气郁体质": {
                "春季": {
                    "therapies": ["针灸", "推拿", "心理疏导"],
                    "recipes": ["玫瑰花茶", "合欢粥"],
                    "ingredients": ["玫瑰花", "合欢花", "柴胡"]
                },
                "夏季": {
                    "therapies": ["针灸", "推拿"],
                    "recipes": ["玫瑰花茶", "合欢粥"],
                    "ingredients": ["玫瑰花", "合欢花", "柴胡"]
                },
                "秋季": {
                    "therapies": ["针灸", "推拿", "心理疏导"],
                    "recipes": ["玫瑰花茶", "合欢粥", "百合粥"],
                    "ingredients": ["玫瑰花", "合欢花", "柴胡", "百合"]
                },
                "冬季": {
                    "therapies": ["针灸", "推拿"],
                    "recipes": ["玫瑰花茶", "合欢粥"],
                    "ingredients": ["玫瑰花", "合欢花", "柴胡"]
                }
            },
            "特禀体质": {
                "春季": {
                    "therapies": ["针灸", "推拿"],
                    "recipes": ["黄芪粥", "防风粥"],
                    "ingredients": ["黄芪", "防风", "白术"]
                },
                "夏季": {
                    "therapies": ["针灸", "推拿"],
                    "recipes": ["黄芪粥", "防风粥"],
                    "ingredients": ["黄芪", "防风", "白术"]
                },
                "秋季": {
                    "therapies": ["针灸", "推拿"],
                    "recipes": ["黄芪粥", "防风粥", "百合粥"],
                    "ingredients": ["黄芪", "防风", "白术", "百合"]
                },
                "冬季": {
                    "therapies": ["针灸", "推拿"],
                    "recipes": ["黄芪粥", "防风粥"],
                    "ingredients": ["黄芪", "防风", "白术"]
                }
            },
            "平和体质": {
                "春季": {
                    "therapies": ["针灸", "推拿"],
                    "recipes": ["营养粥", "养生汤"],
                    "ingredients": ["枸杞", "红枣", "山药"]
                },
                "夏季": {
                    "therapies": ["针灸"],
                    "recipes": ["营养粥", "养生汤", "绿豆汤"],
                    "ingredients": ["枸杞", "红枣", "山药", "绿豆"]
                },
                "秋季": {
                    "therapies": ["针灸", "推拿"],
                    "recipes": ["营养粥", "养生汤", "梨汤"],
                    "ingredients": ["枸杞", "红枣", "山药", "梨"]
                },
                "冬季": {
                    "therapies": ["针灸", "推拿"],
                    "recipes": ["营养粥", "养生汤", "生姜汤"],
                    "ingredients": ["枸杞", "红枣", "山药", "生姜"]
                }
            }
        }

    def get_current_solar_term(self):
        """
        获取当前的节气
        """
        today = datetime.now()
        today_str = today.strftime("%m-%d")
        
        # 找到当前日期对应的节气
        for term in self.solar_terms:
            start_date = term["start_date"]
            end_date = term["end_date"]
            
            # 处理跨年的情况
            if start_date > end_date:
                if today_str >= start_date or today_str <= end_date:
                    return term["name"]
            else:
                if today_str >= start_date and today_str <= end_date:
                    return term["name"]
        
        return "立春" # 默认返回立春
    
    def get_season_by_solar_term(self, solar_term):
        """
        根据节气获取季节
        """
        for season, terms in self.season_map.items():
            if solar_term in terms:
                return season
        return "春季" # 默认返回春季

    async def generate_recipe_details(self, recipe_name: str, ingredients: List[str]) -> dict:
        """
        为没有具体做法的菜谱生成详细的介绍和做法步骤
        """
        # 如果没有设置 API 密钥，直接返回默认文本
        if not self.client:
            return {
                "introduction": f"{recipe_name} 是一道结合中医食疗理念的养生佳肴，搭配适当食材，助您调理身体。",
                "steps": [
                    "将所有食材洗净备用。",
                    "结合常规健康烹饪方法（如清蒸、炖煮或少油快炒）进行处理。",
                    "出锅前根据个人口味适量调味即可食用。"
                ]
            }
            
        ingredients_str = ", ".join(ingredients) if ingredients else "常规食材"
        prompt = f"""
        任务: 请你扮演一位精通中医食疗和厨艺的药膳大师。
        当前需要为一个食疗菜谱生成“整体介绍”和“详细的制作步骤”。
        菜谱名称: {recipe_name}
        主要食材: {ingredients_str}
        
        要求:
        1. 整体介绍 (introduction): 100字左右，结合食材在中医上的寒热温凉、归经，描述这道菜的食疗功效与特色。
        2. 制作步骤 (steps): 提供详细可行、普通家庭可操作的烹饪步骤，用字符串数组形式返回。
        3. 请务必采用直接返回 JSON 的方式，必须使用以下格式，不要包含Markdown标记(` ```json `):
        {{
            "introduction": "此处填写整体介绍...",
            "steps": [
                "步骤1...",
                "步骤2..."
            ]
        }}
        """

        try:
            response = await self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "你是一位中医食疗养生专家兼厨艺大师，擅长以深入浅出的话语解释菜品的功效并提供详细可行的烹饪步骤。"},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"AI 生成菜谱做法失败: {e}")
            return {
                "introduction": f"{recipe_name} 是一道营养丰富的养生佳肴，适合日常保健补益。",
                "steps": [
                    "准备好所有食材并清理干净。",
                    "采用慢火炖煮或少油烹饪的方式进行制作。",
                    "最后根据个人口味适量添加调味料即可。"
                ]
            }

    async def _get_ai_reasons(self, constitution: str, solar_term: str, season: str, items: list) -> dict:
        """
        核心 AI 调用逻辑：批量生成推荐理由
        """
        # 如果没有设置 API 密钥，直接返回默认理由
        if not self.client:
            return {item: "符合您的健康体质、当前节气和季节" for item in items} # 兜底逻辑
        
        # 1. 构造 Prompt
        items_str = ", ".join(items)
        prompt = f"""
        患者体质: {constitution}
        当前节气: {solar_term}
        当前季节: {season}
        推荐项目: [{items_str}]
        任务: 请以名老中医的口吻，为每个项目撰写一段15字以内的中医原理解释，说明其适合该体质、当前节气和季节的道理。
        要求: 
        1. 使用中医经典术语，如阴阳五行、经络气血、寒热虚实等
        2. 结合《黄帝内经》《伤寒杂病论》等经典理论
        3. 语气沉稳、专业，体现行医多年的经验与智慧
        4. 严禁现代白话，保持中医传统表述风格
        5. 直接返回 JSON 格式，格式如下: 
        {{"项目名": "理由", ...}}
        """

        try:
            response = await self.client.chat.completions.create(
                model="deepseek-chat", # 或 gpt-4o-mini
                messages=[
                    {"role": "system", "content": "你是一位行医数十年的名老中医，精通《黄帝内经》《伤寒杂病论》等经典著作，擅长根据体质、节气和季节进行辨证施治。你的语言风格古朴典雅，充满中医智慧，善于用经典理论解释食疗原理。"},
                    {"role": "user", "content": prompt}
                ],
                response_format={{"type": "json_object"}} # 强制返回 JSON
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"AI 接口调用失败: {e}")
            return {item: "符合您的健康体质、当前节气和季节" for item in items} # 兜底逻辑

    async def get_smart_recommendations(self, user_id: str, constitution: str, age: Optional[int] = None, gender: Optional[str] = None):
        """
        获取智能推荐 (已直接对接本地纯净数据集 caipu/shicai)
        """
        import random
        from api.therapy import therapy_service
        from core.preloader import ingredient_db
        from models.recommendation import RecommendationItem

        # 获取当前节气和季节
        solar_term = self.get_current_solar_term()
        season = self.get_season_by_solar_term(solar_term)
        
        # 1. 真实食疗食谱推荐
        matched_recipes = therapy_service.query(constitution=constitution)
        if not matched_recipes:
            # 兼容：如果该体质没有严格匹配的菜谱，则放宽至整个数据库随机
            matched_recipes = therapy_service.query()
        # 随机挑选3条避免每次推荐重复视觉疲劳
        selected_recipes = random.sample(matched_recipes, min(3, len(matched_recipes)))

        # 2. 真实食材推荐
        matched_ingredients = []
        for ing_id, ing_data in ingredient_db.items():
            suitable = ing_data.get('suitable', [])
            if isinstance(suitable, str):
                if constitution in suitable: 
                    matched_ingredients.append(ing_data)
            elif isinstance(suitable, list):
                if constitution in suitable or any(constitution in s for s in suitable):
                    matched_ingredients.append(ing_data)
        if not matched_ingredients:
            matched_ingredients = list(ingredient_db.values())
        selected_ingredients = random.sample(matched_ingredients, min(3, len(matched_ingredients)))
        
        # 3. 疗法推荐 (因为疗法不包含图片且为操作手段，继续保留规则库过滤)
        rule_constitution_key = constitution
        if rule_constitution_key.endswith("质") and not rule_constitution_key.endswith("体质"):
            rule_constitution_key = rule_constitution_key.replace("质", "体质")
            
        therapies_str = ["艾灸", "推拿"]
        if rule_constitution_key in self.recommendation_rules:
            c_rules = self.recommendation_rules[rule_constitution_key]
            if season in c_rules:
                therapies_str = c_rules[season].get("therapies", therapies_str)
            else:
                therapies_str = c_rules.get("春季", {}).get("therapies", therapies_str)
        
        # 4. 请求 AI 批量生成理由
        items_for_ai = therapies_str + \
                       [r.name for r in selected_recipes] + \
                       [i.get('name', '未知名') for i in selected_ingredients]
                       
        reasons_map = await self._get_ai_reasons(constitution, solar_term, season, items_for_ai)

        # 5. 封装置为含有真实 ID 和 image 的 RecommendationItem
        therapies_obj = [
            RecommendationItem(title=t, reason=reasons_map.get(t, "依照您的体质特别推荐的日常疗法"))
            for t in therapies_str
        ]
        
        recipes_obj = [
            RecommendationItem(
                id=r.id, 
                title=r.name, 
                reason=reasons_map.get(r.name, "搭配适当食材，助您调理身体"), 
                image=getattr(r, 'images', getattr(r, 'image', ''))
            )
            for r in selected_recipes
        ]
        
        ingredients_obj = [
            RecommendationItem(
                id=i.get('id', 0), 
                title=i.get('name', ''), 
                reason=reasons_map.get(i.get('name', ''), "符合当前体质日常所需的绝佳食材"), 
                image=i.get('image', i.get('images', ''))
            )
            for i in selected_ingredients
        ]

        # 6. 构造总结
        summary = f"基于您最近的评估，由于您偏向{constitution}，当前节气为{solar_term}，处于{season}。"
        if age:
            summary += f"同时考虑到您的年龄（{age}岁）"
        if gender:
            summary += f"与特征（{gender}），"
        summary += "以下是系统连线中医库为您定制的高清美味且完全真实的食疗推荐方案。"

        return {
            "constitution": constitution,
            "solar_term": solar_term,
            "season": season,
            "age": age,
            "gender": gender,
            "summary": summary,
            "therapies": therapies_obj,
            "recipes": recipes_obj,
            "ingredients": ingredients_obj
        }
