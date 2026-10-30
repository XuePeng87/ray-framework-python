"""
角色模块依赖注入

提供角色相关的 Repository、Service、Facade 的依赖注入函数
"""
from typing import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.role.repository.role_repository import RoleRepository
from app.modules.role.repository.role_user_relation_repository import RoleUserRelationRepository
from app.modules.role.service.role_service import RoleService
from app.modules.role.facade.role_facade import RoleFacade
from app.ioc.transaction import get_transaction_manager


# ============================================================================
# Repository 依赖
# ============================================================================

async def get_role_repository(
        db: AsyncSession = Depends(get_db)
) -> AsyncGenerator[RoleRepository, None]:
    """
    获取 RoleRepository 实例

    Args:
        db: 数据库会话（自动注入）

    Yields:
        RoleRepository: 角色 Repository 实例
    """
    yield RoleRepository(db)


async def get_role_user_relation_repository(
        db: AsyncSession = Depends(get_db)
) -> AsyncGenerator[RoleUserRelationRepository, None]:
    """
    获取 RoleUserRelationRepository 实例

    Args:
        db: 数据库会话（自动注入）

    Yields:
        RoleUserRelationRepository: 角色用户关联 Repository 实例
    """
    yield RoleUserRelationRepository(db)


# ============================================================================
# Service 依赖
# ============================================================================

async def get_role_service(
        repo: RoleRepository = Depends(get_role_repository),
        role_user_repo: RoleUserRelationRepository = Depends(get_role_user_relation_repository),
) -> AsyncGenerator[RoleService, None]:
    """
    获取 RoleService 实例

    Args:
        repo: 角色 Repository（自动注入）
        role_user_repo: 角色用户关联 Repository（自动注入）

    Yields:
        RoleService: 角色 Service 实例
    """
    yield RoleService(repo, role_user_repo)


# ============================================================================
# Facade 依赖
# ============================================================================

async def get_role_facade(
        service: RoleService = Depends(get_role_service),
        transaction_manager=get_transaction_manager,
) -> AsyncGenerator[RoleFacade, None]:
    """
    获取 RoleFacade 实例

    Args:
        service: 角色 Service（自动注入）
        transaction_manager: 事务管理器（自动注入）

    Yields:
        RoleFacade: 角色 Facade 实例
    """
    yield RoleFacade(service, transaction_manager)
