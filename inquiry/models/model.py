from sqlalchemy import Integer, String, Text, Boolean, orm, DECIMAL
from sqlalchemy.dialects.mysql import LONGTEXT

from inquiry.extensions.base_model import Base, Column


class User(Base):
    """用户表"""
    __tablename__ = 'User'
    USid = Column(String(64), primary_key=True)
    USname = Column(String(255), nullable=False, comment='用户微信名')
    USheader = Column(Text, url=True, comment='用户头像')
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
    ADid = Column(String(64), comment='创建者ID')
    BNshow = Column(Boolean, default=False, comment='是否展示')
    BNsort = Column(Integer, comment='顺序')
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
    PCurl = Column(Text, comment='跳转URL')


class ProductParams(Base):
    """产品参数"""
    __tablename__ = 'ProductParams'
    PPid = Column(String(64), primary_key=True)
    PRid = Column(String(64), comment='产品ID')
    PPname = Column(Text, comment='参数名')
    PPrequired = Column(Boolean, default=False, comment='是否必填')
    PPtype = Column(Integer, default=10, comment='10 数字 20 单选 30 立柱 40 地铁参数')
    PPfront = Column(String(64), comment='前置参数选项')
    PPoptions = Column(Text, comment='如果是单选 或者 立柱、地铁参数的选项')
    PPremarks = Column(Text, comment='参数备注')


class Pillars(Base):
    """立柱样式"""
    __tablename__ = 'Pillars'
    PIid = Column(String(64), primary_key=True)
    PIurl = Column(Text, url=True, comment='图片URL')
    PPid = Column(String(64), comment='参数')
    PIprice = Column(DECIMAL(precision=28, scale=2), comment='单价')


class UnitCategory(Base):
    """部件分类"""
    __tablename__ = 'UnitCategory'
    UCid = Column(String(64), primary_key=True)
    UCname = Column(Text, comment='分类名')


class Unit(Base):
    """部件计算项"""
    __tablename__ = 'Unit'
    UNid = Column(String(64), primary_key=True)
    UCid = Column(String(64), comment='分类ID')
    PRid = Column(String(64), comment='商品ID')
    UCrequired = Column(Boolean, default=False, comment='是否必选 必选参数参与')
    UNunit = Column(String(64), comment='单位')
    UNunitPrice = Column(DECIMAL(precision=28, scale=2), comment='单价')
    UNname = Column(Text, comment='参数名')
    UNtype = Column(Integer, default=10, comment='10 宽 20 高 30 周长 40 面积 50 ')
    UNlimit = Column(DECIMAL(precision=28, scale=2), comment='限制条件')


class UserLoginTime(Base):
    __tablename__ = 'UserLoginTime'
    ULTid = Column(String(64), primary_key=True)
    USid = Column(String(64), nullable=False, comment='用户id')
    USTip = Column(String(64), comment='登录ip地址')
    ULtype = Column(Integer, default=1, comment='登录用户类型 1: 用户，2 管理员')
    OSVersion = Column(String(25), comment='手机系统版本')
    PhoneModel = Column(String(16), comment='手机型号')
    WechatVersion = Column(String(16), comment='微信版本')
    NetType = Column(String(10), comment='用户网络')
    UserAgent = Column(Text, comment='浏览器User-Agent')


class Admin(Base):
    """
    管理员
    """
    __tablename__ = 'Admin'
    ADid = Column(String(64), primary_key=True)
    ADnum = Column(Integer, autoincrement=True)
    ADname = Column(String(255), comment='管理员名')
    ADtelephone = Column(String(13), comment='管理员联系电话')
    ADpassword = Column(Text, nullable=False, comment='密码')
    ADfirstpwd = Column(Text, comment=' 初始密码 明文保存')
    ADfirstname = Column(Text, comment=' 初始用户名')
    ADheader = Column(Text, comment='头像', url=True)
    ADlevel = Column(Integer, default=2, comment='管理员等级，{1: 超级管理员, 2: 普通管理员}')
    ADstatus = Column(Integer, default=0, comment='账号状态，{0:正常, 1: 被冻结, 2: 已删除}')
# class WhiteList(Base):
#     """白名单"""
#     WLid = Column(String())


class AdminActions(Base):
    """
    记录管理员行为
    """
    __tablename__ = 'AdminAction'
    AAid = Column(String(64), primary_key=True)
    ADid = Column(String(64), comment='管理员id')
    AAaction = Column(Integer, default=1, comment='管理员行为, {1: 添加, 2: 删除 3: 修改}')
    AAmodel = Column(String(255), comment='操作的数据表')
    AAdetail = Column(LONGTEXT, comment='请求的data')
    AAkey = Column(String(255), comment='操作数据表的主键的值')


class AdminNotes(Base):
    """
    管理员变更记录
    """
    __tablename__ = 'AdminNotes'
    ANid = Column(String(64), primary_key=True)
    ADid = Column(String(64), nullable=False, comment='管理员id')
    ANaction = Column(Text, comment='变更动作')
    ANdoneid = Column(String(64), comment='修改人id')

