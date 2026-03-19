"""
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
