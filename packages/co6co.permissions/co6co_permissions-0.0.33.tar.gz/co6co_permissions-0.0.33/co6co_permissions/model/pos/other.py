from __future__ import annotations
from co6co_db_ext.po import BasePO, TimeStampedModelPO, UserTimeStampedModelPO, CreateUserStampedModelPO
from sqlalchemy import func, INTEGER, SmallInteger, Integer, UUID,  INTEGER, BigInteger, Column, ForeignKey, String, DateTime, CheckConstraint
from sqlalchemy.orm import relationship, declarative_base, Relationship
import co6co.utils as tool
from co6co.utils import hash
import sqlalchemy
from sqlalchemy.schema import DDL
from sqlalchemy import MetaData
import uuid


class sysConfigPO(UserTimeStampedModelPO):
    """
    系统配置
    """
    __tablename__ = "sys_config"
    id = Column("id", Integer, autoincrement=True, primary_key=True)
    name = Column("name", String(64))
    code = Column("code", String(64),  unique=True)
    sysFlag = Column("sys_flag", String(1),  comment="Y:系统,N:不是")
    dictFlag = Column("dict_flag", String(1),  comment="Y:使用字典做配置,N:手动配置")
    dictTypeId = Column("dict_type_id", Integer,  comment="字典类型ID")
    value = Column("value", String(2048),  comment="配置值")
    remark = Column("remark", String(2048), comment="备注")

    def update(self, po: sysConfigPO):
        self.name = po.name
        self.code = po.code
        self.dictFlag = po.dictFlag
        self.sysFlag = po.sysFlag
        self.value = po.value
        self.remark = po.remark


class sysDictTypePO(UserTimeStampedModelPO):
    """
    字典类型
    """
    __tablename__ = "sys_dict_type"
    id = Column("id", Integer, autoincrement=True, primary_key=True)
    name = Column("name", String(64))
    code = Column("code", String(64),  unique=True)
    desc = Column("desc", String(1024))
    sysFlag = Column("sys_flag", String(1), comment="系统标识:Y/N")
    # py 层限制 取值范围为:(0-1)
    state = Column("state", SmallInteger,  CheckConstraint(
        'state >= 0 AND state <= 1'), comment="状态:0/1->禁用/启用",)
    order = Column("order", Integer, comment="排序")

    def update(self, po: sysDictTypePO):
        self.name = po.name
        self.code = po.code
        self.desc = po.desc
        self.sysFlag = po.sysFlag
        self.state = po.state
        self.order = po.order


class sysDictPO(UserTimeStampedModelPO):
    """
    字典
    """
    __tablename__ = "sys_dict"
    id = Column("id", Integer, autoincrement=True, primary_key=True)
    dictTypeId = Column("dict_type_id", Integer, comment="字典类型ID")
    name = Column("name", String(64))
    flag = Column("flag", String(64))
    value = Column("value", String(1024))
    desc = Column("desc", String(1024))
    # py 层限制 取值范围为:(0-1)
    state = Column("state", SmallInteger,  CheckConstraint(
        'state >= 0 AND state <= 1'), comment="状态:0/1->禁用/启用",)
    order = Column("order", Integer, comment="排序")

    def update(self, po: sysDictPO):
        self.dictTypeId = po.dictTypeId
        self.name = po.name
        self.flag = po.flag
        self.value = po.value
        self.desc = po.desc

        self.state = po.state
        self.order = po.order
