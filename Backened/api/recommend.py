"""
[API Router] 智能推荐接口
职责：提供智能推荐相关的 API 接口，包含获取智能推荐功能。
实施功能：
- 获取智能推荐，根据用户体质、当前节气和季节生成推荐
- 支持根据年龄和性别调整推荐
- 调用 AI 生成推荐理由
- 从 recommend_engines.py 模块获取推荐逻辑
"""

"""
[API Router] 智能推荐接口
职责：接收用户 ID，获取当前体质上下文，返回全量推荐方案。
"""
from fastapi import APIRouter, Query
from typing import Optional
from models.recommendation import RecommendationResponse
from core.engines.recommend_engines import RecommendEngine

router = APIRouter(tags=["智能推荐"])
engine = RecommendEngine()

@router.get("/daily", response_model=RecommendationResponse)
async def get_daily_recommendation(
    user_id: str,
    constitution: Optional[str] = Query(None, description="用户体质（来自健康档案）"),
    age: Optional[int] = Query(None, description="用户年龄"),
    gender: Optional[str] = Query(None, description="用户性别"),
    temperature: Optional[float] = Query(None, description="当前气温"),
    humidity: Optional[float] = Query(None, description="当前湿度"),
    city: Optional[str] = Query(None, description="所在城市")
):
    # 1. 使用前端传入的体质；没有传则兜底到 平和质
    user_constitution = constitution or "平和质"
    
    weather_data = None
    if temperature is not None or humidity is not None or city is not None:
        weather_data = {
            "temperature": temperature,
            "humidity": humidity,
            "city": city
        }
    
    # 2. 调用引擎生成推荐
    result = await engine.get_smart_recommendations(
        user_id, user_constitution, age, gender, weather_data=weather_data
    )
    return result