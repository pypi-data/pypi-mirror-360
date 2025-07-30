
from co6co_web_db.view_model import BaseMethodView

from sanic.response import text
from sanic import Request
from co6co_sanic_ext.utils import JSON_util
from co6co_sanic_ext.model.res.result import Result

from sqlalchemy.sql import Select,  Update
from co6co_db_ext.db_utils import db_tools
from co6co_web_db.services.jwt_service import createToken, setCurrentUser
from co6co.utils import log

from co6co_web_db.view_model import get_one
from ..model.pos.right import UserPO
from .aop.login_log import loginLog
from ..services import getSecret, generatePageToken
from ..model.enum import user_state
from datetime import datetime
from ..services.configCache import get_user_config


class login_view(BaseMethodView):
    routePath = "/login"

    @loginLog
    async def post(self, request: Request):
        """
        登录
        """
        try:
            where = UserPO()
            isLock = -1  # 1 锁定 0 解锁
            session = self.get_db_session(request)
            config = await get_user_config(request)
            failTimes = config.get("loginFail", 3)
            seconds = config.get("lockSeconds", 60)
            where.__dict__.update(request.json)
            status = [user_state.enabled.val, user_state.locked.val]
            select = Select(UserPO).filter(UserPO.userName.__eq__(where.userName), UserPO.state.in_(status))
            user: UserPO = await get_one(request, select)

            verifyCode = request.json.get("verifyCode", "")
            _, sessionDict = self.get_Session(request)
            memCode = sessionDict.pop("verifyCode")

            # // todo 为什么 应用 重启后 session 还在
            if verifyCode == "" or memCode != verifyCode:
                return JSON_util.response(Result.fail(message="验证码不能为空!"))
            if user != None:
                lockTime: datetime | None = user.lockTime
                if lockTime == None:
                    lockTime = datetime.now()
                lockTime = lockTime.timestamp()
                now = datetime.now().timestamp()
                waitingLogin: float = seconds-(now-lockTime)
                if user.state == user_state.locked.val and lockTime and waitingLogin > 0:
                    return JSON_util.response(Result.fail(message=f"账号已锁定，{round(waitingLogin, 3)}s后再试!"))

                if user.password == user.encrypt(where.password):
                    tokenData = await generatePageToken(getSecret(request), user, userOpenId=user.userGroupId)
                    # 让日志能获得用户信息
                    log.warn("用户状态", user.state)
                    if user.state == user_state.locked.val:
                        isLock = 0

                    await setCurrentUser(request, user.to_jwt_dict())
                    return JSON_util.response(Result.success(data=tokenData, message="登录成功"))
                else:
                    logingErrorCount = sessionDict.get("logingErrorCount", 0)
                    log.info("登录失败次数", logingErrorCount)
                    logingErrorCount += 1
                    sessionDict["logingErrorCount"] = logingErrorCount
                    if logingErrorCount == failTimes:
                        # 锁定
                        isLock = 1
                        sessionDict["logingErrorCount"] = 0
                        log.warn(f"用户登录失败次数达到{logingErrorCount}次，账号已锁定。")
                    return JSON_util.response(Result.fail(message="登录用户名或者密码不正确!"))
            else:
                log.warn(f"未找到用户名[{where.userName}],。")
                return JSON_util.response(Result.fail(message="登录用户名或者密码不正确!"))
        except Exception as e:
            log.err(f"登录失败:{e}", e)
            return JSON_util.response(Result.fail(message="登录失败!"))
        finally:
            if isLock != -1:
                updateSml = Update(UserPO).filter(UserPO.id.__eq__(user.id)).values(
                    {
                        UserPO.state: user_state.locked.val if isLock == 1 else user_state.enabled.val,
                        UserPO.lockTime: datetime.now() if isLock == 1 else None}
                )
                result = await db_tools.execSQL(session, updateSml)
                await session.commit()
            pass
