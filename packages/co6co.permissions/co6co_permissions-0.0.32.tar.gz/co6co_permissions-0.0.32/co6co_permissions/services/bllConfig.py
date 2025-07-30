
from .bll import BaseBll
from co6co_permissions.model.pos.other import sysConfigPO
from sqlalchemy import Select
from co6co_db_ext.db_utils import QueryOneCallable
import json as sysJson
from co6co.utils import log


class config_bll(BaseBll):
    async def query_config_value(self,  key: str, parseDict: bool = False) -> str | dict:
        select = (
            Select(sysConfigPO.value)
            .filter(sysConfigPO.code.__eq__(key))
        )
        call = QueryOneCallable(self.session)
        result = await call(select, isPO=False)
        if not result:
            log.warn("未找到'{}'的相关配置".format(key))
            return {} if parseDict else None
        result: str = result.get("value")
        if parseDict:
            result = sysJson.loads(result)
        return result
