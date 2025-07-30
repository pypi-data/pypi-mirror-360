from sanic.request import Request


from sqlalchemy .orm.attributes import InstrumentedAttribute
from typing import Tuple
from co6co_db_ext.db_filter import absFilterItems
from co6co.utils import log
from sqlalchemy import func, or_, and_, Select
from ..pos.right import RolePO
from ...view_model.aop.authonCache import AuthonCacheManage


class role_filter(absFilterItems):
    """
    角色 filter
    """
    name: str = None
    code: str = None
    request: Request = None
    currentRoles: list = None

    def __init__(self, request: Request):
        super().__init__(RolePO)
        self.request = request

    async def init(self):
        cache = AuthonCacheManage(self.request)
        self.currentRoles = await cache.currentRoles
        # 1 超级角色
        if 1 in self.currentRoles:
            self.currentRoles = None

    def filter(self) -> list:
        """
        过滤条件
        """
        filters_arr = []

        if self.checkFieldValue(self.name):
            filters_arr.append(RolePO.name.like(f"%{self.name}%"))
        if self.checkFieldValue(self.code):
            filters_arr.append(RolePO.code.like(f"%{self.code}%"))
        if self.currentRoles != None and len(self.currentRoles) > 0:
            filters_arr.append(RolePO.id.in_(self.currentRoles))

        return filters_arr

    def getDefaultOrderBy(self) -> Tuple[InstrumentedAttribute]:
        """
        默认排序
        """
        return (RolePO.order.asc(),)
