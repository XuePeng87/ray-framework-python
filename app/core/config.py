"""
应用配置（使用 Pydantic Settings）
所有配置必须从 .env 文件或环境变量读取，不设默认值
"""
from pathlib import Path
from urllib.parse import quote_plus
from pydantic_settings import BaseSettings, SettingsConfigDict

# 获取项目根目录（.env 文件所在位置）
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_FILE = BASE_DIR / ".env"


class Settings(BaseSettings):
    """应用配置"""

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # 应用配置（必填，从 .env 读取）
    APP_NAME: str
    APP_VERSION: str
    APP_DESCRIPTION: str
    DEBUG: bool
    APP_HOST: str
    APP_PORT: int

    # 数据库配置（必填，从 .env 读取）
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str

    @property
    def DATABASE_URL(self) -> str:
        """生成数据库 URL（对密码进行 URL 编码）"""
        # 对用户名和密码进行 URL 编码，处理特殊字符
        encoded_user = quote_plus(self.DB_USER)
        encoded_password = quote_plus(self.DB_PASSWORD)
        return f"mysql+aiomysql://{encoded_user}:{encoded_password}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    # 日志配置（必填，从 .env 读取）
    LOG_LEVEL: str
    LOG_FILE: str
    LOG_ROTATION: str
    LOG_RETENTION: str
    LOG_FORMAT: str

    # JWT 配置（必填，从 .env 读取）
    JWT_SECRET_KEY: str
    JWT_EXPIRE_MINUTES: int
    JWT_ISSUER: str
    JWT_AUDIENCE: str


# 全局配置实例
settings = Settings()
