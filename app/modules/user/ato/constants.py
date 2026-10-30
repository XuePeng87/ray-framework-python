"""
用户模块 ATO 常量定义

集中管理重复的描述和示例字符串，避免代码重复
"""

# ============================================================================
# 通用字段描述
# ============================================================================

# 部门编号
DEPT_CODE_DESCRIPTION = "部门编号"
DEPT_CODE_EXAMPLES = ["DEPT_TECH"]

# 用户编号
USER_CODE_DESCRIPTION = "用户编号"
USER_CODE_EXAMPLES = ["USER_ADMIN"]

# 手机号码
PHONE_NUMBER_DESCRIPTION = "手机号码"
PHONE_NUMBER_EXAMPLES = ["13800138000"]

# 姓名
NAME_DESCRIPTION = "姓名"
NAME_EXAMPLES = ["张三"]

# 邮箱
EMAIL_DESCRIPTION = "邮箱"
EMAIL_EXAMPLES = ["zhangsan@example.com"]

# 头像
AVATAR_DESCRIPTION = "头像URL"
AVATAR_EXAMPLES = ["https://example.com/avatar.jpg"]

# 密码
PASSWORD_DESCRIPTION = "密码"
PASSWORD_EXAMPLES = ["******"]

# 状态字段
STATUS_DESCRIPTION = "状态：0=停用，1=启用"
STATUS_EXAMPLES = [1]

# 备注字段
REMARK_DESCRIPTION = "备注"
REMARK_EXAMPLES = ["系统管理员"]

# ============================================================================
# 查询相关描述
# ============================================================================

DEPT_CODE_QUERY_DESCRIPTION = "部门编号（精确匹配）"
PHONE_NUMBER_QUERY_DESCRIPTION = "手机号码（模糊匹配）"
NAME_QUERY_DESCRIPTION = "姓名（模糊匹配）"
EMAIL_QUERY_DESCRIPTION = "邮箱（模糊匹配）"

# ============================================================================
# 时间字段描述
# ============================================================================

CREATE_TIME_DESCRIPTION = "创建时间"
CREATE_TIME_EXAMPLES = ["2026-01-15T10:30:00"]

MODIFY_TIME_DESCRIPTION = "修改时间"
MODIFY_TIME_EXAMPLES = ["2026-01-15T10:30:00"]

# ============================================================================
# 分页字段描述
# ============================================================================

PAGE_DESCRIPTION = "页码（从1开始）"
PAGE_EXAMPLES = [1]

PAGE_SIZE_DESCRIPTION = "每页数量（1-100）"
PAGE_SIZE_EXAMPLES = [10]

TOTAL_DESCRIPTION = "总记录数"
TOTAL_EXAMPLES = [100]

TOTAL_PAGES_DESCRIPTION = "总页数"
TOTAL_PAGES_EXAMPLES = [10]

# ============================================================================
# 其他字段描述
# ============================================================================

ID_DESCRIPTION = "主键ID"
ID_EXAMPLES = [1]

ROLE_CODES_DESCRIPTION = "角色编号列表"
ROLE_CODES_EXAMPLES = [["ROLE_ADMIN", "ROLE_USER"]]

# ============================================================================
# 密码相关描述
# ============================================================================

OLD_PASSWORD_DESCRIPTION = "旧密码"
NEW_PASSWORD_DESCRIPTION = "新密码（6-128位）"
