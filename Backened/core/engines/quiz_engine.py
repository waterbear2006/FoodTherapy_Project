"""
[Business Engine] 体质测试引擎
职责：计算用户体质测试的得分，生成体质测试结果。
实施功能：
- 计算用户九种体质的得分
- 根据得分生成体质测试结果
- 支持九种体质类型的测试
- 提供体质测试结果的详细信息
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
        计算每种体质的得分
        
        Args:
            answers: 用户提交的答案列表，每个答案包含 category 和 score 字段
            
        Returns:
            每种体质的得分向量
        """
        # 初始化得分字典
        scores = {constitution: 0.0 for constitution in self.constitutions}
        
        # 统计每种体质的得分
        for answer in answers:
            category = answer.get("category")
            score = answer.get("score", 0)
            
            if category in scores:
                scores[category] += score
        
        # 计算转化分（满分100）
        # 这里简化处理，实际中医体质测试有更复杂的计算方法
        # 假设每道题满分5分，9道题满分45分，转化为100分制
        max_possible_score = 5 * 9  # 假设每道题满分5分，共9道题
        for constitution in scores:
            # 转化为0-100分
            scores[constitution] = (scores[constitution] / max_possible_score) * 100
        
        return scores
    
    def get_result(self, score_vector: Dict[str, float]) -> Dict[str, Any]:
        """
        根据得分向量生成测试结果
        
        Args:
            score_vector: 每种体质的得分向量
            
        Returns:
            体质测试结果，包含主体质和得分向量
        """
        # 找出得分最高的体质作为主体质
        primary_constitution = max(score_vector, key=score_vector.get)
        
        # 构建返回结果
        result = {
            "primary_constitution": primary_constitution,
            "constitution_vector": score_vector,
            "status": "success"
        }
        
        return result