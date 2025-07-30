
from sanic import Request
from sqlalchemy.sql import Select
from co6co.utils import log
from sqlalchemy.ext.asyncio import AsyncSession
from .baseCache import BaseCache
from co6co_db_ext.db_utils import DbCallable, db_tools
from ..model.pos.other import sysConfigPO
import json as sysJson
from typing import TypedDict


async def get_config(request: Request, code: str, *, useDist=False, default: any = None) -> str | dict | None:
    """
    获取配置
    """
    try:
        cache = ConfigCache(request)
        result = cache.getConfig(code)
        if result == None:
            await cache.queryConfig(code)
            result = cache.getConfig(code)
        if result and useDist:
            result = sysJson.loads(result)
            # 　如果default是dict,则合并，
            result = default.update(result) if default and isinstance(default, dict) else result
        if result == None:
            log.warn("未找到'{}'的相关配置,使用默认配置：{}".format(code, default))
            result = default
        return result
    except Exception as e:
        log.error("获取配置失败:{},使用默认配置：{}".format(e, default))
        return default


async def get_upload_path(request: Request) -> str:
    """
    获取上传路径
    数据库未配置使用 /upload
    """
    key = "SYS_CONFIG_UPLOAD_PATH"
    return await get_config(request, key, default="/upload")


async def get_terminal_access_token(request: Request) -> str:
    """
    获取终端配置
    """
    cache = ConfigCache(request)
    cache.setCache("SYS_CONFIG_TERMINAL_ACCESS_TOKEN", "123456")
    # 获取
    return cache.getConfig("SYS_CONFIG_TERMINAL_ACCESS_TOKEN")


class UserConfig(TypedDict):
    loginFail: int
    lockSeconds: int


async def get_user_config(request: Request) -> UserConfig:
    key = "SYS_USER_CONFIG"
    default = {"loginFail": 3, "lockSeconds": 5*60}
    config = await get_config(request, key, useDist=True, default=default)

    return config


class ConfigCache(BaseCache):

    def __init__(self, request: Request) -> None:
        super().__init__(request)

    @property
    def configKeyPrefix(self):
        return 'ConfigKey'

    def getKey(self, code: str):
        """
        获取Key
        """
        return "{}_{}".format(self.configKeyPrefix, code)

    async def queryConfig(self, code: str) -> str | None:
        """
        查询当前用户的所拥有的角色
        结果放置在cache中
        """
        callable = DbCallable(self.session)

        async def exe(session) -> str | None:
            select = (
                Select(sysConfigPO.name, sysConfigPO.code,
                       sysConfigPO.value, sysConfigPO.remark)
                .filter(sysConfigPO.code.__eq__(code))
            )
            data: dict | None = await db_tools.execForMappings(session, select, queryOne=True)
            result = None
            if data == None:
                log.warn("query {} config is NULL".format(code))
            else:
                result = data.get("value")
                # 配置的是否时json字符串
                if "{" in result and "}" in result:
                    try:
                        result = sysJson.loads(result)
                    except:
                        log.error("load json config error:{},check config key :{}".format(result, code))
                self.setConfig(code, result)
            return result

        return await callable(exe)

    def setConfig(self, code: str, value: str):
        if code != None:
            self.setCache(self.getKey(code), value)

    def getConfig(self, code: str) -> str | None:
        if code != None:
            return self.getCache(self.getKey(code))

    def clear(self, code: str) -> str | None:
        if code != None:
            return self.remove(self.getKey(code))
