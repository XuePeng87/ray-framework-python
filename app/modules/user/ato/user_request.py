"""
用户模块 ATO - 请求模型（对外接口契约）

这些模型定义了 API 接口接收的请求格式
面向前端/外部调用者，需要考虑稳定性和兼容性
"""
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr

from app.common.base_request import BasePageRequest
from app.modules.user.ato.constants import (
    DEPT_CODE_DESCRIPTION,
    DEPT_CODE_EXAMPLES,
    PHONE_NUMBER_DESCRIPTION,
    PHONE_NUMBER_EXAMPLES,
    NAME_DESCRIPTION,
    NAME_EXAMPLES,
    EMAIL_DESCRIPTION,
    EMAIL_EXAMPLES,
    STATUS_DESCRIPTION,
    STATUS_EXAMPLES,
    REMARK_DESCRIPTION,
    REMARK_EXAMPLES,
    ROLE_CODES_DESCRIPTION,
    ROLE_CODES_EXAMPLES,
    OLD_PASSWORD_DESCRIPTION,
    NEW_PASSWORD_DESCRIPTION,
)


class UserCreateRequest(BaseModel):
    """
    创建用户请求 ATO

    面向前端：定义创建用户时需要传入的字段
    """
    dept_code: str = Field(
        ...,
        min_length=1,
        max_length=32,
        description=DEPT_CODE_DESCRIPTION,
        examples=DEPT_CODE_EXAMPLES,
    )
    phone_number: str = Field(
        ...,
        min_length=11,
        max_length=32,
        description=PHONE_NUMBER_DESCRIPTION,
        examples=PHONE_NUMBER_EXAMPLES,
    )
    name: str = Field(
        ...,
        min_length=1,
        max_length=32,
        description=NAME_DESCRIPTION,
        examples=NAME_EXAMPLES,
    )
    email: EmailStr = Field(
        ...,
        max_length=128,
        description=EMAIL_DESCRIPTION,
        examples=EMAIL_EXAMPLES,
    )
    status: int = Field(
        ...,
        ge=0,
        le=1,
        description=STATUS_DESCRIPTION,
        examples=STATUS_EXAMPLES,
    )
    remark: Optional[str] = Field(
        None,
        max_length=256,
        description=REMARK_DESCRIPTION,
        examples=REMARK_EXAMPLES,
    )
    role_codes: List[str] = Field(
        default_factory=list,
        description=ROLE_CODES_DESCRIPTION,
        examples=ROLE_CODES_EXAMPLES,
    )


class UserUpdateRequest(BaseModel):
    """
    更新用户请求 ATO

    面向前端：定义更新用户时可以传入的字段
    所有字段可选，只更新传入的字段
    """
    dept_code: Optional[str] = Field(
        None,
        min_length=1,
        max_length=32,
        description=DEPT_CODE_DESCRIPTION,
        examples=DEPT_CODE_EXAMPLES,
    )
    phone_number: Optional[str] = Field(
        None,
        min_length=11,
        max_length=32,
        description=PHONE_NUMBER_DESCRIPTION,
        examples=PHONE_NUMBER_EXAMPLES,
    )
    name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=32,
        description=NAME_DESCRIPTION,
        examples=NAME_EXAMPLES,
    )
    email: Optional[EmailStr] = Field(
        None,
        max_length=128,
        description=EMAIL_DESCRIPTION,
        examples=EMAIL_EXAMPLES,
    )
    status: Optional[int] = Field(
        None,
        ge=0,
        le=1,
        description=STATUS_DESCRIPTION,
        examples=STATUS_EXAMPLES,
    )
    remark: Optional[str] = Field(
        None,
        max_length=256,
        description=REMARK_DESCRIPTION,
        examples=REMARK_EXAMPLES,
    )
    role_codes: Optional[List[str]] = Field(
        None,
        description=ROLE_CODES_DESCRIPTION,
        examples=ROLE_CODES_EXAMPLES,
    )


class UserUpdatePasswordRequest(BaseModel):
    """
    修改密码请求 ATO

    面向前端：定义修改密码时需要传入的字段
    """
    old_password: str = Field(
        ...,
        min_length=1,
        description=OLD_PASSWORD_DESCRIPTION,
    )
    new_password: str = Field(
        ...,
        min_length=6,
        max_length=128,
        description=NEW_PASSWORD_DESCRIPTION,
    )


class UserQueryRequest(BasePageRequest):
    """
    用户查询请求 ATO

    面向前端：定义查询用户时的参数
    继承 BasePageRequest 获得分页能力
    """
    dept_code: Optional[str] = Field(
        None,
        description=DEPT_CODE_DESCRIPTION,
        examples=DEPT_CODE_EXAMPLES,
    )
    phone_number: Optional[str] = Field(
        None,
        description=PHONE_NUMBER_DESCRIPTION,
        examples=PHONE_NUMBER_EXAMPLES,
    )
    name: Optional[str] = Field(
        None,
        description=NAME_DESCRIPTION,
        examples=NAME_EXAMPLES,
    )
    email: Optional[str] = Field(
        None,
        description=EMAIL_DESCRIPTION,
        examples=EMAIL_EXAMPLES,
    )
    status: Optional[int] = Field(
        None,
        ge=0,
        le=1,
        description=STATUS_DESCRIPTION,
        examples=STATUS_EXAMPLES,
    )
