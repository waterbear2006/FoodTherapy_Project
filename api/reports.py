from datetime import date
from pathlib import Path
from typing import List, TypedDict

from fastapi import APIRouter, Query

from core.food_therapy.models import TherapyDetail
from core.food_therapy.service import TherapyService


router = APIRouter()


def _create_service() -> TherapyService:
    project_root = Path(__file__).resolve().parents[1]
    data_path = project_root / "therapy_data.csv"
    service = TherapyService(file_path=data_path)
    service.load_data()
    return service


_service: TherapyService = _create_service()


class DailyReport(TypedDict):
    """每日食疗推荐报告结构"""

    date: str
    constitution: str | None
    tag: str | None
    count: int
    highlights: List[TherapyDetail]
    summary: str


def _render_summary_text(
    items: List[TherapyDetail],
    constitution: str | None,
    tag: str | None,
) -> str:
    """
    AI 润色占位实现:
    真实项目中可在这里接入大模型, 对原始要点进行自然语言优化.
    """
    if not items:
        base = "今日未为你找到合适的食疗方案。建议适当调整饮食结构，多样化搭配。"
        if constitution:
            base = f"针对「{constitution}」体质，{base}"
        return base

    names = "、".join(i.name for i in items[:5])
    base = f"为你精选了 {len(items)} 条食疗方案，其中代表性食谱包括：{names}。"
    if constitution and tag:
        return f"针对「{constitution}」体质、侧重「{tag}」功效，{base}建议在专业医生指导下灵活搭配日常饮食。"
    if constitution:
        return f"结合你偏向「{constitution}」的体质特征，{base}可适量纳入日常三餐，注意荤素与冷热的平衡。"
    if tag:
        return f"围绕「{tag}」这一核心功效，{base}搭配使用时仍需留意个体体质差异与既往病史。"
    return base + "合理安排作息与运动，将更有助于整体调理效果。"


@router.get(
    "/daily",
    response_model=DailyReport,
    summary="生成每日食疗报告",
)
def generate_daily_report(
    constitution: str | None = Query(None, description="用户主要体质，用于个性化推荐"),
    tag: str | None = Query(None, description="重点关注的食疗功效标签"),
    limit: int = Query(10, ge=1, le=50, description="报告中返回的食疗上限"),
) -> DailyReport:
    """
    每日报告流程:
    1. 通过 service.query 调用核心索引与算法
    2. 选出前若干条作为「今日推荐」
    3. 生成一段可读性较好的报告文案 (AI 润色占位)
    """
    # 使用综合查询入口，内部自动调度 Trie / Hash / KMP / LRU
    keyword = ""
    items = _service.query(
        keyword=keyword,
        tag=tag,
        constitution=constitution,
        use_full_text=False,
    )
    items = items[:limit]

    summary = _render_summary_text(items, constitution=constitution, tag=tag)

    report: DailyReport = {
        "date": date.today().isoformat(),
        "constitution": constitution,
        "tag": tag,
        "count": len(items),
        "highlights": items,
        "summary": summary,
    }
    return report

