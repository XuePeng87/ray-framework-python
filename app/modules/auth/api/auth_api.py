"""
认证模块 API 路由

提供登录、登出、获取当前用户等认证接口
"""
from typing import Annotated
from fastapi import APIRouter, Depends
from loguru import logger

from app.ioc import get_auth_facade, verify_token
from app.core.result import Result
from app.modules.auth.facade.auth_facade import AuthFacade
from app.modules.auth.ato.auth_request import LoginRequest
from app.modules.auth.ato.auth_response import LoginResponse

# 创建路由器
router = APIRouter(
    prefix="/auth",
    tags=["认证管理"],
)

# 定义依赖注入的类型别名
AuthFacadeDep = Annotated[AuthFacade, Depends(get_auth_facade)]


@router.post(
    "/login",
    response_model=Result[LoginResponse],
    summary="用户登录",
    description="使用手机号和密码登录，返回 JWT Token",
)
async def login(
        request: LoginRequest,
        facade: AuthFacadeDep,
):
    """
    用户登录

    - **phone_number**: 手机号
    - **password**: 密码

    返回：
    - access_token: JWT 访问令牌
    - token_type: 令牌类型（Bearer）
    - expires_in: 过期时间（秒）
    - user_code: 用户编号
    - user_name: 用户姓名
    """
    result = await facade.login(request)
    logger.info(f"API: 用户登录成功 - {request.phone_number}")
    return Result.ok(result, message="登录成功")


@router.get(
    "/me",
    response_model=Result[str],
    summary="获取当前登录用户",
    description="根据 Token 获取当前登录用户的编号（需要认证）",
)
async def me(
        token_payload: Annotated[dict, Depends(verify_token)]
):
    """
    获取当前登录用户编号

    **需要认证**：请求头必须携带有效的 JWT Token
    - Authorization: Bearer <access_token>

    返回：
    - user_code: 当前登录用户的编号
    """
    # 从 token_payload 中获取 user_code（存储在 sub 字段）
    user_code = token_payload.get("sub")
    # 调用 Facade 获取用户编号

    logger.info(f"API: 获取当前用户成功 - {user_code}")
    return Result.ok(user_code, message="获取当前登录用户编号成功")
