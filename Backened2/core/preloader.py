import json
from core.structures.trie import Trie
from core.structures.hash_index import HashIndex

# 全局单例实例，供 api 层调用
ingredient_db = {} 
ingredient_trie = Trie()
recipe_inverted_index = HashIndex()

def load_all_data():
    """从 JSON 种子数据预热内存结构"""
    try:
        with open("data/ingredients.json", "r", encoding="utf-8") as f:
            raw_data = json.load(f) [cite: 8]
            
        for item in raw_data:
            idx = item["id"]
            # 1. 存入基础详情库 [cite: 8]
            ingredient_db[idx] = item
            
            # 2. 灌入对方写的 Trie 树（用于模块三前缀搜索） [cite: 20]
            ingredient_trie.insert(item["name"], idx)
            
            # 3. 灌入对方写的倒排索引（用于模块四反推） [cite: 15, 30]
            if "related_recipes" in item:
                for r_id in item["related_recipes"]:
                    recipe_inverted_index.add_mapping(idx, r_id)
        
        print(f"✅ [Preloader] 成功加载 {len(ingredient_db)} 种食材并构建索引")
    except Exception as e:
        print(f"❌ [Preloader] 数据预热失败: {e}")