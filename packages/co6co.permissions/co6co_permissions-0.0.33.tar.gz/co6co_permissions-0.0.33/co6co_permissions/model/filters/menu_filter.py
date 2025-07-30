

from ..pos.right import menuPO
from sqlalchemy .orm.attributes import InstrumentedAttribute
from typing import Tuple
from co6co_db_ext.db_filter import absFilterItems
from co6co.utils import log
from sqlalchemy import func, or_, and_, Select


class menu_filter(absFilterItems): 
    """
    用户组 filter
    """
    pid:int=None
    name: str = None
    code: str = None 

    def __init__(self): 
        super().__init__(menuPO) 
 
    def filter(self) -> list:
        """
        过滤条件
        """
        filters_arr = []
        if self.checkFieldValue(self.pid) :
            filters_arr.append(menuPO.parentId.__eq__(self.pid))
        if self.checkFieldValue(self.name)  : 
            filters_arr.append(menuPO.name.like(f"%{self.name}%"))
        if self.checkFieldValue(self.code):
            filters_arr.append(menuPO.code.like(f"%{self.code}%")) 
        return filters_arr

   
    def getDefaultOrderBy(self) -> Tuple[InstrumentedAttribute]:
        """
        默认排序
        """
        return (menuPO.order.asc(),)
