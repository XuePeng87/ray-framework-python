"""
认证模块 ATO - 响应模型（对外接口契约）

这些模型定义了 API 接口返回的响应格式
面向前端/外部调用者，需要考虑稳定性和兼容性
"""
from pydantic import BaseModel, Field

from app.modules.auth.ato.constants import (
    ACCESS_TOKEN_DESCRIPTION,
    ACCESS_TOKEN_EXAMPLES,
    TOKEN_TYPE_DESCRIPTION,
    TOKEN_TYPE_EXAMPLES,
    EXPIRES_IN_DESCRIPTION,
    EXPIRES_IN_EXAMPLES,
    USER_CODE_DESCRIPTION,
    USER_CODE_EXAMPLES,
    USER_NAME_DESCRIPTION,
    USER_NAME_EXAMPLES,
)


class LoginResponse(BaseModel):
    """
    登录响应 ATO

    面向前端：定义登录成功后返回的数据格式
    """
    access_token: str = Field(
        ...,
        description=ACCESS_TOKEN_DESCRIPTION,
        examples=ACCESS_TOKEN_EXAMPLES,
    )
    token_type: str = Field(
        ...,
        description=TOKEN_TYPE_DESCRIPTION,
        examples=TOKEN_TYPE_EXAMPLES,
    )
    expires_in: int = Field(
        ...,
        description=EXPIRES_IN_DESCRIPTION,
        examples=EXPIRES_IN_EXAMPLES,
    )
    user_code: str = Field(
        ...,
        description=USER_CODE_DESCRIPTION,
        examples=USER_CODE_EXAMPLES,
    )
    user_name: str = Field(
        ...,
        description=USER_NAME_DESCRIPTION,
        examples=USER_NAME_EXAMPLES,
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                    "token_type": "Bearer",
                    "expires_in": 3600,
                    "user_code": "user123",
                    "user_name": "张三"
                }
            ]
        }
    }
