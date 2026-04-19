"""
数据加载器
从 CSV 文件加载食疗数据
"""
import csv
from typing import List, Optional, Union
from pathlib import Path
from models.therapy import TherapyDetail


def load_therapy_data(file_path: Union[str, Path]) -> List[TherapyDetail]:
    """
    从 CSV 文件加载食疗数据
    
    Args:
        file_path: CSV 文件路径
        
    Returns:
        食疗详情列表
    """
    therapy_items = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # 解析数据
                id = int(row.get('id', 0))
                name = row.get('name', '')
                
                # 解析标签，处理多个标签的情况
                tags_str = row.get('tags', '')
                tags = [tag.strip() for tag in tags_str.split('/') if tag.strip()]
                
                # 解析制作方法
                methods = row.get('methods', '')
                
                # 解析搭配食材
                matches_str = row.get('matches', '')
                matches = [match.strip() for match in matches_str.split('/') if match.strip()]
                
                # 解析禁忌
                taboos_str = row.get('taboos', '')
                taboos = [taboo.strip() for taboo in taboos_str.split('/') if taboo.strip()]
                
                # 解析适用体质
                constitution_str = row.get('constitution', '')
                constitution = [con.strip() for con in constitution_str.split('/') if con.strip()]
                
                # 创建 TherapyDetail 对象
                therapy_item = TherapyDetail(
                    id=id,
                    name=name,
                    tags=tags,
                    methods=methods,
                    matches=matches,
                    taboos=taboos,
                    constitution=constitution
                )
                
                therapy_items.append(therapy_item)
    except Exception as e:
        print(f"加载食疗数据失败: {e}")
    
    return therapy_items
