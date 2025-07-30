

from sanic.request import Request
from ...model.pos.right import UserPO
from co6co_sanic_ext.utils import JSON_util
from co6co_sanic_ext.model.res.result import Result
from ...services import getCurrentUserId


ObjectExistRoute = "/exist/<code:str>/<pk:int>"


def exist(isExist: bool = True, tableName="用户", name: str = "xxx"):
    if isExist:
        return JSON_util.response(Result.success(data=True, message=f"{tableName}'{name}'已存在。"))
    else:
        return JSON_util.response(Result.success(data=False, message=f"{tableName}'{name}'不已存在。"))
