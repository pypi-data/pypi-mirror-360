
from ..pos.right import UserPO, UserGroupPO
from sqlalchemy .orm.attributes import InstrumentedAttribute
from typing import Tuple
from co6co_db_ext.db_filter import absFilterItems
from co6co.utils import log
from sqlalchemy import func, or_, and_, Select


class user_filter(absFilterItems):
    """
        用户表过滤器
    """
    name: str = None
    userGroupId: int = None
    state: int = None

    def __init__(self, userName=None, userGroupId: int = None):
        super().__init__(UserPO)
        self.name = userName
        self.userGroupId = userGroupId
        self.listSelectFields = [UserPO.id, UserPO.userGroupId, UserPO.category, UserPO.state, UserPO.createTime, UserPO.userName]

    def filter(self) -> list:
        """
        过滤条件
        """
        filters_arr = []
        if self.checkFieldValue(self.userGroupId):
            filters_arr.append(UserPO.userGroupId.__eq__(self.userGroupId))
        if self.checkFieldValue(self.state):
            filters_arr.append(UserPO.state.__eq__(self.state))
        if self.checkFieldValue(self.name):
            filters_arr.append(UserPO.userName.like(f"%{self.name}%"))
        return filters_arr

    def create_List_select(self):
        select = (
            Select(UserPO.id, UserPO.userGroupId, UserPO.state, UserPO.category, UserPO.createTime, UserPO.userName, UserGroupPO.name.label("groupName"), UserGroupPO.id.label("groupId"))
            .join(UserGroupPO, isouter=True, onclause=UserPO.userGroupId == UserGroupPO.id)
            .filter(and_(*self.filter()))
        )
        return select

    def getDefaultOrderBy(self) -> Tuple[InstrumentedAttribute]:
        """
        默认排序
        """
        return (UserPO.createTime.desc(),)
