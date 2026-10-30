"""
角色模块 ATO - 请求模型（对外接口契约）

这些模型定义了 API 接口接收的请求格式
面向前端/外部调用者，需要考虑稳定性和兼容性
"""
from typing import Optional
from pydantic import BaseModel, Field

from app.common.base_request import BasePageRequest
from app.modules.role.ato.constants import (
    NAME_DESCRIPTION,
    NAME_EXAMPLES,
    STATUS_DESCRIPTION,
    STATUS_EXAMPLES,
    SEQUENCE_DESCRIPTION,
    SEQUENCE_EXAMPLES,
    REMARK_DESCRIPTION,
    REMARK_EXAMPLES,
    CODE_QUERY_DESCRIPTION,
    CODE_EXAMPLES,
    NAME_QUERY_DESCRIPTION,
    FUNC_CODES_DESCRIPTION,
    FUNC_CODES_EXAMPLES,
)


class RoleCreateRequest(BaseModel):
    """
    创建角色请求 ATO

    面向前端：定义创建角色时需要传入的字段
    """
    name: str = Field(
        ...,
        min_length=1,
        max_length=32,
        description=NAME_DESCRIPTION,
        examples=NAME_EXAMPLES,
    )
    status: int = Field(
        ...,
        ge=0,
        le=1,
        description=STATUS_DESCRIPTION,
        examples=STATUS_EXAMPLES,
    )
    sequence: int = Field(
        ...,
        ge=0,
        description=SEQUENCE_DESCRIPTION,
        examples=SEQUENCE_EXAMPLES,
    )
    remark: Optional[str] = Field(
        None,
        max_length=256,
        description=REMARK_DESCRIPTION,
        examples=REMARK_EXAMPLES,
    )


class RoleUpdateRequest(BaseModel):
    """
    更新角色请求 ATO

    面向前端：定义更新角色时可以传入的字段
    所有字段可选，只更新传入的字段
    """
    name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=32,
        description=NAME_DESCRIPTION,
        examples=["超级管理员"],
    )
    status: Optional[int] = Field(
        None,
        ge=0,
        le=1,
        description=STATUS_DESCRIPTION,
        examples=STATUS_EXAMPLES,
    )
    sequence: Optional[int] = Field(
        None,
        ge=0,
        description="排序",
        examples=[2],
    )
    remark: Optional[str] = Field(
        None,
        max_length=256,
        description=REMARK_DESCRIPTION,
        examples=["系统超级管理员角色"],
    )


class RoleQueryRequest(BasePageRequest):
    """
    角色查询请求 ATO

    面向前端：定义查询角色时的参数
    继承 BasePageRequest 获得分页能力
    """
    code: Optional[str] = Field(
        None,
        description=CODE_QUERY_DESCRIPTION,
        examples=CODE_EXAMPLES,
    )
    name: Optional[str] = Field(
        None,
        description=NAME_QUERY_DESCRIPTION,
        examples=["管理"],
    )
    status: Optional[int] = Field(
        None,
        ge=0,
        le=1,
        description=STATUS_DESCRIPTION,
        examples=STATUS_EXAMPLES,
    )


class GrantPermissionsRequest(BaseModel):
    """
    授权功能请求 ATO

    面向前端：定义授权时需要传入的字段
    """
    func_codes: list[str] = Field(
        ...,
        min_length=1,
        description=FUNC_CODES_DESCRIPTION,
        examples=FUNC_CODES_EXAMPLES,
    )
