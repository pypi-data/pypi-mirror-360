
from functools import wraps
from sanic import Blueprint, Sanic
from co6co.utils import log
from sanic.request import Request
from ...services.baseCache import AccessTokenCache
from typing import Callable


def AccessTokenChange(f: Callable[[Request, str], dict]):
    """
    缓存配置相关
    @param f:方法参数为  Request, token, 返回值:setCurrentUser需要的参数
    setCurrentUser
    """
    @wraps(f)
    async def _function(*args, **kwargs):
        for arg in args:
            if isinstance(arg, Request):
                cacheManage = AccessTokenCache(arg)
                break
        token = kwargs.get("token", None)
        value = await f(*args, **kwargs)
        if value:
            if cacheManage != None:
                value = await f(*args, **kwargs)
                cacheManage.setCache(token, value)
            else:
                log.warn("AccessTokenChange 未找到 Request 参数")
        return value

    return _function
