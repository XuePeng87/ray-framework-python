"""
系统角色 Repository

提供角色相关的数据访问操作
"""
from typing import Optional, List
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.role.entity.role_entity import SysRole
from app.common.base_repository import BaseRepository


class RoleRepository(BaseRepository[SysRole]):
    """
    系统角色 Repository

    继承 BaseRepository，自动获得：
    - ✅ 软删除自动过滤
    - ✅ 通用 CRUD 操作
    - ✅ 分页查询支持

    使用示例：
        repo = RoleRepository(SysRole, session)

        # 查询（自动过滤已删除）
        role = await repo.get_by_code("ROLE_ADMIN")

        # 软删除
        await repo.delete(role.id)
    """

    def __init__(self, session: AsyncSession):
        """
        初始化 Repository

        Args:
            session: 数据库会话
        """
        super().__init__(SysRole, session)

    async def get_by_code(self, code: str) -> Optional[SysRole]:
        """
        根据角色编号查询

        Args:
            code: 角色编号

        Returns:
            Optional[SysRole]: 角色对象，不存在返回 None
        """
        stmt = select(SysRole).where(
            and_(
                SysRole.code == code,
                SysRole.is_active()  # 自动过滤已删除
            )
        )

        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Optional[SysRole]:
        """
        根据角色名称查询

        Args:
            name: 角色名称

        Returns:
            Optional[SysRole]: 角色对象，不存在返回 None
        """
        stmt = select(SysRole).where(
            and_(
                SysRole.name == name,
                SysRole.is_active()
            )
        )

        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def exists_by_code(self, code: str, exclude_id: Optional[int] = None) -> bool:
        """
        检查角色编号是否存在

        Args:
            code: 角色编号
            exclude_id: 排除的角色 ID（用于更新时）

        Returns:
            bool: 是否存在
        """
        conditions = [
            SysRole.code == code,
            SysRole.is_active()
        ]

        if exclude_id:
            conditions.append(SysRole.id != exclude_id)

        stmt = select(func.count()).select_from(SysRole).where(and_(*conditions))
        result = await self.session.execute(stmt)
        count = result.scalar()

        return count > 0

    async def exists_by_name(self, name: str, exclude_id: Optional[int] = None) -> bool:
        """
        检查角色名称是否存在

        Args:
            name: 角色名称
            exclude_id: 排除的角色 ID（用于更新时）

        Returns:
            bool: 是否存在
        """
        conditions = [
            SysRole.name == name,
            SysRole.is_active()
        ]

        if exclude_id:
            conditions.append(SysRole.id != exclude_id)

        stmt = select(func.count()).select_from(SysRole).where(and_(*conditions))
        result = await self.session.execute(stmt)
        count = result.scalar()

        return count > 0

    async def list_by_condition(
            self,
            code: Optional[str] = None,
            name: Optional[str] = None,
            status: Optional[int] = None,
            skip: int = 0,
            limit: Optional[int] = None,  # None 表示不限制
    ) -> List[SysRole]:
        """
        根据条件查询角色列表

        Args:
            code: 角色编号（精确匹配）
            name: 角色名称（模糊匹配）
            status: 状态
            skip: 跳过记录数
            limit: 限制返回数量（None 表示不限制）

        Returns:
            List[SysRole]: 角色列表
        """
        conditions = [SysRole.is_active()]

        if code:
            conditions.append(SysRole.code == code)
        if name:
            conditions.append(SysRole.name.like(f"%{name}%"))
        if status is not None:
            conditions.append(SysRole.status == status)

        stmt = (
            select(SysRole)
            .where(and_(*conditions))
            .order_by(SysRole.sequence, SysRole.id.desc())
        )

        # 只在传了 skip/limit 时才加分页
        if skip > 0:
            stmt = stmt.offset(skip)
        if limit is not None:
            stmt = stmt.limit(limit)

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def count_by_condition(
            self,
            code: Optional[str] = None,
            name: Optional[str] = None,
            status: Optional[int] = None,
    ) -> int:
        """
        根据条件统计角色数量

        Args:
            code: 角色编号（精确匹配）
            name: 角色名称（模糊匹配）
            status: 状态

        Returns:
            int: 记录数量
        """
        conditions = [SysRole.is_active()]

        if code:
            conditions.append(SysRole.code == code)
        if name:
            conditions.append(SysRole.name.like(f"%{name}%"))
        if status is not None:
            conditions.append(SysRole.status == status)

        stmt = select(func.count()).select_from(SysRole).where(and_(*conditions))
        result = await self.session.execute(stmt)
        return result.scalar()

    async def page_by_condition(
            self,
            code: Optional[str] = None,
            name: Optional[str] = None,
            status: Optional[int] = None,
            page: int = 1,
            page_size: int = 10,
    ) -> tuple[List[SysRole], int]:
        """
        根据条件分页查询角色

        Args:
            code: 角色编号（精确匹配）
            name: 角色名称（模糊匹配）
            status: 状态
            page: 页码（从1开始）
            page_size: 每页数量

        Returns:
            tuple[List[SysRole], int]: (角色列表, 总数)
        """
        skip = (page - 1) * page_size

        items = await self.list_by_condition(
            code=code,
            name=name,
            status=status,
            skip=skip,
            limit=page_size,
        )

        total = await self.count_by_condition(
            code=code,
            name=name,
            status=status,
        )

        return items, total

    async def get_assignable_roles(self) -> List[SysRole]:
        """
        获取可分配的角色列表

        返回所有启用的角色（排除超级管理员）

        Returns:
            List[SysRole]: 可分配的角色列表
        """
        stmt = (
            select(SysRole)
            .where(
                and_(
                    SysRole.is_active(),
                    SysRole.status == 1,
                    SysRole.code != "ROLE_SUPER_ADMIN"
                )
            )
            .order_by(SysRole.sequence, SysRole.id.desc())
        )

        result = await self.session.execute(stmt)
        return list(result.scalars().all())
