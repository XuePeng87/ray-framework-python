"""
全局异常处理器

业务异常返回 HTTP 200，通过 Result 格式包装
协议异常（如 404、401 等）才返回对应的 HTTP 状态码
"""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from loguru import logger

from app.common.base_exception import BusinessException
from app.core.result import Result


def register_exception_handlers(app: FastAPI):
    """注册全局异常处理器"""

    @app.exception_handler(BusinessException)
    async def business_exception_handler(request: Request, exc: BusinessException):
        """
        处理业务异常

        根据异常的 http_status_code 返回不同的 HTTP 状态码
        - 默认 HTTP 200（业务失败）
        - HTTP 401（未授权）- 添加 WWW-Authenticate header
        - HTTP 403（禁止访问）
        - 其他自定义 HTTP 状态码
        """
        logger.warning(f"业务异常: {exc.message} (code: {exc.code}, http_status: {exc.http_status_code})")

        # 业务异常根据 http_status_code 返回对应的 HTTP 状态码
        result = Result.fail(message=exc.message, code=exc.code)

        # 对于 401 错误，添加 WWW-Authenticate header
        headers = {}
        if exc.http_status_code == 401:
            headers["WWW-Authenticate"] = "Bearer"

        return JSONResponse(
            status_code=exc.http_status_code,  # 使用异常中定义的 HTTP 状态码
            content=result.model_dump(),
            headers=headers if headers else None,
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """
        处理未捕获的异常

        未捕获的异常返回 HTTP 500，表示服务器内部错误
        """
        logger.exception(f"未捕获的异常: {exc}")
        result = Result.fail(message="服务器内部错误", code="INTERNAL_ERROR")
        return JSONResponse(
            status_code=500,  # 真正的服务器错误才返回 500
            content=result.model_dump(),
        )
