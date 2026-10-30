"""
CORS 中间件

配置跨域资源共享（Cross-Origin Resource Sharing）
"""
from fastapi.middleware.cors import CORSMiddleware


def get_cors_middleware_config():
    """
    获取 CORS 中间件配置

    Returns:
        tuple: (中间件类, 配置参数)
    """
    # TODO: 生产环境应该从配置文件读取允许的域名列表
    allow_origins = ["*"]  # 允许所有来源（开发环境）

    return (
        CORSMiddleware,
        {
            "allow_origins": allow_origins,
            "allow_credentials": True,
            "allow_methods": ["*"],  # 允许所有 HTTP 方法
            "allow_headers": ["*"],  # 允许所有 HTTP 头
        }
    )
