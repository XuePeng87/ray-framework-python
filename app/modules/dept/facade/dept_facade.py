"""
部门模块 Facade 层

职责：
1. 编排 Service（可以调用多个 Service）
2. 负责 ATO ↔ DTO 的相互转换
3. 不包含核心业务逻辑

使用示例：
    facade = DeptFacade(dept_service, transaction_manager)
    response = await facade.create_dept(request_ato)
"""
from typing import List, Optional
from loguru import logger

from app.core.transaction import TransactionManager
from app.modules.dept.service.dept_service import DeptService
from app.modules.dept.dto.dept_dto import (
    DeptCreateDTO,
    DeptUpdateDTO,
    DeptQueryDTO,
    DeptMoveDTO,
    DeptDTO,
    DeptTreeDTO,
)
from app.common.base_dto import PageDTO
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


class DeptFacade:
    """
    部门模块门面类

    编排 Service，负责 ATO ↔ DTO 转换
    """

    def __init__(
        self,
        dept_service: DeptService,
        transaction_manager: TransactionManager,
    ):
        """
        初始化 Facade

        Args:
            dept_service: 部门 Service
        """
        self.dept_service = dept_service
        self.transaction_manager = transaction_manager

    # ========================================================================
    # ATO → DTO 转换方法（使用 model_dump 简化）
    # ========================================================================

    def _to_create_dto(self, ato: DeptCreateRequest) -> DeptCreateDTO:
        """将创建请求 ATO 转换为 DTO"""
        return DeptCreateDTO(**ato.model_dump())

    def _to_update_dto(self, ato: DeptUpdateRequest) -> DeptUpdateDTO:
        """将更新请求 ATO 转换为 DTO"""
        return DeptUpdateDTO(**ato.model_dump())

    def _to_query_dto(self, ato: DeptQueryRequest) -> DeptQueryDTO:
        """将查询请求 ATO 转换为 DTO"""
        return DeptQueryDTO(**ato.model_dump())

    def _to_move_dto(self, ato: DeptMoveRequest) -> DeptMoveDTO:
        """将移动请求 ATO 转换为 DTO"""
        return DeptMoveDTO(**ato.model_dump())

    # ========================================================================
    # DTO → ATO 转换方法（使用 model_validate 简化）
    # ========================================================================

    def _to_response_ato(self, dto: DeptDTO) -> DeptResponse:
        """将部门 DTO 转换为响应 ATO"""
        return DeptResponse.model_validate(dto.model_dump())

    def _to_tree_response_ato(self, dto: DeptTreeDTO) -> DeptTreeResponse:
        """将部门树 DTO 转换为树形响应 ATO"""
        return DeptTreeResponse.model_validate(dto.model_dump())

    def _to_page_response_ato(self, dto: PageDTO[DeptDTO]) -> DeptPageResponse[DeptResponse]:
        """将分页 DTO 转换为分页响应 ATO"""
        return DeptPageResponse[DeptResponse](
            items=[self._to_response_ato(item) for item in dto.items],
            total=dto.total,
            page=dto.page,
            page_size=dto.page_size,
            total_pages=dto.total_pages,
        )

    # ========================================================================
    # 业务编排方法（调用 Service）
    # ========================================================================

    async def create_dept(
        self,
        request: DeptCreateRequest,
        current_user: str = "system",
    ) -> bool:
        """
        创建部门

        编排流程：
        1. ATO → DTO 转换
        2. 调用 Service 创建
        3. 返回结果
        """
        dto = self._to_create_dto(request)
        async with self.transaction_manager.transaction():
            result = await self.dept_service.create(dto, current_user)
        logger.info("Facade: 创建部门完成")
        return result

    async def update_dept(
        self,
        code: str,
        request: DeptUpdateRequest,
        current_user: str = "system",
    ) -> bool:
        """
        更新部门

        编排流程：
        1. ATO → DTO 转换
        2. 调用 Service 更新
        3. 返回结果
        """
        dto = self._to_update_dto(request)
        async with self.transaction_manager.transaction():
            result = await self.dept_service.update(code, dto, current_user)
        logger.info(f"Facade: 更新部门完成 - {code}")
        return result

    async def delete_dept(self, code: str) -> bool:
        """
        删除部门

        编排流程：
        1. 调用 Service 删除
        2. 返回结果
        """
        async with self.transaction_manager.transaction():
            result = await self.dept_service.delete(code)
        logger.info(f"Facade: 删除部门完成 - {code}")
        return result

    async def get_dept_by_code(self, code: str) -> DeptResponse:
        """
        根据编号获取部门

        编排流程：
        1. 调用 Service 查询
        2. DTO → ATO 转换
        3. 返回 ATO
        """
        dto = await self.dept_service.get_by_code(code)
        return self._to_response_ato(dto)

    async def list_depts(
        self,
        parent_code: Optional[str] = None,
        name: Optional[str] = None,
        status: Optional[int] = None,
    ) -> List[DeptResponse]:
        """
        查询部门列表（不分页）

        编排流程：
        1. 调用 Service 查询
        2. DTO 列表 → ATO 列表转换
        3. 返回 ATO 列表
        """
        dtos = await self.dept_service.list(
            parent_code=parent_code,
            name=name,
            status=status,
        )
        return [self._to_response_ato(dto) for dto in dtos]

    async def page_depts(self, query: DeptQueryRequest) -> DeptPageResponse[DeptResponse]:
        """
        分页查询部门

        编排流程：
        1. ATO → DTO 转换
        2. 调用 Service 分页查询
        3. DTO → ATO 转换
        4. 返回分页 ATO
        """
        query_dto = self._to_query_dto(query)
        page_dto = await self.dept_service.page(query_dto)
        return self._to_page_response_ato(page_dto)

    async def get_dept_tree(
        self,
        parent_code: str = "0",
        name: Optional[str] = None,
        status: Optional[int] = None,
    ) -> List[DeptTreeResponse]:
        """
        查询部门树形结构

        编排流程：
        1. 调用 Service 获取树形结构
        2. DeptTreeDTO 列表 → DeptTreeResponse 列表转换
        3. 返回 ATO 列表
        """
        tree_dtos = await self.dept_service.get_dept_tree(
            parent_code=parent_code,
            name=name,
            status=status,
        )
        return [self._to_tree_response_ato(dto) for dto in tree_dtos]

    async def move_dept(
        self,
        code: str,
        request: DeptMoveRequest,
        current_user: str = "system",
    ) -> bool:
        """
        移动部门

        编排流程：
        1. ATO → DTO 转换
        2. 调用 Service 移动
        3. 返回结果
        """
        dto = self._to_move_dto(request)
        async with self.transaction_manager.transaction():
            result = await self.dept_service.move(code, dto, current_user)
        logger.info(f"Facade: 移动部门完成 - {code}")
        return result
