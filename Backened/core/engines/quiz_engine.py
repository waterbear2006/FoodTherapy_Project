"""
[Business Engine] 体质测试引擎
职责：计算用户体质测试的得分，生成体质测试结果。
实施功能：
- 计算用户九种体质的得分（采用标准转化分公式）
- 根据 2009 版《中医体质分类与判定》判定体质类型
- 支持九种体质类型的测试与结果生成
"""
from typing import List, Dict, Any

class ConstitutionScorer:
    """
    体质测试评分器
    负责计算用户的体质测试得分，并生成测试结果
    """
    
    def __init__(self):
        """
        初始化体质测试评分器
        """
        # 九种体质类型
        self.constitutions = [
            "平和质", "气虚质", "阳虚质", "阴虚质", 
            "痰湿质", "湿热质", "血瘀质", "气郁质", "特禀质"
        ]
    
    def calculate_scores(self, answers: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        计算每种体质的转化分（标准公式）
        转化分 = [(原始分 - 题目数) / (题目数 * 4)] * 100
        """
        # 统计每种体质的原始分总和与题目统计
        category_stats = {c: {"sum": 0, "count": 0} for c in self.constitutions}
        
        for answer in answers:
            category = answer.get("category")
            score = answer.get("score", 0)
            if category in category_stats:
                category_stats[category]["sum"] += score
                category_stats[category]["count"] += 1
        
        # 计算转化分
        scores = {}
        for category, stats in category_stats.items():
            count = stats["count"]
            if count > 0:
                # 标准公式计算
                converted = ((stats["sum"] - count) / (count * 4)) * 100
                scores[category] = round(converted, 1)
            else:
                scores[category] = 0.0
        
        return scores
    
    def get_result(self, score_vector: Dict[str, float]) -> Dict[str, Any]:
        """
        根据 2009 版《中医体质分类与判定》标准进行判定
        判定规则：
        1. 偏颇体质：转化分 >= 40 为“是”，30-39 为“有倾向”。
        2. 平和质：平和质转化分 >= 60 且 其他 8 种体质转化分均 < 30。
        """
        pinghe_score = score_vector.get("平和质", 0)
        imbalanced = {k: v for k, v in score_vector.items() if k != "平和质"}
        
        results = []
        is_combination = False
        
        # 1. 判定偏颇体质 (确定的)
        for cat, score in imbalanced.items():
            if score >= 40:
                results.append(cat)
        
        # 2. 如果没有确定的，检查是否有倾向 (30-39)
        if not results:
            for cat, score in imbalanced.items():
                if score >= 30:
                    results.append(cat)
                    
        # 3. 最后判定平和质 (只有在完全没有偏居倾向时才判定为平和)
        if not results:
            # 找到得分最高的体质（排除平和质）
            max_bias_cat = max(imbalanced, key=imbalanced.get)
            max_bias_score = imbalanced[max_bias_cat]
            
            # 如果最高偏颇分超过或等于 30 (倾向值)，即使平和质分再高也要提示不平衡
            if max_bias_score >= 30:
                results = [max_bias_cat]
            elif pinghe_score >= 60:
                results = ["平和质"]
            else:
                # 都不足 30 时，再看谁得分最高
                results = [max_bias_cat if max_bias_score > pinghe_score else "平和质"]

        if len(results) > 1:
            is_combination = True
        return {
            "primary_constitution": results[0],
            "constitutions": results,
            "is_combination": is_combination,
            "constitution_vector": score_vector,
            "status": "success",
            "description": f"经过专业辨识，您的主体质是【{results[0]}】" + ("，并带有其他兼夹体质。" if is_combination else "。")
        }