import sys
import os
from pathlib import Path

# --- 路径适配核心步骤 ---
# 1. 获取当前 main.py 所在的根目录
project_root = Path(__file__).resolve().parent

# 2. 将根目录加入 sys.path，这样 Python 才能识别出 'core' 是一个包
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# 3. 按照新结构进行导入 (对应 core/food_therapy/__init__.py 中的导出)
try:
    from core.foodtherapy import TherapyService, TherapyDetail
except ImportError as e:
    print(f"导入失败，请确保文件夹内包含 __init__.py 文件。错误: {e}")
    sys.exit(1)

def run_demo(service: TherapyService):
    """演示新结构下的功能"""
    print("\n=== 1. Trie 前缀搜索 (匹配「山」) ===")
    results = service.search_by_name("山")
    for r in results:
        print(f"  找到食疗方: {r.name}")

    print("\n=== 2. 图算法：食材搭配推荐 ===")
    # 假设数据中包含该项
    combos = service.find_compatible_combinations("山药", max_depth=2)
    print(f"  与「山药」兼容的组合建议: {combos}")

def main():
    # 4. 自动定位数据文件 (假设它在根目录)
    csv_path = project_root / "therapy_data.csv"
    
    # 初始化服务
    service = TherapyService(file_path=csv_path)

    if csv_path.exists():
        count = service.load_data()
        print(f"成功加载数据：{count} 条 (来源: {csv_path})")
        run_demo(service)
    else:
        print(f"[警告] 未找到数据文件: {csv_path}，将进入空数据演示模式。")
        # 这里可以调用你之前的 demo_without_data() 逻辑

if __name__ == "__main__":
    main()