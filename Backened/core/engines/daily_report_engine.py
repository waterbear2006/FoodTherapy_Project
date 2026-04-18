import csv
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
import os
import json
import asyncio
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()
@dataclass
class User:
    user_id: str
    constitution_vector: Dict[str, float] = field(default_factory=dict)
    previous_constitution_vector: Dict[str, float] = field(default_factory=dict)
    primary_constitution: str = ""

    def update_constitution(self, new_vector: Dict[str, float]) -> None:
        self.previous_constitution_vector = dict(self.constitution_vector)
        self.constitution_vector = {k: float(v) for k, v in new_vector.items()} if new_vector else {}
        # 只有在体质向量非空时才计算主导体质
        if self.constitution_vector:
            self.primary_constitution = max(self.constitution_vector, key=self.constitution_vector.get)
        else:
            self.primary_constitution = "平和质"  # 默认值

    def constitution_delta(self) -> Dict[str, float]:
        keys = set(self.constitution_vector) | set(self.previous_constitution_vector)
        return {
            key: round(self.constitution_vector.get(key, 0.0) - self.previous_constitution_vector.get(key, 0.0), 2)
            for key in sorted(keys)
        }


@dataclass
class Report:
    user_id: str
    report_date: str
    raw_results: Dict
    report_text: str


class _RecipeGraph:
    """食材 - 菜谱双向图：ingredient -> recipe、recipe -> ingredient。"""

    def __init__(self) -> None:
        self.neighbors: Dict[str, Set[str]] = {}

    def add_edge(self, u: str, v: str) -> None:
        self.neighbors.setdefault(u, set()).add(v)
        self.neighbors.setdefault(v, set()).add(u)

    def get_neighbors(self, node: str) -> List[str]:
        return list(self.neighbors.get(node, set()))


