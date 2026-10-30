"""
系统用户 API 路由（RESTful 标准风格）

提供用户的 CRUD 操作、密码管理功能
使用 ATO 作为对外接口契约，通过 Facade 调用 Service
"""
from typing import List, Annotated
from fastapi import APIRouter, Depends, status, Query
from loguru import logger

from app.modules.user.ato.user_request import (
    UserCreateRequest,
    UserUpdateRequest,
    UserUpdatePasswordRequest,
    UserQueryRequest,
)
from app.modules.user.ato.user_response import (
    UserResponse,
    UserListResponse,
)
from app.modules.user.facade.user_facade import UserFacade
from app.ioc import get_user_facade, verify_token
from app.core.result import Result, Page
from app.common.base_dto import PageDTO

# 创建路由器（RESTful 风格：资源名用复数）
router = APIRouter(
    prefix="/users",
    tags=["系统用户管理"],
    responses={404: {"description": "用户不存在"}},
    dependencies=[Depends(verify_token)],
)

# 定义依赖注入和查询参数的类型别名
UserFacadeDep = Annotated[UserFacade, Depends(get_user_facade)]
DeptCodeQuery = Annotated[str | None, Query(description="部门编号（精确匹配）")]
NameQuery = Annotated[str | None, Query(description="姓名（模糊匹配）")]
StatusQuery = Annotated[int | None, Query(ge=0, le=1, description="状态：0=停用，1=启用")]
PageQuery = Annotated[int | None, Query(ge=1, description="页码（从1开始）")]
PageSizeQuery = Annotated[int | None, Query(ge=1, le=100, description="每页数量（1-100）")]


# ============================================================================
# 1. 增（Create）
# ============================================================================

@router.post(
    "",
    response_model=Result[bool],
    status_code=status.HTTP_201_CREATED,
    summary="创建用户",
    description="创建一个新的系统用户，用户编号由后端自动生成（UUID格式），默认密码为 000000",
)
async def create_user(
    request: UserCreateRequest,
    facade: UserFacadeDep,
):
    """
    创建系统用户

    - **dept_code**: 部门编号
    - **phone_number**: 手机号码（唯一）
    - **name**: 姓名
    - **email**: 邮箱（唯一）
    - **status**: 状态（0=停用，1=启用）
    - **remark**: 备注（可选）
    - **role_codes**: 角色编号列表（可选）

    注意：
    - 用户编号（code）由后端自动生成，无需传入
    - 默认密码为 "000000"，首次登录后应修改密码
    """
    result = await facade.create_user(request, current_user="system")
    logger.info("API: 创建用户成功")
    return Result.ok(result, message="创建用户成功")


# ============================================================================
# 2. 改（Update）
# ============================================================================

@router.put(
    "/{code}",
    response_model=Result[bool],
    summary="更新用户",
    description="根据用户编号更新用户信息，只更新传入的字段",
)
async def update_user(
    code: str,
    request: UserUpdateRequest,
    facade: UserFacadeDep,
):
    """
    更新系统用户

    - **code**: 用户编号（路径参数，不可修改）
    - **dept_code**: 部门编号（可选）
    - **phone_number**: 手机号码（可选，唯一）
    - **name**: 姓名（可选）
    - **email**: 邮箱（可选，唯一）
    - **status**: 状态（可选）
    - **remark**: 备注（可选）
    - **role_codes**: 角色编号列表（可选）
    """
    result = await facade.update_user(code, request, current_user="system")
    logger.info(f"API: 更新用户成功 - {code}")
    return Result.ok(result, message="更新用户成功")


@router.put(
    "/{code}/password",
    response_model=Result[bool],
    summary="修改密码",
    description="修改用户密码，需要验证旧密码",
)
async def update_password(
    code: str,
    request: UserUpdatePasswordRequest,
    facade: UserFacadeDep,
):
    """
    修改密码

    - **code**: 用户编号
    - **old_password**: 旧密码
    - **new_password**: 新密码（6-128位）

    密码规则：
    - 长度 6-128 位
    - 建议使用字母、数字、特殊字符组合
    """
    result = await facade.update_password(code, request)
    logger.info(f"API: 修改密码成功 - {code}")
    return Result.ok(result, message="修改密码成功")


