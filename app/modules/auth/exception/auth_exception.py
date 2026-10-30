"""
认证模块异常

登录、Token 验证等认证相关的异常
"""
from app.common.base_exception import BusinessException, UnauthorizedException, ForbiddenException, ValidationException


class AuthErrorCode:
    """认证模块错误码（40000-40999）"""

    # 通用错误
    AUTH_ERROR = 40000
    AUTH_ERROR_MESSAGE = "认证错误"

    # 登录相关（40001-40009）
    LOGIN_FAILED = 40001
    LOGIN_FAILED_MESSAGE = "账号或密码错误"

    ACCOUNT_DISABLED = 40002
    ACCOUNT_DISABLED_MESSAGE = "账号已停用，请联系管理员"

    ACCOUNT_NOT_FOUND = 40003
    ACCOUNT_NOT_FOUND_MESSAGE = "账号不存在"

    # Token 相关（40010-40019）
    TOKEN_EXPIRED = 40010
    TOKEN_EXPIRED_MESSAGE = "Token 已过期"

    TOKEN_INVALID = 40011
    TOKEN_INVALID_MESSAGE = "Token 无效"

    TOKEN_MISSING = 40012
    TOKEN_MISSING_MESSAGE = "Token 缺失"

    JWT_CONFIG_ERROR = 40013
    JWT_CONFIG_ERROR_MESSAGE = "JWT 配置错误"

    @classmethod
    def get_message(cls, code: int) -> str:
        """根据错误码获取对应的默认消息"""
        message_map = {
            cls.AUTH_ERROR: cls.AUTH_ERROR_MESSAGE,
            cls.LOGIN_FAILED: cls.LOGIN_FAILED_MESSAGE,
            cls.ACCOUNT_DISABLED: cls.ACCOUNT_DISABLED_MESSAGE,
            cls.ACCOUNT_NOT_FOUND: cls.ACCOUNT_NOT_FOUND_MESSAGE,
            cls.TOKEN_EXPIRED: cls.TOKEN_EXPIRED_MESSAGE,
            cls.TOKEN_INVALID: cls.TOKEN_INVALID_MESSAGE,
            cls.TOKEN_MISSING: cls.TOKEN_MISSING_MESSAGE,
            cls.JWT_CONFIG_ERROR: cls.JWT_CONFIG_ERROR_MESSAGE,
        }
        return message_map.get(code, "未知错误")


class LoginFailedException(UnauthorizedException):
    """登录失败异常（账号或密码错误）- HTTP 401"""

    def __init__(self, message: str = None):
        # 使用默认消息或自定义消息
        msg = message or AuthErrorCode.LOGIN_FAILED_MESSAGE
        super().__init__(message=msg)
        self.code = str(AuthErrorCode.LOGIN_FAILED)


class AccountDisabledException(ForbiddenException):
    """账号已停用异常 - HTTP 403"""

    def __init__(self, message: str = None):
        msg = message or AuthErrorCode.ACCOUNT_DISABLED_MESSAGE
        super().__init__(message=msg)
        self.code = str(AuthErrorCode.ACCOUNT_DISABLED)


class AccountNotFoundException(UnauthorizedException):
    """账号不存在异常 - HTTP 401"""

    def __init__(self, message: str = None):
        msg = message or AuthErrorCode.ACCOUNT_NOT_FOUND_MESSAGE
        super().__init__(message=msg)
        self.code = str(AuthErrorCode.ACCOUNT_NOT_FOUND)


class TokenExpiredException(UnauthorizedException):
    """Token 已过期异常 - HTTP 401"""

    def __init__(self, message: str = None):
        msg = message or AuthErrorCode.TOKEN_EXPIRED_MESSAGE
        super().__init__(message=msg)
        self.code = str(AuthErrorCode.TOKEN_EXPIRED)


class TokenInvalidException(UnauthorizedException):
    """Token 无效异常 - HTTP 401"""

    def __init__(self, message: str = None):
        msg = message or AuthErrorCode.TOKEN_INVALID_MESSAGE
        super().__init__(message=msg)
        self.code = str(AuthErrorCode.TOKEN_INVALID)


class TokenMissingException(UnauthorizedException):
    """Token 缺失异常 - HTTP 401"""

    def __init__(self, message: str = None):
        msg = message or AuthErrorCode.TOKEN_MISSING_MESSAGE
        super().__init__(message=msg)
        self.code = str(AuthErrorCode.TOKEN_MISSING)


class JWTConfigException(ValidationException):
    """JWT 配置错误异常"""

    def __init__(self, message: str = None):
        msg = message or AuthErrorCode.JWT_CONFIG_ERROR_MESSAGE
        super().__init__(message=msg)
        self.code = str(AuthErrorCode.JWT_CONFIG_ERROR)
