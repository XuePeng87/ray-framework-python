from app.common.base_exception import BusinessException, NotFoundException, DuplicateException


class DeptErrorCode:
    """部门模块错误码（11000-11999）"""

    # 通用错误
    DEPT_ERROR = 11000

    # 查询相关
    DEPT_NOT_FOUND = 11001
    DEPT_QUERY_ERROR = 11002

    # 创建相关
    DEPT_CODE_EXISTS = 11010
    DEPT_NAME_EXISTS = 11011
    DEPT_CREATE_ERROR = 11012

    # 更新相关
    DEPT_UPDATE_ERROR = 11020
    DEPT_STATUS_ERROR = 11021

    # 删除相关
    DEPT_DELETE_ERROR = 11030
    DEPT_HAS_CHILDREN = 11031  # 部门下有子部门，不能删除

    # 移动相关
    DEPT_MOVE_ERROR = 11040
    DEPT_MOVE_TO_SELF = 11041  # 不能移动到自己下
    DEPT_MOVE_CIRCULAR = 11042  # 循环引用（移动到子部门下）

    # 参数验证
    DEPT_INVALID_CODE = 11050
    DEPT_INVALID_PARENT = 11051
    DEPT_INVALID_NAME = 11052


class DeptException(BusinessException):
    """部门相关的基础异常"""

    def __init__(self, message: str, code: int = DeptErrorCode.DEPT_ERROR):
        super().__init__(message=message, code=str(code))


class DeptNotFoundException(NotFoundException):
    """部门未找到异常"""

    def __init__(self, message: str = "部门不存在"):
        super().__init__(message=message)
        self.code = str(DeptErrorCode.DEPT_NOT_FOUND)


class DeptCodeExistsException(DuplicateException):
    """部门编号已存在异常"""

    def __init__(self, message: str = "部门编号已存在"):
        super().__init__(message=message)
        self.code = str(DeptErrorCode.DEPT_CODE_EXISTS)


class DeptNameExistsException(DuplicateException):
    """部门名称已存在异常"""

    def __init__(self, message: str = "部门名称已存在"):
        super().__init__(message=message)
        self.code = str(DeptErrorCode.DEPT_NAME_EXISTS)


class DeptHasChildrenException(BusinessException):
    """部门有子部门，不能删除"""

    def __init__(self, message: str = "部门下有子部门，请先删除子部门"):
        super().__init__(message=message, code=str(DeptErrorCode.DEPT_HAS_CHILDREN))


class DeptMoveToSelfException(BusinessException):
    """不能移动到自己下"""

    def __init__(self, message: str = "不能将部门移动到自己下"):
        super().__init__(message=message, code=str(DeptErrorCode.DEPT_MOVE_TO_SELF))


class DeptMoveCircularException(BusinessException):
    """循环引用异常"""

    def __init__(self, message: str = "不能将部门移动到其子部门下，会造成循环引用"):
        super().__init__(message=message, code=str(DeptErrorCode.DEPT_MOVE_CIRCULAR))