@router.post(
    "/{code}/reset-password",
    response_model=Result[bool],
    summary="重置密码",
    description="重置用户密码为默认密码（000000）",
)
async def reset_password(
    code: str,
    facade: UserFacadeDep,
):
    """
    重置密码

    - **code**: 用户编号
    - 密码将被重置为默认密码 "000000"
    """
    result = await facade.reset_password(code)
    logger.info(f"API: 重置密码成功 - {code}")
    return Result.ok(result, message="重置密码成功")


# ============================================================================
# 3. 删（Delete）
# ============================================================================

@router.delete(
    "/{code}",
    response_model=Result[bool],
    summary="删除用户",
    description="根据用户编号删除用户（软删除）",
)
async def delete_user(
    code: str,
    facade: UserFacadeDep,
):
    """
    删除系统用户（软删除）

    - **code**: 用户编号
    """
    result = await facade.delete_user(code)
    logger.info(f"API: 删除用户成功 - {code}")
    return Result.ok(result, message="删除用户成功")


# ============================================================================
# 4. 查（Read/Query）
# ============================================================================

@router.get(
    "",
    response_model=Result[List[UserResponse] | Page[UserResponse]],
    summary="查询用户列表",
    description="查询用户列表，支持分页（传入 page 和 page_size 参数）",
)
async def get_users(
    facade: UserFacadeDep,
    dept_code: DeptCodeQuery = None,
    name: NameQuery = None,
    status: StatusQuery = None,
    page: PageQuery = None,
    page_size: PageSizeQuery = None,
):
    """
    查询用户列表

    - **不分页**：不传 page/page_size 参数，返回所有数据
    - **分页**：传入 page/page_size 参数，返回分页结果

    支持的查询条件：
    - **dept_code**: 部门编号（精确匹配）
    - **name**: 姓名（模糊匹配）
    - **status**: 状态（精确匹配）
    """
    if page is not None and page_size is not None:
        # 分页查询
        query = UserQueryRequest(
            dept_code=dept_code,
            name=name,
            status=status,
            page=page,
            page_size=page_size,
        )
        page_dto = await facade.page_users(query)
        page_result = Page.create(
            items=page_dto.items,
            total=page_dto.total,
            page=page_dto.page,
            page_size=page_dto.page_size,
        )
        return Result.ok(page_result, message="查询用户分页成功")
    else:
        # 列表查询（不分页）
        result = await facade.list_users(
            dept_code=dept_code,
            name=name,
            status=status,
        )
        return Result.ok(result, message="查询用户列表成功")


@router.get(
    "/list",
    response_model=Result[List[UserListResponse]],
    summary="查询用户列表（精简版）",
    description="查询用户列表（精简版，仅包含 code 和 name），用于下拉选择等场景",
)
async def get_users_simple(
    facade: UserFacadeDep,
    dept_code: DeptCodeQuery = None,
    name: NameQuery = None,
    status: StatusQuery = None,
):
    """
    查询用户列表（精简版）

    仅返回 code 和 name 字段，用于下拉选择等场景

    支持的查询条件：
    - **dept_code**: 部门编号（精确匹配）
    - **name**: 姓名（模糊匹配）
    - **status**: 状态（精确匹配）
    """
    result = await facade.list_users_simple(
        dept_code=dept_code,
        name=name,
        status=status,
    )
    return Result.ok(result, message="查询用户列表成功")


@router.get(
    "/{code}",
    response_model=Result[UserResponse],
    summary="获取用户详情",
    description="根据用户编号查询用户详细信息",
)
async def get_user(
    code: str,
    facade: UserFacadeDep,
):
    """
    根据编号查询用户

    - **code**: 用户编号
    """
    result = await facade.get_user_by_code(code)
    return Result.ok(result, message="查询用户详情成功")
