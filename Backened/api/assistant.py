# -*- coding: utf-8 -*-
"""
食疗助手 API - 使用 DeepSeek API (OpenAI 兼容)
职责：提供 AI 食疗咨询相关的 API 接口，包含智能问答功能。
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from openai import AsyncOpenAI
import os
from dotenv import load_dotenv

# 加载 .env 环境变量
load_dotenv()

router = APIRouter(tags=["AI 食疗助手"])

# 从环境变量获取 API Key 和 Base URL
API_KEY = os.getenv("DEEPSEEK_API_KEY")
BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")

if not API_KEY:
    print("⚠️ 警告: DEEPSEEK_API_KEY 未找到，AI 功能将受限")

# 初始化 OpenAI 兼容客户端
client = AsyncOpenAI(api_key=API_KEY, base_url=BASE_URL)

YIBAO_SYSTEM_PROMPT = """你现在的身份是一位名叫“颐宝”的古风小生。你出身中医世家，饱读诗书，但你生活在现代，是一位温柔、细心且懂科学的调理专家。

你的说话原则：
1. **去文言化**：严禁使用“之乎者也”、“尔等”、“尚未”等生涩词汇。使用 100% 的现代语法。
2. **温润如玉**：语气要缓和，多用“请、不妨、建议、阁下、且听我一言”。
3. **通俗解释**：遇到中医术语（如脾虚、湿气、经络），必须用现代生活化的比喻。
   - 错误：脾主运化，虚则水肿。
   - 正确：脾胃就像咱们身体里的“运输小队”，如果它们累了（脾虚），身体里的水分就运不走，容易让人觉得沉重。
4. **古风点缀**：少量使用好懂的古意词汇（如：安好、消遣、清润、些许、愿君）。
5. **结构清晰**：即便语气温柔，回答也要用 Markdown 列表，保证可读性。

交互逻辑：
- 开场白：从这类风格中选取适当的词句（如：“见阁下眉间微蹙，可是近日饮食不慎，身子有些沉重？”）。
- 古籍引用：在回答结尾，用最白话的方式提一句古籍（如：“《本草》里曾提过，山药最是润人，阁下不妨一试。”）。
- 结束语：带上书生式的关怀（如：“医理虽好，也需阁下早些休息，愿今夜好梦。”）。"""


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
    
    if not API_KEY:
        return ChatResponse(reply="抱歉，AI 助手暂时未配置密钥，无法为您解答。", status="error")

    messages = [
        {"role": "system", "content": YIBAO_SYSTEM_PROMPT},
        {"role": "user", "content": request.message.strip()}
    ]
    
    try:
        response = await client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            max_tokens=1024,
            temperature=0.7
        )
        
        reply = response.choices[0].message.content
        return ChatResponse(reply=reply, status="success")
            
    except Exception as e:
        print(f"❌ AI Assistant Error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"AI 服务调用失败：{str(e)}")


class FoodTherapyAssistant:
    """食疗助手类，用于其他模块调用"""
    
    def __init__(self):
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        self.base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
        self.client = AsyncOpenAI(api_key=self.api_key, base_url=self.base_url)
    
    async def ask(self, user_input: str) -> str:
        """异步向 DeepSeek 提问，返回食疗建议"""
        if not self.api_key:
            return "未配置 API Key"

        messages = [
            {"role": "system", "content": YIBAO_SYSTEM_PROMPT},
            {"role": "user", "content": user_input}
        ]
        
        try:
            response = await self.client.chat.completions.create(
                model="deepseek-chat",
                messages=messages,
                max_tokens=512,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"网络或接口错误：{e}"


# 导出助手实例
assistant = FoodTherapyAssistant()
