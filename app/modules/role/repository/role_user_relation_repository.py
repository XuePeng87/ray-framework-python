"""
角色用户关联 Repository

提供角色与用户关联关系的数据访问操作
"""
from typing import List
from sqlalchemy import select, delete, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.role.entity.role_user_relation_entity import SysRoleUserRelation


class RoleUserRelationRepository:
    """
    角色用户关联 Repository

    提供角色与用户关联关系的增删查操作
    """

    def __init__(self, session: AsyncSession):
        """初始化 Repository"""
        self.session = session

    async def create(self, relation: SysRoleUserRelation) -> SysRoleUserRelation:
        """创建角色用户关联"""
        self.session.add(relation)
        await self.session.flush()
        await self.session.refresh(relation)
        return relation

    async def batch_create(self, relations: List[SysRoleUserRelation]) -> List[SysRoleUserRelation]:
        """批量创建角色用户关联"""
        self.session.add_all(relations)
        await self.session.flush()
        for rel in relations:
            await self.session.refresh(rel)
        return relations

    async def find_by_user_code(self, user_code: str) -> List[SysRoleUserRelation]:
        """根据用户编号查询所有角色关联"""
        stmt = select(SysRoleUserRelation).where(
            SysRoleUserRelation.user_code == user_code
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_role_code(self, role_code: str) -> List[SysRoleUserRelation]:
        """根据角色编号查询所有用户关联"""
        stmt = select(SysRoleUserRelation).where(
            SysRoleUserRelation.role_code == role_code
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def delete_by_user_code(self, user_code: str) -> bool:
        """根据用户编号删除所有角色关联"""
        stmt = delete(SysRoleUserRelation).where(
            SysRoleUserRelation.user_code == user_code
        )
        await self.session.execute(stmt)
        await self.session.flush()
        return True

    async def delete_by_role_code(self, role_code: str) -> bool:
        """根据角色编号删除所有用户关联"""
        stmt = delete(SysRoleUserRelation).where(
            SysRoleUserRelation.role_code == role_code
        )
        await self.session.execute(stmt)
        await self.session.flush()
        return True

    async def exists(self, role_code: str, user_code: str) -> bool:
        """检查角色用户关联是否存在"""
        stmt = select(SysRoleUserRelation).where(
            and_(
                SysRoleUserRelation.role_code == role_code,
                SysRoleUserRelation.user_code == user_code
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None
