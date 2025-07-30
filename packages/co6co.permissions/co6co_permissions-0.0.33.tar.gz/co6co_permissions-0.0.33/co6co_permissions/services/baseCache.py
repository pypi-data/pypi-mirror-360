
from sanic import Request
from sqlalchemy.orm import joinedload
from sqlalchemy.sql import Select
from co6co.utils import log
from co6co_web_db.services.cacheManage import CacheManage
from ..model.pos.right import UserPO
from co6co_db_ext.db_utils import DbCallable, db_tools
from . import getCurrentUserId, getSecret, generateCode
from co6co_db_ext.db_session import db_service
from sqlalchemy.ext.asyncio import AsyncSession
from co6co_web_db.view_model import get_one
from ..model.enum import user_state
from co6co_web_db.services.jwt_service import setCurrentUser
from ..services import queryUerByAccessToken
from sqlalchemy.ext.asyncio import AsyncSession


class BaseCache(CacheManage):

    request = Request

    def __init__(self, request: Request) -> None:

        self.request = request
        super().__init__(request.app)
        self._session: AsyncSession = None

    @property
    def userId(self):
        """
        当前用户ID
        """
        # 微信认证中 userid可能未挂在上去
        return getCurrentUserId(self.request)

    @property
    def session(self):
        """
        当前用户ID
        """
        if self._session is None:
            self._session = self.dbservice.createAsyncSession()
        return self._session
        # return CacheManage.session(self.request)


class AccessTokenCache(BaseCache):
    """
    令牌缓存
    """

    def __init__(self, request: Request) -> None:
        super().__init__(request)

    async def validAccessToken(self, token: str) -> bool:
        """
        验证token是否有效
        :param token: 令牌
        :return: bool
        """
        result = self.getCache(token)
        if result:
            await setCurrentUser(self.request, result)
            return True

        # select = Select(UserPO).filter(UserPO.password.__eq__(token), UserPO.state.in_([user_state.enabled]))
        # user: UserPO = await db_tools.execForPo(self._session, select, remove_db_instance_state=False)
        async with self.session:  # , self.session.begin() begin会开启事务
            user: UserPO = await queryUerByAccessToken(self._session, token)
            if user == None:
                log.warn("query {} accessToken is NULL".format(token))
                return False
            else:
                data = user.to_jwt_dict()
                self.setCache(token, user.to_jwt_dict())
                await setCurrentUser(self.request, data)
                return True
