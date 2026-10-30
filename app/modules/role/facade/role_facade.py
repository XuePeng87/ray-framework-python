"""
角色模块 Facade 层

职责：
1. 编排 Service（可以调用多个 Service）
2. 负责 ATO ↔ DTO 的相互转换
3. 不包含核心业务逻辑

使用示例：
    facade = RoleFacade(role_service, transaction_manager)
    response = await facade.create_role(request_ato)
"""
from typing import List
from loguru import logger

from app.core.transaction import TransactionManager
from app.modules.role.service.role_service import RoleService
from app.modules.role.dto.role_dto import (
    RoleCreateDTO,
    RoleUpdateDTO,
    RoleQueryDTO,
    RoleDTO,
    PageDTO,
)
from app.modules.role.ato.role_request import (
    RoleCreateRequest,
    RoleUpdateRequest,
    RoleQueryRequest,
    GrantPermissionsRequest,
)
from app.modules.role.ato.role_response import (
    RoleResponse,
    PageResponse,
)


class RoleFacade:
    """
    角色模块门面类

    编排 Service，负责 ATO ↔ DTO 转换
    """

    def __init__(
            self,
            role_service: RoleService,
            transaction_manager: TransactionManager,
    ):
        """
        初始化 Facade

        Args:
            role_service: 角色 Service
        """
        self.role_service = role_service
        self.transaction_manager = transaction_manager

    # ========================================================================
    # ATO → DTO 转换方法（使用 model_dump 简化）
    # ========================================================================

    def _to_create_dto(self, ato: RoleCreateRequest) -> RoleCreateDTO:
        """将创建请求 ATO 转换为 DTO"""
        return RoleCreateDTO(**ato.model_dump())

    def _to_update_dto(self, ato: RoleUpdateRequest) -> RoleUpdateDTO:
        """将更新请求 ATO 转换为 DTO"""
        return RoleUpdateDTO(**ato.model_dump())

    def _to_query_dto(self, ato: RoleQueryRequest) -> RoleQueryDTO:
        """将查询请求 ATO 转换为 DTO"""
        return RoleQueryDTO(**ato.model_dump())

    # ========================================================================
    # DTO → ATO 转换方法（使用 model_validate 简化）
    # ========================================================================

    def _to_response_ato(self, dto: RoleDTO) -> RoleResponse:
        """将角色 DTO 转换为响应 ATO"""
        return RoleResponse.model_validate(dto.model_dump())

    def _to_page_response_ato(self, dto: PageDTO[RoleDTO]) -> PageResponse[RoleResponse]:
        """将分页 DTO 转换为分页响应 ATO"""
        return PageResponse[RoleResponse](
            items=[self._to_response_ato(item) for item in dto.items],
            total=dto.total,
            page=dto.page,
            page_size=dto.page_size,
            total_pages=dto.total_pages,
        )

    # ========================================================================
    # 业务编排方法（调用 Service）
    # ========================================================================

    async def create_role(
            self,
            request: RoleCreateRequest,
            current_user: str = "system",
    ) -> bool:
        """
        创建角色

        编排流程：
        1. ATO → DTO 转换
        2. 调用 Service 创建
        3. 返回结果

        Args:
            request: 创建请求 ATO
            current_user: 当前操作用户

        Returns:
            bool: 是否创建成功
        """
        # 转换
        dto = self._to_create_dto(request)

        async with self.transaction_manager.transaction():
            result = await self.role_service.create(dto, current_user)

        logger.info("Facade: 创建角色完成")
        return result

    async def update_role(
            self,
            code: str,
            request: RoleUpdateRequest,
            current_user: str = "system",
    ) -> bool:
        """
        更新角色

        编排流程：
        1. ATO → DTO 转换
        2. 调用 Service 更新
        3. 返回结果
        """
        dto = self._to_update_dto(request)
        async with self.transaction_manager.transaction():
            result = await self.role_service.update(code, dto, current_user)

        logger.info(f"Facade: 更新角色完成 - {code}")
        return result

    async def delete_role(self, code: str) -> bool:
        """
        删除角色

        编排流程：
        1. 调用 Service 删除
        2. 返回结果
        """
        async with self.transaction_manager.transaction():
            result = await self.role_service.delete(code)

        logger.info(f"Facade: 删除角色完成 - {code}")
        return result

    async def get_role_by_code(self, code: str) -> RoleResponse:
        """
        根据编号获取角色

        编排流程：
        1. 调用 Service 查询
        2. DTO → ATO 转换
        3. 返回 ATO
        """
        dto = await self.role_service.get_by_code(code)
        return self._to_response_ato(dto)

    async def list_roles(
            self,
            code: str = None,
            name: str = None,
            status: int = None,
    ) -> List[RoleResponse]:
        """
        查询角色列表（不分页）

        编排流程：
        1. 调用 Service 查询
        2. DTO 列表 → ATO 列表转换
        3. 返回 ATO 列表
        """
        dtos = await self.role_service.list(code=code, name=name, status=status)
        return [self._to_response_ato(dto) for dto in dtos]

    async def page_roles(self, query: RoleQueryRequest) -> PageResponse[RoleResponse]:
        """
        分页查询角色

        编排流程：
        1. ATO → DTO 转换
        2. 调用 Service 分页查询
        3. DTO → ATO 转换
        4. 返回分页 ATO
        """
        query_dto = self._to_query_dto(query)
        page_dto = await self.role_service.page(query_dto)
        return self._to_page_response_ato(page_dto)

    async def get_assignable_roles(self) -> List[RoleResponse]:
        """
        获取可分配的角色列表

        编排流程：
        1. 调用 Service 获取
        2. DTO 列表 → ATO 列表转换
        3. 返回 ATO 列表
        """
        dtos = await self.role_service.get_assignable_roles()
        return [self._to_response_ato(dto) for dto in dtos]

    async def grant_permissions(
            self,
            code: str,
            request: GrantPermissionsRequest,
    ) -> bool:
        """
        授权功能给角色

        编排流程：
        1. 调用 Service 授权
        2. 返回结果

        说明：此方法展示了未来可能需要编排多个 Service 的场景
        例如：授权后需要通知 UserService 刷新用户权限缓存
        """
        result = await self.role_service.grant_functions(code, request.func_codes)

        logger.info(f"Facade: 授权功能完成 - {code}")
        return result

    async def get_permissions(self, code: str) -> List[str]:
        """
        查询角色已授权的功能列表

        编排流程：
        1. 调用 Service 查询
        2. 返回结果
        """
        result = await self.role_service.get_functions(code)

        logger.info(f"Facade: 查询权限完成 - {code}")
        return result

    # ========================================================================
    # 角色用户关联管理方法
    # ========================================================================

    async def grant_users_to_role(
        self,
        role_code: str,
        user_codes: List[str],
    ) -> bool:
        """
        给角色批量分配用户

        编排流程：
        1. 调用 Service 处理
        2. 返回结果
        """
        async with self.transaction_manager.transaction():
            result = await self.role_service.grant_users_to_role(role_code, user_codes)

        logger.info(f"Facade: 角色分配用户完成 - {role_code}")
        return result

    async def get_role_users(self, role_code: str) -> List[str]:
        """
        查询角色的用户列表

        编排流程：
        1. 调用 Service 查询
        2. 返回结果
        """
        result = await self.role_service.get_role_users(role_code)

        logger.info(f"Facade: 查询角色用户完成 - {role_code}")
        return result

    async def get_user_roles(self, user_code: str) -> List[str]:
        """
        查询用户的角色列表

        编排流程：
        1. 调用 Service 查询
        2. 返回结果
        """
        result = await self.role_service.get_user_roles(user_code)

        logger.info(f"Facade: 查询用户角色完成 - {user_code}")
        return result
