from sanic.request import Request


from sqlalchemy .orm.attributes import InstrumentedAttribute
from typing import Tuple
from co6co_db_ext.db_filter import absFilterItems
from co6co.utils import log
from sqlalchemy import func, or_, and_, Select
from ..pos.other import sysConfigPO


class Filter(absFilterItems):
    """
    配置 filter
    """
    name: str = None
    code: str = None
    remark: str = None

    def __init__(self):
        super().__init__(sysConfigPO)

    def filter(self) -> list:
        """
        过滤条件
        """
        filters_arr = []

        if self.checkFieldValue(self.name):
            filters_arr.append(sysConfigPO.name.like(f"%{self.name}%"))
        if self.checkFieldValue(self.code):
            filters_arr.append(sysConfigPO.code.like(f"%{self.code}%"))
        if self.checkFieldValue(self.remark):
            filters_arr.append(sysConfigPO.remark.like(f"%{self.desc}%"))

        return filters_arr

    def getDefaultOrderBy(self) -> Tuple[InstrumentedAttribute]:
        """
        默认排序
        """
        return (sysConfigPO.createTime.desc(),)
