"""
测试每日报告 API
"""
import asyncio
from api.reports import generate_daily_report
from models.daily_report import DailyReportRequest


async def test_daily_report():
    # 模拟请求数据
    payload = DailyReportRequest(
        user_id="test_user_001",
        constitution_vector={
            "平和质": 0.3,
            "气虚质": 0.8,
            "阳虚质": 0.5,
            "阴虚质": 0.2,
            "痰湿质": 0.3,
            "湿热质": 0.4,
            "血瘀质": 0.2,
            "气郁质": 0.3,
            "特禀质": 0.1,
        },
        available_ingredients=["山药", "红枣", "小米"],
        force_refresh=True,
    )
    
    # 调用接口
    result = await generate_daily_report(payload)
    
    print("=" * 60)
    print("📊 每日养生建议报告")
    print("=" * 60)
    print(f"用户 ID: {result.user_id}")
    print(f"日期：{result.date}")
    print(f"节气：{result.solar_term} ({result.season})")
    print(f"主体质：{result.primary_constitution}")
    print(f"\n📝 养生建议:")
    print(result.report_text)
    print(f"\n🥬 推荐食材:")
    for ing in result.recommended_ingredients[:5]:
        print(f"  - {ing}")
    print(f"\n🍲 推荐菜谱:")
    for recipe in result.recommended_recipes[:3]:
        print(f"  - {recipe.recipe_name} (匹配度：{recipe.match_rate:.0%})")
    print(f"\n💡 UI 卡片:")
    print(f"  标题：{result.ui_card.module_title}")
    print(f"  标签：{result.ui_card.season_tag}")
    print(f"  推荐食疗：{result.ui_card.recommended_recipe}")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_daily_report())
