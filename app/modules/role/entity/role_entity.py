from sqlalchemy import BigInteger, String, Integer, SmallInteger
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.common.base_model import BaseBusinessModel


class SysRole(Base, BaseBusinessModel):
    """
    系统角色表

    字段说明：
    - id: 主键ID（自增）
    - code: 角色编号（唯一）
    - name: 角色名称
    - status: 状态（0=停用，1=启用）
    - sequence: 排序
    - remark: 备注
    - deleted: 软删除标记（来自 BaseBusinessModel）
    - create_user: 创建人（来自 BaseBusinessModel）
    - create_time: 创建时间（来自 BaseBusinessModel）
    - modify_user: 修改人（来自 BaseBusinessModel）
    - modify_time: 修改时间（来自 BaseBusinessModel）

    使用示例：
        # 查询未删除的角色
        stmt = select(SysRole).where(SysRole.is_active())

        # 软删除角色
        role.soft_delete()
    """

    __tablename__ = "sys_role"

    # 主键
    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
        comment="主键ID"
    )

    # 业务字段
    code: Mapped[str] = mapped_column(
        String(32),
        unique=True,
        nullable=False,
        index=True,
        comment="角色编号"
    )
    name: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        comment="角色名称"
    )
    status: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
        default=1,
        comment="状态：0=停用，1=启用"
    )
    sequence: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="排序"
    )
    remark: Mapped[str | None] = mapped_column(
        String(256),
        nullable=True,
        comment="备注"
    )

    def __repr__(self) -> str:
        return f"<SysRole(id={self.id}, code='{self.code}', name='{self.name}')>"
