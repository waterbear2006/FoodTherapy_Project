"""
[Main Entry] 项目总入口
功能：初始化 FastAPI 实例，挂载全局中间件（CORS等），并注册所有业务路由。
职责：大堂经理，负责启动服务并分配请求。
"""

from fastapi import FastAPI
from api import quiz, ingredients, search, recommend, therapy, recipes  # 导入路由模块
from core.preloader import load_all_data  # 导入数据加载函数

# 启动时加载数据
load_all_data()

app = FastAPI(title="食疗养生推荐系统 API", version="1.0.0")

# 将路由注册到总 APP 上
app.include_router(quiz.router, prefix="/api")  # 体质测试路由
app.include_router(ingredients.router)  # 食材库路由
app.include_router(search.router)  # 搜索模块路由
app.include_router(recommend.router)  # 智能推荐路由
app.include_router(therapy.router)  # 食疗库路由
app.include_router(recipes.router)  # 菜谱模块路由

@app.get("/")
async def root():
    return {"message": "Welcome to Food Therapy API"}