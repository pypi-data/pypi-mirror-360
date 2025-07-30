from co6co_web_db.view_model import BaseMethodView, Request
from .aop.api_auth import authorized, ctx

from co6co_db_ext.db_operations import DbOperations
from co6co_db_ext.db_utils import db_tools
from ..services import getCurrentUserId, getCurrentUserName


class _view():
    def getUserId(self, request: Request):
        """
        获取用户ID
        """
        return getCurrentUserId(request)

    def getUserName(self, request: Request):
        """
        获取当前用户名
        """
        return getCurrentUserName(request)


class CtxMethodView(BaseMethodView, _view):
    decorators = [ctx]


class AuthMethodView(BaseMethodView, _view):
    """
    token 校验 
    api 校验
    """
    decorators = [authorized]
