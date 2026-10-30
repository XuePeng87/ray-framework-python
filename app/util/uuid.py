"""
UUID 工具函数

提供 UUID 生成相关的工具函数
"""
import uuid


def generate_uuid(with_dash: bool = False) -> str:
    """
    生成 UUID

    Args:
        with_dash: 是否包含短横线，默认 False

    Returns:
        str: UUID 字符串

    Examples:
        >>> generate_uuid()
        'a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6'  # 32位，无-

        >>> generate_uuid(with_dash=True)
        'a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6'  # 36位，有-
    """
    u = uuid.uuid4()
    if with_dash:
        return str(u)
    else:
        return str(u).replace('-', '')


def generate_short_uuid(length: int = 8) -> str:
    """
    生成短 UUID

    Args:
        length: 长度，默认 8 位，最大 32 位

    Returns:
        str: 短 UUID 字符串

    Examples:
        >>> generate_short_uuid()
        'a1b2c3d4'  # 8位

        >>> generate_short_uuid(16)
        'a1b2c3d4e5f6g7h8'  # 16位
    """
    if length < 1 or length > 32:
        raise ValueError("长度必须在 1-32 之间")

    u = generate_uuid(with_dash=False)
    return u[:length]


def is_valid_uuid(uuid_str: str) -> bool:
    """
    验证是否是有效的 UUID

    Args:
        uuid_str: UUID 字符串

    Returns:
        bool: 是否是有效的 UUID

    Examples:
        >>> is_valid_uuid('a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6')
        True

        >>> is_valid_uuid('invalid-uuid')
        False
    """
    try:
        # 移除短横线后验证
        clean_str = uuid_str.replace('-', '')
        if len(clean_str) != 32:
            return False
        # 尝试转换为 UUID
        uuid.UUID(clean_str)
        return True
    except (ValueError, AttributeError):
        return False
