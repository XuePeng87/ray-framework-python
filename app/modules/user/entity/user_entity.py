from sqlalchemy import BigInteger, String, SmallInteger
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.common.base_model import BaseBusinessModel


class SysUser(Base, BaseBusinessModel):
    """
    系统用户表

    字段说明：
    - id: 主键ID（自增）
    - dept_code: 部门编号（关联 sys_dept.code）
    - code: 用户编号（唯一）
    - phone_number: 手机号码
    - name: 姓名
    - password: 密码（加密存储）
    - email: 邮箱
    - avatar: 头像URL
    - status: 状态（0=停用，1=启用）
    - remark: 备注
    - deleted: 软删除标记（来自 BaseBusinessModel）
    - create_user: 创建人（来自 BaseBusinessModel）
    - create_time: 创建时间（来自 BaseBusinessModel）
    - modify_user: 修改人（来自 BaseBusinessModel）
    - modify_time: 修改时间（来自 BaseBusinessModel）

    使用示例：
        # 查询未删除的用户
        stmt = select(SysUser).where(SysUser.is_active())

        # 软删除用户
        user.soft_delete()
    """

    __tablename__ = "sys_user"

    # 主键
    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
        comment="主键ID"
    )
    # 关联字段
    dept_code: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        index=True,
        comment="部门编号"
    )
    # 业务字段
    code: Mapped[str] = mapped_column(
        String(32),
        unique=True,
        nullable=False,
        index=True,
        comment="用户编号"
    )
    phone_number: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        comment="手机号码"
    )
    name: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="",
        comment="姓名"
    )
    password: Mapped[str] = mapped_column(
        String(256),
        nullable=False,
        comment="密码（加密存储）"
    )
    email: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        comment="邮箱"
    )
    avatar: Mapped[str] = mapped_column(
        String(256),
        nullable=False,
        default="",
        comment="头像URL"
    )
    status: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
        default=1,
        comment="状态：0=停用，1=启用"
    )
    remark: Mapped[str | None] = mapped_column(
        String(256),
        nullable=True,
        default="",
        comment="备注"
    )

    def __repr__(self) -> str:
        return f"<SysUser(id={self.id}, code='{self.code}', name='{self.name}', phone='{self.phone_number}')>"
