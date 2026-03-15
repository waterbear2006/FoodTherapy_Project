from fastapi import APIRouter

from .ingredients import router as ingredients_router
from .recipes import router as recipes_router
from .search import router as search_router
from .reports import router as reports_router


def create_api_router() -> APIRouter:
    """
    聚合业务路由入口
    在主应用中使用:

        from api import create_api_router
        app.include_router(create_api_router(), prefix="/api")
    """
    router = APIRouter()
    router.include_router(ingredients_router, prefix="/ingredients", tags=["ingredients"])
    router.include_router(recipes_router, prefix="/recipes", tags=["recipes"])
    router.include_router(search_router, prefix="/search", tags=["search"])
    router.include_router(reports_router, prefix="/reports", tags=["reports"])
    return router

