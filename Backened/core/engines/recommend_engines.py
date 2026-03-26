"""
[Business Engine] 智能推荐调度引擎 (规则版)
职责：根据用户体质、当前节气和季节，生成个性化的食疗推荐方案。
"""
import os
import sys
from typing import Optional, List
from datetime import datetime

# 将项目根目录添加到 sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from models.recommendation import RecommendationItem

class RecommendEngine:
    def __init__(self):
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

    def _build_rule_reasons(self, constitution: str, solar_term: str, season: str, items: list) -> dict:
        """基于规则生成推荐理由，替代 AI 调用。"""
        return {
            item: f"匹配{constitution}，且适合{solar_term}({season})调理"
            for item in items
        }

    async def get_smart_recommendations(self, user_id: str, constitution: str, age: Optional[int] = None, gender: Optional[str] = None):
        """
        获取智能推荐
        
        Args:
            user_id: 用户 ID
            constitution: 用户体质
            age: 用户年龄（可选）
            gender: 用户性别（可选）
            
        Returns:
            推荐结果
        """
        # 获取当前节气和季节
        solar_term = self.get_current_solar_term()
        season = self.get_season_by_solar_term(solar_term)
        
        # 1. 基础召回 (这里后期对接你的 Graph 和 DFS)
        # 根据体质、节气和季节生成推荐
        if constitution in self.recommendation_rules:
            # 获取对应体质的推荐规则
            constitution_rules = self.recommendation_rules[constitution]
            # 获取对应季节的推荐
            if season in constitution_rules:
                raw_data = constitution_rules[season]
            else:
                # 默认使用春季的推荐
                raw_data = constitution_rules["春季"]
        else:
            # 默认推荐
            raw_data = {
                "therapies": ["针灸", "推拿"],
                "recipes": ["营养粥", "养生汤"],
                "ingredients": ["枸杞", "红枣"]
            }
        
        # 2. 根据年龄和性别调整推荐
        if age:
            if age < 18:
                # 青少年推荐
                raw_data["recipes"].append("成长粥")
                raw_data["ingredients"].append("核桃")
            elif age > 60:
                # 老年人推荐
                raw_data["recipes"].append("养生粥")
                raw_data["ingredients"].append("黑芝麻")
        
        if gender == "女性":
            # 女性推荐
            raw_data["recipes"].append("红枣桂圆汤")
            raw_data["ingredients"].append("桂圆")
        elif gender == "男性":
            # 男性推荐
            raw_data["recipes"].append("枸杞汤")
            raw_data["ingredients"].append("玛咖")
        
        # 3. 提取所有项目，准备“打包问 AI”
        all_items = raw_data["therapies"] + raw_data["recipes"] + raw_data["ingredients"]
        
        # 4. 规则生成推荐理由（无 AI 依赖）
        reasons_map = self._build_rule_reasons(constitution, solar_term, season, all_items)

        # 5. 组装最终结果
        def build_items(category_list):
            return [RecommendationItem(title=item, reason=reasons_map.get(item, "益气养生")) for item in category_list]

        # 生成个性化总结
        summary = f"基于您最近的评估，您属于{constitution}，当前节气为{solar_term}，处于{season}。"
        if age:
            summary += f"您的年龄为{age}岁，"
        if gender:
            summary += f"性别为{gender}，"
        summary += "建议重点调理，以下是为您定制的食疗方案。"

        return {
            "constitution": constitution,
            "solar_term": solar_term,
            "season": season,
            "age": age,
            "gender": gender,
            "summary": summary,
            "therapies": build_items(raw_data["therapies"]),
            "recipes": build_items(raw_data["recipes"]),
            "ingredients": build_items(raw_data["ingredients"])
        }

