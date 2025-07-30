
from sanic.response import text
from sanic import Request
from co6co_sanic_ext.utils import JSON_util
from co6co_sanic_ext.model.res.result import Result
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy.sql import Select, or_, and_, text as sqlText
from co6co_db_ext.db_utils import db_tools
from co6co_web_db.view_model import BaseMethodView, Request
from ..base_view import CtxMethodView
from ...model.enum import menu_type
from ...model.pos.right import menuPO, MenuRolePO, UserPO, UserGroupRolePO, UserRolePO
from ...model.filters.menu_filter import menu_filter
from ...services import getCurrentUserId
from co6co.utils import log


class ui_tree_view(CtxMethodView):
    routePath = "/tree/"

    async def get(self, request: Request):
        """
        树形选择下拉框数据
        selectTree :  el-Tree
        """
        queryRoleSml = sqlText(
            """
            (select  g.role_id from sys_user_group_role g
            INNER JOIN sys_user u
            on g.user_group_id=u.user_group_id
            where u.id=:userId)
            UNION
            (select ur.role_id from sys_user_role ur
            INNER JOIN sys_user u
            on ur.user_id=u.id
            where u.id=:userId)
            """
        )
        currentId = getCurrentUserId(request)
        userRolesSelect = (
            Select(UserRolePO.roleId).filter(UserRolePO.userId == UserPO.id, UserPO.id == currentId)
        )
        userGroupRolesSelect = (
            Select(UserGroupRolePO.roleId).filter(UserGroupRolePO.userGroupId == UserPO.userGroupId, UserPO.id == currentId)
        )
        # roleList=await self._query(request,queryRoleSml,isPO=False,param={"userId":1})
        roleList = await self._query(request, userRolesSelect.union(userGroupRolesSelect), isPO=False)
        #log.warn(roleList)
        roleList = [d.get("role_id") for d in roleList]
        select = (
            Select(menuPO.id, menuPO.category, menuPO.parentId, menuPO.name, menuPO.code, menuPO.icon,  menuPO.url, menuPO.component, menuPO.permissionKey, menuPO.methods)
            .join(MenuRolePO, onclause=MenuRolePO.menuId == menuPO.id)
            .filter(and_(or_(menuPO.category.__eq__(menu_type.group.val), menuPO.category.__eq__(menu_type.subView.val), menuPO.category.__eq__(menu_type.view.val), menuPO.category.__eq__(menu_type.button.val)), MenuRolePO.roleId.in_(roleList)))
            .order_by(menuPO.parentId.asc(), menuPO.order.asc())
        ).distinct(menuPO.id)

        return await self.query_tree(request, select, rootValue=0, pid_field='parentId', id_field="id", isPO=False)

    async def post(self, request: Request):
        """
        树形 table数据
        tree 形状 table
        """
        param = menu_filter()
        param.__dict__.update(request.json)
        if len(param.filter()) > 0:
            return await self.query_page(request, param)
        return await self.query_tree(request, param.create_List_select(), rootValue=0, pid_field='parentId', id_field="id")
