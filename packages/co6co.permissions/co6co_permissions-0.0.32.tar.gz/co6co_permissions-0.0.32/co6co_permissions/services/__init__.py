
from co6co_web_db.view_model import BaseMethodView

from sanic.response import text
from sanic import Request
from co6co_sanic_ext.utils import JSON_util
from co6co_sanic_ext.model.res.result import Result
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy.sql import Select, Delete
from co6co_db_ext.db_utils import db_tools
from co6co_web_db.services.jwt_service import createToken, decodeToken
from co6co.utils import log

from co6co_web_db.view_model import get_one
from ..model.pos.right import UserPO, RolePO, UserRolePO, AccountPO
from co6co.utils.tool_util import to_underscore
import uuid


def getSecret(request: Result):
    """
    获取加密密钥
    """
    return request.app.config.SECRET


def getCurrentUserId(request: Request):
    if "current_user" in request.ctx.__dict__.keys():
        return request.ctx.current_user["id"]
    return None


def getCurrentUserName(request: Request):
    if "current_user" in request.ctx.__dict__.keys():
        return request.ctx.current_user["userName"]
    return None


def getCtxData(user: UserPO):
    """
    通过user获取 dict 保存在 request.ctx.current_user 中 
    """
    return user.to_jwt_dict()


async def generatePageToken(SECRET: str, user: UserPO, expire_seconds: int = 86400, **kvarg):
    """
    生成登录token和刷新token
    """
    tokenData = await generateUserToken(SECRET, getCtxData(user), expire_seconds=expire_seconds, **kvarg)
    refreshToken = await generateRefreshToken(SECRET, user.id)
    tokenData.update({"refreshToken": refreshToken})
    return tokenData


async def queryUer(session: AsyncSession, userId: int):
    select = Select(UserPO).filter(UserPO.id.__eq__(userId))
    user: UserPO = await db_tools.execForPo(session, select, remove_db_instance_state=False)
    return user


async def generateUserToken(SECRET: str,   data: dict, userOpenId: str = None, expire_seconds: int = 86400):
    """
    SECRET:密钥 
    data:   放置token所需数据 
    userOpenId: role 放置
    expire_seconds: 过期时间,前端使用
    """
    if data != None:
        token = await createToken(SECRET, data, expire_seconds)
        return {"token": token, "expireSeconds": expire_seconds,   "role": userOpenId}
    else:
        raise Exception("data can't is NUll! ")


async def generateRefreshToken(SECRET: str, userId: any,  expire_seconds=30*86400):
    """
    创建刷新Token
    若要使已生成的 刷新 Token 失效可以 修改加密密码
    """
    token = await generateCode(SECRET, userId,  expire_seconds)
    return {"token": token, "expireSeconds": expire_seconds}


async def generateCode(SECRET: str, userId: any,  expire_seconds=180):
    """
    创建 code
    可以通过 code 得到授权token
    """
    token = await createToken(SECRET, {"userId": userId}, expire_seconds)
    return token


async def decodeCode(SECRET: str, codeToken: str):
    """
    创建 code
    可以通过 code 得到授权token
    """
    try:
        data = decodeToken(codeToken, SECRET)
        if "userId" in data:
            return data.get("userId")
        return None
    except:
        return None
