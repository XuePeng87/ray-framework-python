"""
系统部门 API 路由（RESTful 标准风格）

提供部门的 CRUD 操作、树形查询和移动功能
使用 ATO 作为对外接口契约，通过 Facade 调用 Service
"""
from typing import List, Annotated
from fastapi import APIRouter, Depends, status, Query
from loguru import logger

from app.modules.dept.ato.dept_request import (
    DeptCreateRequest,
    DeptUpdateRequest,
    DeptQueryRequest,
    DeptMoveRequest,
)
from app.modules.dept.ato.dept_response import (
    DeptResponse,
    DeptTreeResponse,
    DeptPageResponse,
)
from app.modules.dept.facade.dept_facade import DeptFacade
from app.ioc import get_dept_facade, verify_token
from app.core.result import Result, Page

# 创建路由器（RESTful 风格：资源名用复数）
router = APIRouter(
    prefix="/depts",
    tags=["系统部门管理"],
    responses={404: {"description": "部门不存在"}},
    dependencies=[Depends(verify_token)],
)

# 定义依赖注入和查询参数的类型别名（符合 FastAPI 最佳实践）
DeptFacadeDep = Annotated[DeptFacade, Depends(get_dept_facade)]
ParentCodeQuery = Annotated[str | None, Query(description="父级编号（精确匹配）")]
NameQuery = Annotated[str | None, Query(description="部门名称（模糊匹配）")]
StatusQuery = Annotated[int, Query(ge=0, le=1, description="状态：0=停用，1=启用", alias="status")]
PageQuery = Annotated[int | None, Query(ge=1, description="页码（从1开始，传入则启用分页）")]
PageSizeQuery = Annotated[int | None, Query(ge=1, le=100, description="每页数量（1-100）")]


# ============================================================================
# 1. 增（Create）
# ============================================================================

@router.post(
    "",
    response_model=Result[bool],
    status_code=status.HTTP_201_CREATED,
    summary="创建部门",
    description="创建一个新的系统部门，部门编号由后端自动生成（UUID格式）",
)
async def create_dept(
    request: DeptCreateRequest,
    facade: DeptFacadeDep,
):
    """
    创建系统部门

    - **parent_code**: 父级编号（根节点传 '0'）
    - **name**: 部门名称
    - **status**: 状态（0=停用，1=启用）
    - **sequence**: 排序（数字越小越靠前）
    - **remark**: 备注（可选）

    注意：部门编号（code）由后端自动生成，无需传入
    """
    result = await facade.create_dept(request, current_user="system")
    logger.info("API: 创建部门成功")
    return Result.ok(result, message="创建部门成功")


# ============================================================================
# 2. 改（Update）
# ============================================================================

@router.put(
    "/{code}",
    response_model=Result[bool],
    summary="更新部门",
    description="根据部门编号更新部门信息，只更新传入的字段",
)
async def update_dept(
    code: str,
    request: DeptUpdateRequest,
    facade: DeptFacadeDep,
):
    """
    更新系统部门

    - **code**: 部门编号（路径参数，不可修改）
    - **name**: 部门名称（可选）
    - **status**: 状态（可选）
    - **sequence**: 排序（可选）
    - **remark**: 备注（可选）
    """
    result = await facade.update_dept(code, request, current_user="system")
    logger.info(f"API: 更新部门成功 - {code}")
    return Result.ok(result, message="更新部门成功")


# ============================================================================
# 3. 删（Delete）
# ============================================================================

@router.delete(
    "/{code}",
    response_model=Result[bool],
    summary="删除部门",
    description="根据部门编号删除部门（软删除），如果有子部门则拒绝删除",
)
async def delete_dept(
    code: str,
    facade: DeptFacadeDep,
):
    """
    删除系统部门（软删除）

    - **code**: 部门编号
    - 如果有子部门，会拒绝删除并返回错误提示
    """
    result = await facade.delete_dept(code)
    logger.info(f"API: 删除部门成功 - {code}")
    return Result.ok(result, message="删除部门成功")


