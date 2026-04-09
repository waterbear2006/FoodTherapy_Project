"""
每日健康报告 API
职责：聚合体质变化 + 食疗推荐集合，并输出可读日报文本。
"""

from fastapi import APIRouter

from core.engines.daily_report_engine import DailyReportEngine
from models.daily_report import DailyReportRequest, DailyReportResponse

router = APIRouter(prefix="/api/reports", tags=["每日报告"])
engine = DailyReportEngine()


@router.post("/daily", response_model=DailyReportResponse)
async def generate_daily_report(payload: DailyReportRequest):
    weather_data = payload.weather.model_dump() if payload.weather else None
    result = await engine.get_daily_report(
        user_id=payload.user_id,
        constitution_vector=payload.constitution_vector,
        available_ingredients=payload.available_ingredients,
        force_refresh=payload.force_refresh,
        weather_data=weather_data,
    )
    return result
