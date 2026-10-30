"""
角色模块 ATO - 响应模型（对外接口契约）

这些模型定义了 API 接口返回的响应格式
面向前端/外部调用者，需要考虑稳定性和兼容性
"""
from datetime import datetime
from typing import Optional, List, TypeVar, Generic
from pydantic import BaseModel, Field

from app.common.base_response import BaseResponse
from app.modules.role.ato.constants import (
    ID_DESCRIPTION,
    ID_EXAMPLES,
    CODE_DESCRIPTION,
    CODE_EXAMPLES,
    NAME_DESCRIPTION,
    NAME_EXAMPLES,
    STATUS_DESCRIPTION,
    STATUS_EXAMPLES,
    SEQUENCE_DESCRIPTION,
    SEQUENCE_EXAMPLES,
    REMARK_DESCRIPTION,
    REMARK_EXAMPLES,
    CREATE_TIME_DESCRIPTION,
    CREATE_TIME_EXAMPLES,
    MODIFY_TIME_DESCRIPTION,
    MODIFY_TIME_EXAMPLES,
    ITEMS_DESCRIPTION,
    PAGE_DESCRIPTION,
    PAGE_EXAMPLES,
    PAGE_SIZE_DESCRIPTION,
    PAGE_SIZE_EXAMPLES,
    TOTAL_DESCRIPTION,
    TOTAL_EXAMPLES,
    TOTAL_PAGES_DESCRIPTION,
    TOTAL_PAGES_EXAMPLES,
)


T = TypeVar("T")


class RoleResponse(BaseResponse):
    """
    角色响应 ATO

    面向前端：定义返回给前端的角色信息格式
    """
    id: int = Field(
        ...,
        description=ID_DESCRIPTION,
        examples=ID_EXAMPLES,
    )
    code: str = Field(
        ...,
        description=CODE_DESCRIPTION,
        examples=CODE_EXAMPLES,
    )
    name: str = Field(
        ...,
        description=NAME_DESCRIPTION,
        examples=NAME_EXAMPLES,
    )
    status: int = Field(
        ...,
        description=STATUS_DESCRIPTION,
        examples=STATUS_EXAMPLES,
    )
    sequence: int = Field(
        ...,
        description=SEQUENCE_DESCRIPTION,
        examples=SEQUENCE_EXAMPLES,
    )
    remark: Optional[str] = Field(
        None,
        description=REMARK_DESCRIPTION,
        examples=REMARK_EXAMPLES,
    )
    create_time: datetime = Field(
        ...,
        description=CREATE_TIME_DESCRIPTION,
        examples=CREATE_TIME_EXAMPLES,
    )
    modify_time: datetime = Field(
        ...,
        description=MODIFY_TIME_DESCRIPTION,
        examples=MODIFY_TIME_EXAMPLES,
    )

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "examples": [
                {
                    "id": 1,
                    "code": "ROLE_ADMIN",
                    "name": "管理员",
                    "status": 1,
                    "sequence": 1,
                    "remark": "系统管理员角色",
                    "create_time": "2026-01-15T10:30:00",
                    "modify_time": "2026-01-15T10:30:00"
                }
            ]
        }
    }


class PageResponse(BaseModel, Generic[T]):
    """
    分页响应 ATO（泛型）

    面向前端：定义分页查询的返回格式
    可以复用于其他模块的分页响应
    """
    items: List[T] = Field(
        ...,
        description=ITEMS_DESCRIPTION,
    )
    total: int = Field(
        ...,
        ge=0,
        description=TOTAL_DESCRIPTION,
        examples=TOTAL_EXAMPLES,
    )
    page: int = Field(
        ...,
        ge=1,
        description=PAGE_DESCRIPTION,
        examples=PAGE_EXAMPLES,
    )
    page_size: int = Field(
        ...,
        ge=1,
        description=PAGE_SIZE_DESCRIPTION,
        examples=PAGE_SIZE_EXAMPLES,
    )
    total_pages: int = Field(
        ...,
        ge=0,
        description=TOTAL_PAGES_DESCRIPTION,
        examples=TOTAL_PAGES_EXAMPLES,
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "items": [],
                    "total": 0,
                    "page": 1,
                    "page_size": 10,
                    "total_pages": 0
                }
            ]
        }
    }
