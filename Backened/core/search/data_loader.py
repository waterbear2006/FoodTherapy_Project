"""
<<<<<<< HEAD
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
=======
数据加载接口
支持 .csv / .xlsx，预留扩展
"""
from pathlib import Path
from typing import List, Optional, Union

import pandas as pd

from .models import TherapyDetail


def load_from_csv(path: Union[str, Path]) -> pd.DataFrame:
    """从 CSV 加载"""
    return pd.read_csv(path)


def load_from_excel(path: Union[str, Path], sheet: Union[int, str] = 0) -> pd.DataFrame:
    """从 Excel 加载"""
    return pd.read_excel(path, sheet_name=sheet)


def parse_row_to_therapy(row: pd.Series) -> TherapyDetail:
    """
    将数据行解析为 TherapyDetail
    列名约定：id, name, tags, methods, matches, taboos, constitution
    多值字段用逗号分隔
    """
    def _split(s) -> List[str]:
        if pd.isna(s):
            return []
        raw = str(s).strip()
        if not raw:
            return []
        # 支持逗号、斜杠分隔
        parts = raw.replace("/", ",").split(",")
        return [x.strip() for x in parts if x.strip()]

    return TherapyDetail(
        id=int(row["id"]),
        name=str(row["name"]).strip(),
        tags=_split(row.get("tags", "")),
        methods=str(row.get("methods", "")).strip(),
        matches=_split(row.get("matches", "")),
        taboos=_split(row.get("taboos", "")),
        constitution=_split(row.get("constitution", "")),
    )


def load_therapy_data(
    path: Union[str, Path],
    format_hint: Optional[str] = None,
) -> List[TherapyDetail]:
    """
    统一加载接口
    format_hint: "csv" | "excel" | None(自动根据后缀)
    """
    path = Path(path)
    if not path.exists():
        return []

    fmt = format_hint or path.suffix.lower().lstrip(".")
    if fmt in ("csv",):
        df = load_from_csv(path)
    elif fmt in ("xlsx", "xls"):
        df = load_from_excel(path)
    else:
        raise ValueError(f"不支持格式: {fmt}")

    items: List[TherapyDetail] = []
    for _, row in df.iterrows():
        try:
            items.append(parse_row_to_therapy(row))
        except Exception as e:
            # 可记录日志
            continue
    return items
>>>>>>> 5509c1398c0685e011f840fcbbe6dd0969d7e3cb
