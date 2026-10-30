from sqlalchemy import BigInteger, String, Integer, SmallInteger
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.common.base_model import BaseBusinessModel


class SysDept(Base, BaseBusinessModel):
    """
    系统部门表

    字段说明：
    - id: 主键ID（自增）
    - tenant_code: 租户编号（多租户支持，默认 'DEFAULT'）
    - parent_code: 父级编号（逻辑外键，根节点为 '0'）
    - code: 部门编号（唯一索引，UUID格式）
    - name: 部门名称
    - status: 状态（0=停用，1=启用）
    - sequence: 排序
    - remark: 备注
    - deleted: 软删除标记（来自 BaseBusinessModel）
    - create_user: 创建人（来自 BaseBusinessModel）
    - create_time: 创建时间（来自 BaseBusinessModel）
    - modify_user: 修改人（来自 BaseBusinessModel）
    - modify_time: 修改时间（来自 BaseBusinessModel）
    """

    __tablename__ = "sys_dept"

    # 主键
    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
        comment="主键ID"
    )

    # 父子关系字段（树形结构核心）
    parent_code: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        index=True,
        comment="父级编号（根节点为 '0'）"
    )

    # 业务字段
    code: Mapped[str] = mapped_column(
        String(32),
        unique=True,
        nullable=False,
        index=True,
        comment="部门编号"
    )
    name: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        comment="部门名称"
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
        return f"<SysDept(id={self.id}, code='{self.code}', name='{self.name}', parent_code='{self.parent_code}')>"
