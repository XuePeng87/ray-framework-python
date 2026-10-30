"""
认证模块 ATO 常量定义

集中管理重复的描述和示例字符串，避免代码重复
"""

# ============================================================================
# 登录相关描述
# ============================================================================

PHONE_NUMBER_DESCRIPTION = "手机号码"
PHONE_NUMBER_EXAMPLES = ["13800138000"]

PASSWORD_DESCRIPTION = "密码"
PASSWORD_EXAMPLES = ["000000"]

# ============================================================================
# Token 相关描述
# ============================================================================

ACCESS_TOKEN_DESCRIPTION = "访问令牌"
ACCESS_TOKEN_EXAMPLES = ["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."]

TOKEN_TYPE_DESCRIPTION = "令牌类型"
TOKEN_TYPE_EXAMPLES = ["Bearer"]

EXPIRES_IN_DESCRIPTION = "过期时间（秒）"
EXPIRES_IN_EXAMPLES = [3600]

# ============================================================================
# 用户信息描述
# ============================================================================

USER_CODE_DESCRIPTION = "用户编号"
USER_CODE_EXAMPLES = ["user123"]

USER_NAME_DESCRIPTION = "用户姓名"
USER_NAME_EXAMPLES = ["张三"]
