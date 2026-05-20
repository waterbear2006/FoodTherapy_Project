"""搜索匹配工具：统一关键词与多值字段的匹配规则。"""
import re
from typing import List, Optional


def split_multi(value: Optional[str]) -> List[str]:
    """把 CSV 的多值字段拆成列表（兼容 、/，/空格 等分隔符）。"""
    if not value:
        return []
    return [p.strip() for p in re.split(r"[、，,/;\s]+", value) if p.strip()]


def matches_ingredient_keyword(item: dict, keyword: str, trie_search_prefix) -> bool:
    """
    食材关键词匹配：名称、功效标签、体质、做法。
    不匹配 avoid（禁忌列举的是相克食材，非本食材属性）。
    """
    kw = keyword.strip()
    if not kw:
        return True

    name = str(item.get("name", ""))
    matched_names = trie_search_prefix(kw)
    if name in matched_names or kw in name:
        return True

    for field in ("tag", "effect", "suitable", "methods"):
        val = item.get(field)
        if val and kw in str(val):
            return True
    return False


def matches_recipe_keyword(recipe, keyword: str, use_full_text: bool = False) -> bool:
    """
    菜谱关键词匹配：名称、食材列表、功效。
    默认不匹配 taboo/steps（多为相克说明或操作步骤中的其他食材名）。
    """
    kw = keyword.strip()
    if not kw:
        return True

    if kw in recipe.name:
        return True
    if any(kw in ing for ing in (recipe.ingredients or [])):
        return True
    if any(kw in effect for effect in (recipe.effect or [])):
        return True
    if use_full_text:
        if recipe.steps and kw in recipe.steps:
            return True
        if recipe.taboo and kw in recipe.taboo:
            return True
    return False
