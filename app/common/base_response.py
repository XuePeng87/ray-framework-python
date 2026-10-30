from pydantic import BaseModel


class BaseResponse(BaseModel):
    """
    响应模型基类

    配置项：
    - from_attributes: 支持从 ORM 模型（SQLAlchemy）直接转换
    - json_schema_extra: 可添加示例等额外信息
    """
    model_config = {
        "from_attributes": True,
    }
