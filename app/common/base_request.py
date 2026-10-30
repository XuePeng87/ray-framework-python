from typing import Optional
from pydantic import BaseModel, Field


class BasePageRequest(BaseModel):
    """
    分页查询基类

    用于需要分页的查询请求，提供通用分页字段
    """
    page: int = Field(
        1,
        ge=1,
        description="页码（从1开始）",
        examples=[1]
    )
    page_size: int = Field(
        10,
        ge=1,
        le=100,
        description="每页数量（1-100）",
        examples=[10]
    )


class BaseSortRequest(BaseModel):
    """
    排序查询基类

    用于需要排序的查询请求，提供通用排序字段
    """
    sort_by: Optional[str] = Field(
        None,
        description="排序字段",
        examples=["create_time"]
    )
    sort_order: Optional[str] = Field(
        None,
        pattern="^(asc|desc)$",
        description="排序方向：asc=升序，desc=降序",
        examples=["desc"]
    )


class BaseQueryRequest(BasePageRequest, BaseSortRequest):
    """
    完整查询基类

    同时支持分页和排序的查询请求
    """
    pass
