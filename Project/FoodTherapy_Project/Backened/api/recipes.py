from pathlib import Path
from typing import Dict, List, Set

from fastapi import APIRouter, Depends, Header, HTTPException, Query, status

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

# 简单的内存收藏表: user_id -> set[recipe_id]
_user_favorites: Dict[str, Set[int]] = {}


def get_current_user(authorization: str = Header(..., alias="Authorization")) -> str:
    """
    极简 JWT 鉴权占位实现:
    - 约定前端在 Header 中直接传: Authorization: Bearer <user_id>
    - 实际项目中可替换为真正的 JWT 校验逻辑
    """
    prefix = "Bearer "
    if not authorization.startswith(prefix):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="认证信息格式错误，应为 'Bearer <token>'",
        )
    token = authorization[len(prefix) :].strip()
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效 token",
        )
    # 在示例中直接将 token 视为 user_id
    return token


@router.get(
    "/",
    response_model=List[TherapyDetail],
    summary="浏览食疗食谱列表",
)
def list_recipes(
    keyword: str = Query("", description="关键词（名称前缀 / 全文）"),
    tag: str | None = Query(None, description="功能标签，如：补气、去湿"),
    constitution: str | None = Query(None, description="体质，如：气虚体质"),
    full_text: bool = Query(
        False, description="是否启用全文搜索（KMP，methods/matches/taboos 等字段）"
    ),
) -> List[TherapyDetail]:
    """
    通过业务服务层访问 FoodTherapyIndex:
    - 不同参数组合下会使用 Trie / Hash / KMP + LRU 缓存.
    """
    return _service.query(
        keyword=keyword,
        tag=tag,
        constitution=constitution,
        use_full_text=full_text,
    )


@router.get(
    "/{recipe_id}",
    response_model=TherapyDetail,
    summary="查看单个食疗详情",
)
def get_recipe_detail(recipe_id: int) -> TherapyDetail:
    # 通过综合查询拿到所有数据后按 id 过滤
    all_items = _service.query(keyword="")
    for item in all_items:
        if item.id == recipe_id:
            return item
    raise HTTPException(status_code=404, detail="未找到对应食疗")


@router.post(
    "/{recipe_id}/favorite",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="收藏食疗（需要 JWT）",
)
def favorite_recipe(
    recipe_id: int,
    user_id: str = Depends(get_current_user),
):
    """
    收藏流程示例:
    - 依赖 get_current_user 完成 JWT 校验
    - 使用内存结构记录收藏关系
    - 实际项目中可替换为数据库/缓存
    """
    # 先确保食谱存在
    all_items = _service.query(keyword="")
    if not any(item.id == recipe_id for item in all_items):
        raise HTTPException(status_code=404, detail="食疗不存在")

    favorites = _user_favorites.setdefault(user_id, set())
    favorites.add(recipe_id)


@router.delete(
    "/{recipe_id}/favorite",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="取消收藏食疗（需要 JWT）",
)
def unfavorite_recipe(
    recipe_id: int,
    user_id: str = Depends(get_current_user),
):
    favorites = _user_favorites.setdefault(user_id, set())
    favorites.discard(recipe_id)


@router.get(
    "/me/favorites",
    response_model=List[TherapyDetail],
    summary="查看当前用户收藏的食疗",
)
def list_my_favorites(user_id: str = Depends(get_current_user)) -> List[TherapyDetail]:
    favorites = _user_favorites.get(user_id, set())
    if not favorites:
        return []
    all_items = _service.query(keyword="")
    return [item for item in all_items if item.id in favorites]

