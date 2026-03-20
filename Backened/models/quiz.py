# quiz.py - 定义体质测试相关的数据模型，包含前端提交的问卷数据和后端返回的测试结果。

from pydantic import BaseModel, Field
from typing import List, Dict

# ----------------- 接收前端数据的模型 (Request) -----------------

class AnswerItem(BaseModel):
    """单道题目的答题数据"""
    category: str = Field(..., description="该题目对应的体质类别，如：阳虚质", example="阳虚质")
    # 使用 Field(ge=1, le=5) 严格限制分数只能是 1 到 5 之间的整数
    score: int = Field(..., ge=1, le=5, description="用户选择的选项分值 (1-5)", example=4)

class QuizSubmission(BaseModel):
    """前端提交的完整测试问卷"""
    user_id: str = Field(..., description="用户的唯一标识符", example="user_1024")
    answers: List[AnswerItem] = Field(..., description="用户提交的答案列表")

# ----------------- 返回给前端的模型 (Response) -----------------

class QuizResponse(BaseModel):
    """后端返回的体质测试结果"""
    primary_constitution: str = Field(..., description="得分最高的主体质，即最终判定结果", example="阳虚质")
    # Dict[str, float] 表示键是字符串(体质名)，值是浮点数(转化分)
    constitution_vector: Dict[str, float] = Field(..., description="九大体质的转化分向量")
    status: str = Field(default="success", description="接口请求状态")