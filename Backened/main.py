"""
[Main Entry] 项目总入口
功能：初始化 FastAPI 实例，挂载全局中间件（CORS 等），并注册所有业务路由。
职责：大堂经理，负责启动服务并分配请求。
"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from api import quiz, ingredients, search, recommend, therapy, recipes  # 导入路由模块
from api import reports  # 健康档案路由
from api import daily_report # 每日健康报告
from api import assistant  # AI 食疗助手路由
from core.preloader import load_all_data  # 导入数据加载函数

# 启动时加载数据
load_all_data()

app = FastAPI(title="食疗养生推荐系统 API", version="1.0.0")

# 添加 CORS 中间件，允许前端跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有 HTTP 方法
    allow_headers=["*"],  # 允许所有 HTTP 头
)

# 挂载静态文件目录，提供图片访问
BASE_DIR = Path(__file__).resolve().parent
data_dir = BASE_DIR / "data"
app.mount("/data", StaticFiles(directory=str(data_dir)), name="data")

# 将路由注册到总 APP 上
app.include_router(quiz.router, prefix="/api/quiz", tags=["体质测试"])  # 体质测试路由
app.include_router(ingredients.router, prefix="/api/ingredients", tags=["食材库"])  # 食材库路由
app.include_router(search.router, prefix="/api/search", tags=["搜索"])  # 搜索模块路由
app.include_router(recommend.router, prefix="/api/recommend", tags=["智能推荐"])  # 智能推荐路由
app.include_router(therapy.router, prefix="/api/therapy", tags=["食疗库"])  # 食疗库路由
app.include_router(recipes.router, prefix="/api/recipes", tags=["菜谱"])  # 菜谱模块路由
app.include_router(reports.router, prefix="/api/reports", tags=["健康档案"])  # 健康档案路由
app.include_router(daily_report.router) # 每日健康报告路由
app.include_router(assistant.router, prefix="/api/assistant", tags=["AI 食疗助手"])  # AI 食疗助手路由
@app.get("/")
async def root():
    return {"message": "Welcome to Food Therapy API"}

if __name__ == "__main__":
    # 启动服务器
    uvicorn.run(app, host="127.0.0.1", port=8002)