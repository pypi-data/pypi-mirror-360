
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
from ..aop import exist, ObjectExistRoute
from ...model.filters.config_filter import Filter
from ...model.pos.other import sysConfigPO
from ..aop.config_aop import ConfigEntry
from ...services .configCache import ConfigCache


class ConfigView(AuthMethodView):
    """
    通过代码获取配置
    """
    routePath = "/<code:str>"

    async def get(self, request: Request, code: str):
        """ 
        获取配置
        code: 配置代码
        """
        select = (
            Select(sysConfigPO.name, sysConfigPO.code,
                   sysConfigPO.value, sysConfigPO.remark)
            .filter(sysConfigPO.code.__eq__(code))
        )
        return await self.query_mapping(request, select, oneRecord=True)


class ConfigByCacheView(AuthMethodView):
    """
    通过代码获取配置
    """
    routePath = "/Cache/<code:str>"

    async def post(self, request: Request, code: str):
        """ 
        获取配置
        code: 配置代码

        return str,配置值
        """
        cache = ConfigCache(request)
        config = cache.getConfig(code)
        if not config:
            config = await cache .queryConfig(code)
        return self.response_json(Result.success(config))


class ExistView(AuthMethodView):
    routePath = ObjectExistRoute

    async def get(self, request: Request, code: str, pk: int = 0):
        result = await self.exist(request, sysConfigPO.code == code, sysConfigPO.id != pk)
        return exist(result, "配置code", code)


@ConfigEntry
async def configValueChange(request: Request, code: str, value: str):
    return value


class Views(AuthMethodView):
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
        po = sysConfigPO()
        userId = self.getUserId(request)

        async def before(po: sysConfigPO, session: AsyncSession, request):
            exist = await db_tools.exist(session,  sysConfigPO.code.__eq__(po.code), column=sysConfigPO.id)
            if exist:
                return JSON_util.response(Result.fail(message=f"'{po.code}'已存在！"))

        async def after(po: sysConfigPO, session, request):
            await configValueChange(request, po.code, po.value)

        return await self.add(request, po, userId=userId, beforeFun=before, afterFun=after)


class View(AuthMethodView):
    routePath = "/<pk:int>"

    async def put(self, request: Request, pk: int):
        """
        编辑
        """
        async def before(oldPo: sysConfigPO, po: sysConfigPO, session: AsyncSession, request):
            exist = await db_tools.exist(session, sysConfigPO.id != oldPo.id, sysConfigPO.code.__eq__(po.code), column=sysConfigPO.id)
            if exist:
                return JSON_util.response(Result.fail(message=f"'{po.code}'已存在！"))
            await configValueChange(request, po.code, po.value)

        return await self.edit(request, pk, sysConfigPO, userId=self.getUserId(request), fun=before)

    async def delete(self, request: Request, pk: int):
        """
        删除
        """
        return await self.remove(request, pk, sysConfigPO)
