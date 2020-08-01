import json
import random
import re
from datetime import datetime
import os
import uuid
from decimal import Decimal

import requests
from flask import request, current_app
from sqlalchemy import false
from werkzeug.security import check_password_hash, generate_password_hash

from inquiry.common.default_head import GithubAvatarGenerator
from inquiry.common.identifying_code import SendSMS
from inquiry.config.enums import AdminLevel, AdminStatus, UserLoginTimetype, WhiteListAction, AdminAction, AdminActionS
from inquiry.config.secret import MiniProgramAppId, MiniProgramAppSecret
from inquiry.config.timeformat import format_for_web_second
from inquiry.extensions.error_response import TokenError, WXLoginError, ParamsError, AuthorityError, NotFound, TimeError
from inquiry.extensions.interface.user_interface import token_required, admin_required, get_current_admin, is_admin, \
    is_user, get_current_user
from inquiry.extensions.params_validates import parameter_required
from inquiry.extensions.register_ext import db
from inquiry.extensions.request_handler import _get_user_agent
from inquiry.extensions.success_response import Success
from inquiry.extensions.token_handler import usid_to_token
from inquiry.extensions.weixin import WeixinLogin
from inquiry.models import User, UserLoginTime, Admin, AdminNotes, UserLevelSetting, IdentifyingCode, UserHistory, \
    Product


