
from sanic.response import text
from sanic import Request
from co6co_sanic_ext.utils import JSON_util
from co6co_sanic_ext.model.res.result import Result
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy.sql import Select, Delete

from co6co_db_ext.db_utils import db_tools, DbCallable
from co6co_web_db.model.params import associationParam

from datetime import datetime
from ..aop import exist
from ..base_view import AuthMethodView
from ...model.filters.dict_filter import DictFilter
from ...model.pos.other import sysDictPO, sysDictTypePO
from ...model.enum import dict_state


class DictSelectView(AuthMethodView):
    routePath = "/<dictTypeCode:str>/<category:int>"

    async def get(self, request: Request, dictTypeCode: str, category: int):
        """ 
        获取字典选择
        dictTypeCode: 字典类型代码
        """
        # NameValueFlag = 0,
        # NameValue = 1,
        # NameFlag = 2,
        # All = 999,
        fields = [sysDictPO.id, sysDictPO.name, sysDictPO.flag,  sysDictPO.value]
        if category == 1:
            fields = [sysDictPO.id, sysDictPO.name,  sysDictPO.value]
        if category == 2:
            fields = [sysDictPO.id, sysDictPO.name,  sysDictPO.flag]
        if category == 999:
            fields = [sysDictPO.id, sysDictPO.name, sysDictPO.flag, sysDictPO.value, sysDictPO.desc]

        select = (
            Select(*fields)
            .join(sysDictTypePO, onclause=sysDictPO.dictTypeId == sysDictTypePO.id)
            .filter(sysDictTypePO.code.__eq__(dictTypeCode), sysDictPO.state.__eq__(dict_state.enabled.val))
            .order_by(sysDictPO.order.asc())
        )
        return await self.query_list(request, select,  isPO=False)


class Views(AuthMethodView):
    async def get(self, request: Request):
        """
        字典、字典类型状态
        枚举类型 : dict_state
        """
        return JSON_util.response(Result.success(data=dict_state.to_dict_list()))

    async def post(self, request: Request):
        """
        table数据 
        """
        param = DictFilter()
        return await self.query_page(request, param)

    async def put(self, request: Request):
        """
        增加
        """
        po = sysDictPO()
        userId = self.getUserId(request)

        async def before(po: sysDictPO, session: AsyncSession, request):
            exist = await db_tools.exist(session, sysDictPO.dictTypeId == po.dictTypeId, sysDictPO.value == po.value,   column=sysDictPO.id)
            if exist:
                return JSON_util.response(Result.fail(message=f"'{po.value}'在该字典中已存在！"))
        return await self.add(request, po, userId=userId, beforeFun=before)


class View(AuthMethodView):
    routePath = "/<pk:int>"

    async def put(self, request: Request, pk: int):
        """
        编辑
        """
        async def before(oldPo: sysDictPO, po: sysDictPO, session: AsyncSession, request):
            exist = await db_tools.exist(session, sysDictPO.dictTypeId == po.dictTypeId, sysDictPO.value == po.value, sysDictPO.id != oldPo.id, column=sysDictPO.id)
            if exist:
                return JSON_util.response(Result.fail(message=f"'{po.value}'在该字典中已存在！"))

        return await self.edit(request, pk, sysDictPO, userId=self.getUserId(request), fun=before)

    async def delete(self, request: Request, pk: int):
        """
        删除
        """
        return await self.remove(request, pk, sysDictPO)
