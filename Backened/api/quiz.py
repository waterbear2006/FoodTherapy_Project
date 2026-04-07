"""
[API Router] 体质测试接口
职责：提供体质测试相关的 API 接口，包含获取题库和提交答案两大功能。
实施功能：
- 获取体质测试题库
- 提交体质测试答案并计算体质
- 支持九种体质类型的测试
- 从 quiz_questions.json 文件加载题库数据
"""
# 体制测试相关的 API 路由，包含获取题库和提交答案两大功能。

import json
from pathlib import Path
from fastapi import APIRouter, HTTPException
# 假设你已经建好了 models/quiz.py 和 core/engines/quiz_engine.py
from models.quiz import QuizSubmission, QuizResponse
from core.engines.quiz_engine import ConstitutionScorer

# 1. 初始化路由器，贴上标签，方便 Swagger 文档分类
router = APIRouter(tags=["体质测试"])

# 2. 实例化引擎（把后厨准备好）
scorer = ConstitutionScorer()

# 获取题库的绝对路径（防止你在不同终端目录下运行报错）
BASE_DIR = Path(__file__).resolve().parent.parent
QUESTIONS_PATH = BASE_DIR / "data" / "quiz_questions.json"

@router.get("/questions", summary="获取九种体质测试题库")
async def get_quiz_questions():
    """读取本地 JSON 题库并返回给前端渲染"""
    try:
        with open(QUESTIONS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        # 返回 questions 数组
        return {"status": "success", "data": data.get("questions", [])}
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="题库文件未找到，请检查 data 目录")

@router.post("/submit", response_model=QuizResponse, summary="提交答案并计算体质")
async def submit_quiz(submission: QuizSubmission):
    """
    接收前端传来的答案数组，调用引擎计算，返回九维体质向量
    """
    # 提取 Pydantic 模型里的 answers 列表转为字典供引擎使用
    answers_dict_list = [ans.dict() for ans in submission.answers]
    
    # 调用引擎算分 (瘦控制器体现：这里只有一行核心调用)
    vector = scorer.calculate_scores(answers_dict_list)
    result = scorer.get_result(vector)
    print(f"📥 [Quiz Debug] 原始向量: {vector}")
    print(f"🏁 [Quiz Debug] 判定结果: {result['primary_constitution']}")
    
    return result