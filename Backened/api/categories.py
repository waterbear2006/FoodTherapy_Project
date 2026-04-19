from fastapi import APIRouter, HTTPException
from core.engines.category_service import category_service
from models.unified import StandardResourceResponse

router = APIRouter(tags=["分类库模块"])

@router.get("/{name}", response_model=StandardResourceResponse)
async def get_category_detail(name: str):
    """获取分类/体质/功效的详细标准化信息"""
    data = category_service.get_by_name(name)
    if not data:
        # 如果找不到，返回一个基础结构而不是 404，以保证图谱流畅度
        return StandardResourceResponse(
            name=name,
            summary="资料整理中...",
            ancient_quote="",
            type="category"
        )
    
    return StandardResourceResponse(
        name=data["name"],
        summary=data["summary"],
        ancient_quote=data.get("ancient_quote") or "",
        type="category"
    )
