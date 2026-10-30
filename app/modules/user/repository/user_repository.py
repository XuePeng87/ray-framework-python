"""
系统用户 Repository

提供用户相关的数据访问操作
"""
from typing import Optional, List
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.user.entity.user_entity import SysUser
from app.common.base_repository import BaseRepository


class UserRepository(BaseRepository[SysUser]):
    """系统用户 Repository"""

    def __init__(self, session: AsyncSession):
        super().__init__(SysUser, session)

    async def get_by_code(self, code: str) -> Optional[SysUser]:
        """根据用户编号查询"""
        stmt = select(SysUser).where(
            and_(SysUser.code == code, SysUser.is_active())
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_phone_number(self, phone_number: str) -> Optional[SysUser]:
        """根据用户手机号查询"""
        stmt = select(SysUser).where(
            and_(SysUser.phone_number == phone_number, SysUser.is_active())
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def exists_by_phone(self, phone_number: str, exclude_id: Optional[int] = None) -> bool:
        """检查手机号是否存在"""
        conditions = [SysUser.phone_number == phone_number, SysUser.is_active()]
        if exclude_id:
            conditions.append(SysUser.id != exclude_id)
        stmt = select(func.count()).select_from(SysUser).where(and_(*conditions))
        result = await self.session.execute(stmt)
        return result.scalar() > 0

    async def exists_by_email(self, email: str, exclude_id: Optional[int] = None) -> bool:
        """检查邮箱是否存在"""
        conditions = [SysUser.email == email, SysUser.is_active()]
        if exclude_id:
            conditions.append(SysUser.id != exclude_id)
        stmt = select(func.count()).select_from(SysUser).where(and_(*conditions))
        result = await self.session.execute(stmt)
        return result.scalar() > 0

    async def list_by_condition(
        self,
        dept_code: Optional[str] = None,
        name: Optional[str] = None,
        status: Optional[int] = None,
    ) -> List[SysUser]:
        """根据条件查询用户列表（不分页）"""
        conditions = [SysUser.is_active()]

        if dept_code:
            conditions.append(SysUser.dept_code == dept_code)
        if name:
            conditions.append(SysUser.name.like(f"%{name}%"))
        if status is not None:
            conditions.append(SysUser.status == status)

        stmt = (
            select(SysUser)
            .where(and_(*conditions))
            .order_by(SysUser.id.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def page_by_condition(
        self,
        dept_code: Optional[str] = None,
        name: Optional[str] = None,
        status: Optional[int] = None,
        page: int = 1,
        page_size: int = 10,
    ) -> tuple[List[SysUser], int]:
        """根据条件分页查询用户"""
        skip = (page - 1) * page_size
        conditions = [SysUser.is_active()]
        
        if dept_code:
            conditions.append(SysUser.dept_code == dept_code)
        if name:
            conditions.append(SysUser.name.like(f"%{name}%"))
        if status is not None:
            conditions.append(SysUser.status == status)

        # 查询总数
        count_stmt = select(func.count()).select_from(SysUser).where(and_(*conditions))
        total = (await self.session.execute(count_stmt)).scalar()

        # 查询列表
        stmt = (
            select(SysUser)
            .where(and_(*conditions))
            .order_by(SysUser.id.desc())
            .offset(skip)
            .limit(page_size)
        )
        result = await self.session.execute(stmt)
        items = list(result.scalars().all())

        return items, total

    async def update_password(self, code: str, new_password_hash: str) -> bool:
        """更新用户密码"""
        user = await self.get_by_code(code)
        if not user:
            return False
        user.password = new_password_hash
        await self.session.flush()
        await self.session.refresh(user)
        return True

    async def delete_by_code(self, code: str) -> bool:
        """根据编号删除用户（软删除）"""
        user = await self.get_by_code(code)
        if not user:
            return False
        return await self.delete(user.id)
