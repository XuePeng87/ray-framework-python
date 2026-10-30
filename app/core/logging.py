"""
日志配置（使用 loguru）
"""
import sys
from pathlib import Path
from loguru import logger

from app.core.config import settings, BASE_DIR


def setup_logging():
    """配置日志"""
    # 移除默认处理器
    logger.remove()

    # 添加控制台处理器
    logger.add(
        sys.stderr,
        level=settings.LOG_LEVEL,
        format=settings.LOG_FORMAT,
    )

    # 添加文件处理器（使用项目根目录的 logs 目录）
    log_file = BASE_DIR / settings.LOG_FILE
    logger.add(
        str(log_file),
        rotation=settings.LOG_ROTATION,
        retention=settings.LOG_RETENTION,
        level="INFO",
        format=settings.LOG_FORMAT,
    )


# 初始化日志
setup_logging()
