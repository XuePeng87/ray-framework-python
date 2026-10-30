"""
部门模块 ATO - 请求模型（对外接口契约）

这些模型定义了 API 接口接收的请求格式
面向前端/外部调用者，需要考虑稳定性和兼容性
"""
from typing import Optional
from pydantic import BaseModel, Field

from app.common.base_request import BasePageRequest
from app.modules.dept.ato.constants import (
    PARENT_CODE_DESCRIPTION,
    PARENT_CODE_EXAMPLES,
    NAME_DESCRIPTION,
    NAME_EXAMPLES,
    STATUS_DESCRIPTION,
    STATUS_EXAMPLES,
    SEQUENCE_DESCRIPTION,
    SEQUENCE_EXAMPLES,
    REMARK_DESCRIPTION,
    REMARK_EXAMPLES,
    NEW_PARENT_CODE_DESCRIPTION,
    NEW_PARENT_CODE_EXAMPLES,
    NAME_QUERY_DESCRIPTION,
    PARENT_CODE_QUERY_DESCRIPTION,
)


class DeptCreateRequest(BaseModel):
    """
    创建部门请求 ATO

    面向前端：定义创建部门时需要传入的字段
    """
    parent_code: str = Field(
        ...,
        min_length=1,
        max_length=32,
        description=PARENT_CODE_DESCRIPTION,
        examples=PARENT_CODE_EXAMPLES,
    )
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


class DeptUpdateRequest(BaseModel):
    """
    更新部门请求 ATO

    面向前端：定义更新部门时可以传入的字段
    所有字段可选，只更新传入的字段
    """
    name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=32,
        description=NAME_DESCRIPTION,
        examples=["产品部"],
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
        description=SEQUENCE_DESCRIPTION,
        examples=[2],
    )
    remark: Optional[str] = Field(
        None,
        max_length=256,
        description=REMARK_DESCRIPTION,
        examples=["产品研发部门"],
    )


class DeptQueryRequest(BasePageRequest):
    """
    部门查询请求 ATO

    面向前端：定义查询部门时的参数
    继承 BasePageRequest 获得分页能力
    """
    parent_code: Optional[str] = Field(
        None,
        description=PARENT_CODE_QUERY_DESCRIPTION,
        examples=PARENT_CODE_EXAMPLES,
    )
    name: Optional[str] = Field(
        None,
        description=NAME_QUERY_DESCRIPTION,
        examples=["技术"],
    )
    status: Optional[int] = Field(
        None,
        ge=0,
        le=1,
        description=STATUS_DESCRIPTION,
        examples=STATUS_EXAMPLES,
    )


class DeptMoveRequest(BaseModel):
    """
    移动部门请求 ATO

    面向前端：定义移动部门时需要传入的字段
    """
    new_parent_code: str = Field(
        ...,
        min_length=1,
        max_length=32,
        description=NEW_PARENT_CODE_DESCRIPTION,
        examples=NEW_PARENT_CODE_EXAMPLES,
    )
