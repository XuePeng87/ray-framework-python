from contextlib import asynccontextmanager
from typing import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession


class TransactionRollbackOnlyError(RuntimeError):
    """
    事务已标记为回滚时抛出的异常
    """


class TransactionManager:
    """
    通用事务管理器

    管理共享 AsyncSession 的事务提交与回滚，供 Facade 层定义业务事务边界

    特性：
    - 所有嵌套作用域共享同一个数据库事务
    - 最外层作用域统一提交或回滚
    - 内层异常即使被捕获，也会使整个事务回滚

    使用示例：
        async with transaction_manager.transaction():
            await role_service.create(role_dto)
            await audit_service.record_role_created(...)
    """

    def __init__(self, session: AsyncSession):
        """
        初始化事务管理器

        Args:
            session: 当前请求共享的数据库会话
        """
        self._session = session
        self._depth = 0
        self._rollback_only = False
        self._rollback_cause: BaseException | None = None

    async def _begin_outermost(self) -> None:
        """
        初始化最外层事务状态，并在必要时开启数据库事务
        """
        self._rollback_only = False
        self._rollback_cause = None
        if not self._session.in_transaction():
            # 查询可能已触发 SQLAlchemy autobegin，此时复用已有事务。
            await self._session.begin().start()

    async def _finish_outermost(self) -> None:
        """
        根据回滚标记结束最外层事务

        Raises:
            TransactionRollbackOnlyError: 事务已被标记为回滚
        """
        if self._rollback_only:
            cause = self._rollback_cause
            await self._session.rollback()
            error = TransactionRollbackOnlyError(
                "嵌套事务发生异常，当前事务已回滚"
            )
            if cause is not None:
                raise error from cause
            raise error

        try:
            await self._session.commit()
        except BaseException:
            await self._session.rollback()
            raise

    @asynccontextmanager
    async def transaction(self) -> AsyncIterator[None]:
        """
        开启事务作用域，嵌套作用域共享最外层事务

        Yields:
            None: 事务作用域

        Raises:
            TransactionRollbackOnlyError: 内层异常被捕获后，最外层退出时事务已回滚
            BaseException: 事务作用域中的异常，回滚后继续向外抛出
        """
        outermost = self._depth == 0
        if outermost:
            await self._begin_outermost()

        self._depth += 1
        try:
            yield
        except BaseException as exc:
            # 异常可能被上层捕获，仍需禁止最外层提交。
            self._rollback_only = True
            if self._rollback_cause is None:
                self._rollback_cause = exc
            self._depth -= 1
            if outermost:
                await self._session.rollback()
            raise
        else:
            self._depth -= 1
            if outermost:
                await self._finish_outermost()

    def set_rollback_only(self) -> None:
        """
        标记当前事务在最外层退出时回滚

        Raises:
            RuntimeError: 当前没有活动事务
        """
        if self._depth == 0:
            raise RuntimeError("当前没有活动事务")
        self._rollback_only = True
