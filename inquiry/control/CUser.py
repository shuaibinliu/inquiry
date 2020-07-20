import datetime
import os
import uuid

import requests
from flask import request, current_app
from sqlalchemy import false

from inquiry.common.default_head import GithubAvatarGenerator
from inquiry.config.enums import AdminLevel, AdminStatus, UserLoginTimetype, WhiteListAction
from inquiry.config.secret import MiniProgramAppId, MiniProgramAppSecret
from inquiry.extensions.error_response import TokenError, WXLoginError, ParamsError, AuthorityError
from inquiry.extensions.interface.user_interface import token_required, admin_required, get_current_admin
from inquiry.extensions.params_validates import parameter_required
from inquiry.extensions.register_ext import db
from inquiry.extensions.request_handler import _get_user_agent
from inquiry.extensions.success_response import Success
from inquiry.extensions.token_handler import usid_to_token
from inquiry.extensions.weixin import WeixinLogin
from inquiry.models import User, UserLoginTime, Admin


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
        user = self._get_exist_user((User.USopenid1 == openid,))
        if user:
            current_app.logger.info('get exist user by openid: {}'.format(user.__dict__))
        elif unionid:
            user = self._get_exist_user((User.USunionid == unionid,))
            if user:
                current_app.logger.info('get exist user by unionid: {}'.format(user.__dict__))

        head = self._get_local_head(userinfo.get("avatarUrl"), openid)
        sex = userinfo.get('gender')
        sex = int(sex) if str(sex) in '12' else 0

        user_update_dict = {'USheader': head,
                            'USname': userinfo.get('nickName'),
                            'USopenid1': openid,
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
                'USopenid1': openid,
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
        binded_phone = True if user and user.UStelephone else False
        data = {'token': token, 'binded_phone': binded_phone, 'session_key': session_key}
        current_app.logger.info('return_data : {}'.format(data))
        return Success('登录成功', data=data)

    @token_required
    def bind_phone(self):
        """小程序绑定手机号更新用户"""
        data = parameter_required(('session_key',))
        phone = data.get('phonenumber')
        if not phone:
            raise ParamsError('为获得更优质的服务，请允许授权您的手机号码')

        user = self._get_exist_user((User.USid == getattr(request, 'user').id,))
        if user.UStelephone:
            raise TokenError('您已绑定过手机号码')

        session_key = data.get('session_key')
        current_app.logger.info('手机加密数据为{}'.format(phone))
        encrypteddata = phone.get('encryptedData')
        iv = phone.get('iv')

        try:
            encrypted_user_info = self._decrypt_encrypted_user_data(encrypteddata, session_key, iv)
        except Exception as e:
            current_app.logger.error('手机号解密失败: {}'.format(e))
            raise WXLoginError()

        current_app.logger.info(f'plain_text: {encrypted_user_info}')
        phonenumber = encrypted_user_info.get('phoneNumber')
        covered_number = str(phonenumber).replace(str(phonenumber)[3:7], '*' * 4)

        if self._get_exist_user((User.USid != getattr(request, 'user').id, User.UStelephone == phonenumber)):
            raise ParamsError(f'该手机号({covered_number})已被其他用户绑定，请联系客服处理')

        with db.auto_commit():
            user.update({'UStelephone': phonenumber})
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
        data = parameter_required("usid", "action")
        usid = data.get('usid')
        action = data.get('action', 0)
        if action:
            try:
                action = WhiteListAction(int(action)).value
            except:
                raise ParamsError('action 只能是整数')

        user = User.queruy.filter(User.USid == usid, User.isdelete == false()).first()
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

        return Success(data='{}修改成功'.format(user.USname))
