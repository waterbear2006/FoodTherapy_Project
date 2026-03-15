"""
食疗库系统入口
90%+ 代码为数据结构与算法实现
"""
import sys
import os

# 将项目根目录强制加入 Python 搜索路径（兜底方案）
project_root = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, project_root)

# 之后再导入 core 模块
from core.food_therapy import TherapyService, TherapyDetail

if __name__ == "__main__":
    print("导入成功！")
from core.food_therapy import TherapyService, TherapyDetail


def demo_without_data():
    """无数据文件时的演示：手动插入示例"""
    service = TherapyService()
    # 手动添加示例数据
    items = [
        TherapyDetail(
            id=1,
            name="山药粥",
            tags=["补气", "健脾"],
            methods="山药洗净切块，与大米同煮成粥",
            matches=["大米", "枸杞", "红枣"],
            taboos=["萝卜", "甘遂"],
            constitution=["气虚质", "阳虚质"],
        ),
        TherapyDetail(
            id=2,
            name="薏米红豆汤",
            tags=["去湿", "健脾"],
            methods="薏米、红豆浸泡后同煮，可加冰糖",
            matches=["红豆", "冰糖", "茯苓"],
            taboos=["孕妇慎用"],
            constitution=["湿热质", "痰湿质"],
        ),
        TherapyDetail(
            id=3,
            name="枸杞菊花茶",
            tags=["明目", "养肝"],
            methods="枸杞、菊花沸水冲泡",
            matches=["菊花", "决明子", "蜂蜜"],
            taboos=["脾胃虚寒慎用"],
            constitution=["阴虚质", "气郁质"],
        ),
    ]
    for item in items:
        service.add_item(item)

    print("=== 1. Trie 前缀搜索 ===")
    for r in service.search_by_name("山"):
        print(f"  {r.name}: {r.tags}")

    print("\n=== 2. Hash 标签筛选 ===")
    for r in service.filter_by_tag("健脾"):
        print(f"  {r.name}")

    print("\n=== 3. 体质匹配 ===")
    for r in service.filter_by_constitution("气虚质"):
        print(f"  {r.name}: {r.constitution}")

    print("\n=== 4. KMP 全文检索 ===")
    for r in service.full_text_search("冰糖"):
        print(f"  {r.name}: methods 含「冰糖」")

    print("\n=== 5. 食材搭配与禁忌 ===")
    print("  薏米红豆汤 搭配:", service.get_matches("薏米红豆汤"))
    print("  薏米红豆汤 禁忌:", service.get_taboos("薏米红豆汤"))

    print("\n=== 6. DFS 组合寻优 ===")
    for combo in service.find_compatible_combinations("薏米红豆汤", max_depth=2):
        print("  ", combo)


def main():
    import os
    csv_path = os.path.join(os.path.dirname(__file__), "therapy_data.csv")
    service = TherapyService(file_path=csv_path)

    if os.path.exists(csv_path):
        n = service.load_data()
        print(f"已从 {csv_path} 加载 {n} 条数据。")
        # 快速演示
        print("\n--- 演示 ---")
        print("Trie 搜索「山」:", [r.name for r in service.search_by_name("山")])
        print("标签「健脾」:", [r.name for r in service.filter_by_tag("健脾")])
        print("KMP 全文「冰糖」:", [r.name for r in service.full_text_search("冰糖")])
    else:
        print("未找到 therapy_data.csv，使用内置示例演示。")
        demo_without_data()
        return

    print("\n食疗库系统已准备就绪。")
    print("1. 搜索功能：基于 Trie 前缀树算法。")
    print("2. 分类功能：基于 Hash Map 索引。")
    print("3. 全文检索：基于 KMP 字符串匹配。")
    print("4. 搭配/禁忌：基于图结构 + DFS 组合寻优。")
    print("5. 缓存：Hash Map + 双向链表 LRU。")


if __name__ == "__main__":
    main()
