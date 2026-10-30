"""
角色模块 DTO - 内部传输对象（Service 层使用）

这些模型用于 Service 层内部传输
不对外暴露，可以随业务需求灵活变更
"""
from datetime import datetime
from typing import Optional
from pydantic import Field

from app.common.base_dto import BaseDTO, PageDTO  # 导入泛型 PageDTO


class RoleCreateDTO(BaseDTO):
    """
    创建角色 DTO

    内部使用：Service 层创建角色时的数据载体
    """
    name: str = Field(..., min_length=1, max_length=32)
    status: int = Field(..., ge=0, le=1)
    sequence: int = Field(..., ge=0)
    remark: Optional[str] = Field(None, max_length=256)


class RoleUpdateDTO(BaseDTO):
    """
    更新角色 DTO

    内部使用：Service 层更新角色时的数据载体
    """
    name: Optional[str] = Field(None, min_length=1, max_length=32)
    status: Optional[int] = Field(None, ge=0, le=1)
    sequence: Optional[int] = Field(None, ge=0)
    remark: Optional[str] = Field(None, max_length=256)


class RoleQueryDTO(BaseDTO):
    """
    查询角色 DTO

    内部使用：Service 层查询角色时的条件载体
    """
    code: Optional[str] = None
    name: Optional[str] = None
    status: Optional[int] = Field(None, ge=0, le=1)
    page: int = Field(1, ge=1)
    page_size: int = Field(10, ge=1, le=100)


class RoleDTO(BaseDTO):
    """
    角色 DTO

    内部使用：Service 层传递角色数据的载体
    """
    id: int
    code: str
    name: str
    status: int
    sequence: int
    remark: Optional[str] = None
    create_time: datetime
    modify_time: datetime

    model_config = {"from_attributes": True}


# 角色分页 DTO 类型别名（可选，用于类型注解更清晰）
RolePageDTO = PageDTO[RoleDTO]
