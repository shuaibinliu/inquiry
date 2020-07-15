from sqlalchemy import Integer, String, Text, Boolean, orm, DECIMAL
from sqlalchemy.dialects.mysql import LONGTEXT

from inquiry.extensions.base_model import Base, Column


class User(Base):
    """用户表"""
    __tablename__ = 'User'
    USid = Column(String(64), primary_key=True)
    USname = Column(String(255), nullable=False, comment='用户微信名')
    USavatar = Column(Text, url=True, comment='用户头像')
    USgender = Column(Integer, default=2, comment='性别 {0: unknown 1：male，2：female}')
    USlevel = Column(Integer, default=0, comment='vip等级')
    USopenid = Column(Text, comment='小程序 openid')
    USunionid = Column(Text, comment='统一 unionID')
    UStelphone = Column(String(16), comment="手机号")
    USinWhiteList = Column(Boolean, default=False, comment='用户是否在白名单')

    @orm.reconstructor
    def __init__(self):
        super(User, self).__init__()
        self.hide('USopenid', 'USunionid')


class Banner(Base):
    """首页banner"""
    __tablename__ = 'Banner'
    BNid = Column(String(64), primary_key=True)
    BNurl = Column(Text, url=True, comment='图片url')
    BNshow = Column(Boolean, default=False, comment='是否展示')
    contentlink = Column(LONGTEXT, comment='跳转链接')


class UserLevelSetting(Base):
    """用户等级价格系数设置"""
    __tablename__ = 'UserLevelSetting'
    ULSid = Column(String(64), primary_key=True)
    ULSlevel = Column(Integer, nullable=False, comment='用户等级')
    ULScoefficient = Column(DECIMAL(precision=28, scale=2), comment='价格系数')


class UserHistory(Base):
    """用户查询历史"""
    __tablename__ = 'UserHistory'
    UHid = Column(String(64), primary_key=True)
    USid = Column(String(64), comment='用户id')
    UHparams = Column(Text, comment='查询参数')
    PRid = Column(String(64), comment="产品ID")
    UHprice = Column(DECIMAL(precision=28, scale=2), comment='计算得出价格')


class Product(Base):
    """产品"""
    __tablename__ = 'Product'
    PRid = Column(String(64), primary_key=True)
    PRname = Column(Text, comment='产品名')
    PCid = Column(String(64), comment='分类ID')


class ProductCategory(Base):
    """产品类目"""
    __tablename__ = 'ProductCategory'
    PCid = Column(String(64), primary_key=True)
    PCname = Column(Text, comment='分类名')


class ProductParams(Base):
    """产品参数"""
    __tablename__ = 'ProductParams'
    PPid = Column(String(64), primary_key=True)
    PPname = Column(Text, comment='参数名')
    PPrequired = Column(Boolean, default=False, comment='是否必填')
    PPtype = Column(Integer, default=10, comment='10 数字 20 单选 30 立柱 ')