from typing import List, Annotated
from fastapi import APIRouter, Depends, status, Query
from pydantic import BaseModel, Field
from loguru import logger

from app.modules.role.ato.constants import STATUS_DESCRIPTION
from app.modules.role.ato.role_request import (
    RoleCreateRequest,
    RoleUpdateRequest,
    RoleQueryRequest,
    GrantPermissionsRequest,
)
from app.modules.role.ato.role_response import (
    RoleResponse,
)
from app.modules.role.facade.role_facade import RoleFacade
from app.ioc import get_role_facade, verify_token
from app.core.result import Result, Page

# 创建路由器（RESTful 风格：资源名用复数）
router = APIRouter(
    prefix="/roles",
    tags=["系统角色管理"],
    responses={404: {"description": "角色不存在"}},
    dependencies=[Depends(verify_token)],
)

# 定义依赖注入和查询参数的类型别名（符合 FastAPI 最佳实践）
RoleFacadeDep = Annotated[RoleFacade, Depends(get_role_facade)]
NameQuery = Annotated[str | None, Query(description="角色名称（模糊匹配）")]
StatusQuery = Annotated[int, Query(ge=0, le=1, description=STATUS_DESCRIPTION, alias="status")]
PageQuery = Annotated[int | None, Query(ge=1, description="页码（从1开始，传入则启用分页）")]
PageSizeQuery = Annotated[int | None, Query(ge=1, le=100, description="每页数量（1-100）")]


# ============================================================================
# 1. 增（Create）
# ============================================================================

@router.post(
    "",
    response_model=Result[bool],
    status_code=status.HTTP_201_CREATED,
    summary="创建角色",
    description="创建一个新的系统角色，角色编号由后端自动生成（UUID格式）",
)
async def create_role(
        request: RoleCreateRequest,
        facade: RoleFacadeDep,
):
    """
    创建系统角色

    - **name**: 角色名称
    - **status**: 状态（0=停用，1=启用）
    - **sequence**: 排序（数字越小越靠前）
    - **remark**: 备注（可选）

    注意：角色编号（code）由后端自动生成，无需传入
    """
    result = await facade.create_role(request, current_user="system")
    logger.info("API: 创建角色成功")
    return Result.ok(result, message="创建角色成功")


# ============================================================================
# 2. 改（Update）
# ============================================================================

@router.put(
    "/{code}",
    response_model=Result[bool],
    summary="更新角色",
    description="根据角色编号更新角色信息，只更新传入的字段",
)
async def update_role(
        code: str,
        request: RoleUpdateRequest,
        facade: RoleFacadeDep,
):
    """
    更新系统角色

    - **code**: 角色编号（路径参数，不可修改）
    - **name**: 角色名称（可选）
    - **status**: 状态（可选）
    - **sequence**: 排序（可选）
    - **remark**: 备注（可选）
    """
    result = await facade.update_role(code, request, current_user="system")
    logger.info(f"API: 更新角色成功 - {code}")
    return Result.ok(result, message="更新角色成功")


# ============================================================================
# 3. 删（Delete）
# ============================================================================

@router.delete(
    "/{code}",
    response_model=Result[bool],
    summary="删除角色",
    description="根据角色编号删除角色（软删除）",
)
async def delete_role(
        code: str,
        facade: RoleFacadeDep,
):
    """
    删除系统角色（软删除）

    - **code**: 角色编号
    """
    result = await facade.delete_role(code)
    logger.info(f"API: 删除角色成功 - {code}")
    return Result.ok(result, message="删除角色成功")


# ============================================================================
# 4. 查（Read/Query）
# ============================================================================

# ----------------------------------------------------------------------------
# 4.1 集合查询（Collection）
# ----------------------------------------------------------------------------

