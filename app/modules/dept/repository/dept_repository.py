"""
系统部门 Repository

提供部门相关的数据访问操作，包含树形结构查询
"""
from typing import Optional, List
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.dept.entity.dept_entity import SysDept
from app.common.base_repository import BaseRepository


class DeptRepository(BaseRepository[SysDept]):
    """
    系统部门 Repository

    继承 BaseRepository，自动获得：
    - ✅ 软删除自动过滤
    - ✅ 通用 CRUD 操作
    - ✅ 分页查询支持

    额外提供：
    - 树形结构查询
    - 子部门检查
    - 后代节点查询
    """

    def __init__(self, session: AsyncSession):
        """初始化 Repository"""
        super().__init__(SysDept, session)

    async def get_by_code(self, code: str) -> Optional[SysDept]:
        """根据部门编号查询"""
        stmt = select(SysDept).where(
            and_(
                SysDept.code == code,
                SysDept.is_active()
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str, parent_code: Optional[str] = None) -> Optional[SysDept]:
        """
        根据部门名称查询

        Args:
            name: 部门名称
            parent_code: 父级编号（可选，用于同层级唯一性检查）
        """
        conditions = [
            SysDept.name == name,
            SysDept.is_active()
        ]
        if parent_code is not None:
            conditions.append(SysDept.parent_code == parent_code)

        stmt = select(SysDept).where(and_(*conditions))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def exists_by_code(self, code: str, exclude_id: Optional[int] = None) -> bool:
        """检查部门编号是否存在"""
        conditions = [
            SysDept.code == code,
            SysDept.is_active()
        ]
        if exclude_id:
            conditions.append(SysDept.id != exclude_id)

        stmt = select(func.count()).select_from(SysDept).where(and_(*conditions))
        result = await self.session.execute(stmt)
        count = result.scalar()
        return count > 0

    async def exists_by_name(self, name: str, parent_code: str, exclude_id: Optional[int] = None) -> bool:
        """
        检查部门名称是否存在（同层级唯一性）

        Args:
            name: 部门名称
            parent_code: 父级编号
            exclude_id: 排除的部门ID（用于更新时排除自己）
        """
        conditions = [
            SysDept.name == name,
            SysDept.parent_code == parent_code,
            SysDept.is_active()
        ]
        if exclude_id:
            conditions.append(SysDept.id != exclude_id)

        stmt = select(func.count()).select_from(SysDept).where(and_(*conditions))
        result = await self.session.execute(stmt)
        count = result.scalar()
        return count > 0

    async def list_by_condition(
            self,
            parent_code: Optional[str] = None,
            name: Optional[str] = None,
            status: Optional[int] = None,
            skip: int = 0,
            limit: Optional[int] = None,
    ) -> List[SysDept]:
        """根据条件查询部门列表"""
        conditions = [SysDept.is_active()]

        if parent_code is not None:
            conditions.append(SysDept.parent_code == parent_code)
        if name:
            conditions.append(SysDept.name.like(f"%{name}%"))
        if status is not None:
            conditions.append(SysDept.status == status)

        stmt = (
            select(SysDept)
            .where(and_(*conditions))
            .order_by(SysDept.sequence, SysDept.id)
        )

        if skip > 0:
            stmt = stmt.offset(skip)
        if limit is not None:
            stmt = stmt.limit(limit)

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def count_by_condition(
            self,
            parent_code: Optional[str] = None,
            name: Optional[str] = None,
            status: Optional[int] = None,
    ) -> int:
        """根据条件统计部门数量"""
        conditions = [SysDept.is_active()]

        if parent_code is not None:
            conditions.append(SysDept.parent_code == parent_code)
        if name:
            conditions.append(SysDept.name.like(f"%{name}%"))
        if status is not None:
            conditions.append(SysDept.status == status)

        stmt = select(func.count()).select_from(SysDept).where(and_(*conditions))
        result = await self.session.execute(stmt)
        return result.scalar()

    async def page_by_condition(
            self,
            parent_code: Optional[str] = None,
            name: Optional[str] = None,
            status: Optional[int] = None,
            page: int = 1,
            page_size: int = 10,
    ) -> tuple[List[SysDept], int]:
        """根据条件分页查询部门"""
        skip = (page - 1) * page_size

        items = await self.list_by_condition(
            parent_code=parent_code,
            name=name,
            status=status,
            skip=skip,
            limit=page_size,
        )

        total = await self.count_by_condition(
            parent_code=parent_code,
            name=name,
            status=status,
        )

        return items, total

    async def get_all_active(self) -> List[SysDept]:
        """获取所有活跃的部门（用于构建树形结构）"""
        stmt = (
            select(SysDept)
            .where(SysDept.is_active())
            .order_by(SysDept.sequence, SysDept.id)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def has_children(self, code: str) -> bool:
        """
        检查部门是否有子部门

        Args:
            code: 部门编号

        Returns:
            bool: 是否有子部门
        """
        stmt = select(func.count()).select_from(SysDept).where(
            and_(
                SysDept.parent_code == code,
                SysDept.is_active()
            )
        )
        result = await self.session.execute(stmt)
        count = result.scalar()
        return count > 0

    async def get_children(self, code: str) -> List[SysDept]:
        """获取直接子部门"""
        stmt = select(SysDept).where(
            and_(
                SysDept.parent_code == code,
                SysDept.is_active()
            )
        ).order_by(SysDept.sequence, SysDept.id)

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_descendants(self, code: str) -> List[SysDept]:
        """
        获取所有后代部门（递归查询）

        用于移动部门时检测循环引用

        Args:
            code: 部门编号

        Returns:
            List[SysDept]: 所有后代部门列表
        """
        # 先获取直接子部门
        children = await self.get_children(code)
        descendants = list(children)

        # 递归获取子部门的后代
        for child in children:
            child_descendants = await self.get_descendants(child.code)
            descendants.extend(child_descendants)

        return descendants

    async def update_parent_code(self, code: str, new_parent_code: str) -> bool:
        """
        更新部门的父级编号（移动部门）

        Args:
            code: 部门编号
            new_parent_code: 新的父级编号

        Returns:
            bool: 是否更新成功
        """
        dept = await self.get_by_code(code)
        if not dept:
            return False

        dept.parent_code = new_parent_code
        await self.session.flush()
        await self.session.refresh(dept)
        return True

    async def delete_by_code(self, code: str) -> bool:
        """根据编号删除部门（软删除）"""
        dept = await self.get_by_code(code)
        if not dept:
            return False

        return await self.delete(dept.id)
