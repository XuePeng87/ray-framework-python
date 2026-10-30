"""
IoC (Inversion of Control) 包

提供依赖注入相关的功能

使用方式：
    from app.ioc import (
        get_role_facade,
        get_dept_facade,
        get_user_facade,
        get_auth_facade,
        verify_token,
    )
"""

# 事务管理器
from app.ioc.transaction import get_transaction_manager

# 角色模块依赖
from app.ioc.role_provider import (
    get_role_repository,
    get_role_user_relation_repository,
    get_role_service,
    get_role_facade,
)

# 部门模块依赖
from app.ioc.dept_provider import (
    get_dept_repository,
    get_dept_service,
    get_dept_facade,
)

# 用户模块依赖
from app.ioc.user_provider import (
    get_user_repository,
    get_user_service,
    get_user_facade,
)

# 认证模块依赖
from app.ioc.auth_provider import (
    get_auth_facade,
    verify_token,
)

__all__ = [
    # 事务管理器
    "get_transaction_manager",

    # 角色模块
    "get_role_repository",
    "get_role_user_relation_repository",
    "get_role_service",
    "get_role_facade",

    # 部门模块
    "get_dept_repository",
    "get_dept_service",
    "get_dept_facade",

    # 用户模块
    "get_user_repository",
    "get_user_service",
    "get_user_facade",

    # 认证模块
    "get_auth_facade",
    "verify_token",
]
