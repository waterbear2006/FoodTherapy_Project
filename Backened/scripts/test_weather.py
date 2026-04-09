import asyncio
import json
import sys
from pathlib import Path

# 添加相对路径保证能找到 core
sys.path.append(str(Path(__file__).resolve().parent.parent))

from core.engines.daily_report_engine import DailyReportEngine


async def run_test():
    engine = DailyReportEngine()
    
    # 场景 1: 没有天气干预
    res_normal = await engine.get_daily_report(
        user_id="test_user_1",
        constitution_vector={"平和质": 100},
        available_ingredients=["薏米", "赤小豆", "山药", "猪肉", "大白菜"],
        force_refresh=True,
    )
    
    print("=== 无天气干预 ===")
    print("推荐食材:", res_normal["recommended_ingredients"][:5])
    print("报告文本:", res_normal["report_text"])
    
    # 场景 2: 高湿天气干预
    res_wet = await engine.get_daily_report(
        user_id="test_user_1",
        constitution_vector={"平和质": 100},
        available_ingredients=["薏米", "赤小豆", "山药", "猪肉", "大白菜"],
        force_refresh=True,
        weather_data={"humidity": 85, "temperature": 28, "city": "广州"}
    )
    
    print("\n=== 高湿度干预 ===")
    print("环境变量生效:", res_wet.get("environmental_tags"))
    print("推荐食材:", res_wet["recommended_ingredients"][:5])
    print("报告文本:", res_wet["report_text"])
    
    # 场景 3: 寒冷天气干预
    res_cold = await engine.get_daily_report(
        user_id="test_user_1",
        constitution_vector={"平和质": 100},
        available_ingredients=["生姜", "羊肉", "白萝卜", "猪肉", "大白菜"],
        force_refresh=True,
        weather_data={"humidity": 40, "temperature": 5, "city": "北京"}
    )
    
    print("\n=== 寒冷天气干预 ===")
    print("环境变量生效:", res_cold.get("environmental_tags"))
    print("推荐食材:", res_cold["recommended_ingredients"][:5])
    print("报告文本:", res_cold["report_text"])

if __name__ == "__main__":
    asyncio.run(run_test())
