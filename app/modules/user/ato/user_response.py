"""
用户模块 ATO - 响应模型（对外接口契约）

这些模型定义了 API 接口返回的响应格式
面向前端/外部调用者，需要考虑稳定性和兼容性
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

from app.common.base_response import BaseResponse
from app.modules.user.ato.constants import (
    ID_DESCRIPTION,
    ID_EXAMPLES,
    DEPT_CODE_DESCRIPTION,
    DEPT_CODE_EXAMPLES,
    USER_CODE_DESCRIPTION,
    USER_CODE_EXAMPLES,
    PHONE_NUMBER_DESCRIPTION,
    PHONE_NUMBER_EXAMPLES,
    NAME_DESCRIPTION,
    NAME_EXAMPLES,
    EMAIL_DESCRIPTION,
    EMAIL_EXAMPLES,
    AVATAR_DESCRIPTION,
    AVATAR_EXAMPLES,
    STATUS_DESCRIPTION,
    STATUS_EXAMPLES,
    REMARK_DESCRIPTION,
    REMARK_EXAMPLES,
    CREATE_TIME_DESCRIPTION,
    CREATE_TIME_EXAMPLES,
    MODIFY_TIME_DESCRIPTION,
    MODIFY_TIME_EXAMPLES,
    ROLE_CODES_DESCRIPTION,
    ROLE_CODES_EXAMPLES,
)


class UserResponse(BaseResponse):
    """
    用户响应 ATO

    面向前端：定义返回给前端的用户信息格式
    """
    id: int = Field(
        ...,
        description=ID_DESCRIPTION,
        examples=ID_EXAMPLES,
    )
    dept_code: str = Field(
        ...,
        description=DEPT_CODE_DESCRIPTION,
        examples=DEPT_CODE_EXAMPLES,
    )
    code: str = Field(
        ...,
        description=USER_CODE_DESCRIPTION,
        examples=USER_CODE_EXAMPLES,
    )
    phone_number: str = Field(
        ...,
        description=PHONE_NUMBER_DESCRIPTION,
        examples=PHONE_NUMBER_EXAMPLES,
    )
    name: str = Field(
        ...,
        description=NAME_DESCRIPTION,
        examples=NAME_EXAMPLES,
    )
    email: str = Field(
        ...,
        description=EMAIL_DESCRIPTION,
        examples=EMAIL_EXAMPLES,
    )
    avatar: str = Field(
        ...,
        description=AVATAR_DESCRIPTION,
        examples=AVATAR_EXAMPLES,
    )
    status: int = Field(
        ...,
        description=STATUS_DESCRIPTION,
        examples=STATUS_EXAMPLES,
    )
    remark: Optional[str] = Field(
        None,
        description=REMARK_DESCRIPTION,
        examples=REMARK_EXAMPLES,
    )
    role_codes: List[str] = Field(
        default_factory=list,
        description=ROLE_CODES_DESCRIPTION,
        examples=ROLE_CODES_EXAMPLES,
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
                    "dept_code": "DEPT_TECH",
                    "code": "USER_ADMIN",
                    "phone_number": "13800138000",
                    "name": "张三",
                    "email": "zhangsan@example.com",
                    "avatar": "https://example.com/avatar.jpg",
                    "status": 1,
                    "remark": "系统管理员",
                    "role_codes": ["ROLE_ADMIN"],
                    "create_time": "2026-01-15T10:30:00",
                    "modify_time": "2026-01-15T10:30:00"
                }
            ]
        }
    }


class UserListResponse(BaseResponse):
    """
    用户列表响应 ATO（精简版）

    面向前端：用于下拉选择等场景
    """
    code: str = Field(
        ...,
        description=USER_CODE_DESCRIPTION,
        examples=USER_CODE_EXAMPLES,
    )
    name: str = Field(
        ...,
        description=NAME_DESCRIPTION,
        examples=NAME_EXAMPLES,
    )

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "examples": [
                {
                    "code": "USER_ADMIN",
                    "name": "张三"
                }
            ]
        }
    }
