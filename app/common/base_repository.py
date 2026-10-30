"""
基础 Repository 类

提供通用的 CRUD 操作，包含软删除自动过滤功能
类似 MyBatis-Plus 的 BaseMapper
"""
from typing import TypeVar, Generic, Type, Optional, List
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.core.database import Base
from app.common.base_model import SoftDeleteMixin

# 泛型类型变量
T = TypeVar("T", bound=Base)


class BaseRepository(Generic[T]):
    """
    基础 Repository 类

    提供通用的 CRUD 操作，自动处理软删除过滤
    所有 Repository 都应该继承此类

    特性：
    - ✅ 自动过滤已删除记录（如果模型包含 deleted 字段）
    - ✅ 软删除支持（自动将 delete 转为 update）
    - ✅ 通用 CRUD 方法
    - ✅ 分页查询支持

    使用示例：
        class RoleRepository(BaseRepository[SysRole]):
            pass

        repo = RoleRepository(SysRole, session)
        role = await repo.get_by_id(1)  # 自动过滤已删除
        await repo.soft_delete(1)  # 软删除
    """

    def __init__(self, model: Type[T], session: AsyncSession):
        """
        初始化 Repository

        Args:
            model: SQLAlchemy 模型类
            session: 数据库会话
        """
        self.model = model
        self.session = session

    def _has_soft_delete(self) -> bool:
        """
        检查模型是否支持软删除

        Returns:
            bool: 是否支持软删除
        """
        return issubclass(self.model, SoftDeleteMixin)

    def _apply_active_filter(self, stmt):
        """
        应用软删除过滤条件

        Args:
            stmt: SQLAlchemy 查询语句

        Returns:
            查询语句（已添加过滤条件）
        """
        if self._has_soft_delete():
            stmt = stmt.where(self.model.is_active())
        return stmt

    async def get_by_id(self, obj_id: int) -> Optional[T]:
        """
        根据 ID 查询（自动过滤已删除）

        Args:
            obj_id: 主键 ID

        Returns:
            Optional[T]: 查询结果，不存在返回 None
        """
        stmt = select(self.model).where(self.model.id == obj_id)
        stmt = self._apply_active_filter(stmt)

        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        order_by=None,
    ) -> List[T]:
        """
        查询所有记录（自动过滤已删除）

        Args:
            skip: 跳过记录数
            limit: 限制返回数量
            order_by: 排序字段

        Returns:
            List[T]: 记录列表
        """
        stmt = select(self.model)
        stmt = self._apply_active_filter(stmt)

        if order_by:
            stmt = stmt.order_by(order_by)

        stmt = stmt.offset(skip).limit(limit)

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def count(self) -> int:
        """
        统计记录数（自动过滤已删除）
        Returns:
            int: 记录总数
        """
        stmt = select(func.count()).select_from(self.model)
        stmt = self._apply_active_filter(stmt)

        result = await self.session.execute(stmt)
        return result.scalar()

    async def create(self, obj: T) -> T:
        """
        创建记录

        Args:
            obj: 要创建的对象

        Returns:
            T: 创建后的对象
        """
        self.session.add(obj)
        await self.session.flush()
        await self.session.refresh(obj)
        logger.info(f"创建 {self.model.__name__} 成功: {obj}")
        return obj

    async def update(self, obj: T) -> T:
        """
        更新记录

        Args:
            obj: 要更新的对象

        Returns:
            T: 更新后的对象
        """
        await self.session.flush()
        await self.session.refresh(obj)
        logger.info(f"更新 {self.model.__name__} 成功: {obj}")
        return obj

    async def delete(self, obj_id: int) -> bool:
        """
        删除记录（自动判断软删除或物理删除）

        如果模型支持软删除，则执行软删除
        否则执行物理删除

        Args:
            obj_id: 主键 ID

        Returns:
            bool: 是否删除成功
        """
        obj = await self.get_by_id(obj_id)
        if not obj:
            logger.warning(f"{self.model.__name__} 不存在: id={obj_id}")
            return False

        if self._has_soft_delete():
            # 软删除
            obj.soft_delete()
            logger.info(f"软删除 {self.model.__name__} 成功: id={obj_id}")
        else:
            # 物理删除
            await self.session.delete(obj)
            logger.info(f"物理删除 {self.model.__name__} 成功: id={obj_id}")

        return True

    async def exists(self, obj_id: int) -> bool:
        """
        检查记录是否存在（自动过滤已删除）

        Args:
            obj_id: 主键 ID

        Returns:
            bool: 是否存在
        """
        obj = await self.get_by_id(obj_id)
        return obj is not None

    async def batch_create(self, objs: List[T]) -> List[T]:
        """
        批量创建记录

        Args:
            objs: 要创建的对象列表

        Returns:
            List[T]: 创建后的对象列表
        """
        self.session.add_all(objs)
        await self.session.flush()

        for obj in objs:
            await self.session.refresh(obj)

        logger.info(f"批量创建 {self.model.__name__} 成功: {len(objs)} 条")
        return objs

    async def batch_delete(self, obj_ids: List[int]) -> int:
        """
        批量删除记录（软删除）

        Args:
            obj_ids: 主键 ID 列表

        Returns:
            int: 成功删除的数量
        """
        count = 0
        for obj_id in obj_ids:
            if await self.delete(obj_id):
                count += 1

        logger.info(f"批量删除 {self.model.__name__} 成功: {count}/{len(obj_ids)} 条")
        return count
