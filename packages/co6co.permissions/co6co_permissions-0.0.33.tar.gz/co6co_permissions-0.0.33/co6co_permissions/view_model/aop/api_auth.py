
from functools import wraps
from sanic import Blueprint, Sanic
from sanic.response import json
from sanic.request import Request

from co6co_web_db.services.jwt_service import validToken, JWT_service
from co6co_sanic_ext.model.res.result import Result
from co6co_sanic_ext.utils import JSON_util
from sqlalchemy.sql import Select
from sqlalchemy.ext.asyncio import AsyncSession
from co6co_db_ext.db_utils import db_tools, DbCallable
from co6co.utils import log

from ...model.pos.right import UserPO, UserRolePO, UserGroupRolePO, menuPO, MenuRolePO
from ...model.enum import menu_type
from .api_check import apiPermissionCheck
from .authonCache import AuthonCacheManage
from ...services.baseCache import AccessTokenCache


async def checkApi(request: Request):
    """
    查询当前用户的对当前API是否有权限
    """
    check = apiPermissionCheck(request)
    await check.init()
    return check.check()


def authorized(f):
    """
    认证
    认证不通过 返回 403,不在执行f 函数
    """
    @wraps(f)
    async def decorated_function(request: Request, *args, **kwargs):
        secret = request.app.config.SECRET
        token = request.token
        valid = False
        # 使用 accessToken 认证
        if token and '.' not in token:
            accessToken = AccessTokenCache(request)
            valid = await accessToken.validAccessToken(token)
        elif token:
            valid = await validToken(request, secret)
        if not valid:
            return JSON_util.response(Result.fail(message="token invalid or expire"), status=403)
        # //dodo debug
        valid = await checkApi(request)
        if valid:
            # the user is authorized.
            # run the handler method and return the response
            response = await f(request, *args, **kwargs)
            return response
        else:
            # the user is not authorized.
            return JSON_util.response(Result.fail(message="not_authorized"), status=403)
    return decorated_function


def ctx(f):
    """
    设置请求上下文
    有token 将可以再上下文中获取 用户Id等信息 
    """
    @wraps(f)
    async def decorated_function(request: Request, *args, **kwargs):
        await validToken(request, request.app.config.SECRET)
        response = await f(request, *args, **kwargs)
        return response

    return decorated_function


def menuChanged(f):
    """
    设置请求上下文
    有token 将可以再上下文中获取 用户Id等信息 
    """
    @wraps(f)
    async def decorated_function(*args, **kwargs):
        for a in args:
            if isinstance(a, Request):
                cacheManage = AuthonCacheManage(a)
                cacheManage.setMenuDataInvalid()
        response = await f(*args, **kwargs)
        return response

    return decorated_function


def userRoleChanged(f):
    """
    设置请求上下文
    有token 将可以再上下文中获取 用户Id等信息 
    """
    @wraps(f)
    async def decorated_function(*args, **kwargs):
        for a in args:
            if isinstance(a, Request):
                cacheManage = AuthonCacheManage(a)
                cacheManage.setRolesInvalid()
                cacheManage.setMenuDataInvalid()
        response = await f(*args, **kwargs)
        return response

    return decorated_function
