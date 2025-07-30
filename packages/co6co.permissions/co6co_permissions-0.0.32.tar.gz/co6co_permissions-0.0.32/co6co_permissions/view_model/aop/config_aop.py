
from functools import wraps
from sanic import Blueprint, Sanic
from co6co.utils import log
from sanic.request import Request
from ...services.configCache import ConfigCache


def ConfigEntry(f):
    """
    缓存配置相关
    """
    @wraps(f)
    async def _function(*args, **kwargs):
        for arg in args:
            if isinstance(arg, Request):
                cacheManage = ConfigCache(arg)
                break
        code = kwargs.get("code", None)
        value = await f(*args, **kwargs)
        if code != None and "SYS_CONFIG" in code:
            if cacheManage != None:
                value = await f(*args, **kwargs)
                cacheManage.setConfig(code, value)
            else:
                log.warn("cacheManage 未找到 Request 参数")
        return value

    return _function
