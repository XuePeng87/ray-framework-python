from app.common.base_exception import BusinessException, NotFoundException, DuplicateException


class RoleErrorCode:
    """角色模块错误码"""

    # 通用错误
    ROLE_ERROR = 10000

    # 查询相关
    ROLE_NOT_FOUND = 10001
    ROLE_QUERY_ERROR = 10002

    # 创建相关
    ROLE_CODE_EXISTS = 10010
    ROLE_NAME_EXISTS = 10011
    ROLE_CREATE_ERROR = 10012

    # 更新相关
    ROLE_UPDATE_ERROR = 10020
    ROLE_STATUS_ERROR = 10021

    # 删除相关
    ROLE_DELETE_ERROR = 10030
    ROLE_HAS_USERS = 10031  # 角色下还有用户，不能删除

    # 权限相关
    ROLE_PERMISSION_ERROR = 10040
    ROLE_GRANT_ERROR = 10041

    # 参数验证
    ROLE_INVALID_CODE = 10050
    ROLE_INVALID_NAME = 10051
    ROLE_INVALID_STATUS = 10052


class RoleException(BusinessException):
    """角色相关的基础异常"""

    def __init__(self, message: str, code: int = RoleErrorCode.ROLE_ERROR):
        super().__init__(message=message, code=str(code))


class RoleNotFoundException(NotFoundException):
    """角色未找到异常"""

    def __init__(self, message: str = "角色不存在"):
        super().__init__(message=message)
        self.code = str(RoleErrorCode.ROLE_NOT_FOUND)


class RoleCodeExistsException(DuplicateException):
    """角色编号已存在异常"""

    def __init__(self, message: str = "角色编号已存在"):
        super().__init__(message=message)
        self.code = str(RoleErrorCode.ROLE_CODE_EXISTS)


class RoleNameExistsException(DuplicateException):
    """角色名称已存在异常"""

    def __init__(self, message: str = "角色名称已存在"):
        super().__init__(message=message)
        self.code = str(RoleErrorCode.ROLE_NAME_EXISTS)


class RoleStatusException(BusinessException):
    """角色状态异常"""

    def __init__(self, message: str = "角色状态异常"):
        super().__init__(message=message, code=str(RoleErrorCode.ROLE_STATUS_ERROR))


class RolePermissionException(BusinessException):
    """角色权限异常"""

    def __init__(self, message: str = "角色权限不足"):
        super().__init__(message=message, code=str(RoleErrorCode.ROLE_PERMISSION_ERROR))
