import uuid

from flask import request
from sqlalchemy import true, false

from inquiry.extensions.interface.user_interface import is_admin, admin_required
from inquiry.extensions.params_validates import parameter_required
from inquiry.extensions.register_ext import db
from inquiry.extensions.success_response import Success
from inquiry.models import Banner


class CIndex(object):
    def list_mp_banner(self):
        """小程序轮播图获取"""
        filter_args = [Banner.isdelete == false(), ]
        if not is_admin():
            filter_args.append(Banner.BNshow == true())
        mpbs = Banner.query.filter(*filter_args).order_by(Banner.BNsort.asc(),
                                                          Banner.createtime.desc()).all()
        [x.hide('ADid') for x in mpbs]
        return Success(data=mpbs)

    @admin_required
    def set_mp_banner(self):
        """小程序轮播图"""
        data = parameter_required(('bnurl',))
        bnid = data.get('bnid')
        bndict = {'BNurl': data.get('bnurl'),
                  'BNsort': data.get('bnsort'),
                  'BNshow': data.get('bnshow'),
                  'contentlink': data.get('contentlink')}
        with db.auto_commit():
            if not bnid:
                bndict['BNid'] = str(uuid.uuid1())
                bndict['ADid'] = getattr(request, 'user').id
                bn_instance = Banner.create(bndict)

                msg = '添加成功'
            else:
                bn_instance = Banner.query.filter_by(BNid=bnid, isdelete=false()).first_('未找到该轮播图信息')
                if data.get('delete'):
                    bn_instance.update({'isdelete': True})
                    msg = '删除成功'
                else:
                    bn_instance.update(bndict, null='not')
                    msg = '编辑成功'
            db.session.add(bn_instance)
        return Success(message=msg, data={'bnid': bn_instance.BNid})
