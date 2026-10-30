"""
认证模块 Facade 层

职责：
1. 编排多个 Service 完成认证流程
2. 负责 ATO ↔ DTO 的相互转换
3. 不包含核心业务逻辑

登录流程：
1. UserService 根据手机号查询用户
2. PasswordUtil 验证密码
3. JWTUtil 生成 Token
4. 返回登录结果
"""
from loguru import logger

from app.core.transaction import TransactionManager
from app.modules.user.service.user_service import UserService
from app.modules.user.dto.user_dto import UserDTO
from app.modules.auth.ato.auth_request import LoginRequest
from app.modules.auth.ato.auth_response import LoginResponse
from app.modules.auth.exception.auth_exception import (
    LoginFailedException,
    AccountDisabledException,
    AccountNotFoundException,
)
from app.util.jwt_util import jwt_util
from app.util.password_util import password_util
from app.core.config import settings


class AuthFacade:
    """认证模块门面类"""

    def __init__(
            self,
            user_service: UserService,
            transaction_manager: TransactionManager
    ):
        """
        初始化 AuthFacade

        Args:
            user_service: 用户 Service
            transaction_manager: 事务管理器
        """
        self.user_service = user_service
        self.transaction_manager = transaction_manager

    async def login(self, request: LoginRequest) -> LoginResponse:
        """
        用户登录

        业务流程：
        1. 根据手机号查询用户
        2. 验证用户状态（是否停用）
        3. 验证密码
        4. 生成 JWT Token
        5. 返回登录结果

        Args:
            request: 登录请求 ATO

        Returns:
            LoginResponse: 登录响应（包含 Token）

        Raises:
            AccountNotFoundException: 账号不存在
            AccountDisabledException: 账号已停用
            LoginFailedException: 密码错误
        """
        phone_number = request.phone_number
        password = request.password

        # 1. 根据手机号查询用户
        try:
            user_dto: UserDTO = await self.user_service.get_by_phone_number(phone_number)
        except Exception:
            # 用户不存在
            logger.warning(f"登录失败：手机号 {phone_number} 不存在")
            raise AccountNotFoundException(f"账号 {phone_number} 不存在")

        # 2. 验证用户状态
        if user_dto.status == 0:
            logger.warning(f"登录失败：账号 {phone_number} 已停用")
            raise AccountDisabledException(f"账号 {phone_number} 已停用，请联系管理员")

        # 3. 验证密码
        # password_util.verify_password() 返回 True/False
        password_valid = password_util.verify_password(
            password=password,
            password_hash=user_dto.password,
        )

        if not password_valid:
            logger.warning(f"登录失败：手机号 {phone_number} 密码错误")
            raise LoginFailedException("账号或密码错误")

        # 4. 生成 JWT Token
        # 使用 user_code 作为 Token 的 sub
        access_token = jwt_util.create_access_token(user_code=user_dto.code)

        # 5. 计算过期时间（秒）
        expires_in = settings.JWT_EXPIRE_MINUTES * 60

        # 6. 构建响应
        response = LoginResponse(
            access_token=access_token,
            token_type="Bearer",
            expires_in=expires_in,
            user_code=user_dto.code,
            user_name=user_dto.name,
        )

        logger.info(f"用户登录成功：{phone_number} - {user_dto.name}")
        return response
