
"""
密码安全工具类

功能：
1. 使用 Argon2id 算法对密码进行单向哈希
2. 验证用户输入的明文密码
3. 检查历史密码哈希是否需要升级
4. 验证成功后自动重新生成新参数的密码哈希

依赖：
    pip install argon2-cffi

注意：
    1. 数据库只保存 password_hash，不保存明文密码
    2. Argon2id 自动生成随机 Salt，不需要手动生成
    3. 密码哈希是 CPU 和内存密集型操作
    4. 在 FastAPI async 路由中，建议通过线程池调用
"""

from dataclasses import dataclass
from typing import Optional

from argon2 import PasswordHasher, Type
from argon2.exceptions import (
    VerifyMismatchError,
    VerificationError,
    InvalidHashError,
    HashingError,
)

from app.common.base_exception import ValidationException
from app.modules.user.exception.user_exception import UserPasswordHashException


@dataclass(frozen=True)
class PasswordVerifyResult:
    """密码验证结果"""

    # 密码是否正确
    valid: bool

    # 是否需要更新数据库中的密码哈希
    needs_rehash: bool = False

    # 新生成的密码哈希；不需要升级时为 None
    new_hash: Optional[str] = None


class Argon2PasswordUtil:
    """
    Argon2id 密码工具类。

    参数说明：
        time_cost:
            时间成本，控制内部计算轮数。

        memory_cost:
            内存成本，单位为 KiB。
            65536 KiB = 64 MiB。

        parallelism:
            Argon2 算法内部的并行度。
            不代表 FastAPI Worker 数量。

        hash_len:
            哈希结果长度，单位为字节。

        salt_len:
            随机盐长度，单位为字节。
    """

    def __init__(
        self,
        time_cost: int = 3,
        memory_cost: int = 65536,
        parallelism: int = 4,
        hash_len: int = 32,
        salt_len: int = 16,
    ):
        # 初始化 Argon2id 哈希器。
        # 参数需要结合服务器性能和认证并发量进行压测。
        self._hasher = PasswordHasher(
            time_cost=time_cost,
            memory_cost=memory_cost,
            parallelism=parallelism,
            hash_len=hash_len,
            salt_len=salt_len,
            type=Type.ID,
        )

    def hash_password(self, password: str) -> str:
        """
        将明文密码转换为 Argon2id 哈希字符串。

        参数：
            password: 用户输入的明文密码。

        返回：
            可以直接保存到数据库的完整哈希字符串。

        说明：
            每次调用都会自动生成新的随机 Salt。
            即使明文密码相同，哈希结果通常也不同。
        """
        if not isinstance(password, str):
            raise ValidationException("密码必须是字符串")

        if not password:
            raise ValidationException("密码不能为空")

        try:
            return self._hasher.hash(password)

        except HashingError as exc:
            # 不向上层暴露底层库的详细异常信息。
            raise UserPasswordHashException("密码哈希生成失败") from exc

    def verify_password(
        self,
        password: str,
        password_hash: str,
    ) -> bool:
        """
        验证明文密码与数据库中的哈希是否匹配。

        参数：
            password: 用户登录时提交的明文密码。
            password_hash: 从数据库查询得到的哈希值。

        返回：
            True：密码正确。
            False：密码错误。

        注意：
            密码不匹配是正常认证失败，不应视为系统异常。
            哈希格式损坏等问题属于内部异常。
        """
        if not isinstance(password, str):
            raise ValidationException("密码必须是字符串")

        if not isinstance(password_hash, str):
            raise ValidationException("密码哈希必须是字符串")

        try:
            return self._hasher.verify(
                password_hash,
                password,
            )

        except VerifyMismatchError:
            # 用户输入的密码不正确。
            return False

        except (VerificationError, InvalidHashError) as exc:
            # 或底层验证过程发生错误。
            raise UserPasswordHashException("密码验证失败") from exc

    def needs_rehash(self, password_hash: str) -> bool:
        """
        判断数据库中的密码哈希是否需要升级。

        使用场景：
            系统最初使用较低的计算成本，
            后续提高了 time_cost 或 memory_cost。

        返回：
            True：当前哈希参数与新配置不一致，需要升级。
            False：无需升级。

        注意：
            该方法不验证密码是否正确。
        """
        if not isinstance(password_hash, str):
            raise ValidationException("密码哈希必须是字符串")

        try:
            return self._hasher.check_needs_rehash(
                password_hash
            )

        except (InvalidHashError, ValueError) as exc:
            raise UserPasswordHashException("密码哈希格式无效") from exc

    def verify_and_rehash(
        self,
        password: str,
        password_hash: str,
    ) -> PasswordVerifyResult:
        """
        验证密码，并在必要时生成升级后的哈希。

        执行流程：
            1. 验证明文密码是否正确。
            2. 密码错误，直接返回 valid=False。
            3. 密码正确，检查哈希参数是否过时。
            4. 如果参数过时，生成新的哈希字符串。
            5. 返回结果，由业务层决定是否更新数据库。

        注意：
            本方法不会直接修改数据库。
            数据库更新应由 Service / Repository 负责。
        """

        # 第一步：验证密码
        valid = self.verify_password(
            password,
            password_hash,
        )

        if not valid:
            return PasswordVerifyResult(valid=False)

        # 第二步：判断是否需要升级哈希参数
        if not self.needs_rehash(password_hash):
            return PasswordVerifyResult(valid=True)

        # 第三步：使用当前配置重新计算密码哈希
        new_hash = self.hash_password(password)

        return PasswordVerifyResult(
            valid=True,
            needs_rehash=True,
            new_hash=new_hash,
        )


# 每个 Worker 进程内可以复用该工具实例。
# PasswordHasher 保存的是算法配置，不保存用户密码。
password_util = Argon2PasswordUtil()
