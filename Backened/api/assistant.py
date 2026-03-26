# -*- coding: utf-8 -*-
"""
食疗助手 - 使用阿里云通义千问 API
需要先安装：pip install dashscope
"""

import dashscope  # 修改点

# ============================================================
# 请将你的 API Key 填写在下面的引号中
# 获取地址：https://dashscope.aliyun.com/ (登录后创建 API Key)
API_KEY = "sk-3e91e714355047328cc6f00a4ba7a7f1"   # ← 在这里粘贴你的 API Key
# ============================================================

class FoodTherapyAssistant:
    def __init__(self, api_key=API_KEY):
        """初始化助手，设置 API Key"""
        if api_key == "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxx":
            raise ValueError("请先在代码中设置有效的 API Key！")
        # 正确设置 API Key
        dashscope.api_key = api_key

    def ask(self, user_input):
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
            response = dashscope.Generation.call(  # 使用 dashscope.Generation
                model="qwen-turbo",
                messages=messages,
                result_format="message",
                max_tokens=512,
                temperature=0.7
            )
        except Exception as e:
            import traceback
            traceback.print_exc()
            return f"网络或接口错误：{e}"

        if response.status_code == 200:
            return response.output.choices[0].message.content
        else:
            return f"请求失败，状态码：{response.status_code}，原因：{response.message}"

# 测试
if __name__ == "__main__":
    assistant = FoodTherapyAssistant()
    print("食疗助手已启动，输入问题开始咨询（输入 exit 退出）")
    while True:
        q = input("\n你：")
        if q.lower() in ("exit", "quit"):
            break
        ans = assistant.ask(q)
        print("AI：", ans)