class CUser(object):
    @staticmethod
    def _decrypt_encrypted_user_data(encrypteddata, session_key, iv):
        """小程序信息解密"""
        from ..common.WXBizDataCrypt import WXBizDataCrypt
        pc = WXBizDataCrypt(MiniProgramAppId, session_key)
        plain_text = pc.decrypt(encrypteddata, iv)
        return plain_text

    def mini_program_login(self):
        args = request.json
        code = args.get("code")
        info = args.get("info")
        current_app.logger.info('info: {}'.format(info))
        userinfo = info.get('userInfo')
        if not userinfo:
            raise TokenError

        mplogin = WeixinLogin(MiniProgramAppId, MiniProgramAppSecret)
        try:
            get_data = mplogin.jscode2session(code)
            current_app.logger.info('get_code2session_response: {}'.format(get_data))
            session_key = get_data.get('session_key')
            openid = get_data.get('openid')
            unionid = get_data.get('unionid')
        except Exception as e:
            current_app.logger.error('mp_login_error : {}'.format(e))
            raise WXLoginError
        if not unionid or not openid:
            current_app.logger.info('pre get unionid: {}'.format(unionid))
            current_app.logger.info('pre get openid: {}'.format(openid))
            encrypteddata = info.get('encryptedData')
            iv = info.get('iv')
            try:
                encrypted_user_info = self._decrypt_encrypted_user_data(encrypteddata, session_key, iv)
                unionid = encrypted_user_info.get('unionId')
                openid = encrypted_user_info.get('openId')
                current_app.logger.info('encrypted_user_info: {}'.format(encrypted_user_info))
            except Exception as e:
                current_app.logger.error('用户信息解密失败: {}'.format(e))

        current_app.logger.info('get unionid is {}'.format(unionid))
        current_app.logger.info('get openid is {}'.format(openid))
        user = self._get_exist_user((User.USopenid == openid,))
        if user:
            current_app.logger.info('get exist user by openid: {}'.format(user.__dict__))
        elif unionid:
            user = self._get_exist_user((User.USunionid == unionid,))
            if user:
                current_app.logger.info('get exist user by unionid: {}'.format(user.__dict__))

        head = self._get_local_head(userinfo.get("avatarUrl"), openid)
        current_app.logger.info('get head = {}'.format(head))
        sex = userinfo.get('gender')
        sex = int(sex) if str(sex) in '12' else 0

        user_update_dict = {'USheader': head,
                            'USname': userinfo.get('nickName'),
                            'USopenid': openid,
                            'USgender': sex,
                            'USunionid': unionid
                            }
        with db.auto_commit():

            if user:
                usid = user.USid

                user.update(user_update_dict)
            else:
                current_app.logger.info('This is a new guy : {}'.format(userinfo.get('nickName')))

                usid = str(uuid.uuid1())

                user = User.create({
                    'USid': usid,
                    'USname': userinfo.get('nickName'),
                    'USgender': sex,
                    'USheader': head,
                    'USlevel': 1,
                    'USopenid': openid,
                    'USunionid': unionid,
                })
            db.session.add(user)
            db.session.flush()

            userloggintime = UserLoginTime.create({"ULTid": str(uuid.uuid1()),
                                                   "USid": usid,
                                                   "USTip": request.remote_addr
                                                   })
            useragent = _get_user_agent()
            if useragent:
                setattr(userloggintime, 'OSVersion', useragent[0])
                setattr(userloggintime, 'PhoneModel', useragent[1])
                setattr(userloggintime, 'WechatVersion', useragent[2])
                setattr(userloggintime, 'NetType', useragent[3])
                setattr(userloggintime, 'UserAgent', useragent[4])
            db.session.add(userloggintime)

        token = usid_to_token(user.USid, level=user.USlevel, username=user.USname)
        binded_phone = True if user and user.UStelphone else False
        inwhitelist = bool(user and user.USinWhiteList)
        data = {'token': token, 'binded_phone': binded_phone, 'inwhitelist': inwhitelist, 'session_key': session_key}
        current_app.logger.info('return_data : {}'.format(data))
        return Success('登录成功', data=data)

    @token_required
    def bind_phone(self):
        """小程序绑定手机号更新用户"""
        data = parameter_required(('ustelphone', 'identifyingcode',))
        ustelphone = data.get('ustelphone')
        if not ustelphone:
            raise ParamsError('为获得更优质的服务，请允许授权您的手机号码')

        user = self._get_exist_user((User.USid == getattr(request, 'user').id,))
        if user.UStelphone:
            raise TokenError('您已绑定过手机号码')
        self.__check_identifyingcode(ustelphone, data.get("identifyingcode"))

        covered_number = str(ustelphone).replace(str(ustelphone)[3:7], '*' * 4)

        if self._get_exist_user((User.USid != getattr(request, 'user').id, User.UStelphone == ustelphone)):
            raise ParamsError(f'该手机号({covered_number})已被其他用户绑定，请联系客服处理')

        with db.auto_commit():
            user.update({'UStelphone': ustelphone})
            db.session.add(user)
            res_user = user

        token = usid_to_token(res_user.USid, level=res_user.USlevel, username=res_user.USname)  # 更换token
        response = {'phonenumber': covered_number, 'token': token}
        current_app.logger.info('return_data: {}'.format(response))
        return Success('绑定成功', response)

    @staticmethod
    def _get_exist_user(filter_args, msg=None):
        return User.query.filter(User.isdelete == false(), *filter_args).first_(msg)

    def _get_local_head(self, headurl, openid):
        """转置微信头像到服务器，用以后续二维码生成"""
        if not headurl:
            return GithubAvatarGenerator().save_avatar(openid)
        data = requests.get(headurl)
        filename = openid + '.png'
        filepath, filedbpath = self._get_path('avatar')
        filedbname = os.path.join(filedbpath, filename)
        filename = os.path.join(filepath, filename)
        with open(filename, 'wb') as head:
            head.write(data.content)

        return filedbname

    def _get_path(self, fold):
        """获取服务器上文件路径"""
        time_now = datetime.now()
        year = str(time_now.year)
        month = str(time_now.month)
        day = str(time_now.day)
        filepath = os.path.join(current_app.config['BASEDIR'], 'img', fold, year, month, day)
        file_db_path = os.path.join('/img', fold, year, month, day)
        if not os.path.isdir(filepath):
            os.makedirs(filepath)
        return filepath, file_db_path

    @admin_required
    def get_user_list(self):
        admin = get_current_admin()
        if not admin:
            raise AuthorityError
        data = parameter_required()
        ustelphone = data.get('ustelphone')
        usname = data.get('usname')
        uslevel = data.get('uslevel')
        filter_args = [User.isdelete == false()]
        if ustelphone:
            filter_args.append(User.UStelphone.ilike('%{}%'.format(ustelphone)))
        if usname:
            filter_args.append(User.USname.ilike('%{}%'.format(usname)))
        if uslevel or uslevel == 0:
            try:
                uslevel = int(uslevel)
            except Exception:
                raise ParamsError('等级只能是整数')

            filter_args.append(User.USlevel == uslevel)

        user_list = User.query.filter(*filter_args).all_with_page()
        return Success('获取成功', data=user_list)

    @token_required
    def get_admin_list(self):
        """获取管理员列表"""
        superadmin = get_current_admin()
        if superadmin.ADlevel != AdminLevel.super_admin.value or \
                superadmin.ADstatus != AdminStatus.normal.value:
            raise AuthorityError('当前非超管权限')
        args = request.args.to_dict()
        page = args.get('page_num')
        count = args.get('page_size')
        if page and count:
            admins = Admin.query.filter(
                Admin.isdelete == false(), Admin.ADlevel == AdminLevel.common_admin.value).order_by(
                Admin.createtime.desc()).all_with_page()
        else:
            admins = Admin.query.filter(
                Admin.isdelete == false(), Admin.ADlevel == AdminLevel.common_admin.value).order_by(
                Admin.createtime.desc()).all()
        for admin in admins:
            admin.fields = ['ADid', 'ADname', 'ADheader', 'createtime', 'ADnum']
            admin.fill('adlevel', AdminLevel(admin.ADlevel).zh_value)
            admin.fill('adstatus', AdminStatus(admin.ADstatus).zh_value)
            admin.fill('adpassword', '*' * 6)
            admin.fill('adtelphone', admin.ADtelephone)
            admin_login = UserLoginTime.query.filter_by_(
                USid=admin.ADid, ULtype=UserLoginTimetype.admin.value).order_by(UserLoginTime.createtime.desc()).first()
            logintime = None
            if admin_login:
                logintime = admin_login.createtime
            admin.fill('logintime', logintime)

        return Success('获取管理员列表成功', data=admins)

    @admin_required
    def update_white_list(self):
        admin = get_current_admin()
        if not admin:
            raise AuthorityError
        data = parameter_required(("usid", "action"))
        usid = data.get('usid')
        action = data.get("action", 10)

        if action:
            try:
                action = WhiteListAction(int(action)).value
            except:
                raise ParamsError('action 只能是整数')

        user = User.query.filter(User.USid == usid, User.isdelete == false()).first()
        if not user:
            raise ParamsError('用户不在本系统')
        with db.auto_commit():
            if action == WhiteListAction.putin.value:
                if user.USinWhiteList:
                    raise ParamsError('用户已在白名单')
                user.USinWhiteList = True
            elif action == WhiteListAction.delete.value:
                if not user.USinWhiteList:
                    raise ParamsError('用户不在白名单')
                user.USinWhiteList = False
            else:
                raise ParamsError('参数异常')
            db.session.add(user)
        return Success(data='{}修改成功'.format(user.USname))

    @admin_required
    def update_user_level(self):
        admin = get_current_admin()
        if not admin:
            raise AuthorityError
        data = parameter_required(("usid", "uslevel"))
        usid = data.get('usid')
        uslevel = data.get("uslevel", 0)

        if uslevel or uslevel == 0:
            try:
                uslevel = int(uslevel)
            except:
                raise ParamsError('uslevel 只能是整数')

        user = User.query.filter(User.USid == usid, User.isdelete == false()).first()
        if not user:
            raise ParamsError('用户不在本系统')
        with db.auto_commit():
            user.USlevel = uslevel
            db.session.add(user)
        return Success(data='{}修改成功'.format(user.USname))

    @token_required
    def update_admin_password(self):
        """更新管理员密码"""
        if not is_admin():
            raise AuthorityError('权限不足')

        data = parameter_required(('password_old', 'password_new', 'password_repeat'))
        admin = get_current_admin()
        pwd_new = data.get('password_new')
        pwd_old = data.get('password_old')
        pwd_repeat = data.get('password_repeat')
        if pwd_new != pwd_repeat:
            raise ParamsError('两次输入的密码不同')
        with db.auto_commit():
            if check_password_hash(admin.ADpassword, pwd_old):
                self.__check_password(pwd_new)
                admin.ADpassword = generate_password_hash(pwd_new)
                # BASEADMIN().create_action(AdminActionS.update.value, 'none', 'none')
                db.session.add(admin)
                return Success('更新密码成功')
            current_app.logger.info('{0} update pwd failed'.format(admin.ADname))
            raise ParamsError('旧密码有误')

        raise AuthorityError('账号已被回收')

    def admin_login(self):
        """管理员登录"""
        data = parameter_required(('adname', 'adpassword'))
        admin = Admin.query.filter(Admin.isdelete == false(), Admin.ADname == data.get('adname')).first_('用户不存在')

        # 密码验证
        if admin and check_password_hash(admin.ADpassword, data.get("adpassword")):
            current_app.logger.info('管理员登录成功 %s' % admin.ADname)
            # 创建管理员登录记录
            ul_instance = UserLoginTime.create({
                "ULTid": str(uuid.uuid1()),
                "USid": admin.ADid,
                "USTip": request.remote_addr,
                "ULtype": UserLoginTimetype.admin.value,
                "UserAgent": request.user_agent.string
            })
            db.session.add(ul_instance)
            token = usid_to_token(admin.ADid, 'Admin', admin.ADlevel, username=admin.ADname)
            admin.fields = ['ADname', 'ADheader', 'ADlevel']

            admin.fill('adlevel', AdminLevel(admin.ADlevel).zh_value)
            admin.fill('adstatus', AdminStatus(admin.ADstatus).zh_value)

            return Success('登录成功', data={'token': token, "admin": admin})
        return ParamsError("用户名或密码错误")

    @token_required
    def add_admin_by_superadmin(self):
        """超级管理员添加普通管理"""
        superadmin = get_current_admin()
        if superadmin.ADlevel != AdminLevel.super_admin.value or \
                superadmin.ADstatus != AdminStatus.normal.value:
            raise AuthorityError('当前非超管权限')

        data = request.json
        current_app.logger.info("add admin data is %s" % data)
        parameter_required(('adname', 'adpassword', 'adtelphone'))
        adid = str(uuid.uuid1())
        password = data.get('adpassword')
        # 密码校验
        self.__check_password(password)

        adname = data.get('adname')
        adlevel = getattr(AdminLevel, data.get('adlevel', ''))
        adlevel = 2 if not adlevel else int(adlevel.value)
        header = data.get('adheader') or GithubAvatarGenerator().save_avatar(adid)
        # 等级校验
        if adlevel not in [1, 2, 3]:
            raise ParamsError('adlevel参数错误')
        telephone = data.get('adtelphone')
        if not re.match(r'^1[0-9]{10}$', str(telephone)):
            raise ParamsError('手机号格式错误')
        # 账户名校验
        self.__check_adname(adname, adid)
        adnum = self.__get_adnum()
        # 创建管理员
        with db.auto_commit():
            adinstance = Admin.create({
                'ADid': adid,
                'ADnum': adnum,
                'ADname': adname,
                'ADtelephone': telephone,
                'ADfirstpwd': password,
                'ADfirstname': adname,
                'ADpassword': generate_password_hash(password),
                'ADheader': header,
                'ADlevel': adlevel,
                'ADstatus': 0,
            })
            db.session.add(adinstance)

            # 创建管理员变更记录
            an_instance = AdminNotes.create({
                'ANid': str(uuid.uuid1()),
                'ADid': adid,
                'ANaction': '{0} 创建管理员{1} 等级{2}'.format(superadmin.ADname, adname, adlevel),
                "ANdoneid": request.user.id
            })

            db.session.add(an_instance)
        return Success('创建管理员成功')

    @token_required
    def update_admin(self):
        """更新管理员信息"""
        if not is_admin():
            raise AuthorityError('权限不足')
        data = request.json or {}
        admin = get_current_admin()
        if admin.ADstatus != AdminStatus.normal.value:
            raise AuthorityError('权限不足')
        update_admin = {}
        action_list = []
        with db.auto_commit():
            if data.get("adname"):
                update_admin['ADname'] = data.get("adname")
                action_list.append(str(AdminAction.ADname.value) + '为' + str(data.get("adname")) + '\n')

            if data.get('adheader'):
                update_admin['ADheader'] = data.get("adheader")
                action_list.append(str(AdminAction.ADheader.value) + '\n')
            if data.get('adtelphone'):
                # self.__check_identifyingcode(data.get('adtelphone'), data.get('identifyingcode'))
                update_admin['ADtelephone'] = data.get('adtelphone')
                action_list.append(str(AdminAction.ADtelphone.value) + '为' + str(data.get("adtelphone")) + '\n')
            password = data.get('adpassword')
            if password and password != '*' * 6:
                self.__check_password(password)
                password = generate_password_hash(password)
                update_admin['ADpassword'] = password
                action_list.append(str(AdminAction.ADpassword.value) + '为' + str(password) + '\n')

            if admin.ADlevel == AdminLevel.super_admin.value:
                filter_adid = data.get('adid') or admin.ADid
                if getattr(AdminLevel, data.get('adlevel', ""), ""):
                    update_admin['ADlevel'] = getattr(AdminLevel, data.get('adlevel')).value
                    action_list.append(
                        str(AdminAction.ADlevel.value) + '为' + getattr(AdminLevel, data.get('adlevel')).zh_value + '\n')
                if getattr(AdminStatus, data.get('adstatus', ""), ""):
                    update_admin['ADstatus'] = getattr(AdminStatus, data.get('adstatus')).value
                    action_list.append(
                        str(AdminAction.ADstatus.value) + '为' + getattr(AdminStatus,
                                                                        data.get('adstatus')).zh_value + '\n')
            else:
                filter_adid = admin.ADid
            self.__check_adname(data.get("adname"), filter_adid)

            update_admin = {k: v for k, v in update_admin.items() if v or v == 0}
            update_result = Admin.query.filter(Admin.ADid == filter_adid, Admin.isdelete == false()).update(
                update_admin)
            if not update_result:
                raise ParamsError('管理员不存在')
            filter_admin = Admin.query.filter(Admin.isdelete == false(), Admin.ADid == filter_adid).first_('管理员不存在')

            action_str = admin.ADname + '修改' + filter_admin.ADname + ','.join(action_list)

            an_instance = AdminNotes.create({
                'ANid': str(uuid.uuid1()),
                'ADid': filter_adid,
                'ANaction': action_str,
                "ANdoneid": request.user.id
            })
            db.session.add(an_instance)
        # if is_admin():
        #     self.base_admin.create_action(AdminActionS.insert.value, 'AdminNotes', str(uuid.uuid1()))
        return Success("操作成功")

    def __check_password(self, password):
        if not password or len(password) < 4:
            raise ParamsError('密码长度低于4位')
        zh_pattern = re.compile(r'[\u4e00-\u9fa5]+')
        match = zh_pattern.search(password)
        if match:
            raise ParamsError(u'密码包含中文字符')
        return True

    def __check_adname(self, adname, adid):
        """账户名校验"""
        if not adname or adid:
            return True
        suexist = Admin.query.filter_by(ADname=adname, isdelete=False).first()
        if suexist and suexist.ADid != adid:
            raise ParamsError('用户名已存在')
        return True

    def __get_adnum(self):
        admin = Admin.query.order_by(Admin.ADnum.desc()).first()
        if not admin:
            return 100000
        return admin.ADnum + 1

    @staticmethod
    def test_login():
        """测试登录"""
        data = parameter_required()
        tel = data.get('ustelphone')
        user = User.query.filter(User.isdelete == false(), User.UStelphone == tel).first()
        if not user:
            raise NotFound
        token = usid_to_token(user.USid, model='User', username=user.USname)
        return Success(data={'token': token, 'usname': user.USname})

    @admin_required
    def get_userlevelsetting(self):
        admin = get_current_admin()
        usllist = UserLevelSetting.query.filter(UserLevelSetting.isdelete == false()).order_by(
            UserLevelSetting.ULSlevel.desc()).all()

        return Success('获取成功', data=usllist)

    @admin_required
    def set_userlevelsetting(self):
        admin = get_current_admin()
        data = parameter_required()
        ulsid, ulslevel, ulscoefficient = data.get('ulsid'), data.get('ulslevel'), data.get('ulscoefficient')
        ulsdict = {}
        if ulslevel or ulslevel == 0:
            try:
                ulslevel = int(ulslevel)
            except:
                raise ParamsError('等级只能是整数')
            ulsdict['ULSlevel'] = ulslevel
        if ulscoefficient or ulscoefficient == 0:
            try:
                ulscoefficient = Decimal(ulscoefficient)
            except:
                raise ParamsError('系数只能是数字')
            ulsdict['ULScoefficient'] = ulscoefficient
        with db.auto_commit():
            if not ulsid:
                if not ulslevel:
                    raise ParamsError('等级参数缺失')
                if not ulscoefficient:
                    raise ParamsError('系数缺失')
                ulsdict['ULSid'] = str(uuid.uuid1())
                # 同级校验
                uls = UserLevelSetting.query.filter(
                    UserLevelSetting.isdelete == false(), UserLevelSetting.ULSlevel == ulslevel).first()
                if uls:
                    raise ParamsError('该等级已设置对应系数')
                ulsinstance = UserLevelSetting.create(ulsdict)
                msg = '添加成功'
            else:
                ulsinstance = UserLevelSetting.query.filter(
                    UserLevelSetting.isdelete == false(), UserLevelSetting.ULSid == ulsid).first_('系数设置已删除')
                if data.get('delete'):
                    ulsinstance.update({'isdelete': True})
                    msg = '删除成功'
                else:
                    ulsinstance.update(ulsdict)
                    msg = '更新成功'
            db.session.add(ulsinstance)
        return Success(msg, data={'ulsid': ulsinstance.ULSid})

    def get_inforcode(self):
        """发送/校验验证码"""
        args = request.args.to_dict()
        # print('get inforcode args: {0}'.format(args))
        Utel = args.get('ustelphone')
        if not Utel or not re.match(r'^1[1-9][0-9]{9}$', str(Utel)):
            raise ParamsError('请输入正确的手机号码')
        if is_user():
            user = User.query.filter_by_(USid=request.user.id).first()
            if (user and user.UStelphone) and str(Utel) != user.UStelphone:
                raise ParamsError('请使用已绑定手机号 {} 获取验证码'
                                  ''.format(str(user.UStelphone).replace(str(user.UStelphone)[3:7], '*' * 4)))
        # 拼接验证码字符串（6位）
        code = ""
        while len(code) < 6:
            item = random.randint(1, 9)
            code = code + str(item)

        # 获取当前时间，与上一次获取的时间进行比较，小于60秒的获取直接报错

        time_time = datetime.now()

        # 根据电话号码获取时间
        time_up = IdentifyingCode.query.filter(
            IdentifyingCode.ICtelphone == Utel, IdentifyingCode.isdelete == False).order_by(
            IdentifyingCode.createtime.desc()).first_()
        # print("this is time up %s", time_up)

        if time_up:
            delta = time_time - time_up.createtime
            if delta.seconds < 60:
                raise TimeError("验证码已发送")

        with db.auto_commit():
            newidcode = IdentifyingCode.create({
                "ICtelphone": Utel,
                "ICcode": code,
                "ICid": str(uuid.uuid1())
            })
            db.session.add(newidcode)

        params = {"code": code}
        response_send_message = SendSMS(Utel, params)

        if not response_send_message:
            raise SystemError('发送验证码失败')

        response = {
            'ustelphone': Utel
        }
        return Success('获取验证码成功', data=response)

    def __check_identifyingcode(self, ustelphone, identifyingcode):
        """验证码校验"""
        # identifyingcode = str(data.get('identifyingcode'))
        if not ustelphone or not identifyingcode:
            raise ParamsError("验证码/手机号缺失")
        idcode = IdentifyingCode.query.filter(
            IdentifyingCode.ICtelphone == ustelphone, IdentifyingCode.isdelete == False).order_by(
            IdentifyingCode.createtime.desc()).first_()

        if not idcode or str(idcode.ICcode) != identifyingcode:
            current_app.logger.info('get identifyingcode ={0} get idcode = {1}'.format(identifyingcode, idcode.ICcode))
            raise ParamsError('验证码有误')

        timenow = datetime.now()
        if (timenow - idcode.createtime).seconds > 600:
            current_app.logger.info('get timenow ={0}, sendtime = {1}'.format(timenow, idcode.createtime))
            raise ParamsError('验证码已经过期')
        return True

    @token_required
    def useristory(self):
        """用户查询记录"""
        data = parameter_required()
        usname, ustelphone, starttime, endtime = data.get('usname'), data.get('ustelphone'), data.get(
            'starttime'), data.get('endtime')

        filter_args = []
        if is_user():
            user = get_current_user()
            filter_args.append(User.USid == user.USid)
        if usname:
            filter_args.append(User.USname.ilike("%{}%".format(usname)))
        if ustelphone:
            filter_args.append((User.UStelphone.ilike("%{}%".format(ustelphone))))

        starttime = self._check_time(starttime)
        endtime = self._check_time(endtime)
        if starttime:
            filter_args.append(UserHistory.createtime >= starttime)
        if endtime:
            filter_args.append(UserHistory.createtime <= endtime)

        uhlist = UserHistory.query.join(User, User.USid == UserHistory.USid).filter(*filter_args).order_by(
            UserHistory.createtime.desc()).all_with_page()
        productdict = {}
        product_list = Product.query.join(UserHistory, UserHistory.PRid == Product.PRid).filter(
            Product.isdelete == false(), UserHistory.isdelete == false()).all()
        for product in product_list:
            productdict[product.PRid] = product.PRname

        user_list = User.query.join(UserHistory, UserHistory.USid == User.USid).filter(
            User.isdelete == false(), UserHistory.isdelete == false()).all()
        user_dict = {user_item.USid: user_item for user_item in user_list}
        for uh in uhlist:
            uh.add("createtime")
            uh.fill('prname', productdict.get(uh.PRid))
            user_item = user_dict.get(uh.USid)
            uh.fill('usname', user_item.USname)
            uh.fill('ustelphone', user_item.UStelphone)
            uh.fill('uhparams', json.loads(uh.UHparams))
            uh.fill('uhcost', json.loads(uh.UHcost or '[]'))
        return Success("获取查询记录成功", data=uhlist)

    def _check_time(self, check_time):
        if not check_time:
            return
        # 日期校验
        if not isinstance(check_time, datetime):
            try:
                check_time = datetime.strptime(str(check_time), format_for_web_second)
            except:
                raise ParamsError('日期格式不对，具体格式为{}'.format(format_for_web_second))
        return check_time
