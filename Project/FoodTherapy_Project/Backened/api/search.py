from pathlib import Path
from typing import List

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


def _simple_intent_routing(q: str) -> str:
    """
    极简意图解析:
    - 包含“禁忌 / 相克”等字样 -> taboo
    - 包含“搭配 / 配伍”等字样     -> match
    - 默认 -> general
    """
    lowered = q.lower()
    if any(k in lowered for k in ["禁忌", "相克", "不宜"]):
        return "taboo"
    if any(k in lowered for k in ["搭配", "配伍", "组合"]):
        return "match"
    return "general"


@router.get(
    "/",
    response_model=List[TherapyDetail],
    summary="智能搜索食疗",
)
def smart_search(
    q: str = Query(..., description="自然语言搜索词"),
    constitution: str | None = Query(None, description="体质过滤"),
    tag: str | None = Query(None, description="功能标签过滤"),
) -> List[TherapyDetail]:
    """
    智能搜索调度逻辑:
    1. 使用极简意图解析判断用户是在问「搭配」「禁忌」还是普通搜索
    2. 普通搜索:
       - 短词优先 Trie 前缀搜索
       - 长文本优先 KMP 全文搜索
       - 结果再根据体质 / 标签过滤
    """
    intent = _simple_intent_routing(q)
    q = q.strip()
    if not q:
        return []

    result: List[TherapyDetail]

    # 普通语义下：根据长度在 Trie 与 KMP 之间调度
    if intent == "general":
        if len(q) <= 4:
            # 名称 / 短标签，更像前缀搜索
            result = _service.search_by_name(q)
        else:
            # 偏长文本，走全文检索
            result = _service.full_text_search(q)
    else:
        # 对于「禁忌 / 搭配」等语义，这里仍复用全文搜索，
        # 实际项目中可进一步拆分到图结构接口
        result = _service.full_text_search(q)

    # 追加基于 tag / constitution 的过滤
    if tag:
        result = [item for item in result if tag in item.tags]
    if constitution:
        result = [item for item in result if constitution in item.constitution]

    return result

