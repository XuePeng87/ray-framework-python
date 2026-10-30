"""
事务管理器依赖注入

提供 TransactionManager 的依赖注入函数
"""
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.transaction import TransactionManager


def get_transaction_manager(
        session: AsyncSession = Depends(get_db),
) -> TransactionManager:
    """
    获取 TransactionManager 实例

    Args:
        session: 数据库会话（自动注入）

    Returns:
        TransactionManager: 事务管理器实例
    """
    return TransactionManager(session)
