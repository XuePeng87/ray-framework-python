"""
FastAPI 应用入口
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from loguru import logger

from app.core.config import settings
from app.core.database import init_db, close_db
from app.core.logging import setup_logging
from app.handler.exception_handler import register_exception_handlers
from app.middleware.logging_middleware import logging_middleware
from app.middleware.cors_middleware import get_cors_middleware_config


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理

    启动时：初始化日志、数据库
    关闭时：清理资源
    """
    # 启动事件
    logger.info("🚀 正在启动 ANOV Data Agent...")

    # 初始化日志
    setup_logging()

    # 初始化数据库
    logger.info("📦 正在初始化数据库...")
    await init_db()
    logger.info("✅ 数据库初始化完成")

    logger.info(f"✨ {settings.APP_NAME} v{settings.APP_VERSION} 启动成功！")
    yield

    # 关闭事件
    logger.info("🛑 正在关闭 ANOV Data Agent...")

    # 关闭数据库连接
    await close_db()
    logger.info("✅ 数据库连接已关闭")

    logger.info("👋 应用已安全关闭")


def create_app() -> FastAPI:
    """
    创建并配置 FastAPI 应用实例

    Returns:
        FastAPI: 配置完成的应用实例
    """
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description=settings.APP_DESCRIPTION,
        lifespan=lifespan,
        # Swagger UI 配置：按定义顺序排序（而不是字母顺序）
        swagger_ui_parameters={
            "operationsSorter": None,  # 不排序，按定义顺序
            "tagsSorter": None,  # 不排序标签
        },
    )

    # 注册 CORS 中间件
    cors_middleware, cors_config = get_cors_middleware_config()
    app.add_middleware(cors_middleware, **cors_config)

    # 注册日志中间件
    app.middleware("http")(logging_middleware)

    # 注册异常处理器
    register_exception_handlers(app)

    # 注册路由
    from app.modules.role.api.role_api import router as role_router
    app.include_router(role_router, prefix="/v1")

    from app.modules.dept.api.dept_api import router as dept_router
    app.include_router(dept_router, prefix="/v1")

    from app.modules.user.api.user_api import router as user_router
    app.include_router(user_router, prefix="/v1")

    from app.modules.auth.api.auth_api import router as auth_router
    app.include_router(auth_router, prefix="/v1")

    return app


# 创建应用实例
app = create_app()


@app.get("/")
async def root():
    """根路径 - 应用信息"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "message": "欢迎使用 ANOV Data Agent",
    }


@app.get("/health")
async def health():
    """健康检查端点"""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
    }


def main():
    """
    应用启动入口函数

    使用 uvicorn 启动 FastAPI 应用
    """
    import uvicorn

    logger.info("=" * 60)
    logger.info(f"🚀 {settings.APP_NAME}")
    logger.info(f"📦 版本: {settings.APP_VERSION}")
    logger.info(f"🌐 地址: http://{settings.APP_HOST}:{settings.APP_PORT}")
    logger.info("=" * 60)

    # 启动应用
    uvicorn.run(
        "app.main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.DEBUG,  # DEBUG 模式下启用热重载
        log_level=settings.LOG_LEVEL.lower(),
    )


if __name__ == "__main__":
    main()
