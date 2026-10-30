"""
用户模块异常

定义用户相关的业务异常和错误码
"""
from app.common.base_exception import BusinessException, NotFoundException, DuplicateException


class UserErrorCode:
    """用户模块错误码（12000-12999）"""

    # 通用错误
    USER_ERROR = 12000

    # 查询相关
    USER_NOT_FOUND = 12001
    USER_QUERY_ERROR = 12002

    # 创建相关
    USER_CODE_EXISTS = 12010
    USER_PHONE_EXISTS = 12011  # 手机号已存在
    USER_EMAIL_EXISTS = 12012  # 邮箱已存在
    USER_CREATE_ERROR = 12013

    # 更新相关
    USER_UPDATE_ERROR = 12020
    USER_STATUS_ERROR = 12021

    # 删除相关
    USER_DELETE_ERROR = 12030

    # 密码相关
    USER_PASSWORD_ERROR = 12040
    USER_OLD_PASSWORD_WRONG = 12041  # 旧密码不正确
    USER_PASSWORD_INVALID = 12042  # 密码格式不合规
    USER_PASSWORD_RESET_ERROR = 12043
    USER_PASSWORD_HASH_ERROR = 12044  # 密码哈希处理失败

    # 角色关联相关
    USER_ROLE_GRANT_ERROR = 12050

    # 参数验证
    USER_INVALID_CODE = 12060
    USER_INVALID_PHONE = 12061
    USER_INVALID_EMAIL = 12062
    USER_INVALID_PASSWORD = 12063


class UserException(BusinessException):
    """用户相关的基础异常"""

    def __init__(self, message: str, code: int = UserErrorCode.USER_ERROR):
        super().__init__(message=message, code=str(code))


class UserNotFoundException(NotFoundException):
    """用户未找到异常"""

    def __init__(self, message: str = "用户不存在"):
        super().__init__(message=message)
        self.code = str(UserErrorCode.USER_NOT_FOUND)


class UserPhoneExistsException(DuplicateException):
    """手机号已存在异常"""

    def __init__(self, message: str = "手机号已存在"):
        super().__init__(message=message)
        self.code = str(UserErrorCode.USER_PHONE_EXISTS)


class UserEmailExistsException(DuplicateException):
    """邮箱已存在异常"""

    def __init__(self, message: str = "邮箱已存在"):
        super().__init__(message=message)
        self.code = str(UserErrorCode.USER_EMAIL_EXISTS)


class UserPasswordException(BusinessException):
    """密码相关异常"""

    def __init__(self, message: str = "密码错误", code: int = UserErrorCode.USER_PASSWORD_ERROR):
        super().__init__(message=message, code=str(code))


class UserOldPasswordWrongException(BusinessException):
    """旧密码不正确异常"""

    def __init__(self, message: str = "旧密码不正确"):
        super().__init__(message=message, code=str(UserErrorCode.USER_OLD_PASSWORD_WRONG))


class UserPasswordInvalidException(BusinessException):
    """密码格式不合规异常"""

    def __init__(self, message: str = "密码格式不合规"):
        super().__init__(message=message, code=str(UserErrorCode.USER_PASSWORD_INVALID))


class UserPasswordHashException(BusinessException):
    """密码哈希处理失败异常"""

    def __init__(self, message: str = "密码哈希处理失败"):
        super().__init__(message=message, code=str(UserErrorCode.USER_PASSWORD_HASH_ERROR))
