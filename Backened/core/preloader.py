"""
[System Preloader] 系统预加载器
职责：读取 data/ 中的 CSV 数据，并将其装载至内存中的 Graph、Trie 和 HashIndex。
内容：实现“系统预热 (Warm-up)”，确保 API 响应为毫秒级。
"""
import csv
from pathlib import Path

# 导入数据结构
from core.structures.trie import Trie
from core.structures.hash_index import HashIndex

# 1. 初始化全局单例实例 (Global Singletons)
# 这样其他模块 (如 api/recipes.py) 直接 import 就能用
ingredient_trie = Trie()
recipe_hash_index = HashIndex()
ingredient_db = {}  # 全局食材数据库
ingredient_by_name = {} # 按名称索引的数据库

def load_all_data():
    """系统启动时调用的主加载函数"""
    base_path = Path(__file__).resolve().parent.parent / "data"
    
    # --- 加载食材数据 ---
    ingredients_file = base_path / "shicai_enriched.csv"
    
    try:
        with open(ingredients_file, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # 构建食材对象
                # 使用 tag 字段作为分类（如：补气、补血、滋阴等）
                
                ancient_quote = row.get("ancient_quote", "")
                if not ancient_quote:
                    ancient_quote = row.get("quote", "")
                if not ancient_quote:
                    ancient_quote = row.get("reason", "")
                
                ingredient = {
                    "id": int(row["id"]),
                    "name": row["name"],
                    "tag": row["tag"],
                    "effect": row["effect"],
                    "suitable": row["suitable"],
                    "avoid": row["avoid"],
                    "methods": row["methods"],
                    "images": row["images"].strip(),
                    "category": row["tag"] if row.get("tag") else "其他",  # 使用 tag 作为分类
                    "property": None,  # 可根据需要补充
                    "description": None,  # 可根据需要补充
                    "related_recipes": [],  # 可根据需要补充
                    "ancient_quote": ancient_quote
                }
                
                # 添加到全局食材数据库
                ingredient_db[int(row["id"])] = ingredient
                ingredient_by_name[row["name"]] = ingredient
                
                # B. 装载到前缀树 (Trie) -> 用于搜索框自动补全
                ingredient_trie.insert(row["name"])
                
                # C. 装载到哈希索引 (HashIndex) -> 用于 O(1) 极速反查
                recipe_hash_index.add(row["name"], row["id"])
        
        print(f"[Preloader] 成功加载 {len(ingredient_db)} 种食材数据到内存结构。")

    except FileNotFoundError:
        print(f"[Preloader] 警告：未找到数据文件 {ingredients_file}，算法实例为空。")
    except Exception as e:
        print(f"[Preloader] 发生错误: {e}")

# 在模块被导入时，可以手动调用一次，或者在 main.py 启动时调用