
from sanic.response import text
from sanic import Request
from co6co_sanic_ext.utils import JSON_util
from co6co_sanic_ext.model.res.result import Result
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy.sql import Select, or_, and_, text as sqlText
from co6co_db_ext.db_utils import db_tools
from co6co_web_db.view_model import BaseMethodView, Request
from co6co_web_db.view_model import BaseMethodView
from ...model.enum import menu_type
from ...model.pos.right import menuPO, MenuRolePO, UserPO, UserGroupRolePO, UserRolePO
from ...model.filters.menu_filter import menu_filter
from ...services import getCurrentUserId
from ...services import getSecret, generatePageToken
from co6co_web_db.services import jwt_service
import uuid


class Session_View(BaseMethodView):
    routePath = "/"

    async def post(self, request: Request):
        """
        获取用户Session
        """
        session, _ = self.get_Session(request)
        # data = await jwt_service.createToken(getSecret(request), str(uuid.uuid4()),  session.expiry)
        return self.response_json(Result.success(data={"data":  str(uuid.uuid4()), "expiry": session.expiry}))
