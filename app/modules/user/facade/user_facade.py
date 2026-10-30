"""
用户模块 Facade 层

职责：
1. 编排 Service（可以调用多个 Service）
2. 负责 ATO ↔ DTO 的相互转换
3. 不包含核心业务逻辑
"""
from typing import List, Optional
from loguru import logger

from app.core.transaction import TransactionManager
from app.modules.user.service.user_service import UserService
from app.modules.role.service.role_service import RoleService
from app.modules.user.dto.user_dto import (
    UserCreateDTO,
    UserUpdateDTO,
    UserUpdatePasswordDTO,
    UserQueryDTO,
    UserDTO,
)
from app.common.base_dto import PageDTO
from app.modules.user.ato.user_request import (
    UserCreateRequest,
    UserUpdateRequest,
    UserUpdatePasswordRequest,
    UserQueryRequest,
)
from app.modules.user.ato.user_response import (
    UserResponse,
    UserListResponse,
)


class UserFacade:
    """用户模块门面类"""

    def __init__(
        self,
        user_service: UserService,
        role_service: RoleService,
        transaction_manager: TransactionManager,
    ):
        self.user_service = user_service
        self.role_service = role_service
        self.transaction_manager = transaction_manager

    # ========================================================================
    # ATO → DTO 转换方法
    # ========================================================================

    def _to_create_dto(self, ato: UserCreateRequest) -> UserCreateDTO:
        """将创建请求 ATO 转换为 DTO"""
        return UserCreateDTO(**ato.model_dump())

    def _to_update_dto(self, ato: UserUpdateRequest) -> UserUpdateDTO:
        """将更新请求 ATO 转换为 DTO"""
        return UserUpdateDTO(**ato.model_dump())

    def _to_update_password_dto(self, ato: UserUpdatePasswordRequest) -> UserUpdatePasswordDTO:
        """将修改密码请求 ATO 转换为 DTO"""
        return UserUpdatePasswordDTO(**ato.model_dump())

    def _to_query_dto(self, ato: UserQueryRequest) -> UserQueryDTO:
        """将查询请求 ATO 转换为 DTO"""
        return UserQueryDTO(**ato.model_dump())

    # ========================================================================
    # DTO → ATO 转换方法
    # ========================================================================

    def _to_response_ato(self, dto: UserDTO) -> UserResponse:
        """将用户 DTO 转换为响应 ATO"""
        return UserResponse.model_validate(dto.model_dump())

    def _to_list_response_ato(self, dto: UserDTO) -> UserListResponse:
        """将用户 DTO 转换为列表响应 ATO（精简版）"""
        return UserListResponse(
            code=dto.code,
            name=dto.name,
        )

    # ========================================================================
    # 业务编排方法
    # ========================================================================

    async def create_user(
        self,
        request: UserCreateRequest,
        current_user: str = "system",
    ) -> bool:
        """
        创建用户

        编排流程：
        1. UserService 创建用户（不处理角色）
        2. RoleService 授予角色（接收 user_code + role_codes）
        """
        dto = self._to_create_dto(request)
        async with self.transaction_manager.transaction():
            # 1. 创建用户（UserService 会在 dto 中设置 code）
            result = await self.user_service.create(dto, current_user)

            # 2. 授予角色（如果传了 role_codes）
            if result and dto.role_codes:
                await self.role_service.grant_roles_to_user(
                    user_code=dto.code,  # 从 dto 中获取生成的 code
                    role_codes=dto.role_codes,
                )

        logger.info("Facade: 创建用户完成")
        return result

    async def update_user(
        self,
        code: str,
        request: UserUpdateRequest,
        current_user: str = "system",
    ) -> bool:
        """
        更新用户

        编排流程：
        1. UserService 更新用户信息
        2. 如果传了 role_codes，更新角色关联
        """
        dto = self._to_update_dto(request)
        async with self.transaction_manager.transaction():
            # 1. 更新用户信息
            result = await self.user_service.update(code, dto, current_user)

            # 2. 更新角色关联（如果传了 role_codes）
            if result and request.role_codes is not None:
                await self.role_service.grant_roles_to_user(
                    user_code=code,
                    role_codes=request.role_codes,
                )

        logger.info(f"Facade: 更新用户完成 - {code}")
        return result

    async def delete_user(self, code: str) -> bool:
        """删除用户"""
        async with self.transaction_manager.transaction():
            result = await self.user_service.delete(code)
        logger.info(f"Facade: 删除用户完成 - {code}")
        return result

    async def get_user_by_code(self, code: str) -> UserResponse:
        """
        根据编号获取用户

        编排流程：
        1. 查询用户基本信息（UserService）
        2. 查询用户的角色列表（RoleService）
        3. 填充 role_codes
        """
        # 1. 查询用户基本信息
        dto = await self.user_service.get_by_code(code)

        # 2. 查询用户的角色列表
        role_codes = await self.role_service.get_user_roles(user_code=code)

        # 3. 填充 role_codes（需要在 UserDTO 中添加此字段）
        dto.role_codes = role_codes

        return self._to_response_ato(dto)

    async def list_users(
        self,
        dept_code: Optional[str] = None,
        name: Optional[str] = None,
        status: Optional[int] = None,
    ) -> List[UserResponse]:
        """查询用户列表（不分页）"""
        dtos = await self.user_service.list(
            dept_code=dept_code,
            name=name,
            status=status,
        )
        return [self._to_response_ato(dto) for dto in dtos]

    async def page_users(self, query: UserQueryRequest) -> PageDTO[UserResponse]:
        """分页查询用户"""
        query_dto = self._to_query_dto(query)
        page_dto = await self.user_service.page(query_dto)

        # 转换分页结果中的 DTO 为 ATO
        from app.common.base_dto import build_page_dto
        return build_page_dto(
            (page_dto.items, page_dto.total),
            lambda dto: self._to_response_ato(dto),
            page_dto.page,
            page_dto.page_size,
        )

    async def update_password(
        self,
        code: str,
        request: UserUpdatePasswordRequest,
    ) -> bool:
        """修改密码"""
        dto = self._to_update_password_dto(request)
        async with self.transaction_manager.transaction():
            result = await self.user_service.update_password(code, dto)
        logger.info(f"Facade: 修改密码完成 - {code}")
        return result

    async def reset_password(self, code: str) -> bool:
        """重置密码"""
        async with self.transaction_manager.transaction():
            result = await self.user_service.reset_password(code)
        logger.info(f"Facade: 重置密码完成 - {code}")
        return result

    async def list_users_simple(
        self,
        dept_code: Optional[str] = None,
        name: Optional[str] = None,
        status: Optional[int] = None,
    ) -> List[UserListResponse]:
        """查询用户列表（精简版，用于下拉选择）"""
        dtos = await self.user_service.list(
            dept_code=dept_code,
            name=name,
            status=status,
        )
        return [self._to_list_response_ato(dto) for dto in dtos]
