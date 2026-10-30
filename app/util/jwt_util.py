"""
JWT 工具类

功能：
1. 生成 Access Token
2. 验证 Access Token
3. 解析当前用户编号

依赖：
    pip install PyJWT
"""

from datetime import datetime, timedelta, timezone

import jwt
from jwt import (
    ExpiredSignatureError,
    ImmatureSignatureError,
    InvalidTokenError,
)

from app.core.config import settings
from app.modules.auth.exception.auth_exception import (
    TokenExpiredException,
    TokenInvalidException,
    JWTConfigException,
)


class JWTUtil:
    """
    JWT 工具类。

    设计原则：
    1. 不依赖 FastAPI，方便复用和单元测试。
    2. 不查询数据库，只负责 JWT 本身。
    3. 签名算法固定为 HS256，不接受客户端指定算法。
    4. 使用 UTC 时间，避免服务器时区问题。
    5. 不在 JWT 中存储密码或敏感用户信息。
    6. 配置从 settings 读取，不硬编码默认值。
    """

    ALGORITHM = "HS256"

    def __init__(
            self,
            secret_key: str = None,
            expire_minutes: int = None,
            issuer: str = None,
            audience: str = None,
    ):
        """
        初始化 JWT 工具类。

        如果不传参数，则从 settings 中读取配置。

        :param secret_key: JWT 签名密钥（默认从 settings.JWT_SECRET_KEY 读取）
        :param expire_minutes: Access Token 有效期，单位分钟（默认从 settings.JWT_EXPIRE_MINUTES 读取）
        :param issuer: Token 签发者（默认从 settings.JWT_ISSUER 读取）
        :param audience: Token 目标接收方（默认从 settings.JWT_AUDIENCE 读取）

        :raises JWTConfigError: 配置参数不合法
        """

        # 从 settings 读取配置（如果未传入参数）
        secret_key = secret_key or settings.JWT_SECRET_KEY
        expire_minutes = expire_minutes if expire_minutes is not None else settings.JWT_EXPIRE_MINUTES
        issuer = issuer or settings.JWT_ISSUER
        audience = audience or settings.JWT_AUDIENCE

        if not secret_key or len(secret_key.encode("utf-8")) < 32:
            raise JWTConfigException(
                "JWT secret_key 至少需要 32 字节的高熵随机密钥"
            )

        if expire_minutes <= 0:
            raise JWTConfigException(
                "expire_minutes 必须大于 0"
            )

        self.secret_key = secret_key
        self.expire_minutes = expire_minutes
        self.issuer = issuer
        self.audience = audience

    def create_access_token(self, user_code: str) -> str:
        """
        创建 Access Token。

        :param user_code: 用户编号
        :return: JWT 字符串
        """

        now = datetime.now(timezone.utc)

        payload = {
            # JWT 标准声明要求 sub 是字符串
            "sub": str(user_code),

            # 签发者
            "iss": self.issuer,

            # 接收方
            "aud": self.audience,

            # 签发时间
            "iat": now,

            # 生效时间
            "nbf": now,

            # 过期时间
            "exp": now + timedelta(
                minutes=self.expire_minutes
            ),

            # Token 类型，方便以后区分 Refresh Token
            "type": "access",
        }

        return jwt.encode(
            payload,
            self.secret_key,
            algorithm=self.ALGORITHM,
        )

    def verify_access_token(self, token: str) -> dict:
        """
        验证并解析 Access Token。

        验证内容：
        1. JWT 签名是否合法
        2. 是否过期
        3. 是否已经生效
        4. 签发者是否正确
        5. 接收方是否正确
        6. 必要声明是否存在
        7. Token 类型是否为 access

        :param token: JWT 字符串
        :return: 解码后的 payload 字典

        :raises TokenExpiredException: Token 已过期
        :raises TokenInvalidException: Token 不合法
        """

        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.ALGORITHM],
                issuer=self.issuer,
                audience=self.audience,
                options={
                    "require": [
                        "sub",
                        "iss",
                        "aud",
                        "iat",
                        "nbf",
                        "exp",
                        "type",
                    ]
                },
            )

            # 防止将其他用途的 JWT 当作 Access Token
            if payload.get("type") != "access":
                raise TokenInvalidException()

            # 校验用户编号 是否存在且非空
            user_code = payload.get("sub")

            if not isinstance(user_code, str) or not user_code:
                raise TokenInvalidException()

            return payload

        except ExpiredSignatureError:
            raise TokenExpiredException()

        except (ImmatureSignatureError, InvalidTokenError):
            raise TokenInvalidException()

    def get_user_code(self, token: str) -> str:
        """
        验证 Token 并获取用户编号。

        注意：
        此方法会执行完整的 JWT 验证，
        不是直接解码未经验证的 payload。
        """

        payload = self.verify_access_token(token)

        return payload["sub"]


# 每个 Worker 进程内可以复用该工具实例。
jwt_util = JWTUtil()
