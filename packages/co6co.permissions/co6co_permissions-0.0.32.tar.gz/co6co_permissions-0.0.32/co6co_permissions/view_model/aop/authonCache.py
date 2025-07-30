
import multiprocessing.managers
from sanic.request import Request
from sqlalchemy.sql import Select

from co6co_db_ext.db_utils import db_tools, DbCallable

from ...model.enum import menu_type
from ...model.pos.right import UserPO, UserRolePO, UserGroupRolePO, menuPO, MenuRolePO
from multiprocessing.managers import DictProxy
from co6co_web_db .services.cacheManage import CacheManage
from co6co.utils import log
from ...services import getCurrentUserId


class AuthonCacheManage(CacheManage):
    request: Request

    def __init__(self, request: Request) -> None:
        self.request = request
        super().__init__(request.app)
        pass

    @property
    def userId(self) -> None:
        """
        当前用户ID
        """
        return getCurrentUserId(self.request)

    @property
    def session(self) -> None:
        """
        当前用户ID
        """
        return CacheManage.session(self.request)

    @property
    def _currentRoleKey(self):
        return f'roleids_{self.userId}'

    @property
    def _currentRolevalieKey(self):
        return f'roleids_{self.userId}_valid'

    @property
    async def currentRoles(self) -> list[int]:
        """
        当前用户角色
        """
        if self._currentRoleKey in self.cache and self.cache[self._currentRolevalieKey]:
            if len(self.cache[self._currentRoleKey]) == 0:
                log.warn(f"請查看用戶userId:{self.userId}是否已經關聯角色！！")
            return self.cache[self._currentRoleKey]
        else:
            await self.queryUserRoles()
            return self.cache[self._currentRoleKey]

    def setRolesInvalid(self):
        """
        设置角色缓存无效
        """
        for key in self.cache.keys():
            if "roleids_" in key and '_valid' in key:
                self.cache[key] = False

    async def queryUserRoles(self):
        """
        查询当前用户的所拥有的角色
        结果放置在cache中
        """
        callable = DbCallable(self.session)

        async def exe(session):
            userRolesSelect = (
                Select(UserRolePO.roleId).filter(UserRolePO.userId == UserPO.id, UserPO.id == self.userId)
            )
            userGroupRolesSelect = (
                Select(UserGroupRolePO.roleId).filter(UserGroupRolePO.userGroupId == UserPO.userGroupId, UserPO.id == self.userId)
            )
            ruleList = await db_tools.execForMappings(session, userRolesSelect.union(userGroupRolesSelect))
            roleList = [d.get("role_id") for d in ruleList]
            self.cache[self._currentRoleKey] = roleList
            self.cache[self._currentRolevalieKey] = True
        await callable(exe)

    @property
    def _menuCacheKey(self):
        return 'api_data'

    @property
    def _menuCacheValueKey(self):
        return 'api_data_valid'

    def setMenuDataInvalid(self):
        """
        设置菜单数据缓存无效
        """
        self.cache[self._menuCacheValueKey] = False

    @property
    async def menuData(self):
        """
        所有菜单数据
        """
        if self._menuCacheKey in self.cache and self.cache[self._menuCacheValueKey]:
            return self.cache[self._menuCacheKey]
        else:
            await self.queryMenus()
            return self.cache[self._menuCacheKey]

    async def queryMenus(self):
        """
        所有菜单存在在缓存
        """
        callable = DbCallable(self.session)

        async def exe(session):
            select = (
                Select(menuPO.id,  menuPO.name,   menuPO.url, menuPO.methods, MenuRolePO.roleId)
                .join(MenuRolePO, onclause=MenuRolePO.menuId == menuPO.id)
                .filter(menuPO.category.__eq__(menu_type.api.val))
                .order_by(menuPO.parentId.asc(), menuPO.order.asc())
            )
            menuList = await db_tools.execForMappings(self.session, select)
            self.cache[self._menuCacheKey] = menuList
            self.cache[self._menuCacheValueKey] = True
        await callable(exe)
