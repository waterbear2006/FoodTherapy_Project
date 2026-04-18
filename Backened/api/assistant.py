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

from dotenv import load_dotenv

# 加载 .env 环境变量
load_dotenv()

router = APIRouter(tags=["AI 食疗助手"])

# 从环境变量获取 API Key
# 严禁在代码中硬编码任何 API KEY！！
API_KEY = os.getenv("DASHSCOPE_API_KEY")

if not API_KEY:
    print("⚠️ 警告: DASHSCOPE_API_KEY 未找到，AI 功能将受限")

# 设置 API Key
dashscope.api_key = API_KEY

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
    
    messages = [
        {
            "role": "system",
            "content": YIBAO_SYSTEM_PROMPT
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
    
    def __init__(self, api_key: str = os.getenv("DASHSCOPE_API_KEY")):
        self.api_key = api_key
        dashscope.api_key = api_key
    
    def ask(self, user_input: str) -> str:
        """向通义千问提问，返回食疗建议"""
        messages = [
            {
                "role": "system",
                "content": YIBAO_SYSTEM_PROMPT
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
