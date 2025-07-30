
from sanic.response import text
from sanic import Request
from co6co_sanic_ext.utils import JSON_util
from co6co_sanic_ext.model.res.result import Result
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy.sql import Select, Delete

from co6co_db_ext.db_utils import db_tools, DbCallable
from co6co_web_db.model.params import associationParam

from datetime import datetime
from ..base_view import AuthMethodView
from ..aop import exist
from ...model.filters.dict_type_filter import Filter
from ...model.filters.dict_filter import DictFilter

from ...model.enum import dict_state
from ...model.pos.other import sysDictTypePO, sysDictPO


class DictTypeExistView(AuthMethodView):
    routePath = "/type/exist/<code:str>/<pk:int>"

    async def get(self, request: Request, code: str, pk: int = 0):
        result = await db_tools.exist(request.ctx.session, sysDictTypePO.code == code, sysDictTypePO.id != pk)
        return exist(result, "字典类型", code)


class DictTypeViews(AuthMethodView):
    routePath = "/type"

    async def get(self, request: Request):
        """
        字典类型 下拉 
        """
        select = (
            Select(sysDictTypePO.id, sysDictTypePO.name, sysDictTypePO.code)
            .filter(sysDictTypePO.state.__eq__(dict_state.enabled.val))
            .order_by(sysDictTypePO.order.asc())
        )
        return await self.query_list(request, select,  isPO=False)

    async def post(self, request: Request):
        """
        table数据
        """
        param = Filter()
        return await self.query_page(request, param)

    async def put(self, request: Request):
        """
        增加
        """
        po = sysDictTypePO()
        userId = self.getUserId(request)

        async def before(po: sysDictTypePO, session: AsyncSession, request):
            exist = await db_tools.exist(session,  sysDictTypePO.code.__eq__(po.code), column=sysDictTypePO.id)
            if exist:
                return JSON_util.response(Result.fail(message=f"'{po.code}'已存在！"))
        return await self.add(request, po, userId=userId, beforeFun=before)


class DictTypeView(AuthMethodView):
    routePath = "/type/<pk:int>"

    async def get(self, request: Request, pk: int):
        """
        获取字典选择
        """
        select = (
            Select(sysDictPO.id, sysDictPO.name,
                   sysDictPO.value, sysDictPO.desc)
            .filter(sysDictPO.dictTypeId.__eq__(pk), sysDictPO.state.__eq__(dict_state.enabled.val))
            .order_by(sysDictPO.order.asc())
        )
        return await self.query_list(request, select,  isPO=False)

    async def post(self, request: Request, pk: int):
        """
        获取字典,table数据
        """
        param = DictFilter(pk)
        return await self.query_page(request, param)

    async def put(self, request: Request, pk: int):
        """
        编辑
        """
        async def before(oldPo: sysDictTypePO, po: sysDictTypePO, session: AsyncSession, request):
            exist = await db_tools.exist(session, sysDictTypePO.id != oldPo.id, sysDictTypePO.code.__eq__(po.code), column=sysDictTypePO.id)
            if exist:
                return JSON_util.response(Result.fail(message=f"'{po.code}'已存在！"))

        return await self.edit(request, pk, sysDictTypePO, userId=self.getUserId(request), fun=before)

    async def delete(self, request: Request, pk: int):
        """
        删除
        """
        async def before(po: sysDictTypePO, session: AsyncSession):
            count = await db_tools.count(session, sysDictPO.dictTypeId == po.id, column=sysDictTypePO.id)
            if count > 0:
                return JSON_util.response(Result.fail(message=f"该'{po.name}'关联了字典不能删除！"))

        return await self.remove(request, pk, sysDictTypePO, beforeFun=before)