# ============================================================================
# 4. 查（Read/Query）
# ============================================================================

# ----------------------------------------------------------------------------
# 4.1 部门树查询（特殊集合查询，必须在 {code} 之前定义）
# ----------------------------------------------------------------------------

@router.get(
    "/tree",
    response_model=Result[List[DeptTreeResponse]],
    summary="查询部门树",
    description="查询部门树形结构，支持按父级编号、名称、状态过滤",
)
async def get_dept_tree(
    facade: DeptFacadeDep,
    parent_code: ParentCodeQuery = "0",
    name: NameQuery = None,
    dept_status: StatusQuery = 1,
):
    """
    查询部门树形结构

    - **parent_code**: 从哪个节点开始（默认 '0' 表示根节点）
    - **name**: 部门名称（模糊匹配）
    - **status**: 状态（精确匹配，默认1）

    返回树形结构，包含 children 字段
    """
    result = await facade.get_dept_tree(
        parent_code=parent_code,
        name=name,
        status=dept_status,
    )
    return Result.ok(result, message="查询部门树成功")


# ----------------------------------------------------------------------------
# 4.2 集合查询（支持分页）
# ----------------------------------------------------------------------------

@router.get(
    "",
    response_model=Result[List[DeptResponse] | Page[DeptResponse]],
    summary="查询部门列表",
    description="查询部门列表，支持分页（传入 page 和 page_size 参数）",
)
async def get_depts(
    facade: DeptFacadeDep,
    parent_code: ParentCodeQuery = None,
    name: NameQuery = None,
    dept_status: StatusQuery = 1,
    page: PageQuery = None,
    page_size: PageSizeQuery = None,
):
    """
    查询部门列表

    - **不分页**：不传 page/page_size 参数，返回所有数据
    - **分页**：传入 page/page_size 参数，返回分页结果

    支持的查询条件：
    - **parent_code**: 父级编号（精确匹配）
    - **name**: 部门名称（模糊匹配）
    - **status**: 状态（精确匹配，默认1）
    """
    if page is not None and page_size is not None:
        # 分页查询
        query = DeptQueryRequest(
            parent_code=parent_code,
            name=name,
            status=dept_status,
            page=page,
            page_size=page_size,
        )
        result = await facade.page_depts(query)
        page_result = Page.create(
            items=result.items,
            total=result.total,
            page=result.page,
            page_size=result.page_size,
        )
        return Result.ok(page_result, message="查询部门分页成功")
    else:
        # 列表查询（不分页）
        result = await facade.list_depts(
            parent_code=parent_code,
            name=name,
            status=dept_status,
        )
        return Result.ok(result, message="查询部门列表成功")


# ----------------------------------------------------------------------------
# 4.3 单个资源查询
# ----------------------------------------------------------------------------

@router.get(
    "/{code}",
    response_model=Result[DeptResponse],
    summary="获取部门详情",
    description="根据部门编号查询部门详细信息",
)
async def get_dept(
    code: str,
    facade: DeptFacadeDep,
):
    """
    根据编号查询部门

    - **code**: 部门编号
    """
    result = await facade.get_dept_by_code(code)
    return Result.ok(result, message="查询部门详情成功")


# ============================================================================
# 5. 子资源操作（Sub-resource）
# ============================================================================

@router.put(
    "/{code}/move",
    response_model=Result[bool],
    summary="移动部门",
    description="修改部门的父级（移动部门到其他部门下）",
)
async def move_dept(
    code: str,
    request: DeptMoveRequest,
    facade: DeptFacadeDep,
):
    """
    移动部门（修改父级）

    - **code**: 部门编号（要移动的部门）
    - **new_parent_code**: 新的父级编号

    会自动检测循环引用并拒绝非法操作
    """
    result = await facade.move_dept(code, request, current_user="system")
    logger.info(f"API: 移动部门成功 - {code}")
    return Result.ok(result, message="移动部门成功")
