"""
健康档案 & 每日健康报告 API

用于支撑：
- 体质测试结果保存到健康档案
- 智能推荐/食谱生成读取用户体质
- 每日养生建议报告生成
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from core.db import HealthArchive, get_db
from models.daily_report import DailyReportRequest, DailyReportResponse
from core.engines.daily_report_engine import DailyReportEngine


router = APIRouter(tags=["健康档案", "每日报告"])

# 每日报告引擎
report_engine = DailyReportEngine()


class HealthArchiveUpsert(BaseModel):
    model_config = ConfigDict(extra="allow")

    user_id: str
    constitution: str
    score: Optional[int] = None
    symptoms: Optional[str] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    bmi: Optional[str] = None
    sleep: Optional[str] = None
    water: Optional[str] = None
    steps: Optional[str] = None
    heartRate: Optional[str] = None
    lastUpdated: Optional[str] = None


@router.post("/health-archive")
async def upsert_health_archive(
    payload: HealthArchiveUpsert,
    db: Session = Depends(get_db),
):
    # 1) 整体存 JSON（便于前端字段扩展）
    raw = payload.model_dump()
    user_id = raw.pop("user_id")

    # 2) lastUpdated -> DB 时间（兜底 utcnow）
    last_updated = datetime.utcnow()
    if payload.lastUpdated:
        try:
            last_updated = datetime.fromisoformat(payload.lastUpdated.replace("Z", "+00:00"))
        except Exception:
            last_updated = datetime.utcnow()

    # 3) 写入/更新
    record = db.get(HealthArchive, user_id)
    if record is None:
        record = HealthArchive(user_id=user_id, data_json="", last_updated=last_updated)
        db.add(record)

    import json

    record.data_json = json.dumps(raw, ensure_ascii=False)
    record.last_updated = last_updated
    db.commit()

    # 4) 返回给前端直接使用
    return {
        "status": "success",
        "data": raw,
    }


@router.get("/health-archive")
async def get_health_archive(
    user_id: str = Query(..., description="用户 ID"),
    db: Session = Depends(get_db),
):
    record = db.get(HealthArchive, user_id)
    if record is None:
        raise HTTPException(status_code=404, detail="健康档案不存在，请先完成体质测试并保存")

    import json

    data: Dict[str, Any] = json.loads(record.data_json) if record.data_json else {}
    return {
        "status": "success",
        "data": data,
    }


@router.post("/daily", response_model=DailyReportResponse)
async def generate_daily_report(payload: DailyReportRequest):
    """
    生成每日养生建议报告
    
    根据用户体质、当前节气和季节，生成个性化的食疗推荐方案。
    包含：
    - 当日主体质及变化趋势
    - 推荐食材和菜谱
    - 可读性强的养生建议文本
    - 前端 UI 卡片结构
    """
    result = await report_engine.get_daily_report(
        user_id=payload.user_id,
        constitution_vector=payload.constitution_vector,
        available_ingredients=payload.available_ingredients,
        force_refresh=payload.force_refresh,
    )
    return result
