"""
部门模块 DTO（Data Transfer Object）

内部使用：Service 层与 Repository 层之间的数据传输对象
"""
from datetime import datetime
from typing import Optional, List
from pydantic import Field
from app.common.base_dto import BaseDTO, PageDTO


class DeptCreateDTO(BaseDTO):
    """
    创建部门 DTO

    内部使用：Facade 层向 Service 层传递创建部门的数据
    """
    parent_code: str = Field(..., min_length=1, max_length=32)
    name: str = Field(..., min_length=1, max_length=32)
    status: int = Field(..., ge=0, le=1)
    sequence: int = Field(..., ge=0)
    remark: Optional[str] = Field(None, max_length=256)


class DeptUpdateDTO(BaseDTO):
    """
    更新部门 DTO

    内部使用：Facade 层向 Service 层传递更新部门的数据
    只包含可更新的字段，所有字段可选
    """
    name: Optional[str] = Field(None, min_length=1, max_length=32)
    status: Optional[int] = Field(None, ge=0, le=1)
    sequence: Optional[int] = Field(None, ge=0)
    remark: Optional[str] = Field(None, max_length=256)


class DeptQueryDTO(BaseDTO):
    """
    部门查询 DTO

    内部使用：Facade 层向 Service 层传递查询条件
    """
    parent_code: Optional[str] = None
    name: Optional[str] = None
    status: Optional[int] = Field(None, ge=0, le=1)
    page: int = Field(1, ge=1)
    page_size: int = Field(10, ge=1, le=100)


class DeptMoveDTO(BaseDTO):
    """
    部门移动 DTO

    内部使用：Facade 层向 Service 层传递移动部门的数据
    """
    new_parent_code: str = Field(..., min_length=1, max_length=32)


class DeptDTO(BaseDTO):
    """
    部门信息 DTO

    内部使用：Service 层返回部门详情
    """
    id: int
    parent_code: str
    code: str
    name: str
    status: int
    sequence: int
    remark: Optional[str] = None
    create_time: datetime
    modify_time: datetime
    model_config = {"from_attributes": True}


class DeptTreeDTO(BaseDTO):
    """
    部门树形结构 DTO

    内部使用：Service 层返回部门树形数据
    """
    id: int
    parent_code: str
    code: str
    name: str
    status: int
    sequence: int
    remark: Optional[str] = None
    create_time: datetime
    modify_time: datetime
    children: List["DeptTreeDTO"] = []
    model_config = {"from_attributes": True}
