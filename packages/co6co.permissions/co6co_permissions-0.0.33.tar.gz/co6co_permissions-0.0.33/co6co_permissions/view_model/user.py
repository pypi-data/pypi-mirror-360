
from sanic.response import text
from sanic import Request
from co6co_sanic_ext.utils import JSON_util
from co6co_sanic_ext.model.res.result import Result
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy.sql import Select, Delete
from co6co_db_ext.db_utils import db_tools
from co6co_web_db.model.params import associationParam
from co6co.utils import getRandomStr

from .base_view import AuthMethodView, BaseMethodView
from ..model.pos.right import UserPO, RolePO, UserRolePO, AccountPO
from ..model.enum import user_category
from ..model.filters.user_filter import user_filter
from .aop.api_auth import userRoleChanged
from ..services import generatePageToken, queryUer, getSecret, decodeCode
from .aop.user_aop import AccessTokenChange


@AccessTokenChange
def accessTokenChange(self, token: str, userPo: UserPO = None):
    return userPo.to_jwt_dict()


class user_ass_view(AuthMethodView):
    routePath = "/association/<userId:int>"

    async def post(self, request: Request, userId: int):
        """
        获取用户关联的角色
        """
        subSelect = Select(UserRolePO.roleId, UserRolePO.userId).filter(
            UserRolePO.userId == userId).subquery()
        select = (
            Select(RolePO.id, RolePO.name, RolePO.code,
                   subSelect.c.userId.label("associatedValue"))
            .outerjoin_from(RolePO, subSelect, onclause=subSelect.c.roleId == RolePO.id, full=False)
            .order_by(RolePO.id.asc())
        )
        return await self.query_list(request, select, isPO=False)

    @userRoleChanged
    async def put(self, request: Request, userId: int):
        """
        保存用户关联角色
        """
        param = associationParam()
        param.__dict__.update(request.json)
        currentUserId = self.getUserId(request)
        sml = (
            Delete(UserRolePO).filter(UserRolePO.userId ==
                                      userId, UserRolePO.roleId .in_(param.remove))
        )

        async def createPo(_, roleId: int):
            po = UserRolePO()
            po.roleId = roleId
            po.userId = userId
            return po
        return await self.save_association(request, currentUserId, sml, createPo)


class users_view(AuthMethodView):
    async def get(self, request: Request):
        """
        用户下拉框数据
        selectTree :  el-Tree
        """
        select = (
            Select(UserPO.userName.label("name"), UserPO.id)
            .order_by(UserPO.id.asc())
        )
        return await self.query_list(request, select,  isPO=False)

    async def post(self, request: Request):
        """
        树形 table数据
        tree 形状 table
        """
        param = user_filter()
        param.__dict__.update(request.json)
        return await self.query_page(request, param, isPO=False)

    async def put(self, request: Request):
        """
        增加
        """
        po = UserPO()
        userId = self.getUserId(request)

        async def before(po: UserPO, session: AsyncSession, request):
            exist = await db_tools.exist(session,  UserPO.userName.__eq__(po.userName), column=UserPO.id)
            if exist:
                return JSON_util.response(Result.fail(message=f"'{po.userName}'已存在！"))
            if po.salt == None:
                po.salt = getRandomStr(6)
            if po.category == user_category.normal.val or po.category == user_category.system.val:
                po.password = po.encrypt(po.password)
            else:
                accessTokenChange(po.password, po)
        return await self.add(request, po, userId=userId, beforeFun=before)


class user_view(AuthMethodView):
    routePath = "/<pk:int>"

    async def put(self, request: Request, pk: int):
        """
        编辑
        """
        async def before(oldPo: UserPO, po: UserPO, session: AsyncSession, request):
            exist = await db_tools.exist(session, UserPO.id != oldPo.id, UserPO.userName.__eq__(po.userName), column=UserPO.id)
            if exist:
                return JSON_util.response(Result.fail(message=f"'{po.userName}'已存在！"))

        return await self.edit(request, pk, UserPO, userId=self.getUserId(request), fun=before)

    async def delete(self, request: Request, pk: int):
        """
        删除
        """
        if pk == 1:
            return JSON_util.response(Result.fail(message="不能删除系统默认用户！"))

        async def before(po: UserPO, session: AsyncSession):
            # 用户角色关联
            count = await db_tools.count(session, UserRolePO.userId == po.id, column=UserRolePO.userId)
            if count > 0:
                return JSON_util.response(Result.fail(message=f"该'{po.userName}'用户关联有‘{count}’角色，不能删除！"))
            count = await db_tools.count(session, AccountPO.userId == po.id, column=AccountPO.uid)
            if count > 0:
                return JSON_util.response(Result.fail(message=f"该'{po.userName}'用户关联有‘{count}’账号，不能删除！"))

        return await self.remove(request, pk, UserPO, beforeFun=before)


class sys_users_view(AuthMethodView):
    routePath = "/reset"

    async def post(self, request: Request):
        """
        重置密码
        """
        data = request.json
        userName = data["userName"]
        password = data["password"]
        select = (Select(UserPO).filter(UserPO.userName == userName))
        if userName == None or password == None or len(password) < 6:
            return JSON_util.response(Result.fail(message="请检查提交的用户和密码！"))

        async def edit(_, one: UserPO):
            if one != None:
                if one.salt == None:
                    return JSON_util.response(Result.fail(message=f"用户[{userName}],通过关联创建的用户，完善信息才能重置密码"))
                if one.category == user_category.normal.val or one.category == user_category.system.val:
                    one.password = one.encrypt(password)
                else:
                    one.password = password
                    accessTokenChange(password, one)
                return JSON_util.response(Result.success())
            else:
                return JSON_util.response(Result.fail(message=f"所提供的用户名[{userName}]不存在，请刷新重试！"))

        return await self.update_one(request, select, edit)


class ticketView(BaseMethodView):
    routePath = "/ticket/<code:str>"

    async def get(self, request: Request, code: str):
        """
        通过 code 换取 token
        code 为临时 有过期时间
        """
        userId = await decodeCode(getSecret(request), code)
        if userId == None:
            return JSON_util.response(Result.fail(message="code 无效或已过期"))
        user: UserPO = await queryUer(self.get_db_session(request), userId)
        if user != None:
            token = await generatePageToken(getSecret(request), user)
            return JSON_util.response(Result.success(data=token, message="票据登录成功"))
        else:
            return JSON_util.response(Result.fail(message="未找到所属用户"))
