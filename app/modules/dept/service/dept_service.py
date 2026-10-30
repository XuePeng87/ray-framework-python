"""
系统部门业务逻辑层

包含部门的 CRUD 操作、树形结构构建和业务逻辑处理
使用 DTO 作为内部传输对象
"""
from typing import List, Optional
from loguru import logger

from app.modules.dept.entity.dept_entity import SysDept
from app.modules.dept.dto.dept_dto import (
    DeptCreateDTO,
    DeptUpdateDTO,
    DeptQueryDTO,
    DeptMoveDTO,
    DeptDTO,
    DeptTreeDTO,
)
from app.common.base_dto import PageDTO, build_page_dto
from app.modules.dept.repository.dept_repository import DeptRepository
from app.modules.dept.exception.dept_exception import (
    DeptNotFoundException,
    DeptNameExistsException,
    DeptHasChildrenException,
    DeptMoveToSelfException,
    DeptMoveCircularException,
)
from app.util.uuid import generate_uuid


class DeptService:
    """系统部门服务类"""

    def __init__(self, repo: DeptRepository):
        """
        初始化服务

        Args:
            repo: 部门 Repository（通过依赖注入）
        """
        self.repo = repo

    async def create(self, request: DeptCreateDTO, current_user: str = "system") -> bool:
        """
        创建部门

        Args:
            request: 创建请求 DTO
            current_user: 当前操作用户

        Returns:
            bool: 是否创建成功

        Raises:
            DeptNameExistsException: 部门名称在同层级已存在
        """
        # 检查同层级名称是否已存在
        if await self.repo.exists_by_name(request.name, request.parent_code):
            raise DeptNameExistsException(f"部门名称 '{request.name}' 在同层级已存在")

        # 转换 DTO 为字典
        dept_data = request.to_dict(exclude_none=True)

        # 生成 UUID 作为 code（去掉-）
        code = generate_uuid(with_dash=False)

        dept_data.update({
            "code": code,
            "create_user": current_user,
            "modify_user": current_user,
        })

        # 创建部门对象
        dept = SysDept(**dept_data)

        # 使用 Repository 创建
        dept = await self.repo.create(dept)

        logger.info(f"部门创建成功: {dept.code} - {dept.name}")
        return True

    async def update(self, code: str, request: DeptUpdateDTO, current_user: str = "system") -> bool:
        """
        更新部门

        Args:
            code: 部门编号
            request: 更新请求 DTO
            current_user: 当前操作用户

        Returns:
            bool: 是否更新成功

        Raises:
            DeptNotFoundException: 部门不存在
            DeptNameExistsException: 部门名称在同层级已存在
        """
        dept = await self.repo.get_by_code(code)
        if not dept:
            raise DeptNotFoundException(f"部门 {code} 不存在")

        # 获取要更新的字段
        update_data = request.to_dict_exclude_unset()

        # 如果更新了 name，检查同层级名称是否已存在
        if 'name' in update_data and update_data['name'] != dept.name:
            if await self.repo.exists_by_name(update_data['name'], dept.parent_code, exclude_id=dept.id):
                raise DeptNameExistsException(f"部门名称 '{update_data['name']}' 在同层级已存在")

        # 批量更新字段
        for key, value in update_data.items():
            setattr(dept, key, value)

        # 更新审计字段
        dept.modify_user = current_user

        # 使用 Repository 更新
        dept = await self.repo.update(dept)

        logger.info(f"部门更新成功: {code}")
        return True

    async def delete(self, code: str) -> bool:
        """
        删除部门（软删除）

        Args:
            code: 部门编号

        Returns:
            bool: 是否删除成功

        Raises:
            DeptNotFoundException: 部门不存在
            DeptHasChildrenException: 部门下有子部门，不能删除
        """
        dept = await self.repo.get_by_code(code)
        if not dept:
            raise DeptNotFoundException(f"部门 {code} 不存在")

        # 检查是否有子部门
        if await self.repo.has_children(code):
            raise DeptHasChildrenException(f"部门 '{dept.name}' 下有子部门，请先删除子部门")

        # 执行软删除
        result = await self.repo.delete_by_code(code)

        if result:
            logger.info(f"部门删除成功: {code}")

        return result

    async def get_by_code(self, code: str) -> DeptDTO:
        """
        根据编号查询部门

        Args:
            code: 部门编号

        Returns:
            DeptDTO: 部门 DTO

        Raises:
            DeptNotFoundException: 部门不存在
        """
        dept = await self.repo.get_by_code(code)
        if not dept:
            raise DeptNotFoundException(f"部门 {code} 不存在")

        return DeptDTO.from_orm(dept)

    async def list(
            self,
            parent_code: Optional[str] = None,
            name: Optional[str] = None,
            status: Optional[int] = None,
    ) -> List[DeptDTO]:
        """
        查询部门列表（不分页）

        Args:
            parent_code: 父级编号（精确匹配）
            name: 部门名称（模糊匹配）
            status: 状态

        Returns:
            List[DeptDTO]: 部门 DTO 列表
        """
        depts = await self.repo.list_by_condition(
            parent_code=parent_code,
            name=name,
            status=status,
        )

        return [DeptDTO.from_orm(dept) for dept in depts]

    async def page(self, query: DeptQueryDTO) -> PageDTO[DeptDTO]:
        """
        分页查询部门

        Args:
            query: 查询条件 DTO

        Returns:
            PageDTO[DeptDTO]: 分页 DTO
        """
        result = await self.repo.page_by_condition(
            parent_code=query.parent_code,
            name=query.name,
            status=query.status,
            page=query.page,
            page_size=query.page_size,
        )

        # 使用工具函数构建分页 DTO
        return build_page_dto(
            result,
            lambda dept: DeptDTO.from_orm(dept),
            query.page,
            query.page_size,
        )

    async def get_dept_tree(
            self,
            parent_code: str = "0",
            name: Optional[str] = None,
            status: Optional[int] = None,
    ) -> List[DeptTreeDTO]:
        """
        查询部门树形结构

        算法：
        1. 从数据库查询所有活跃部门（扁平列表）
        2. 在内存中递归构建树形结构
        3. 按 sequence 排序

        Args:
            parent_code: 从哪个节点开始（默认 '0' 表示根节点）
            name: 部门名称过滤（模糊匹配）
            status: 状态过滤

        Returns:
            List[DeptTreeDTO]: 部门树形结构列表
        """
        # 查询所有活跃部门（如果指定了过滤条件，则应用过滤）
        all_depts = await self.repo.list_by_condition(
            name=name,
            status=status,
        )

        # 转换为 DTO
        dept_dtos = [DeptDTO.from_orm(dept) for dept in all_depts]

        # 递归构建树形结构
        return self._build_tree(dept_dtos, parent_code)

    def _build_tree(self, depts: List[DeptDTO], parent_code: str = "0") -> List[DeptTreeDTO]:
        """
        递归构建部门树

        Args:
            depts: 所有部门的扁平列表
            parent_code: 父级编号

        Returns:
            List[DeptTreeDTO]: 树形结构列表
        """
        tree = []
        for dept in depts:
            if dept.parent_code == parent_code:
                # 递归查找子节点
                children = self._build_tree(depts, dept.code)

                # 构建树节点
                tree_node = DeptTreeDTO(
                    id=dept.id,
                    parent_code=dept.parent_code,
                    code=dept.code,
                    name=dept.name,
                    status=dept.status,
                    sequence=dept.sequence,
                    remark=dept.remark,
                    create_time=dept.create_time,
                    modify_time=dept.modify_time,
                    children=children,
                )
                tree.append(tree_node)

        # 按 sequence 排序
        return sorted(tree, key=lambda x: x.sequence)

    async def move(self, code: str, request: DeptMoveDTO) -> bool:
        """
        移动部门（修改父级）

        业务规则：
        1. 不能移动到自己下
        2. 不能移动到子部门下（循环引用）
        3. 新父部门必须存在

        Args:
            code: 部门编号
            request: 移动请求 DTO

        Returns:
            bool: 是否移动成功

        Raises:
            DeptNotFoundException: 部门不存在
            DeptMoveToSelfException: 不能移动到自己下
            DeptMoveCircularException: 循环引用
        """
        new_parent_code = request.new_parent_code

        # 检查部门是否存在
        dept = await self.repo.get_by_code(code)
        if not dept:
            raise DeptNotFoundException(f"部门 {code} 不存在")

        # 不能移动到自己下
        if code == new_parent_code:
            raise DeptMoveToSelfException(f"不能将部门 '{dept.name}' 移动到自己下")

        # 获取所有后代部门
        descendants = await self.repo.get_descendants(code)
        descendant_codes = [d.code for d in descendants]

        # 不能移动到子部门下（循环引用）
        if new_parent_code in descendant_codes:
            raise DeptMoveCircularException(
                f"不能将部门 '{dept.name}' 移动到其子部门下，会造成循环引用"
            )

        # 执行移动
        result = await self.repo.update_parent_code(code, new_parent_code)

        if result:
            logger.info(f"部门移动成功: {code} -> {new_parent_code}")

        return result
