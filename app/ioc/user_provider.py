"""
用户模块依赖注入

提供用户相关的 Repository、Service、Facade 的依赖注入函数
"""
from typing import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.user.repository.user_repository import UserRepository
from app.modules.user.service.user_service import UserService
from app.modules.user.facade.user_facade import UserFacade
from app.modules.role.service.role_service import RoleService
from app.ioc.role_provider import get_role_service
from app.ioc.transaction import get_transaction_manager


# ============================================================================
# Repository 依赖
# ============================================================================

async def get_user_repository(
        db: AsyncSession = Depends(get_db)
) -> AsyncGenerator[UserRepository, None]:
    """
    获取 UserRepository 实例

    Args:
        db: 数据库会话（自动注入）

    Yields:
        UserRepository: 用户 Repository 实例
    """
    yield UserRepository(db)


# ============================================================================
# Service 依赖
# ============================================================================

async def get_user_service(
        repo: UserRepository = Depends(get_user_repository)
) -> AsyncGenerator[UserService, None]:
    """
    获取 UserService 实例

    Args:
        repo: 用户 Repository（自动注入）

    Yields:
        UserService: 用户 Service 实例
    """
    yield UserService(repo)


# ============================================================================
# Facade 依赖
# ============================================================================

async def get_user_facade(
        user_service: UserService = Depends(get_user_service),
        role_service: RoleService = Depends(get_role_service),
        transaction_manager=get_transaction_manager,
) -> AsyncGenerator[UserFacade, None]:
    """
    获取 UserFacade 实例

    Args:
        user_service: 用户 Service（自动注入）
        role_service: 角色 Service（自动注入）
        transaction_manager: 事务管理器（自动注入）

    Yields:
        UserFacade: 用户 Facade 实例
    """
    yield UserFacade(user_service, role_service, transaction_manager)
