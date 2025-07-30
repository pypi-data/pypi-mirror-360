from sanic.request import Request


from sqlalchemy .orm.attributes import InstrumentedAttribute
from typing import Tuple
from co6co_db_ext.db_filter import absFilterItems
from co6co.utils import log
from sqlalchemy import func, or_, and_, Select
from ..pos.other import sysDictPO
from ...view_model.aop.authonCache import AuthonCacheManage


class DictFilter(absFilterItems):
    """
    字典 filter
    """
    name: str = None
    code: str = None
    desc: str = None
    dictTypeId: int = None

    def __init__(self, dictTypeId: int = None):
        super().__init__(sysDictPO)
        self.dictTypeId = dictTypeId

    def filter(self) -> list:
        """
        过滤条件
        """
        filters_arr = []
        if self.checkFieldValue(self.dictTypeId):
            filters_arr.append(sysDictPO.dictTypeId.__eq__(self.dictTypeId))
        if self.checkFieldValue(self.name):
            filters_arr.append(sysDictPO.name.like(f"%{self.name}%"))
        if self.checkFieldValue(self.code):
            filters_arr.append(sysDictPO.code.like(f"%{self.code}%"))
        if self.checkFieldValue(self.desc):
            filters_arr.append(sysDictPO.desc.like(f"%{self.desc}%"))

        return filters_arr

    def getDefaultOrderBy(self) -> Tuple[InstrumentedAttribute]:
        """
        默认排序
        """
        return (sysDictPO.order.asc(),)
