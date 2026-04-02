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

router = APIRouter(tags=["AI 食疗助手"])

# 从环境变量获取 API Key，如果没有则使用默认值
API_KEY = os.getenv("DASHSCOPE_API_KEY", "sk-3e91e714355047328cc6f00a4ba7a7f1")

# 设置 API Key
dashscope.api_key = API_KEY


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
    
    messages = [
        {
            "role": "system",
            "content": "你是一位专业的食疗顾问，精通中医食疗理论。请根据用户的问题提供科学、实用的食疗建议。"
                       "回答要比较古风典雅，重点突出食物搭配和功效。"
                       "如果用户提到体质类型，请结合该体质特点给出针对性建议。"
        },
        {
            "role": "user",
            "content": request.message.strip()
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
        messages = [
            {
                "role": "system",
                "content": "你是一位专业的食疗顾问。请根据用户的问题提供科学、实用的食疗建议。"
                           "回答要比较古风，重点突出食物搭配和功效。"
            },
            {
                "role": "user",
                "content": user_input
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
