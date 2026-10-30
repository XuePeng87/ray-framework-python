"""
共享数据模型 - 通用响应模型
"""
from typing import Generic, TypeVar, Optional, List
from pydantic import BaseModel

T = TypeVar("T")


class Result(BaseModel, Generic[T]):
    """标准 API 响应包装器"""

    success: bool
    data: Optional[T] = None
    message: Optional[str] = None
    code: Optional[str] = None

    @classmethod
    def ok(cls, data: T = None, message: str = None) -> "Result[T]":
        """创建成功响应"""
        return cls(success=True, data=data, message=message, code="20000")

    @classmethod
    def fail(cls, message: str, code: str = "ERROR") -> "Result[T]":
        """创建错误响应"""
        return cls(success=False, message=message, code=code)


class Page(BaseModel, Generic[T]):
    """分页响应"""

    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int

    @classmethod
    def create(
            cls, items: List[T], total: int, page: int, page_size: int
    ) -> "Page[T]":
        """创建分页响应"""
        total_pages = (total + page_size - 1) // page_size
        return cls(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )
