# -*- coding: utf-8 -*-
from .base_enum import Enum


class TestEnum(Enum):
    ok = 66, '成功'


class UserStatus(Enum):
    """user状态,供应商状态"""
    auditing = 10, '待审核'
    usual = 0, '正常'
    forbidden = -10, '禁用'
    all = None


class ProductFrom(Enum):
    """商品来源"""
    platform = (0, '平台')
    supplizer = 10, '供应商'
    # ..其他


class UserAddressFrom(Enum):
    user = 0, '用户'
    supplizer = 10, '供应商'


class ProductBrandStatus(Enum):
    """品牌状态"""
    upper = 0, '上架'
    off_shelves = 10, '下架'


class Client(Enum):
    """客户端"""
    wechat = 0, '微信'
    app = 10, 'app'


# 订单
class OrderFrom(Enum):
    """订单商品来源"""
    carts = 0, '购物车'
    product_info = 10, '商品详情'
    guess_num_award = 30, '猜数字奖品'
    fresh_man = 40, '新人商品'
    magic_box = 50, '帮拆礼盒'
    trial_commodity = 60, '试用商品'
    time_limited = 70, '限时特惠',
    integral_store = 80, '星币商城'
    guess_group = 90, '拼团竞猜'


class OrderMainStatus(Enum):
    """买家主订单状态, 40是售后状态, 未写出"""
    wait_pay = 0, '待支付'
    wait_send = 10, '待发货'
    wait_recv = 20, '待收货'
    wait_comment = 25, '待评价'
    complete_comment = 26, '已评价'
    ready = 30, '已完成'
    cancle = -40, '已取消'


class ActivityOrderNavigation(Enum):
    """活动订单导航标题"""
    fresh_man = 40, '新人首单'
    guess_num_award = 30, '每日竞猜'
    magic_box = 50, '好友魔盒'
    trial_commodity = 60, '免费试用'
    time_limited = 70, '限时特惠'
    integral_store = 80, '星币商城'
    guess_grou = 90, '拼团竞猜'


class OrderEvaluationScore(Enum):
    """订单评分"""
    fine = 5, '非常好'
    good = 4, '好'
    general = 3, '一般'
    bad = 2, '差'
    worst = 1, '非常差'


class ApplyFrom(Enum):
    """申请来源"""
    platform = 0, '平台'
    supplizer = 10, '供应商'
    user = 20, '普通用户'


class ApplyStatus(Enum):
    lose_effect = -40, '已失效'
    shelves = -30, '已下架'
    cancle = -20, '已撤销'
    reject = -10, '已拒绝'
    wait_check = 0, '审核中'
    agree = 10, '已同意'
    lose_agree = 20, '重新审核中'


class OrderRefundOrstatus(Enum):
    """订单退货状态"""
    wait_send = 0, '等待买家发货'
    wait_recv = 10, '等待卖家收货'
    ready_recv = 20, '卖家已收货'
    ready_refund = 30, '已退款'
    cancle = -10, '已取消'  # 未用
    reject = -20, '已拒绝'


class OrderRefundORAstate(Enum):
    """售后申请类型"""
    goods_money = 0, '退货退款'
    only_money = 10, '仅退款'


class ORAproductStatus(Enum):
    """退货申请时商品状态0已收货, 10 未收货"""
    already_recv = 0, '已收货'
    not_recv = 10, '未收货'


class ItemType(Enum):
    """标签类型{0: 商品, 10:资讯, 20:优惠券, 40 品牌标签}"""
    product = 0, '商品'
    news = 10, '资讯'
    coupon = 20, '优惠券'
    brand = 40, '品牌'


class ItemAuthrity(Enum):
    new_user = 10, '新用户'
    no_limit = 0, '无限制'
    admin_only = 20, '仅管理员'
    other = 30, '其他特殊'


class ApprovalType(Enum):
    """审批流状态"""
    toagent = 1
    tosell = 2
    toreturn = 3
    tocash = 4
    topublish = 5


class PermissionType(Enum):
    """审批人类型"""
    #  1: 成为代理商审批 2:商品上架审批 3:订单退换货审批, 4: 提现审批 5: 用户资讯发布审批
    toagent = 1
    toshelves = 2
    toreturn = 3
    tocash = 4
    topublish = 5


class UserIntegralType(Enum):
    all = None
    income = 1, '收入'
    expenditure = 2, '消费'


class AdminLevel(Enum):
    super_admin = 1, '超级管理员'
    common_admin = 2, '普通管理员'
    agent = 3, '供应商'
    finance = 4, '财务'


class AdminStatus(Enum):
    normal = 0, '正常'
    frozen = 1, '已冻结'
    deleted = 2, '已删除'


class AdminActionS(Enum):
    insert = 1, '添加'
    delete = 2, '删除'
    update = 3, '修改'


class UserIntegralAction(Enum):
    signin = 1, '签到'
    consumption = 2, '积分消费'
    favorite = 3, '点赞'
    commit = 4, '评论'
    transmit = 5, '转发'
    trade = 6, '购物'
    news = 7, '发布图文'


class AdminAction(Enum):
    ADname = '用户名'
    ADpassword = '密码'
    ADheader = '头像'
    ADlevel = '用户等级'
    ADstatus = '用户状态'
    ADtelphone = '手机号码'


class ActivityType(Enum):
    """活动类型"""
    fresh_man = 0, '新人'
    guess_num = 1, '猜数字'
    magic_box = 2, '魔术礼盒'
    free_use = 3, '免费试用'
    time_limited = 4, '限时活动'
    guess_group = 5, '竞猜拼团'


class UserLoginTimetype(Enum):
    user = 1, '用户'
    admin = 2, '管理员'


class WXLoginFrom(Enum):
    service = 0, '订阅号'
    subscribe = 1, '服务号'
    miniprogram = 2, '小程序'
    blog = 3, '网页blog'
    app = 4, '移动端'


class BankName(Enum):
    SRCB = 0, "深圳农村商业银行"
    BGB = 1, "广西北部湾银行"
    SHRCB = 2, "上海农村商业银行"
    BJBANK = 3, "北京银行"
    WHCCB = 4, "威海市商业银行"
    BOZK = 5, "周口银行"
    KORLABANK = 6, "库尔勒市商业银行"
    SPABANK = 7, "平安银行"
    SDEB = 8, "顺德农商银行"
    HURCB = 9, "湖北省农村信用社"
    WRCB = 10, "无锡农村商业银行"
    BOCY = 11, "朝阳银行"
    CZBANK = 12, "浙商银行"
    HDBANK = 13, "邯郸银行"
    BOC = 14, "中国银行"
    BOD = 15, "东莞银行"
    CCB = 16, "中国建设银行"
    ZYCBANK = 17, "遵义市商业银行"
    SXCB = 18, "绍兴银行"
    GZRCU = 19, "贵州省农村信用社"
    ZJKCCB = 20, "张家口市商业银行"
    BOJZ = 21, "锦州银行"
    BOP = 22, "平顶山银行"
    HKB = 23, "汉口银行"
    SPDB = 24, "上海浦东发展银行"
    NXRCU = 25, "宁夏黄河农村商业银行"
    NYNB = 26, "广东南粤银行"
    GRCB = 27, "广州农商银行"
    BOSZ = 28, "苏州银行"
    HZCB = 29, "杭州银行"
    HSBK = 30, "衡水银行"
    HBC = 31, "湖北银行"
    JXBANK = 32, "嘉兴银行"
    HRXJB = 33, "华融湘江银行"
    BODD = 34, "丹东银行"
    AYCB = 35, "安阳银行"
    EGBANK = 36, "恒丰银行"
    CDB = 37, "国家开发银行"
    TCRCB = 38, "江苏太仓农村商业银行"
    NJCB = 39, "南京银行"
    ZZBANK = 40, "郑州银行"
    DYCB = 41, "德阳商业银行"
    YBCCB = 42, "宜宾市商业银行"
    SCRCU = 43, "四川省农村信用"
    KLB = 44, "昆仑银行"
    LSBANK = 45, "莱商银行"
    YDRCB = 46, "尧都农商行"
    CCQTGB = 47, "重庆三峡银行"
    FDB = 48, "富滇银行"
    JSRCU = 49, "江苏省农村信用联合社"
    JNBANK = 50, "济宁银行"
    CMB = 51, "招商银行"
    JINCHB = 52, "晋城银行JCBANK"
    FXCB = 53, "阜新银行"
    WHRCB = 54, "武汉农村商业银行"
    HBYCBANK = 55, "湖北银行宜昌分行"
    TZCB = 56, "台州银行"
    TACCB = 57, "泰安市商业银行"
    XCYH = 58, "许昌银行"
    CEB = 59, "中国光大银行"
    NXBANK = 60, "宁夏银行"
    HSBANK = 61, "徽商银行"
    JJBANK = 62, "九江银行"
    NHQS = 63, "农信银清算中心"
    MTBANK = 64, "浙江民泰商业银行"
    LANGFB = 65, "廊坊银行"
    ASCB = 66, "鞍山银行"
    KSRB = 67, "昆山农村商业银行"
    YXCCB = 68, "玉溪市商业银行"
    DLB = 69, "大连银行"
    DRCBCL = 70, "东莞农村商业银行"
    GCB = 71, "广州银行"
    NBBANK = 72, "宁波银行"
    BOYK = 73, "营口银行"
    SXRCCU = 74, "陕西信合"
    GLBANK = 75, "桂林银行"
    BOQH = 76, "青海银行"
    CDRCB = 77, "成都农商银行"
    QDCCB = 78, "青岛银行"
    HKBEA = 79, "东亚银行"
    HBHSBANK = 80, "湖北银行黄石分行"
    WZCB = 81, "温州银行"
    TRCB = 82, "天津农商银行"
    QLBANK = 83, "齐鲁银行"
    GDRCC = 84, "广东省农村信用社联合社"
    ZJTLCB = 85, "浙江泰隆商业银行"
    GZB = 86, "赣州银行"
    GYCB = 87, "贵阳市商业银行"
    CQBANK = 88, "重庆银行"
    DAQINGB = 89, "龙江银行"
    CGNB = 90, "南充市商业银行"
    SCCB = 91, "三门峡银行"
    CSRCB = 92, "常熟农村商业银行"
    SHBANK = 93, "上海银行"
    JLBANK = 94, "吉林银行"
    CZRCB = 95, "常州农村信用联社"
    BANKWF = 96, "潍坊银行"
    ZRCBANK = 97, "张家港农村商业银行"
    FJHXBC = 98, "福建海峡银行"
    ZJNX = 99, "浙江省农村信用社联合社"
    LZYH = 100, "兰州银行"
    JSB = 101, "晋商银行"
    BOHAIB = 102, "渤海银行"
    CZCB = 103, "浙江稠州商业银行"
    YQCCB = 104, "阳泉银行"
    SJBANK = 105, "盛京银行"
    XABANK = 106, "西安银行"
    BSB = 107, "包商银行"
    JSBANK = 108, "江苏银行"
    FSCB = 109, "抚顺银行"
    HNRCU = 110, "河南省农村信用"
    COMM = 111, "交通银行"
    XTB = 112, "邢台银行"
    CITIC = 113, "中信银行"
    HXBANK = 114, "华夏银行"
    HNRCC = 115, "湖南省农村信用社"
    DYCCB = 116, "东营市商业银行"
    ORBANK = 117, "鄂尔多斯银行"
    BJRCB = 118, "北京农村商业银行"
    XYBANK = 119, "信阳银行"
    ZGCCB = 120, "自贡市商业银行"
    CDCB = 121, "成都银行"
    HANABANK = 122, "韩亚银行"
    CMBC = 123, "中国民生银行"
    LYBANK = 124, "洛阳银行"
    GDB = 125, "广东发展银行"
    ZBCB = 126, "齐商银行"
    CBKF = 127, "开封市商业银行"
    H3CB = 128, "内蒙古银行"
    CIB = 129, "兴业银行"
    CRCBANK = 130, "重庆农村商业银行"
    SZSBK = 131, "石嘴山银行"
    DZBANK = 132, "德州银行"
    SRBANK = 133, "上饶银行"
    LSCCB = 134, "乐山市商业银行"
    JXRCU = 135, "江西省农村信用"
    ICBC = 136, "中国工商银行"
    JZBANK = 137, "晋中市商业银行"
    HZCCB = 138, "湖州市商业银行"
    NHB = 139, "南海农村信用联社"
    XXBANK = 140, "新乡银行"
    JRCB = 141, "江苏江阴农村商业银行"
    YNRCC = 142, "云南省农村信用社"
    ABC = 143, "中国农业银行"
    GXRCU = 144, "广西省农村信用"
    PSBC = 145, "中国邮政储蓄银行"
    BZMD = 146, "驻马店银行"
    ARCU = 147, "安徽省农村信用社"
    GSRCU = 148, "甘肃省农村信用"
    LYCB = 149, "辽阳市商业银行"
    JLRCU = 150, "吉林农信"
    URMQCCB = 151, "乌鲁木齐市商业银行"
    XLBANK = 152, "中山小榄村镇银行"
    CSCB = 153, "长沙银行"
    JHBANK = 154, "金华银行"
    BHB = 155, "河北银行"
    NBYZ = 156, "鄞州银行"
    LSBC = 157, "临商银行"
    BOCD = 158, "承德银行"
    SDRCU = 159, "山东农信"
    NCB = 160, "南昌银行"
    TCCB = 161, "天津银行"
    WJRCB = 162, "吴江农商银行"
    CBBQS = 163, "城市商业银行资金清算中心"
    HBRCU = 164, "河北省农村信用社"


class WexinBankCode(Enum):
    """微信提现允许的银行"""
    ICBC = '中国工商银行', 1002
    ABC = '中国农业银行', 1005
    BOC = '中国银行', 1026
    CCB = '中国建设银行', 1003
    CMB = '招商银行', 1001
    PSBC = '中国邮政储蓄银行', 1066
    COMM = '交通银行', 1020
    SPDB = '上海浦东发展银行', 1004
    CMBC = '中国民生银行', 1006
    CIB = '兴业银行', 1009
    SPABANK = '平安银行', 1010
    CITIC = '中信银行', 1021
    HXBANK = '华夏银行', 1025
    GDB = '广东发展银行', 1027
    CEB = "中国光大银行", 1022
    BJBANK = "北京银行", 1032
    NBBANK = "宁波银行", 1056


class CashFor(Enum):
    """提现渠道"""
    wechat = 0, '微信零钱'
    bankcard = 1, '银行卡'


class CashStatus(Enum):
    alreadyAccounted = 2, '已到账'
    agree = 1, '银行处理中'
    refuse = -1, '未通过'
    submit = 0, '审核中'
    cancle = -10, '已取消'


class UserCommissionType(Enum):
    true_commision = 0, '佣金'
    fresh_man = 1, '新人商品'
    deposit = 2, '押金'
    news_award = 3, '圈子打赏'
    group_refund = 4, '拼团退款'
    box_deposit = 5, '礼盒押金'


class UserCommissionStatus(Enum):
    error = -1, '异常'
    preview = 0, '预计到账'
    in_account = 1, '已到账'
    out_count = 2, '已提现'


#
# class ApprovalStatus(Enum):
#     """审批流状态"""
#     cancel = -20, '已取消'
#     refuse = -10, '拒绝'
#     approvaling = 0, '审批中'
#     complate = 10, '审批通过'


# 激活码相关
class UserActivationCodeStatus(Enum):
    forbidden = -10, '不可用'
    wait_use = 0, '可用'
    ready = 10, '已用'


class UserIdentityStatus(Enum):
    ordinary = 1, '普通用户'
    agent = 2, '代理商'
    toagent = 3, '申请成为代理商中'
    toapply = 4, '待提交申请'


class OMlogisticTypeEnum(Enum):
    usual = 0, '普通发货'
    online = 10, '线上发'


class ApprovalAction(Enum):
    agree = 1, '已通过'
    refuse = -1, '未通过'
    submit = 0, '审批中'
    cancle = -10, '已取消'


class PermissionNotesType(Enum):
    pt = 1, '审批流类型'
    pi = 0, '权限标签'
    pe = 2, '审批流处理身份及层级'
    adp = 3, '标签关联管理员'


class UserMediaType(Enum):
    umfront = 1, '身份证正面'
    umback = 2, '身份证反面'


class SupplizerSettementStatus(Enum):
    checking = -2, '财务审核中'
    settlementing = 0, '结算中'
    settlemented = 1, '已结算'
    approvaling = -1, '结算异常处理中'


class NotesStatus(Enum):
    draft = 0, '草稿'
    publish = 1, '发布'


class ExcelTemplateType(Enum):
    product = 0, '商品导入模板'
    delivery = 1, '批量发货模板'


class HistoryStatus(Enum):
    normal = 0, '未购买'
    bought = 10, '已购买'
    invalid = -10, '已失效'


class SupplizerDepositLogType(Enum):
    account_entry = 10, '入账'
    account_out = 20, '出账'


class TimeLimitedStatus(Enum):
    # publish = 0, '发布'
    waiting = 1, '未开始'
    starting = 2, '已开始'
    abort = -10, '中止'
    end = 10, '结束'


class CollectionType(Enum):
    product = 0, '商品'
    news = 1, '圈子'
    user = 2, '用户'
    news_tag = 3, '圈子分类'


class CartFrom(Enum):
    normal = 10, '普通商品'
    fresh_man = 0, '新人'
    guess_num = 1, '猜数字'
    magic_box = 2, '魔术礼盒'
    free_use = 3, '免费试用'
    time_limited = 4, '限时活动'


class NewsItemPostion(Enum):
    """获取圈子标签的页面位置"""
    category = 1, '发现 - 选择分类页'
    homepage = 2, '我的 - 个人主页'
    post = 3, '发布 - 选择标签'


class NewsAwardStatus(Enum):
    """圈子打赏状态"""
    agree = 1, '已打赏'
    refuse = -1, '未通过'
    submit = 0, '审核中'


class UserGrade(Enum):
    # bronze = 0, '青铜会员'
    # silver = 1, '白银会员'
    # gold = 2, '黄金会员'
    # platinum = 3, '铂金会员'
    # diamonds = 4, '钻石会员'
    normal = 1, '大行星会员'
    agent = 2, '合作伙伴'


class PlanetMessageStatus(Enum):
    draft = 0, '草稿'
    publish = 1, '已发布',
    hide = 10, '隐藏'


class UserMessageTyep(Enum):
    txt = 0, '文本'
    img = 1, '图片'
    voice = 2, '语音'
    video = 3, '视频'
    loc = 4, '定位'


class TravelRecordType(Enum):
    """时光记录类别"""
    raiders = 0, '攻略'
    travels = 1, '游记'
    essay = 2, '随笔'


class MiniUserGrade(Enum):
    normal = 0, '游客'
    guide = 5, '导游'


class SigninLogStatus(Enum):
    wait = 0, '未签到'
    success = 1, '已签到'


class CollectStatus(Enum):
    atob = 0, '已关注'
    aandb = 1, '互相关注'
    none = 2, '未关注'


class MiniProgramBannerPosition(Enum):
    """小程序轮播图位置"""
    index = 0, '首页'
    travel = 1, '出游页'


class GuideApplyStatus(Enum):
    """导游申请状态"""
    agree = 1, '已审核'
    auditing = 0, '审核中'
    refuse = -1, '已拒绝'


class PlayPayType(Enum):
    """小程序支付流水类型"""
    enterlog = 10, '报名'
    undertake = 20, '承接'
    ticket = 30, '票务'


class TemplateID(Enum):
    """小程序模板id"""
    enter = 'enter', 'Q1x_k7hWf2bj4Wfn3aWzsmY3-ij-gtDgdcOjzBTjYtQ'
    cancel = 'cancel', 's3OkZQ1Q28VGtqdehYWq46TVj7eTasc8uluJJDoxxKA'
    gather = 'gather', 's3OkZQ1Q28VGtqdehYWq46TVj7eTasc8uluJJDoxxKA'
    activity = 'activity', 's3OkZQ1Q28VGtqdehYWq46TVj7eTasc8uluJJDoxxKA'
    signin = 'signin', 's3OkZQ1Q28VGtqdehYWq46TVj7eTasc8uluJJDoxxKA'
    setsignin = 'setsignin', 's3OkZQ1Q28VGtqdehYWq46TVj7eTasc8uluJJDoxxKA'
    makeover = 'makeover', 's3OkZQ1Q28VGtqdehYWq46TVj7eTasc8uluJJDoxxKA'
    toilet = 'toilet', 's3OkZQ1Q28VGtqdehYWq46TVj7eTasc8uluJJDoxxKA'
    accomplished = 'accomplished', 's3OkZQ1Q28VGtqdehYWq46TVj7eTasc8uluJJDoxxKA'
    guide = 'guide', 's3OkZQ1Q28VGtqdehYWq46TVj7eTasc8uluJJDoxxKA'
    agreement = 'agreement', 's3OkZQ1Q28VGtqdehYWq46TVj7eTasc8uluJJDoxxKA'


class CategoryType(Enum):
    green = 0, '全平台'
    black = 1, '品牌'
    orange = 2, '折扣券'


class ProductStatus(Enum):
    """商品状态"""
    reject = -2, '未通过'
    pending = -1, '待审核'
    ready = 0, '即将开始'
    active = 1, '活动中'
    interrupt = 2, '中止'
    over = 3, '已结束'


class OrderStatus(Enum):
    """已购票状态"""
    cancle = -2, '已取消'
    not_won = -1, '未通过'
    wait_pay = 1, '待支付'
    pending = 2, '已申请'
    has_won = 10, '可使用'
    completed = 20, '已使用'
    accomplish = 30, '已完成'  # 暂时无用


class RoleType(Enum):
    agreement = 0, '转让协议'
    discountrefund = 1, '活动退款协议'
    ticketrole = 2, '门票规则'
    activationrole = 3, '活跃分获取规则'


class TicketDepositType(Enum):
    """票务押金类型"""
    grab = 0, '抢票押金'
    patch = 1, '补交押金'


class LinkageShareType(Enum):
    screenshot = 0, '仅截图'
    links = 1, '截图+链接'


class UserMaterialFeedbackStatus(Enum):
    reject = -1, '未通过'
    wait = 0, '待退押金'
    refund = 1, '已退'


class PayType(Enum):
    """购票支付类型"""
    deposit = 1, '押金购'
    cash = 2, '直购'
    scorepay = 3, '活跃分'


class ShareType(Enum):
    direct = 0, '直接分享小程序'
    promotion = 1, '推广图分享'
    usercode = 2, '用户二维码'


class ActivationTypeEnum(Enum):
    share_new = '100', '分享新人'
    share_old = '200', '分享老人'
    publish = '300', '发布随笔'
    selected = '400', '系统精选随笔'
    reward = '500', '系统打赏'
    redbook = '600', '小红书信息绑定'
    tiktok = '700', '抖音信息绑定'
    qq = '800', 'QQ号信息绑定'
    wechat = '900', '微信号信息绑定'
    sina = '910', 'sina微博信息绑定'


class SupplizerGrade(Enum):
    product = 0, '普通商品供应商'
    ticket = 1, '门票供应商'


class WhiteListAction(Enum):
    putin = 10, '放入白名单'
    delete = 20, '从白名单删除'


class UnitType(Enum):
    wide = 10, '宽'
    high = 20, '高'
    pillars = 40, '立柱'
    metro = 50, '地铁'
    pillarshigh = 60, '立柱高'
    perimeter = 70, '周长'
    area = 80, '面积'
    cost = 90, '成本'
    minner = 100, '宽高较小值'
    mount = 110, '总额'
    alarea = 120, '铝材周长'


class ProductParamsType(Enum):
    wide = 10, '宽'
    high = 20, '高'
    single = 30, '单选'
    pillars = 40, '立柱'
    metro = 50, '地铁'
    pillarshigh = 60, '立柱高'


if __name__ == '__main__':
    print(TemplateID('enterlog').zh_value)
    # import
