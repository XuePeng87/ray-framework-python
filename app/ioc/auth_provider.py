"""
认证模块依赖注入

提供认证相关的 Facade 和 Token 验证的依赖注入函数
"""
from typing import Annotated, AsyncGenerator

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.modules.auth.facade.auth_facade import AuthFacade
from app.modules.auth.exception.auth_exception import TokenExpiredException, TokenInvalidException
from app.ioc.user_provider import get_user_service
from app.ioc.transaction import get_transaction_manager
from app.util.jwt_util import jwt_util


# ============================================================================
# Facade 依赖
# ============================================================================

async def get_auth_facade(
        user_service=Depends(get_user_service),
        transaction_manager=get_transaction_manager,
) -> AsyncGenerator[AuthFacade, None]:
    """
    获取 AuthFacade 实例

    Args:
        user_service: 用户 Service（自动注入）
        transaction_manager: 事务管理器（自动注入）

    Yields:
        AuthFacade: 认证 Facade 实例
    """
    yield AuthFacade(user_service, transaction_manager)


# ============================================================================
# Token 验证依赖
# ============================================================================

def verify_token(
        credentials: Annotated[
            HTTPAuthorizationCredentials,
            Depends(HTTPBearer()),
        ],
) -> dict:
    """
    验证 JWT Token

    用于需要认证的 API 接口，通过 Depends(verify_token) 使用

    Args:
        credentials: HTTP Bearer Token

    Returns:
        dict: Token payload（包含 user_code 等信息）

    Raises:
        TokenExpiredException: Token 已过期（HTTP 401）
        TokenInvalidException: Token 无效（HTTP 401）
    """
    token = credentials.credentials
    # 直接调用 JWTUtil 验证 Token
    # 异常由全局异常处理器统一处理
    payload = jwt_util.verify_access_token(token)
    return payload
