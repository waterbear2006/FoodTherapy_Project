from pydantic import BaseModel
from typing import Optional

class StandardResourceResponse(BaseModel):
    name: str
    summary: str
    ancient_quote: str = ""
    type: str  # ingredient, recipe, category
