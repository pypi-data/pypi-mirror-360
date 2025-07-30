
from sanic.response import text
from sanic import Request
from co6co_sanic_ext.utils import JSON_util
from co6co_sanic_ext.model.res.result import Result
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy.sql import Select, Delete

from co6co_db_ext.db_utils import db_tools, DbCallable
from co6co_web_db.model.params import associationParam

from datetime import datetime
from .base_view import AuthMethodView
from .aop import exist, ObjectExistRoute
from ..model.pos.right import RolePO, MenuRolePO, UserRolePO, UserGroupRolePO, menuPO
from ..model.filters.role_filter import role_filter
from .aop.api_auth import userRoleChanged


class roles_ass_exist_view(AuthMethodView):
    routePath = ObjectExistRoute

    async def get(self, request: Request, code: str, pk: int = 0):
        result = await self.exist(request, RolePO.code == code,
                                  RolePO.id != pk, column=RolePO.id)
        return exist(result, "角色编码", code)


class roles_ass_view(AuthMethodView):
    routePath = "/association/<roleId:int>"

    async def post(self, request: Request, roleId: int):
        """
        获取角色关联菜单
        """
        subSelect = Select(MenuRolePO.menuId, MenuRolePO.roleId).filter(
            MenuRolePO.roleId == roleId).subquery()
        select = (
            Select(menuPO.id, menuPO.name, menuPO.code, menuPO.parentId,
                   subSelect.c.roleId.label("associatedValue"))
            .outerjoin_from(menuPO, subSelect, onclause=subSelect.c.menuId == menuPO.id, full=False)
            .order_by(menuPO.parentId.asc())
        )
        return await self.query_tree(request, select, rootValue=0, pid_field='parentId', id_field="id", isPO=False)

    @userRoleChanged
    async def put(self, request: Request, roleId: int):
        """
        保存角色关联菜单
        """
        param = associationParam()
        param.__dict__.update(request.json)
        userId = self.getUserId(request)

        sml = (
            Delete(MenuRolePO).filter(MenuRolePO.roleId == roleId, MenuRolePO.menuId .in_(param.remove))
        )

        async def createPo(_, menuId: int):
            po = MenuRolePO()
            po.menuId = menuId
            po.roleId = roleId
            return po
        return await self.save_association(request, userId, sml, createPo)


class roles_view(AuthMethodView):
    async def get(self, request: Request):
        """
        树形选择下拉框数据
        selectTree :  el-Tree
        """
        select = (
            Select(RolePO.id, RolePO.name, RolePO.code)
            .order_by(RolePO.order.asc())
        )
        return await self.query_list(request, select,  isPO=False)

    async def post(self, request: Request):
        """
        table数据 
        """
        param = role_filter(request)
        await param.init()
        param.__dict__.update(request.json)
        return await self.query_page(request, param)

    async def put(self, request: Request):
        """
        增加
        """
        po = RolePO()
        userId = self.getUserId(request)

        async def before(po: RolePO, session: AsyncSession, request):
            exist = await db_tools.exist(session,  RolePO.code.__eq__(po.code), column=RolePO.id)
            if exist:
                return JSON_util.response(Result.fail(message=f"'{po.code}'已存在！"))
        return await self.add(request, po, userId=userId, beforeFun=before)

    def patch(self, request: Request):
        return text("I am patch method")


class role_view(AuthMethodView):
    routePath = "/<pk:int>"

    async def put(self, request: Request, pk: int):
        """
        编辑
        """
        async def before(oldPo: RolePO, po: RolePO, session: AsyncSession, request):
            exist = await db_tools.exist(session, RolePO.id != oldPo.id, RolePO.code.__eq__(po.code), column=RolePO.id)
            if exist:
                return JSON_util.response(Result.fail(message=f"'{po.code}'已存在！"))

        return await self.edit(request, pk, RolePO, userId=self.getUserId(request), fun=before)

    async def delete(self, request: Request, pk: int):
        """
        删除
        """
        async def before(po: RolePO, session: AsyncSession):
            count = await db_tools.count(session, MenuRolePO.roleId == po.id, column=RolePO.id)
            if count > 0:
                return JSON_util.response(Result.fail(message=f"该'{po.name}'角色关联了‘{count}’个菜单，不能删除！"))
            count = await db_tools.count(session, UserGroupRolePO.roleId == po.id, column=RolePO.id)
            if count > 0:
                return JSON_util.response(Result.fail(message=f"该'{po.name}'角色关联了‘{count}’个用户组，不能删除！"))
            count = await db_tools.count(session, UserRolePO.roleId == po.id, column=RolePO.id)
            if count > 0:
                return JSON_util.response(Result.fail(message=f"该'{po.name}'角色关联了‘{count}’个用户，不能删除！"))

        return await self.remove(request, pk, RolePO, beforeFun=before)
