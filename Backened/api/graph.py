from fastapi import APIRouter, HTTPException, Query
from core.graph_engine import engine

router = APIRouter()

@router.get("/detail")
async def get_graph_detail(
    name: str = Query(..., description="中心节点名称"),
    depth: int = Query(1, description="检索深度")
):
    """
    获取指定节点的关联图谱数据，支持指定检索深度
    """
    center = (name or "").strip()
    if not center:
        raise HTTPException(status_code=400, detail="节点名称不能为空")

    try:
        if not engine.data_loaded:
            engine.load_data()
        subgraph = engine.get_subgraph(center, depth=depth)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"图谱加载失败: {e}")
    
    # 定义 Echarts 需要的 categories
    categories = [
        {"name": "食材"},
        {"name": "菜谱"},
        {"name": "体质"},
        {"name": "功效"},
        {"name": "其他"}
    ]
    
    return {
        "nodes": subgraph["nodes"],
        "links": subgraph["links"],
        "categories": categories
    }
