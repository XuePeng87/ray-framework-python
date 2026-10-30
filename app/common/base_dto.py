"""
通用 DTO（Data Transfer Object）基类

提供 DTO 通用工具方法，所有内部 DTO 都应该继承此类
"""
from typing import Dict, Any, List, TypeVar, Generic, Tuple, Callable
from pydantic import BaseModel, model_validator


class BaseDTO(BaseModel):
    """
    DTO 基类

    提供通用的数据传输对象方法
    """

    def to_dict(self, exclude_none: bool = False) -> Dict[str, Any]:
        """
        转换为字典

        Args:
            exclude_none: 是否排除 None 值

        Returns:
            Dict[str, Any]: 字典表示
        """
        if exclude_none:
            return {k: v for k, v in self.model_dump().items() if v is not None}
        return self.model_dump()

    def to_dict_exclude_unset(self) -> Dict[str, Any]:
        """
        转换为字典，只包含显式设置的字段

        适用于部分更新场景

        Returns:
            Dict[str, Any]: 只包含已设置字段的字典
        """
        return self.model_dump(exclude_unset=True)

    @classmethod
    def from_orm(cls, obj: Any):
        """
        从 ORM 对象创建 DTO

        Args:
            obj: ORM 对象（如 SQLAlchemy 模型）

        Returns:
            DTO 实例
        """
        return cls.model_validate(obj)


# 泛型类型变量
T = TypeVar("T")


class PageDTO(BaseDTO, Generic[T]):
    """
    泛型分页 DTO

    内部使用：Service 层传递分页数据的载体
    可用于任何业务模块的分页场景

    特性：
    - 自动计算 total_pages（无需手动传入）
    - 泛型支持（PageDTO[RoleDTO], PageDTO[UserDTO] 等）
    - 所有模块共享

    Examples:
        >>> # 角色分页
        >>> role_page = PageDTO[](
        ...     items=[(...), ...],
        ...     total=100,
        ...     page=1,
        ...     page_size=10,
        ... )
        >>> # total_pages 自动计算为 10
    """
    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int = 0  # 默认值，会在 model_validator 中计算

    @model_validator(mode='after')
    def calculate_total_pages(self):
        """
        自动计算 total_pages

        使用向上取整除法：(total + page_size - 1) // page_size
        """
        if self.page_size > 0:
            self.total_pages = (self.total + self.page_size - 1) // self.page_size
        else:
            self.total_pages = 0
        return self


# Entity 类型变量
E = TypeVar("E")  # Entity 类型


def build_page_dto(
        items_and_total: Tuple[List[E], int],
        entity_to_dto: Callable[[E], T],
        page: int,
        page_size: int,
) -> PageDTO[T]:
    """
    构建分页 DTO

    将 Repository 返回的 (items, total) 元组转换为 PageDTO

    Args:
        items_and_total: Repository 返回的 (items, total) 元组
        entity_to_dto: Entity 转 DTO 的函数
        page: 页码
        page_size: 每页数量

    Returns:
        PageDTO[T]: 分页 DTO

    使用示例:
        async def page(self, query: RoleQueryDTO) -> PageDTO[RoleDTO]:
            result = await self.repo.page_by_condition(
                code=query.code,
                name=query.name,
                status=query.status,
                page=query.page,
                page_size=query.page_size,
            )
            return build_page_dto(
                result,
                lambda role: RoleDTO.from_orm(role),
                query.page,
                query.page_size,
            )
    """
    items, total = items_and_total
    dto_items = [entity_to_dto(item) for item in items]

    return PageDTO(
        items=dto_items,
        total=total,
        page=page,
        page_size=page_size,
    )
