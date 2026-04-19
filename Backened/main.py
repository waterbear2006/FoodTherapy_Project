"""
[Main Entry] 项目总入口
功能：初始化 FastAPI 实例，挂载全局中间件（CORS 等），并注册所有业务路由。
职责：大堂经理，负责启动服务并分配请求。
"""

import uvicorn
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
from api import quiz, ingredients, search, recommend, therapy, recipes, graph, categories  # 导入路由模块
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
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "*"],  # 允许所有来源
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有 HTTP 方法
    allow_headers=["*"],  # 允许所有 HTTP 头
)

print("CORS 中间件已配置")

# --- 1. 路径预设 ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
DATA_DIR = os.path.join(BASE_DIR, "data")

# --- 2. 【最高优先级】物理挂载 assets ---
# 这一步必须在任何 @app.get 之前！
# 🚨 【强制挂载】删掉 if 判断，直接硬连！
# 如果路径不对，这行代码在启动时就会直接让程序崩溃报错，这样我们就能立刻发现问题
app.mount("/assets", StaticFiles(directory=os.path.join(STATIC_DIR, "assets")), name="assets")

# 挂载数据目录
app.mount("/data", StaticFiles(directory=DATA_DIR), name="data")

# --- 3. 将业务路由注册到总 APP 上 ---
app.include_router(quiz.router, prefix="/api/quiz", tags=["体质测试"])
app.include_router(ingredients.router, prefix="/api/ingredients", tags=["食材库"])
app.include_router(search.router, prefix="/api/search", tags=["搜索"])
app.include_router(recommend.router, prefix="/api/recommend", tags=["智能推荐"])
app.include_router(therapy.router, prefix="/api/therapy", tags=["食疗库"])
app.include_router(recipes.router, prefix="/api/recipes", tags=["菜谱"])
app.include_router(categories.router, prefix="/api/categories", tags=["分类详情"])
app.include_router(graph.router, prefix="/api/graph", tags=["知识图谱"])
app.include_router(reports.router, prefix="/api/reports", tags=["健康档案"])
app.include_router(daily_report.router)
app.include_router(assistant.router, prefix="/api/assistant", tags=["AI 食疗助手"])

# --- 4. 【首页路由】 ---
@app.get("/")
async def serve_index():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))

# --- 5. 【防御性万能路由】 ---
# 我们给它加一个判断：如果是请求 .js, .css, .svg 等文件的，绝对不返回 index.html
@app.get("/{catchall:path}")
async def catch_all_fallback(catchall: str):
    # 拼接物理路径
    local_path = os.path.join(STATIC_DIR, catchall)
    
    # 如果物理文件真的存在（比如 favicon.svg 等），直接返回它
    if os.path.isfile(local_path):
        return FileResponse(local_path)
    
    # 只有当路径不包含点（说明不是请求文件，而是前端路由）时，才返回 index.html
    if "." not in catchall:
        return FileResponse(os.path.join(STATIC_DIR, "index.html"))
    
    # 如果是请求文件但没找到，返回 404 而不是 index.html（防止 JS 拿到 HTML 内容）
    raise HTTPException(status_code=404)

if __name__ == "__main__":
    # 启动服务器，开启热更新 (reload=True)
    uvicorn.run("main:app", host="127.0.0.1", port=8001, reload=True)