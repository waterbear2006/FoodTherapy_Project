# -*- coding: utf-8 -*-
"""
食疗助手 API - 使用阿里云通义千问 API
需要先安装：pip install dashscope

职责：提供 AI 食疗咨询相关的 API 接口，包含智能问答功能。
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import dashscope
import os
from core.search.caipu_loader import load_caipu_data, search_recipes_by_keyword, search_recipes_by_constitution
from pathlib import Path

router = APIRouter(tags=["AI 食疗助手"])

# 从环境变量获取 API Key，如果没有则使用默认值
API_KEY = os.getenv("DASHSCOPE_API_KEY", "sk-3e91e714355047328cc6f00a4ba7a7f1")

# 设置 API Key
dashscope.api_key = API_KEY

# 加载食谱数据
caipu_file = Path(__file__).parent.parent / "data" / "caipu.csv"
recipes = load_caipu_data(caipu_file)
print(f"成功加载 {len(recipes)} 条食谱数据")


def _build_recipe_context(user_input: str) -> str:
    """辅助函数：根据用户输入搜索食谱并构建上下文"""
    matched_recipes = search_recipes_by_keyword(recipes, user_input)
    if not matched_recipes:
        return "未找到相关食谱数据。\n"
        
    context = "根据我们的食疗数据库，为您推荐以下相关食谱：\n"
    for i, recipe in enumerate(matched_recipes[:3], 1):  # 最多推荐3个食谱
        context += f"{i}. {recipe.name}\n"
        context += f"   食材：{recipe.ingredients}\n"
        context += f"   功效：{recipe.effect}\n"
        context += f"   适用体质：{recipe.suitable}\n"
        context += f"   禁忌：{recipe.taboo}\n"
        if hasattr(recipe, 'ancient_books') and recipe.ancient_books:
            context += f"   古籍记载：{recipe.ancient_books}\n"
        context += f"   制作步骤：{recipe.steps}\n"
        context += "\n"
    return context


class ChatRequest(BaseModel):
    message: str
    user_id: Optional[str] = None


class ChatResponse(BaseModel):
    reply: str
    status: str


@router.post("/chat", response_model=ChatResponse)
async def chat_with_assistant(request: ChatRequest):
    """
    与 AI 食疗助手对话
    
    - **message**: 用户输入的问题
    - **user_id**: 可选的用户 ID
    
    返回 AI 的食疗建议回复
    """
    if not request.message or not request.message.strip():
        raise HTTPException(status_code=400, detail="消息内容不能为空")
    
    user_message = request.message.strip()
    recipe_context = _build_recipe_context(user_message)
    
    messages = [
        {
            "role": "system",
            "content": "你是一位专业的食疗顾问，精通中医食疗理论。请根据用户的问题和提供的食谱数据，提供科学、实用的食疗建议。"
                       "首先，基于提供的食谱数据给出建议，然后再补充其他相关内容。"
                       "回答要比较古风典雅，重点突出食物搭配和功效。"
                       "如果用户提到体质类型，请结合该体质特点给出针对性建议。"
        },
        {
            "role": "user",
            "content": f"{user_message}\n\n{recipe_context}"
        }
    ]
    
    try:
        response = dashscope.Generation.call(
            model="qwen-turbo",
            messages=messages,
            result_format="message",
            max_tokens=1024,
            temperature=0.7
        )
        
        if response.status_code == 200:
            reply = response.output.choices[0].message.content
            return ChatResponse(reply=reply, status="success")
        else:
            return ChatResponse(
                reply=f"请求失败，状态码：{response.status_code}",
                status="error"
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI 服务调用失败：{str(e)}")


# 初始化助手实例（供其他模块使用）
class FoodTherapyAssistant:
    """食疗助手类，用于其他模块调用"""
    
    def __init__(self, api_key: str = API_KEY):
        self.api_key = api_key
        dashscope.api_key = api_key
    
    def ask(self, user_input: str) -> str:
        """向通义千问提问，返回食疗建议"""
        recipe_context = _build_recipe_context(user_input)
        
        messages = [
            {
                "role": "system",
                "content": "你是一位专业的食疗顾问。请根据用户的问题和提供的食谱数据，提供科学、实用的食疗建议。"
                           "首先，基于提供的食谱数据给出建议，然后再补充其他相关内容。"
                           "回答要比较古风，重点突出食物搭配和功效。"
            },
            {
                "role": "user",
                "content": f"{user_input}\n\n{recipe_context}"
            }
        ]
        
        try:
            response = dashscope.Generation.call(
                model="qwen-turbo",
                messages=messages,
                result_format="message",
                max_tokens=512,
                temperature=0.7
            )
        except Exception as e:
            return f"网络或接口错误：{e}"
        
        if response.status_code == 200:
            return response.output.choices[0].message.content
        else:
            return f"请求失败，状态码：{response.status_code}，原因：{response.message}"


# 导出助手实例
assistant = FoodTherapyAssistant()
