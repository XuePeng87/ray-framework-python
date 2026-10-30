"""
用户模块 DTO - 内部传输对象（Service 层使用）

这些模型用于 Service 层内部传输
不对外暴露，可以随业务需求灵活变更
"""
from datetime import datetime
from typing import Optional, List
from pydantic import Field

from app.common.base_dto import BaseDTO


class UserCreateDTO(BaseDTO):
    """创建用户 DTO"""
    dept_code: str = Field(..., min_length=1, max_length=32)
    phone_number: str = Field(..., min_length=11, max_length=32)
    name: str = Field(..., min_length=1, max_length=32)
    email: str = Field(..., min_length=5, max_length=128)
    status: int = Field(..., ge=0, le=1)
    remark: Optional[str] = Field(None, max_length=256)
    role_codes: List[str] = Field(default_factory=list)
    code: Optional[str] = Field(None, description="用户编号（由 Service 层生成）")


class UserUpdateDTO(BaseDTO):
    """更新用户 DTO"""
    dept_code: Optional[str] = Field(None, min_length=1, max_length=32)
    phone_number: Optional[str] = Field(None, min_length=11, max_length=32)
    name: Optional[str] = Field(None, min_length=1, max_length=32)
    email: Optional[str] = Field(None, min_length=5, max_length=128)
    status: Optional[int] = Field(None, ge=0, le=1)
    remark: Optional[str] = Field(None, max_length=256)
    role_codes: Optional[List[str]] = None


class UserUpdatePasswordDTO(BaseDTO):
    """修改密码 DTO"""
    old_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=6, max_length=128)


class UserQueryDTO(BaseDTO):
    """查询用户 DTO"""
    dept_code: Optional[str] = None
    phone_number: Optional[str] = None
    name: Optional[str] = None
    email: Optional[str] = None
    status: Optional[int] = Field(None, ge=0, le=1)
    page: int = Field(1, ge=1)
    page_size: int = Field(10, ge=1, le=100)


class UserDTO(BaseDTO):
    """用户信息 DTO"""
    id: int
    dept_code: str
    code: str
    phone_number: str
    name: str
    password: str
    email: str
    avatar: str
    status: int
    remark: Optional[str] = None
    role_codes: List[str] = Field(default_factory=list)  # 角色编号列表
    create_time: datetime
    modify_time: datetime

    model_config = {"from_attributes": True}


class UserListDTO(BaseDTO):
    """用户列表 DTO（精简版）"""
    code: str
    name: str

    model_config = {"from_attributes": True}
