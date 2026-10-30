"""
系统用户业务逻辑层

包含用户的 CRUD 操作、密码管理和业务逻辑处理
使用 DTO 作为内部传输对象
"""
from typing import List, Optional
from loguru import logger

from app.modules.user.entity.user_entity import SysUser
from app.modules.user.dto.user_dto import (
    UserCreateDTO,
    UserUpdateDTO,
    UserUpdatePasswordDTO,
    UserQueryDTO,
    UserDTO,
)
from app.modules.user.repository.user_repository import UserRepository
from app.modules.user.exception.user_exception import (
    UserNotFoundException,
    UserPhoneExistsException,
    UserEmailExistsException,
    UserOldPasswordWrongException,
    UserPasswordInvalidException,
)
from app.util.password_util import password_util
from app.util.uuid import generate_uuid


def validate_password(password: str) -> bool:
    """
    验证密码规则
    
    规则：
    - 长度 6-128 位
    """
    return 6 <= len(password) <= 128


class UserService:
    """系统用户服务类"""

    def __init__(self, repo: UserRepository):
        self.repo = repo

    async def create(self, request: UserCreateDTO, current_user: str = "system") -> bool:
        """
        创建用户

        业务逻辑：
        1. 手机号唯一性检查
        2. 邮箱唯一性检查
        3. 生成 UUID 作为 code
        4. 设置默认密码（"000000"）
        5. 创建用户

        注意：会将生成的 code 设置到 request.code 中，供 Facade 层使用
        """
        # 检查手机号唯一性
        if await self.repo.exists_by_phone(request.phone_number):
            raise UserPhoneExistsException(f"手机号 '{request.phone_number}' 已存在")

        # 检查邮箱唯一性
        if await self.repo.exists_by_email(request.email):
            raise UserEmailExistsException(f"邮箱 '{request.email}' 已存在")

        # 转换 DTO 为字典
        user_data = request.to_dict(exclude_none=True)

        # 移除 role_codes 字段（不是 SysUser 的字段，由 RoleService 处理）
        user_data.pop('role_codes', None)
        user_data.pop('code', None)  # code 会在下面生成

        # 生成 UUID 作为 code
        code = generate_uuid(with_dash=False)

        # 设置默认密码（MD5 加密）
        password_hash = password_util.hash_password("000000")

        user_data.update({
            "code": code,
            "password": password_hash,
            "avatar": "",  # 默认头像
            "create_user": current_user,
            "modify_user": current_user,
        })

        # 创建用户对象
        user = SysUser(**user_data)

        # 使用 Repository 创建
        user = await self.repo.create(user)

        # 将生成的 code 设置到 request 中，供 Facade 层使用
        request.code = user.code

        logger.info(f"用户创建成功: {user.code} - {user.name}")
        return True

    async def update(self, code: str, request: UserUpdateDTO, current_user: str = "system") -> bool:
        """更新用户"""
        user = await self.repo.get_by_code(code)
        if not user:
            raise UserNotFoundException(f"用户 {code} 不存在")

        # 获取要更新的字段
        update_data = request.to_dict_exclude_unset()

        # 如果更新了 phone_number，检查唯一性
        if 'phone_number' in update_data and update_data['phone_number'] != user.phone_number:
            if await self.repo.exists_by_phone(update_data['phone_number'], exclude_id=user.id):
                raise UserPhoneExistsException(f"手机号 '{update_data['phone_number']}' 已存在")

        # 如果更新了 email，检查唯一性
        if 'email' in update_data and update_data['email'] != user.email:
            if await self.repo.exists_by_email(update_data['email'], exclude_id=user.id):
                raise UserEmailExistsException(f"邮箱 '{update_data['email']}' 已存在")

        # 批量更新字段
        for key, value in update_data.items():
            setattr(user, key, value)

        # 更新审计字段
        user.modify_user = current_user

        # 使用 Repository 更新
        user = await self.repo.update(user)

        logger.info(f"用户更新成功: {code}")
        return True

    async def delete(self, code: str) -> bool:
        """删除用户（软删除）"""
        user = await self.repo.get_by_code(code)
        if not user:
            raise UserNotFoundException(f"用户 {code} 不存在")

        result = await self.repo.delete_by_code(code)

        if result:
            logger.info(f"用户删除成功: {code}")

        return result

    async def get_by_code(self, code: str) -> UserDTO:
        """根据编号查询用户"""
        user = await self.repo.get_by_code(code)
        if not user:
            raise UserNotFoundException(f"用户 {code} 不存在")

        return UserDTO.from_orm(user)

    async def get_by_phone_number(self, phone_number: str) -> UserDTO:
        """根据手机号查询用户"""
        user = await self.repo.get_by_phone_number(phone_number)
        if not user:
            raise UserNotFoundException(f"用户 {phone_number} 不存在")

        return UserDTO.from_orm(user)

    async def list(
            self,
            dept_code: Optional[str] = None,
            name: Optional[str] = None,
            status: Optional[int] = None,
    ) -> List[UserDTO]:
        """查询用户列表（不分页）"""
        users = await self.repo.list_by_condition(
            dept_code=dept_code,
            name=name,
            status=status,
        )

        return [UserDTO.from_orm(user) for user in users]

    async def page(self, query: UserQueryDTO):
        """分页查询用户"""
        result = await self.repo.page_by_condition(
            dept_code=query.dept_code,
            name=query.name,
            status=query.status,
            page=query.page,
            page_size=query.page_size,
        )

        # 使用工具函数构建分页 DTO
        from app.common.base_dto import build_page_dto
        return build_page_dto(
            result,
            lambda user: UserDTO.from_orm(user),
            query.page,
            query.page_size,
        )

    async def update_password(self, code: str, request: UserUpdatePasswordDTO) -> bool:
        """
        修改密码
        
        业务逻辑：
        1. 验证旧密码
        2. 验证新密码规则
        3. 更新密码
        """
        user = await self.repo.get_by_code(code)
        if not user:
            raise UserNotFoundException(f"用户 {code} 不存在")

        # 验证旧密码
        old_password_hash = password_util.hash_password(request.old_password)
        if user.password != old_password_hash:
            raise UserOldPasswordWrongException("旧密码不正确")

        # 验证新密码规则
        if not validate_password(request.new_password):
            raise UserPasswordInvalidException("新密码长度必须在 6-128 位之间")

        # 加密新密码
        new_password_hash = password_util.hash_password(request.new_password)

        # 更新密码
        result = await self.repo.update_password(code, new_password_hash)

        if result:
            logger.info(f"用户密码修改成功: {code}")

        return result

    async def reset_password(self, code: str) -> bool:
        """
        重置密码
        
        业务逻辑：
        将密码重置为默认密码 "000000"
        """
        user = await self.repo.get_by_code(code)
        if not user:
            raise UserNotFoundException(f"用户 {code} 不存在")

        # 设置默认密码
        password_hash = password_util.hash_password("000000")

        # 更新密码
        result = await self.repo.update_password(code, password_hash)

        if result:
            logger.info(f"用户密码重置成功: {code}")

        return result
