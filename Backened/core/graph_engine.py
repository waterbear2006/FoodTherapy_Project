import pandas as pd
import os
from collections import deque
from pathlib import Path
import threading

# 定义节点类型常量
TYPE_INGREDIENT = "ingredient"
TYPE_RECIPE = "recipe"
TYPE_CONSTITUTION = "constitution"
TYPE_EFFECT = "effect"

class GraphEngine:
    def __init__(self):
        self.adj_list = {}
        self.nodes_info = {}
        self.data_loaded = False
        self._lock = threading.Lock()
        self.base_dir = Path(__file__).resolve().parent.parent
        self.csv_paths = {
            "shicai": self.base_dir / "data" / "shicai_enriched.csv",
            "caipu": self.base_dir / "data" / "caipu_enriched.csv"
        }

    def _add_edge(self, node_u, type_u, node_v, type_v, attr_u=None, attr_v=None, role=None, metadata_u=None, metadata_v=None):
        """
        向邻接表中添加一条无向边，并保存节点属性及关联角色 (如君臣佐使)
        """
        if not node_u or not node_v:
            return

        # 确保节点存在
        if node_u not in self.adj_list:
            self.adj_list[node_u] = set()
            self.nodes_info[node_u] = {"type": type_u, "summary": attr_u or "", "metadata": metadata_u or {}}
        if node_v not in self.adj_list:
            self.adj_list[node_v] = set()
            self.nodes_info[node_v] = {"type": type_v, "summary": attr_v or "", "metadata": metadata_v or {}}

        # 补全属性
        if attr_u and not self.nodes_info[node_u]["summary"]:
             self.nodes_info[node_u]["summary"] = attr_u
        if attr_v and not self.nodes_info[node_v]["summary"]:
             self.nodes_info[node_v]["summary"] = attr_v

        # 补全元数据
        if metadata_u:
            self.nodes_info[node_u]["metadata"].update(metadata_u)
        if metadata_v:
            self.nodes_info[node_v]["metadata"].update(metadata_v)

        # 添加边 (双向)
        # 存储边时保留角色信息，使用字典替换原有的集合元素（或单独维护边属性）
        self.adj_list[node_u].add((node_v, role))
        self.adj_list[node_v].add((node_u, role))

    def _split_field(self, field_value):
        """
        处理复杂的分隔符情况
        """
        if pd.isna(field_value) or not isinstance(field_value, str):
            return []
        
        # 兼容多种中英文分隔符
        delimiters = ['、', '，', ',', ';', '；', '\n']
        current_list = [field_value]
        
        for sep in delimiters:
            new_list = []
            for item in current_list:
                new_list.extend([x.strip() for x in item.split(sep) if x.strip()])
            current_list = new_list
            
        return current_list

    def load_data(self):
        """
        加载 CSV 数据并构建邻接表
        """
        with self._lock:
            if self.data_loaded:
                return
            print("🚀 Loading graph data (Cyber TCM Mode)...")
            try:
                # 1. 加载食材数据
                if self.csv_paths["shicai"].exists():
                    df_shicai = pd.read_csv(self.csv_paths["shicai"], encoding='utf-8')
                    for _, row in df_shicai.iterrows():
                        name = row['name']
                        effect_main = row.get('effect', '')
                        metadata = {
                            "tag": row.get('tag', ''),
                            "suitable": row.get('suitable', ''),
                            "avoid": row.get('avoid', ''),
                            "ancient_quote": row.get('ancient_quote', '')
                        }
                        
                        # 食材 ↔ 功效
                        effects = self._split_field(effect_main)
                        for eff in effects:
                            self._add_edge(name, TYPE_INGREDIENT, eff, TYPE_EFFECT, attr_u=effect_main, metadata_u=metadata)
                
                # 2. 加载菜谱数据 (包含君臣佐使逻辑)
                if self.csv_paths["caipu"].exists():
                    df_caipu = pd.read_csv(self.csv_paths["caipu"], encoding='utf-8')
                    for _, row in df_caipu.iterrows():
                        recipe_name = row['name']
                        recipe_eff = row.get('effect', '')
                        metadata = {
                            "ancient_quote": row.get('ancient_quote', ''),
                            "suitable": row.get('suitable', ''),
                            "taboo": row.get('taboo', ''),
                            "ingredients_list": row.get('ingredients', '')
                        }
                        
                        # 菜谱 ↔ 食材
                        ingredients = self._split_field(row.get('ingredients'))
                        for idx, ing in enumerate(ingredients):
                            role = "Jun" if idx == 0 else ("Chen" if idx == 1 else ("Zuo" if idx == 2 else "Shi"))
                            self._add_edge(recipe_name, TYPE_RECIPE, ing, TYPE_INGREDIENT, attr_u=recipe_eff, role=role, metadata_u=metadata)
                            
                        # 菜谱 ↔ 体质
                        constitutions = self._split_field(row.get('suitable'))
                        for const in constitutions:
                            self._add_edge(recipe_name, TYPE_RECIPE, const, TYPE_CONSTITUTION, attr_u=recipe_eff, metadata_u=metadata)
                            
                self.data_loaded = True
                print(f"✅ Cyber Graph constructed: {len(self.nodes_info)} nodes.")
            except Exception as e:
                print(f"❌ Error loading cyber graph: {e}")
                self.data_loaded = False

    def get_subgraph(self, center_node_name, depth=1):
        """
        使用 BFS (广度优先搜索) 检索子图
        支持返回节点度数 (Degree) 和 属性 (Summary)
        以及 边角色 (Role)
        """
        if not self.data_loaded:
            self.load_data()
            
        if center_node_name not in self.nodes_info:
            return {"nodes": [], "links": []}

        nodes_dict = {}
        links = []
        visited_nodes = {center_node_name}
        visited_edges = set()
        queue = deque([(center_node_name, 0)])

        category_map = {
            TYPE_INGREDIENT: 0,
            TYPE_RECIPE: 1,
            TYPE_CONSTITUTION: 2,
            TYPE_EFFECT: 3
        }

        # BFS 核心循环
        center_is_recipe = self.nodes_info[center_node_name]["type"] == TYPE_RECIPE

        while queue:
            current_node, current_depth = queue.popleft()
            
            # 确定节点在当前上下文中的角色 (默认 None)
            contextual_role = None
            if center_is_recipe and current_depth == 1:
                # 从边关系中找角色
                for neighbor, role in self.adj_list.get(center_node_name, []):
                    if neighbor == current_node:
                        contextual_role = role
                        break
            elif current_node == center_node_name and center_is_recipe:
                contextual_role = "Jun" # 菜谱自身在图中作为核心

            # 添加节点信息
            info = self.nodes_info[current_node]
            nodes_dict[current_node] = {
                "id": current_node,
                "name": current_node,
                "category": category_map.get(info["type"], 4),
                "summary": info.get("summary", ""),
                "degree": len(self.adj_list.get(current_node, set())),
                "metadata": info.get("metadata", {}),
                "role": contextual_role  # 注入上下文角色
            }

            if current_depth < depth:
                neighbors_with_roles = self.adj_list.get(current_node, [])
                for neighbor, role in neighbors_with_roles:
                    # 记录边
                    edge_key = tuple(sorted((current_node, neighbor)))
                    if edge_key not in visited_edges:
                        links.append({
                            "source": current_node,
                            "target": neighbor,
                            "role": role  # 返回角色信息
                        })
                        visited_edges.add(edge_key)
                    
                    if neighbor not in visited_nodes:
                        visited_nodes.add(neighbor)
                        queue.append((neighbor, current_depth + 1))

        return {"nodes": list(nodes_dict.values()), "links": links}

# 单例模式
engine = GraphEngine()

# 为了在 FastAPI 启动时预加载，可以暴露一个初始化函数
def init_graph():
    engine.load_data()
