from datetime import datetime
from sqlalchemy import SmallInteger, DateTime
from sqlalchemy.orm import Mapped, mapped_column


class SoftDeleteMixin:
    """
    软删除混入类

    提供软删除功能，包含 deleted 字段和过滤方法
    所有需要软删除的模型都应该继承此类
    """

    deleted: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
        default=0,
        comment="是否删除：0=否，1=是"
    )

    @classmethod
    def is_active(cls):
        """
        返回未删除的过滤条件

        使用示例：
            stmt = select(SysRole).where(SysRole.is_active())

        Returns:
            BinaryExpression: SQLAlchemy 过滤条件
        """
        return cls.deleted == 0

    def soft_delete(self):
        """
        软删除当前对象

        使用示例：
            role.soft_delete()
        """
        self.deleted = 1  # type: ignore[assignment]

    @property
    def is_deleted(self) -> bool:
        """
        检查是否已删除

        Returns:
            bool: 是否已删除
        """
        return self.deleted == 1


class TimestampMixin:
    """
    时间戳混入类

    自动管理创建时间和修改时间
    """

    create_time: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.now,
        comment="创建时间"
    )

    modify_time: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.now,
        onupdate=datetime.now,
        comment="修改时间"
    )


class AuditMixin:
    """
    审计混入类

    记录创建人和修改人
    """

    create_user: Mapped[str | None] = mapped_column(
        nullable=True,
        comment="创建人"
    )

    modify_user: Mapped[str | None] = mapped_column(
        nullable=True,
        comment="修改人"
    )


class BaseBusinessModel(SoftDeleteMixin, TimestampMixin, AuditMixin):
    """
    基础业务模型

    组合了软删除、时间戳、审计功能的完整业务模型基类
    所有业务实体都应该继承此类
    """
    pass
