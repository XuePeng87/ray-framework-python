"""
认证模块 ATO - 请求模型（对外接口契约）

这些模型定义了 API 接口接收的请求格式
面向前端/外部调用者，需要考虑稳定性和兼容性
"""
from pydantic import BaseModel, Field

from app.modules.auth.ato.constants import (
    PHONE_NUMBER_DESCRIPTION,
    PHONE_NUMBER_EXAMPLES,
    PASSWORD_DESCRIPTION,
    PASSWORD_EXAMPLES,
)


class LoginRequest(BaseModel):
    """
    登录请求 ATO

    面向前端：定义登录时需要传入的字段
    """
    phone_number: str = Field(
        ...,
        min_length=11,
        max_length=32,
        description=PHONE_NUMBER_DESCRIPTION,
        examples=PHONE_NUMBER_EXAMPLES,
    )
    password: str = Field(
        ...,
        min_length=6,
        max_length=128,
        description=PASSWORD_DESCRIPTION,
        examples=PASSWORD_EXAMPLES,
    )
