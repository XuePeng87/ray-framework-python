"""
系统角色与用户关联实体

数据库表：sys_role_user_relation
描述：角色与用户的多对多关系表
"""
from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class SysRoleUserRelation(Base):
    """
    系统角色与用户关联表

    字段说明：
    - id: 主键ID（自增）
    - role_code: 角色编号
    - user_code: 用户编号

    使用示例：
        # 查询用户的角色
        stmt = select(SysRoleUserRelation).where(SysRoleUserRelation.user_code == "user123")

        # 查询角色的用户
        stmt = select(SysRoleUserRelation).where(SysRoleUserRelation.role_code == "role_admin")
    """

    __tablename__ = "sys_role_user_relation"

    # 主键
    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
        comment="主键ID"
    )

    # 角色编号
    role_code: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        index=True,
        comment="角色编号"
    )

    # 用户编号
    user_code: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        index=True,
        comment="用户编号"
    )

    def __repr__(self) -> str:
        return f"<SysRoleUserRelation(id={self.id}, role_code='{self.role_code}', user_code='{self.user_code}')>"
