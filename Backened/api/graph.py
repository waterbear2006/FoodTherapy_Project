from fastapi import APIRouter, Query
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
    subgraph = engine.get_subgraph(name, depth=depth)
    
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
