from sanic.response import text
from sanic import Request
from co6co_sanic_ext.utils import JSON_util
from co6co_sanic_ext.model.res.result import Result
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy.sql import Select, Delete
from co6co_db_ext.db_utils import db_tools
from co6co_web_db.model.params import associationParam


from .base_view import AuthMethodView
from co6co_web_db.view_model import get_one
from .resource import resource_baseView, FileResult
from ..model.pos.right import UserPO, RolePO, UserRolePO, AccountPO
from ..model.filters.user_filter import user_filter


class changePwd_view(AuthMethodView):
    routePath = "/changePwd"

    async def post(self, request: Request):
        """
        修改密码：
        {
            oldPassword:"",
            newPassword:"",
            remark:""
        }
        """
        data = request.json

        userId = self.getUserId(request)
        userName = self.getUserName(request)

        oldPassword = data["oldPassword"]
        password = data["newPassword"]
        remark = data["remark"]
        select = (Select(UserPO).filter(UserPO.userName == userName))

        async def edit(_, one: UserPO):
            if one != None:
                if one.password != one.encrypt(oldPassword):
                    return JSON_util.response(Result.fail(message="输入的旧密码不正确！"))
                if one.encrypt(password) == one.encrypt(oldPassword):
                    return JSON_util.response(Result.fail(message="输入的旧密码与新密码一样！"))
                one.password = one.encrypt(password)
                if remark:
                    one.remark = remark
            return JSON_util.response(Result.success())
        return await self.update_one(request, select, edit)


class user_avatar_view(resource_baseView):
    routePath = "/avatar"

    async def get(self, request: Request):
        """
        获取头像
        """
        userName = self.getUserName(request)
        select = Select(UserPO.avatar).filter(UserPO.userName == userName)
        dicts = await get_one(request, select, isPO=False)

        avatar = dicts.get("avatar")
        if avatar:
            return await self.response_local_file(request, avatar)
        else:
            svg_content = '''
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
                <!-- 头部 -->
                <circle cx="50" cy="20" r="10" fill="black"/>
                <!-- 身体 -->
                <line x1="50" y1="30" x2="50" y2="70" stroke="black" stroke-width="3"/>
                <!-- 手臂 -->
                <line x1="30" y1="40" x2="70" y2="40" stroke="black" stroke-width="3"/>
                <!-- 腿部 -->
                <line x1="50" y1="70" x2="30" y2="90" stroke="black" stroke-width="3"/>
                <line x1="50" y1="70" x2="70" y2="90" stroke="black" stroke-width="3"/>
                </svg>
            '''
            return text(svg_content, content_type='image/svg+xml')

    async def put(self, request: Request):
        """
        上传图像
        """
        userName = self.getUserName(request)
        select = Select(UserPO).filter(UserPO.userName == userName)
        result = await self.saveFile(request)
        if type(result) == FileResult:

            async def edit(_, one: UserPO):
                if one != None:
                    if result.path:
                        one.avatar = result.path
                return JSON_util.response(Result.success(data=result.path))
            return await self.update_one(request, select, edit)
        else:
            return result


class user_info_view(AuthMethodView):
    routePath = "/currentUser"

    async def get(self, request: Request):
        """
        当前用户信息  
        return {
            data:{
                avatar:""
                remark:""
                userName:""
            } 
        }
        """
        userName = self.getUserName(request)
        select = Select(UserPO.avatar, UserPO.userName, UserPO.remark).filter(UserPO.userName == userName)
        return await self.get_one(request, select, isPO=False)
