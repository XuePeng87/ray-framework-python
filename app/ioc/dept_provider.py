"""
部门模块依赖注入

提供部门相关的 Repository、Service、Facade 的依赖注入函数
"""
from typing import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.dept.repository.dept_repository import DeptRepository
from app.modules.dept.service.dept_service import DeptService
from app.modules.dept.facade.dept_facade import DeptFacade
from app.ioc.transaction import get_transaction_manager


# ============================================================================
# Repository 依赖
# ============================================================================

async def get_dept_repository(
        db: AsyncSession = Depends(get_db)
) -> AsyncGenerator[DeptRepository, None]:
    """
    获取 DeptRepository 实例

    Args:
        db: 数据库会话（自动注入）

    Yields:
        DeptRepository: 部门 Repository 实例
    """
    yield DeptRepository(db)


# ============================================================================
# Service 依赖
# ============================================================================

async def get_dept_service(
        repo: DeptRepository = Depends(get_dept_repository)
) -> AsyncGenerator[DeptService, None]:
    """
    获取 DeptService 实例

    Args:
        repo: 部门 Repository（自动注入）

    Yields:
        DeptService: 部门 Service 实例
    """
    yield DeptService(repo)


# ============================================================================
# Facade 依赖
# ============================================================================

async def get_dept_facade(
        service: DeptService = Depends(get_dept_service),
        transaction_manager=get_transaction_manager,
) -> AsyncGenerator[DeptFacade, None]:
    """
    获取 DeptFacade 实例

    Args:
        service: 部门 Service（自动注入）
        transaction_manager: 事务管理器（自动注入）

    Yields:
        DeptFacade: 部门 Facade 实例
    """
    yield DeptFacade(service, transaction_manager)
