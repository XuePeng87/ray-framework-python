class BusinessException(Exception):
    """
    基础业务异常

    所有业务逻辑异常都继承此类
    默认 HTTP 返回 200，通过 Result.fail() 的 code 字段区分具体错误类型
    可以通过 http_status_code 参数指定其他 HTTP 状态码（如 401, 403）
    """

    def __init__(self, message: str, code: str = "BUSINESS_ERROR", http_status_code: int = 200):
        self.message = message
        self.code = code
        self.http_status_code = http_status_code
        super().__init__(self.message)


class NotFoundException(BusinessException):
    """资源未找到异常"""

    def __init__(self, message: str = "资源不存在"):
        super().__init__(message=message, code="NOT_FOUND")


class UnauthorizedException(BusinessException):
    """未授权访问异常（HTTP 401）"""

    def __init__(self, message: str = "未授权访问"):
        super().__init__(message=message, code="UNAUTHORIZED", http_status_code=401)


class ForbiddenException(BusinessException):
    """禁止访问异常（HTTP 403）"""

    def __init__(self, message: str = "禁止访问"):
        super().__init__(message=message, code="FORBIDDEN", http_status_code=403)


class ValidationException(BusinessException):
    """验证错误异常"""

    def __init__(self, message: str = "参数验证失败"):
        super().__init__(message=message, code="VALIDATION_ERROR")


class DuplicateException(BusinessException):
    """重复资源异常"""

    def __init__(self, message: str = "资源已存在"):
        super().__init__(message=message, code="DUPLICATE")
