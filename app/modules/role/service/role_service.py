"""
系统角色业务逻辑层

包含角色的 CRUD 操作、业务逻辑处理和角色用户关联管理
使用 DTO 作为内部传输对象
"""
from typing import List
from loguru import logger

from app.modules.role.entity.role_entity import SysRole
from app.modules.role.entity.role_user_relation_entity import SysRoleUserRelation
from app.modules.role.dto.role_dto import (
    RoleCreateDTO,
    RoleUpdateDTO,
    RoleQueryDTO,
    RoleDTO,
)
from app.common.base_dto import PageDTO, build_page_dto
from app.modules.role.repository.role_repository import RoleRepository
from app.modules.role.repository.role_user_relation_repository import RoleUserRelationRepository
from app.modules.role.exception.role_exception import (
    RoleNotFoundException,
    RoleNameExistsException,
)
from app.util.uuid import generate_uuid


class RoleService:
    """系统角色服务类"""

    def __init__(
        self,
        repo: RoleRepository,
        role_user_repo: RoleUserRelationRepository,
    ):
        """
        初始化服务

        Args:
            repo: 角色 Repository（通过依赖注入）
            role_user_repo: 角色用户关联 Repository（通过依赖注入）
        """
        self.repo = repo
        self.role_user_repo = role_user_repo

    async def create(self, request: RoleCreateDTO, current_user: str = "system") -> bool:
        """
        创建角色

        Args:
            request: 创建请求 DTO
            current_user: 当前操作用户

        Returns:
            bool: 是否创建成功

        Raises:
            RoleNameExistsException: 角色名称已存在
        """

        # 检查名称是否已存在
        if await self.repo.exists_by_name(request.name):
            raise RoleNameExistsException(f"角色名称 {request.name} 已存在")

        # 转换 DTO 为字典，添加额外字段
        role_data = request.to_dict(exclude_none=True)

        # 生成 UUID 作为 code（去掉-）
        code = generate_uuid(with_dash=False)

        role_data.update({
            "code": code,
            "create_user": current_user,
            "modify_user": current_user,
        })

        # 创建角色对象
        role = SysRole(**role_data)

        # 使用 Repository 创建
        role = await self.repo.create(role)

        logger.info(f"角色创建成功: {role.code} - {role.name}")
        return True

    async def update(self, code: str, request: RoleUpdateDTO, current_user: str = "system") -> bool:
        """
        更新角色

        Args:
            code: 角色编号
            request: 更新请求 DTO
            current_user: 当前操作用户

        Returns:
            bool: 是否更新成功

        Raises:
            RoleNotFoundException: 角色不存在
            RoleNameExistsException: 角色名称已存在
        """
        role = await self.repo.get_by_code(code)
        if not role:
            raise RoleNotFoundException(f"角色 {code} 不存在")

        # 使用 exclude_unset=True 只获取传入的字段
        update_data = request.to_dict_exclude_unset()

        # 如果更新了 name，检查新名称是否已存在
        if 'name' in update_data and update_data['name'] != role.name:
            if await self.repo.exists_by_name(update_data['name'], exclude_id=role.id):
                raise RoleNameExistsException(f"角色名称 {update_data['name']} 已存在")

        # 批量更新字段
        for key, value in update_data.items():
            setattr(role, key, value)

        # 更新审计字段
        role.modify_user = current_user

        # 使用 Repository 更新
        role = await self.repo.update(role)

        logger.info(f"角色更新成功: {code}")
        return True

    async def delete(self, code: str) -> bool:
        """
        删除角色（软删除）

        Args:
            code: 角色编号

        Returns:
            bool: 是否删除成功

        Raises:
            RoleNotFoundException: 角色不存在
        """
        # 使用 Repository 查询
        role = await self.repo.get_by_code(code)
        if not role:
            raise RoleNotFoundException(f"角色 {code} 不存在")

        # 使用 Repository 删除（自动软删除）
        result = await self.repo.delete(role.id)

        if result:
            logger.info(f"角色删除成功: {code}")

        return result

    async def get_by_code(self, code: str) -> RoleDTO:
        """
        根据编号查询角色

        Args:
            code: 角色编号

        Returns:
            RoleDTO: 角色 DTO

        Raises:
            RoleNotFoundException: 角色不存在
        """
        role = await self.repo.get_by_code(code)
        if not role:
            raise RoleNotFoundException(f"角色 {code} 不存在")

        return RoleDTO.from_orm(role)

    async def list(
            self,
            code: str = None,
            name: str = None,
            status: int = None,
    ) -> List[RoleDTO]:
        """
        查询角色列表（不分页）

        Args:
            code: 角色编号（精确匹配）
            name: 角色名称（模糊匹配）
            status: 状态

        Returns:
            List[RoleDTO]: 角色 DTO 列表
        """
        roles = await self.repo.list_by_condition(
            code=code,
            name=name,
            status=status,
        )

        return [RoleDTO.from_orm(role) for role in roles]

    async def page(self, query: RoleQueryDTO) -> PageDTO[RoleDTO]:
        """
        分页查询角色

        Args:
            query: 查询条件 DTO

        Returns:
            PageDTO[RoleDTO]: 分页 DTO
        """
        result = await self.repo.page_by_condition(
            code=query.code,
            name=query.name,
            status=query.status,
            page=query.page,
            page_size=query.page_size,
        )

        # 使用工具函数构建分页 DTO
        return build_page_dto(
            result,
            lambda role: RoleDTO.from_orm(role),
            query.page,
            query.page_size,
        )

    async def get_assignable_roles(self) -> List[RoleDTO]:
        """
        获取可分配的角色列表

        Returns:
            List[RoleDTO]: 可分配的角色 DTO 列表
        """
        roles = await self.repo.get_assignable_roles()
        return [RoleDTO.from_orm(role) for role in roles]

    async def grant_functions(self, code: str, func_codes: List[str]) -> bool:
        """
        授权功能给角色

        Args:
            code: 角色编号
            func_codes: 功能编号列表

        Returns:
            bool: 是否授权成功

        Raises:
            RoleNotFoundException: 角色不存在
        """
        # 使用 Repository 查询
        role = await self.repo.get_by_code(code)
        if not role:
            raise RoleNotFoundException(f"角色 {code} 不存在")

        # TODO: 实现角色-功能关联表的保存逻辑
        # 这需要创建 sys_role_func 关联表
        logger.info(f"角色 {code} 授权功能: {func_codes}")

        return True

    async def get_functions(self, code: str) -> List[str]:
        """
        查询角色已授权的功能

        Args:
            code: 角色编号

        Returns:
            List[str]: 功能编号列表

        Raises:
            RoleNotFoundException: 角色不存在
        """
        # 使用 Repository 查询
        role = await self.repo.get_by_code(code)
        if not role:
            raise RoleNotFoundException(f"角色 {code} 不存在")

        # TODO: 实现从角色-功能关联表查询
        # 这需要创建 sys_role_func 关联表
        logger.info(f"查询角色 {code} 的授权功能")

        return []

    # ========================================================================
    # 角色用户关联管理方法
    # ========================================================================

    async def grant_roles_to_user(
        self,
        user_code: str,
        role_codes: List[str],
    ) -> bool:
        """
        给用户授予角色列表

        业务逻辑：
        1. 删除该用户的旧角色关联
        2. 批量创建新的角色关联

        Args:
            user_code: 用户编号（字符串，不依赖 User 实体）
            role_codes: 角色编号列表

        Returns:
            bool: 是否授权成功
        """
        # 1. 删除该用户的旧角色关联
        await self.role_user_repo.delete_by_user_code(user_code)

        # 2. 批量创建新的角色关联
        if role_codes:
            relations = [
                SysRoleUserRelation(
                    user_code=user_code,
                    role_code=role_code,
                )
                for role_code in role_codes
            ]
            await self.role_user_repo.batch_create(relations)

        logger.info(f"用户 {user_code} 授予角色: {role_codes}")
        return True

    async def grant_users_to_role(
        self,
        role_code: str,
        user_codes: List[str],
    ) -> bool:
        """
        给角色批量分配用户

        业务逻辑：
        1. 删除该角色的旧用户关联
        2. 批量创建新的用户关联

        Args:
            role_code: 角色编号
            user_codes: 用户编号列表

        Returns:
            bool: 是否授权成功
        """
        # 1. 删除该角色的旧用户关联
        await self.role_user_repo.delete_by_role_code(role_code)

        # 2. 批量创建新的用户关联
        if user_codes:
            relations = [
                SysRoleUserRelation(
                    user_code=user_code,
                    role_code=role_code,
                )
                for user_code in user_codes
            ]
            await self.role_user_repo.batch_create(relations)

        logger.info(f"角色 {role_code} 分配用户: {user_codes}")
        return True

    async def get_user_roles(self, user_code: str) -> List[str]:
        """
        查询用户的角色编号列表

        Args:
            user_code: 用户编号

        Returns:
            List[str]: 角色编号列表
        """
        relations = await self.role_user_repo.find_by_user_code(user_code)
        return [r.role_code for r in relations]

    async def get_role_users(self, role_code: str) -> List[str]:
        """
        查询角色的用户编号列表

        Args:
            role_code: 角色编号

        Returns:
            List[str]: 用户编号列表
        """
        relations = await self.role_user_repo.find_by_role_code(role_code)
        return [r.user_code for r in relations]
