from typing import Dict, List

from pydantic import BaseModel, Field


class DailyReportRequest(BaseModel):
    user_id: str = Field(..., description="用户 ID")
    constitution_vector: Dict[str, float] = Field(..., description="九维体质得分向量")
    available_ingredients: List[str] = Field(default_factory=list, description="用户当日可用食材")
    force_refresh: bool = Field(default=False, description="是否强制刷新同日报告")


class DailyRecommendationRecipe(BaseModel):
    recipe_id: int = Field(..., description="菜谱 ID")
    recipe_name: str = Field(..., description="菜谱名称")
    match_rate: float = Field(..., description="匹配度")
    matched_ingredients: List[str] = Field(default_factory=list, description="已命中食材")
    required_ingredients: List[str] = Field(default_factory=list, description="菜谱所需食材")


class DailySuggestionCard(BaseModel):
    module_title: str = Field(default="今日养生", description="模块标题")
    suggestion_title: str = Field(default="今日养生建议", description="建议标题")
    season_tag: str = Field(..., description="节气/调养标签")
    intro: str = Field(..., description="建议导语")
    recommended_ingredients: List[str] = Field(default_factory=list, description="推荐食材")
    recommended_recipe: str = Field(..., description="推荐食疗名称")
    recipe_tip: str = Field(..., description="食疗建议文案")


class DailyReportResponse(BaseModel):
    user_id: str = Field(..., description="用户 ID")
    date: str = Field(..., description="报告日期 YYYY-MM-DD")
    primary_constitution: str = Field(..., description="当日主体质")
    solar_term: str = Field(..., description="当前节气")
    season: str = Field(..., description="当前季节")
    constitution_vector: Dict[str, float] = Field(..., description="体质得分向量")
    constitution_delta: Dict[str, float] = Field(..., description="相对上一日变化")
    matched_tags: List[str] = Field(default_factory=list, description="体质匹配标签")
    recommended_ingredients: List[str] = Field(default_factory=list, description="推荐食材集合")
    recommended_recipe_ids: List[int] = Field(default_factory=list, description="推荐菜谱 ID 集合")
    recommended_recipes: List[DailyRecommendationRecipe] = Field(default_factory=list, description="推荐菜谱详情")
    report_text: str = Field(..., description="健康日报文本")
    ui_card: DailySuggestionCard = Field(..., description="前端建议卡片结构")
    cache_hit: bool = Field(..., description="是否命中同日缓存")