class DailyReportEngine:
    # 体质 -> 优先标签
    CONSTITUTION_TAG_MAP = {
        "平和质": ["健脾", "补气"],
        "气虚质": ["补气", "健脾"],
        "阳虚质": ["温阳", "补气"],
        "阴虚质": ["滋阴", "清热"],
        "痰湿质": ["健脾", "清热"],
        "湿热质": ["清热", "健脾"],
        "血瘀质": ["补血"],
        "气郁质": ["滋阴", "清热"],
        "特禀质": ["补气", "健脾"],
    }
    SOLAR_TERMS = [
        {"name": "立春", "start": "02-03", "end": "02-17", "season": "春季"},
        {"name": "雨水", "start": "02-18", "end": "03-04", "season": "春季"},
        {"name": "惊蛰", "start": "03-05", "end": "03-19", "season": "春季"},
        {"name": "春分", "start": "03-20", "end": "04-03", "season": "春季"},
        {"name": "清明", "start": "04-04", "end": "04-18", "season": "春季"},
        {"name": "谷雨", "start": "04-19", "end": "05-04", "season": "春季"},
        {"name": "立夏", "start": "05-05", "end": "05-19", "season": "夏季"},
        {"name": "小满", "start": "05-20", "end": "06-04", "season": "夏季"},
        {"name": "芒种", "start": "06-05", "end": "06-20", "season": "夏季"},
        {"name": "夏至", "start": "06-21", "end": "07-06", "season": "夏季"},
        {"name": "小暑", "start": "07-07", "end": "07-22", "season": "夏季"},
        {"name": "大暑", "start": "07-23", "end": "08-06", "season": "夏季"},
        {"name": "立秋", "start": "08-07", "end": "08-22", "season": "秋季"},
        {"name": "处暑", "start": "08-23", "end": "09-06", "season": "秋季"},
        {"name": "白露", "start": "09-07", "end": "09-22", "season": "秋季"},
        {"name": "秋分", "start": "09-23", "end": "10-07", "season": "秋季"},
        {"name": "寒露", "start": "10-08", "end": "10-22", "season": "秋季"},
        {"name": "霜降", "start": "10-23", "end": "11-06", "season": "秋季"},
        {"name": "立冬", "start": "11-07", "end": "11-21", "season": "冬季"},
        {"name": "小雪", "start": "11-22", "end": "12-06", "season": "冬季"},
        {"name": "大雪", "start": "12-07", "end": "12-21", "season": "冬季"},
        {"name": "冬至", "start": "12-22", "end": "01-04", "season": "冬季"},
        {"name": "小寒", "start": "01-05", "end": "01-19", "season": "冬季"},
        {"name": "大寒", "start": "01-20", "end": "02-02", "season": "冬季"},
    ]
    SEASON_TAG_MAP = {
        "春季": "疏肝·健脾",
        "夏季": "清热·祛湿",
        "秋季": "润燥·养阴",
        "冬季": "温中·补气",
    }

    def __init__(self) -> None:
        base_dir = Path(__file__).resolve().parent.parent.parent
        self.ingredients_path = base_dir / "data" / "shicai .csv"
        self.recipes_path = base_dir / "data" / "caipu.csv"
        self.ingredients: List[Dict] = []
        self.recipes: List[Dict] = []
        self.report_cache: Dict[Tuple[str, str], Report] = {}
        self.users: Dict[str, User] = {}
        self.graph = _RecipeGraph()
        self.recipe_by_name: Dict[str, Dict] = {}
        self.recipe_by_id: Dict[int, Dict] = {}

        api_key = os.getenv("AI_API_KEY")
        if api_key:
            self.client = AsyncOpenAI(
                api_key=api_key,
                base_url=os.getenv("AI_BASE_URL", "https://api.openai.com/v1")
            )
        else:
            self.client = None

        self._load_data()
        self._build_graph()

    def _split_multi_value(self, text: str, separators: Optional[List[str]] = None) -> List[str]:
        if not text:
            return []
        seps = separators or ["、", "，", ",", "/"]
        values = [text]
        for sep in seps:
            next_values = []
            for item in values:
                next_values.extend(item.split(sep))
            values = next_values
        return [v.strip() for v in values if v.strip()]

    def _load_data(self) -> None:
        with open(self.ingredients_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                row["id"] = int(row["id"])
                row["tag_list"] = self._split_multi_value(row.get("tag", ""))
                row["suitable_list"] = self._split_multi_value(row.get("suitable", ""))
                self.ingredients.append(row)

        with open(self.recipes_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                row["id"] = int(row["id"])
                row["ingredients_list"] = self._split_multi_value(row.get("ingredients", ""))
                row["suitable_list"] = self._split_multi_value(row.get("suitable", ""))
                self.recipes.append(row)
                self.recipe_by_name[row["name"]] = row
                self.recipe_by_id[row["id"]] = row

    def _build_graph(self) -> None:
        for recipe in self.recipes:
            recipe_name = recipe["name"]
            for ingredient_name in recipe["ingredients_list"]:
                self.graph.add_edge(ingredient_name, recipe_name)

    def _normalize_constitution(self, constitution: str) -> str:
        if constitution.endswith("体质"):
            return constitution.replace("体质", "质")
        return constitution

    def _get_or_create_user(self, user_id: str) -> User:
        if user_id not in self.users:
            self.users[user_id] = User(user_id=user_id)
        return self.users[user_id]

    def _top_tags_for_constitution(self, constitution: str) -> List[str]:
        constitution = self._normalize_constitution(constitution)
        return self.CONSTITUTION_TAG_MAP.get(constitution, ["健脾", "补气"])

    def _get_current_solar_term_and_season(self) -> Tuple[str, str]:
        today_str = datetime.now().strftime("%m-%d")
        for item in self.SOLAR_TERMS:
            start = item["start"]
            end = item["end"]
            if start <= end:
                if start <= today_str <= end:
                    return item["name"], item["season"]
            else:
                if today_str >= start or today_str <= end:
                    return item["name"], item["season"]
        return "立春", "春季"

    def _season_adjusted_tags(self, base_tags: List[str], season: str) -> List[str]:
        season_tag_boost = {
            "春季": ["健脾"],
            "夏季": ["清热"],
            "秋季": ["滋阴"],
            "冬季": ["温阳", "补气"],
        }
        tags = list(dict.fromkeys(base_tags + season_tag_boost.get(season, [])))
        return tags

    def _get_weather_modifiers(self, weather_data: Optional[Dict]) -> Tuple[Dict[str, float], List[str]]:
        if not weather_data:
            return {}, []
        
        modifiers = {}
        applied_tags = []
        
        # 提取数据，转成 float
        try:
            humidity = float(weather_data.get("humidity")) if weather_data.get("humidity") is not None else None
            temperature = float(weather_data.get("temperature")) if weather_data.get("temperature") is not None else None
        except (ValueError, TypeError):
            humidity = None
            temperature = None

        if humidity is not None:
            if humidity > 80:
                modifiers["利湿"] = 3.0
                modifiers["祛湿"] = 3.0
                modifiers["健脾"] = 1.0
                applied_tags.append("高湿利湿")
            elif humidity < 30:
                modifiers["润燥"] = 3.0
                modifiers["生津"] = 2.0
                applied_tags.append("干燥润燥")
                
        if temperature is not None:
            if temperature >= 32:
                modifiers["清热"] = 3.0
                modifiers["解暑"] = 3.0
                if "高温清热" not in applied_tags:
                    applied_tags.append("高温清热")
            elif temperature <= 10:
                modifiers["温阳"] = 3.0
                modifiers["散寒"] = 2.0
                if "寒冷散寒" not in applied_tags:
                    applied_tags.append("寒冷散寒")
                    
        return modifiers, applied_tags

    def _recommend_ingredients(self, constitution: str, tag_targets: List[str], top_k: int = 10, weather_modifiers: Optional[Dict[str, float]] = None) -> List[Dict]:
        constitution = self._normalize_constitution(constitution)
        weather_mods = weather_modifiers or {}
        scored = []
        for ingredient in self.ingredients:
            tag_hits = len(set(tag_targets) & set(ingredient["tag_list"]))
            suitable_hit = 1 if constitution in ingredient["suitable_list"] else 0
            
            # 环境因素权重叠加
            weather_bonus = 0.0
            for tag in ingredient["tag_list"]:
                if tag in weather_mods:
                    weather_bonus += weather_mods[tag]
                    
            score = tag_hits * 2 + suitable_hit + weather_bonus
            if score > 0:
                scored.append((score, ingredient))
        scored.sort(key=lambda item: item[0], reverse=True)
        return [item[1] for item in scored[:top_k]]

    def _dfs_recommend_recipes(
        self,
        available_ingredients: List[str],
        allowed_constitution: str,
        max_depth: int = 2,
        top_k: int = 8,
    ) -> List[Dict]:
        allowed_constitution = self._normalize_constitution(allowed_constitution)
        visited_recipe_names: Set[str] = set()
        candidate_results: List[Dict] = []

        def dfs(current_ingredient: str, depth: int, path_ingredients: Set[str]) -> None:
            if depth > max_depth:
                return
            for recipe_name in self.graph.get_neighbors(current_ingredient):
                if recipe_name in visited_recipe_names:
                    continue
                recipe = self.recipe_by_name.get(recipe_name)
                if not recipe:
                    continue
                if allowed_constitution not in recipe["suitable_list"]:
                    continue
                required = set(recipe["ingredients_list"])
                matched = required & path_ingredients
                match_rate = len(matched) / max(len(required), 1)
                if match_rate > 0:
                    candidate_results.append(
                        {
                            "recipe_id": recipe["id"],
                            "recipe_name": recipe_name,
                            "match_rate": round(match_rate, 2),
                            "matched_ingredients": sorted(list(matched)),
                            "required_ingredients": recipe["ingredients_list"],
                        }
                    )
                    visited_recipe_names.add(recipe_name)
                for next_ingredient in required:
                    if next_ingredient not in path_ingredients:
                        dfs(next_ingredient, depth + 1, path_ingredients | {next_ingredient})

        for ingredient in available_ingredients:
            dfs(ingredient, 0, {ingredient})

        candidate_results.sort(
            key=lambda item: (item["match_rate"], len(item["matched_ingredients"])),
            reverse=True,
        )
        return candidate_results[:top_k]

    def _build_rule_based_report_text(
        self,
        constitution: str,
        solar_term: str,
        season: str,
        tags: List[str],
        recipe_name: str,
        ingredient_names: List[str],
        applied_env_tags: List[str] = None
    ) -> Tuple[str, str, str]:
        env_tags_str = ""
        if applied_env_tags:
            env_tags_str = f"（当前遇到极端天气，已为您触发：{'、'.join(applied_env_tags)} 的调整）"
            
        intro = (
            f"当前处于{solar_term}（{season}），你的当日体质以{constitution}为主。"
            f"建议饮食围绕{('、'.join(tags[:2]) or '均衡调养')}展开。"
            f"{env_tags_str}"
        )
        report_text = (
            f"{intro} 推荐优先使用{('、'.join(ingredient_names[:3]) or '温和食材')}，"
            f"食疗可选{recipe_name}，少量多次、清淡烹调更稳妥。"
        )
        tip = (
            f"早餐或晚餐可尝试{recipe_name}，搭配{('、'.join(ingredient_names[:2]) or '当季食材')}，"
            "尽量避免生冷油腻。"
        )
        return intro, report_text, tip

    async def _get_ai_report_text(
        self,
        constitution: str,
        solar_term: str,
        season: str,
        tags: List[str],
        recipe_name: str,
        ingredient_names: List[str],
        weather_data: Optional[Dict] = None
    ) -> Optional[Tuple[str, str, str]]:
        if not self.client:
            return None
            
        weather_str = ""
        if weather_data:
            temperature = weather_data.get("temperature")
            humidity = weather_data.get("humidity")
            city = weather_data.get("city", "")
            if temperature is not None and humidity is not None:
                weather_str = f"当前天气：{city} 气温{temperature}℃，湿度{humidity}%。"

        prompt = (
            f"用户中医体质：{constitution}。\n"
            f"当前节气/季节：{solar_term}({season})。\n"
            f"{weather_str}\n"
            f"核心调理方向标签：{tags}。\n"
            f"推荐的核心食材：{ingredient_names[:3]}。\n"
            f"推荐的组方菜谱：{recipe_name}。\n\n"
            "请基于上述输入，像一位专业且耐心的老中医一样，给出一份今日养生建议。\n"
            "请务必结合【天气】和【节气】来论述体质调理的逻辑。\n"
            "返回严格的 JSON 格式：\n"
            "{\n"
            '  "intro": "一句话核心点评目前的体况与环境的关系",\n'
            '  "report_text": "详细但通俗的调理建议，字数不超过100字，需要自然融合推荐的食材和菜谱在内",\n'
            '  "tip": "一条简短实用的生活或者饮食小贴士"\n'
            "}"
        )
        try:
            response = await asyncio.wait_for(
                self.client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[{"role": "user", "content": prompt}],
                    response_format={"type": "json_object"}
                ),
                timeout=6.0
            )
            result = json.loads(response.choices[0].message.content)
            return result.get("intro", ""), result.get("report_text", ""), result.get("tip", "")
        except Exception as e:
            print(f"⚠️ [DailyReport Engine] AI 生成超时或失败，退化为规则模板：{e}")
            return None

    async def get_daily_report(
        self,
        user_id: str,
        constitution_vector: Dict[str, float],
        available_ingredients: Optional[List[str]] = None,
        force_refresh: bool = False,
        weather_data: Optional[Dict] = None,
    ) -> Dict:
        today = date.today().isoformat()
        cache_key = (user_id, today)
        if cache_key in self.report_cache and not force_refresh:
            report = self.report_cache[cache_key]
            payload = dict(report.raw_results)
            payload["report_text"] = report.report_text
            payload["cache_hit"] = True
            return payload

        user = self._get_or_create_user(user_id)
        user.update_constitution(constitution_vector)
        constitution = user.primary_constitution
        delta = user.constitution_delta()
        solar_term, season = self._get_current_solar_term_and_season()
        matched_tags = self._season_adjusted_tags(
            self._top_tags_for_constitution(constitution),
            season,
        )
        
        weather_modifiers, applied_env_tags = self._get_weather_modifiers(weather_data)

        recommended_ingredients = self._recommend_ingredients(
            constitution, matched_tags, weather_modifiers=weather_modifiers
        )
        ingredient_names = [item["name"] for item in recommended_ingredients]

        initial_ingredients = list(dict.fromkeys((available_ingredients or []) + ingredient_names[:3]))
        recipe_candidates = self._dfs_recommend_recipes(
            available_ingredients=initial_ingredients,
            allowed_constitution=constitution,
        )
        recipe_ids = [item["recipe_id"] for item in recipe_candidates]
        recipe_names = [item["recipe_name"] for item in recipe_candidates]

        best_recipe = recipe_candidates[0]["recipe_name"] if recipe_candidates else "山药小米粥"
        intro, report_text, tip = self._build_rule_based_report_text(
            constitution=constitution,
            solar_term=solar_term,
            season=season,
            tags=matched_tags,
            recipe_name=best_recipe,
            ingredient_names=ingredient_names,
            applied_env_tags=applied_env_tags,
        )
        
        # 尝试通过大模型赋予更为丰富的辩证文案
        ai_texts = await self._get_ai_report_text(
            constitution, solar_term, season, matched_tags, best_recipe, ingredient_names, weather_data
        )
        if ai_texts and len(ai_texts) == 3 and all(ai_texts):
            intro, report_text, tip = ai_texts

        season_tag = self.SEASON_TAG_MAP.get(season, "四时调养")
        ui_card = {
            "module_title": "今日养生",
            "suggestion_title": "今日养生建议",
            "season_tag": season_tag,
            "intro": intro,
            "recommended_ingredients": ingredient_names[:3],
            "recommended_recipe": best_recipe,
            "recipe_tip": tip,
        }

        raw_results = {
            "user_id": user_id,
            "date": today,
            "primary_constitution": constitution,
            "solar_term": solar_term,
            "season": season,
            "constitution_vector": {k: round(float(v), 2) for k, v in constitution_vector.items()},
            "constitution_delta": delta,
            "matched_tags": matched_tags,
            "environmental_tags": applied_env_tags,
            "weather_info": weather_data,
            "recommended_ingredients": ingredient_names,
            "recommended_recipe_ids": recipe_ids,
            "recommended_recipes": recipe_candidates,
            "ui_card": ui_card,
        }
        report = Report(
            user_id=user_id,
            report_date=today,
            raw_results=raw_results,
            report_text=report_text,
        )
        self.report_cache[cache_key] = report

        payload = dict(raw_results)
        payload["report_text"] = report_text
        payload["cache_hit"] = False
        return payload