@router.get(
    "",
    response_model=Result[List[RoleResponse] | Page[RoleResponse]],
    summary="查询角色列表",
    description="查询角色列表，支持分页（传入 page 和 page_size 参数）",
)
async def get_roles(
        facade: RoleFacadeDep,
        name: NameQuery = None,
        role_status: StatusQuery = 1,
        page: PageQuery = None,
        page_size: PageSizeQuery = None,
):
    """
    查询角色列表

    - **不分页**：不传 page/page_size 参数，返回所有数据
    - **分页**：传入 page/page_size 参数，返回分页结果

    支持的查询条件：
    - **name**: 角色名称（模糊匹配）
    - **status**: 状态（精确匹配，默认1）
    """
    # 判断是否分页
    if page is not None and page_size is not None:
        # 分页查询
        query = RoleQueryRequest(name=name, status=role_status, page=page, page_size=page_size)
        result = await facade.page_roles(query)
        page_result = Page.create(
            items=result.items,
            total=result.total,
            page=result.page,
            page_size=result.page_size,
        )
        return Result.ok(page_result, message="查询角色分页成功")
    else:
        # 列表查询（不分页，直接调用 facade.list_roles）
        result = await facade.list_roles(name=name, status=role_status)
        return Result.ok(result, message="查询角色列表成功")


# ----------------------------------------------------------------------------
# 4.2 特殊集合查询（在 {code} 之前定义）
# ----------------------------------------------------------------------------

@router.get(
    "/assignable",
    response_model=Result[List[RoleResponse]],
    summary="获取可分配角色",
    description="获取所有可分配的角色列表（排除超级管理员）",
)
async def get_assignable_roles(
        facade: RoleFacadeDep,
):
    """
    获取可分配的角色列表

    返回所有启用的角色，排除超级管理员角色（ROLE_SUPER_ADMIN）
    """
    result = await facade.get_assignable_roles()
    return Result.ok(result, message="查询可分配角色成功")


# ----------------------------------------------------------------------------
# 4.3 单个资源查询（Item）
# ----------------------------------------------------------------------------

@router.get(
    "/{code}",
    response_model=Result[RoleResponse],
    summary="获取角色详情",
    description="根据角色编号查询角色详细信息",
)
async def get_role(
        code: str,
        facade: RoleFacadeDep,
):
    """
    根据编号查询角色

    - **code**: 角色编号
    """
    result = await facade.get_role_by_code(code)
    return Result.ok(result, message="查询角色详情成功")


# ============================================================================
# 5. 子资源操作（Sub-resource）
# ============================================================================

@router.post(
    "/{code}/permissions",
    response_model=Result[bool],
    summary="授权功能",
    description="为角色授权功能权限",
)
async def grant_permissions(
        code: str,
        request: GrantPermissionsRequest,
        facade: RoleFacadeDep,
):
    """
    授权功能给角色

    - **code**: 角色编号
    - **func_codes**: 功能编号列表
    """
    result = await facade.grant_permissions(code, request)
    logger.info(f"API: 角色授权功能成功 - {code}")
    return Result.ok(result, message="授权功能成功")


@router.get(
    "/{code}/permissions",
    response_model=Result[List[str]],
    summary="查询授权功能",
    description="查询角色已授权的功能列表",
)
async def get_permissions(
        code: str,
        facade: RoleFacadeDep,
):
    """
    查询角色已授权的功能

    - **code**: 角色编号
    """
    result = await facade.get_permissions(code)
    return Result.ok(result, message="查询授权功能成功")


# ============================================================================
# 6. 角色用户关联管理
# ============================================================================

class GrantUsersToRoleRequest(BaseModel):
    """给角色分配用户请求"""
    user_codes: List[str] = Field(
        ...,
        description="用户编号列表",
        examples=[["user1", "user2", "user3"]],
    )


@router.post(
    "/{code}/users",
    response_model=Result[bool],
    summary="给角色分配用户",
    description="为角色批量分配用户",
)
async def grant_users_to_role(
        code: str,
        request: GrantUsersToRoleRequest,
        facade: RoleFacadeDep,
):
    """
    给角色批量分配用户

    - **code**: 角色编号
    - **user_codes**: 用户编号列表
    """
    result = await facade.grant_users_to_role(code, request.user_codes)
    logger.info(f"API: 角色分配用户成功 - {code}")
    return Result.ok(result, message="角色分配用户成功")


@router.get(
    "/{code}/users",
    response_model=Result[List[str]],
    summary="查询角色的用户列表",
    description="查询角色已分配的用户编号列表",
)
async def get_role_users(
        code: str,
        facade: RoleFacadeDep,
):
    """
    查询角色的用户列表

    - **code**: 角色编号
    """
    result = await facade.get_role_users(code)
    return Result.ok(result, message="查询角色用户成功")
