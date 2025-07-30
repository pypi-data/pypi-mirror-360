from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field
from common.database.base_models import BaseSQLModel


class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None

class PaginatedAPIResponse(APIResponse):
    total: int
    limit: int
    offset: int
    items: List[dict]

class SortBy(str, Enum):
    relevance = "relevance"
    created_at = "created_at"
    updated_at = "updated_at"

class SortOrder(str, Enum):
    asc = "asc"
    desc = "desc"

class PaginationParams(BaseModel):
    limit: int = Field(default=10, ge=1, le=100, description="Number of results to return")
    offset: int = Field(default=0, ge=0, description="Number of results to skip")
    sort_by: SortBy = Field(default=SortBy.relevance, description="Field to sort by")
    sort_order: SortOrder = Field(default=SortOrder.desc, description="Sort order")
