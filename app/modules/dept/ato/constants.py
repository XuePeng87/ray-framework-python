"""
部门模块 ATO 常量定义

集中管理重复的描述和示例字符串，避免代码重复
"""

# ============================================================================
# 通用字段描述
# ============================================================================

# 父级编号字段
PARENT_CODE_DESCRIPTION = "父级编号（根节点为 '0'）"
PARENT_CODE_EXAMPLES = ["0"]

# 编号字段
CODE_DESCRIPTION = "部门编号"
CODE_EXAMPLES = ["DEPT_TECH"]

# 名称字段
NAME_DESCRIPTION = "部门名称"
NAME_EXAMPLES = ["技术部"]

# 状态字段
STATUS_DESCRIPTION = "状态：0=停用，1=启用"
STATUS_EXAMPLES = [1]

# 排序字段
SEQUENCE_DESCRIPTION = "排序（数字越小越靠前）"
SEQUENCE_EXAMPLES = [1]

# 备注字段
REMARK_DESCRIPTION = "备注"
REMARK_EXAMPLES = ["技术研发部门"]

# 租户编号字段
TENANT_CODE_DESCRIPTION = "租户编号"
TENANT_CODE_EXAMPLES = ["DEFAULT"]

# ============================================================================
# 查询相关描述
# ============================================================================

PARENT_CODE_QUERY_DESCRIPTION = "父级编号（精确匹配）"
NAME_QUERY_DESCRIPTION = "部门名称（模糊匹配）"

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

ITEMS_DESCRIPTION = "数据列表"

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

NEW_PARENT_CODE_DESCRIPTION = "新的父级编号"
NEW_PARENT_CODE_EXAMPLES = ["0"]
