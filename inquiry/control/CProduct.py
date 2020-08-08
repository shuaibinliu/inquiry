import json
import math
import os
import random
import time
import uuid
from datetime import datetime
from decimal import Decimal

import tablib
from flask import request, send_from_directory, current_app
from sqlalchemy import false, or_, and_

from inquiry.extensions.base_jsonencoder import JSONEncoder
from inquiry.config.enums import UnitType, ProductParamsType

from inquiry.config.secret import BASEDIR
from inquiry.extensions.error_response import ParamsError, AuthorityError
from inquiry.extensions.interface.user_interface import admin_required, get_current_admin, is_admin, get_current_user, \
    is_user, token_required
from inquiry.extensions.params_validates import parameter_required
from inquiry.extensions.register_ext import db
from inquiry.extensions.success_response import Success
from inquiry.models import Product, ProductCategory, ProductParams, ProductParamsValue, FrontParams, UnitCategory, Unit, \
    UserLevelSetting, UserHistory


class CProduct(object):
    @admin_required
    def set_proudct(self):
        admin = get_current_admin()

        data = parameter_required()
        prid, prname, pcid, prsort = data.get('prid'), data.get('prname'), data.get('pcid'), data.get('prsort')
        product_dict = {"ADid": admin.ADid}
        if prname:
            product_dict['PRname'] = prname
        if pcid:
            pc = ProductCategory.query.filter(
                ProductCategory.PCid == pcid, ProductCategory.isdelete == false()).first_('分类已删除')

            product_dict['PCid'] = pc.PCid
        if prsort:
            try:
                prsort = int(prsort)
            except:
                raise ParamsError('权重只能是整数')
            product_dict['PRsort'] = prsort
        with db.auto_commit():
            if not prid:
                if not prname:
                    raise ParamsError('缺少产品名')
                if not pcid:
                    raise ParamsError('缺少分类ID')

                product_dict['PRid'] = str(uuid.uuid1())
                product = Product.create(product_dict)
                msg = '添加成功'

            else:
                product = Product.query.filter(Product.PRid == prid, Product.isdelete == false()).first_('产品已删除')

                if data.get('delete'):
                    product.update({'isdelete': True})
                    msg = '删除成功'
                else:
                    product.update(product_dict)
                    msg = '编辑成功'

            db.session.add(product)
        return Success(message=msg, data={'prid': product.PRid})

    @token_required
    def list(self):
        data = parameter_required()
        filter_args = [Product.isdelete == false(), ProductCategory.isdelete == false()]
        if is_admin():
            _ = get_current_admin()
        elif is_user():
            user = get_current_user()
            if not user.USinWhiteList:
                raise AuthorityError('用户无权限，请联系管理员')
        else:
            raise AuthorityError

        pcid = data.get('pcid')
        prname = data.get('prname')
        if pcid:
            filter_args.append(Product.PCid == pcid)
        if prname:
            filter_args.append(Product.PRname.ilike('%{}%'.format(prname)))
        product_list = Product.query.join(ProductCategory, ProductCategory.PCid == Product.PCid).filter(
            *filter_args).order_by(Product.PRsort.desc(), Product.createtime.desc()).all_with_page()
        for product in product_list:
            self._fill_pcname(product)
        return Success('获取成功', data=product_list)

    def _fill_pcname(self, product):
        pc = ProductCategory.query.filter(
            ProductCategory.PCid == product.PCid, ProductCategory.isdelete == false()).first()
        product.fill('pcname', pc.PCname)

    @token_required
    def get(self):
        if is_admin():
            _ = get_current_admin()
        elif is_user():
            user = get_current_user()
            if not user.USinWhiteList:
                raise AuthorityError('用户无权限，请联系管理员')
        else:
            raise AuthorityError

        data = parameter_required(('prid',))
        prid = data.get('prid')
        product = Product.query.join(ProductCategory, ProductCategory.PCid == Product.PCid).filter(
            Product.PRid == prid, Product.isdelete == false(), ProductCategory.isdelete == false()).first_("产品已删除")
        self._fill_pcname(product)
        return Success('获取成功', data=product)

    @admin_required
    def set_pc(self):
        _ = get_current_admin()

        data = parameter_required()
        pcid, pcname, pcsort, pcurl, pcicon = data.get('pcid'), data.get('pcname'), data.get('pcsort'), data.get(
            'pcurl'), data.get('pcicon')
        pc_dict = {}
        if pcname:
            pc_dict['PCname'] = pcname
        # if pcurl:
        pc_dict['PCurl'] = pcurl
        if pcicon:
            pc_dict['PCicon'] = pcicon
        if pcsort:
            try:
                pcsort = int(pcsort)
            except:
                raise ParamsError('权重只能是整数')
            pc_dict['PCsort'] = pcsort
        with db.auto_commit():
            if not pcid:
                if not pcname:
                    raise ParamsError('缺少分类名')
                if not pcicon:
                    raise ParamsError('缺少icon')
                pc_dict['PCid'] = str(uuid.uuid1())
                pc = ProductCategory.create(pc_dict)
                msg = '添加成功'

            else:
                pc = ProductCategory.query.filter(
                    ProductCategory.PCid == pcid, ProductCategory.isdelete == false()).first_('分类已删除')

                if data.get('delete'):
                    pc.update({'isdelete': True})
                    msg = '删除成功'
                else:
                    pc.update(pc_dict, null='not ignore')
                    msg = '编辑成功'

            db.session.add(pc)
        return Success(message=msg, data={'pcid': pc.PCid})

    @token_required
    def list_pc(self):
        pc_list = ProductCategory.query.filter(ProductCategory.isdelete == false()).order_by(
            ProductCategory.PCsort.desc(), ProductCategory.createtime.desc()).all()
        return Success('获取成功', data=pc_list)

    @admin_required
    def set_pp(self):
        _ = get_current_admin()

        data = parameter_required()
        ppid, prid, ppname, pprequired, pptype, ppremarks, ppunit, ppsort, ppvlist = data.get(
            'ppid'), data.get('prid'), data.get('ppname'), data.get('pprequired'), data.get(
            'pptype'), data.get('ppremarks'), data.get('ppunit'), data.get('ppsort'), data.get('ppvlist', [])
        pp_dict = {}
        if ppname:
            pp_dict['PPname'] = ppname
        if prid:
            _ = Product.query.filter(Product.PRid == prid, Product.isdelete == false()).first_('商品已删除')
            pp_dict['PRid'] = prid
        # if pprequired:
        pp_dict['PPrequired'] = bool(pprequired)
        if ppsort:
            try:
                ppsort = int(ppsort)
            except:
                raise ParamsError('权重只能是整数')
            pp_dict['PPsort'] = ppsort
        if pptype:
            try:
                pptype = ProductParamsType(int(pptype)).value
            except:
                raise ParamsError('类型有误')
            pp_dict['PPtype'] = pptype
        # if ppunit:
        pp_dict['PPunit'] = ppunit
        if ppremarks:
            pp_dict['PPremarks'] = ppremarks

        with db.auto_commit():
            if not ppid:
                # if not prid:
                #     raise ParamsError('需绑定产品')
                if not ppname:
                    raise ParamsError('缺少参数名')
                if not pptype:
                    raise ParamsError('缺少参数类型')
                pp_dict['PPid'] = str(uuid.uuid1())
                pp = ProductParams.create(pp_dict)
                msg = '添加成功'
            else:
                pp = ProductParams.query.filter(
                    ProductParams.PPid == ppid, ProductParams.isdelete == false()).first_('参数已删除')

                if data.get('delete'):
                    pp.update({'isdelete': True})
                    msg = '删除成功'
                else:
                    pp.update(pp_dict, null='not ignore')
                    msg = '编辑成功'

            db.session.add(pp)
            if isinstance(ppvlist, list):
                # ProductParamsValue.query.filter(ProductParams.PPid == pp.PPid).delete_()
                ppvidlist = []
                instance_list = []
                for ppv in ppvlist:
                    ppvvalue = ppv.get('ppvvalue')
                    ppvprice = ppv.get('ppvprice', 0)
                    ppvid = ppv.get('ppvid')
                    if ppvprice:
                        try:
                            ppvprice = Decimal(str(ppvprice))
                        except:
                            raise ParamsError('单价只能是数字')
                    ppvdict = {'PPid': pp.PPid, "PPVvalue": ppvvalue, "PPVprice": ppvprice}
                    if ppvid:
                        ppv_instance = ProductParamsValue.query.filter(
                            ProductParamsValue.PPVid == ppvid, ProductParamsValue.isdelete == false()).first()
                        if ppv_instance:
                            ppv_instance.update(ppvdict)
                        else:
                            ppvdict.setdefault('PPVid', str(uuid.uuid1()))
                            ppv_instance = ProductParamsValue.create(ppvdict)
                    else:
                        ppvdict.setdefault('PPVid', str(uuid.uuid1()))
                        ppv_instance = ProductParamsValue.create(ppvdict)
                    frontids = ppv.get('frontid', [])
                    if isinstance(frontids, list):
                        fpids = []
                        for frontid in frontids:
                            front = ProductParams.query.filter(
                                ProductParams.PPid == frontid).first_("后续参数已删除")
                            fp_instance = FrontParams.query.filter(
                                FrontParams.PPid == front.PPid,
                                FrontParams.PPVid == ppv_instance.PPVid, FrontParams.isdelete == false()).first()
                            if not fp_instance:
                                fp_instance = FrontParams.create({
                                    "FPid": str(uuid.uuid1()),
                                    "PPid": front.PPid,
                                    "PPVid": ppv_instance.PPVid,

                                })
                                instance_list.append(fp_instance)
                            fpids.append(fp_instance.FPid)
                            front.PRid = ""
                            instance_list.append(front)

                        unused_fp = FrontParams.query.filter(FrontParams.PPVid == ppv_instance.PPVid,
                                                             FrontParams.FPid.notin_(fpids),
                                                             FrontParams.isdelete == false()).all()
                        # 删除无用绑定
                        for fp in unused_fp:
                            unused_pp = ProductParams.query.filter(
                                ProductParams.PPid == fp.PPid,
                                ProductParams.isdelete == false()).first()
                            if unused_pp:
                                unused_pp.PRid = pp.PRid
                                instance_list.append(unused_pp)
                            fp.isdelete = True
                            instance_list.append(fp)

                    ppvidlist.append(ppv_instance.PPVid)
                    instance_list.append(ppv_instance)
                db.session.add_all(instance_list)
                unused_ppv = ProductParamsValue.query.filter(
                    ProductParamsValue.PPid == pp.PPid,
                    ProductParamsValue.PPVid.notin_(ppvidlist)).all()
                ProductParamsValue.query.filter(
                    ProductParamsValue.PPid == pp.PPid,
                    ProductParamsValue.PPVid.notin_(ppvidlist)).delete_(synchronize_session=False)

        return Success(message=msg, data={'ppid': pp.PPid})

    @token_required
    def list_pp(self):
        data = parameter_required(('prid',))
        if is_admin():
            _ = get_current_admin()
        elif is_user():
            user = get_current_user()
            if not user.USinWhiteList:
                raise AuthorityError('用户无权限，请联系管理员')
        else:
            raise AuthorityError
        prid = data.get('prid')
        product = Product.query.filter(Product.PRid == prid, Product.isdelete == false()).first_('产品已删除')
        pplist = ProductParams.query.filter(ProductParams.PRid == prid, ProductParams.isdelete == false()).order_by(
            ProductParams.PPsort.desc(), ProductParams.createtime.desc()).all()
        for pp in pplist:
            pp.fill('prname', product.PRname)
            # 产品参数填充
            self._fill_ppv(pp)
        return Success('获取成功', data=pplist)

    def _fill_ppv(self, pp):
        pvlist = ProductParamsValue.query.filter(
            ProductParamsValue.PPid == pp.PPid, ProductParamsValue.isdelete == false()).order_by(
            ProductParamsValue.createtime.desc()).all()

        for pv in pvlist:
            itemlist = []
            fps = FrontParams.query.filter(FrontParams.PPVid == pv.PPVid, FrontParams.isdelete == false()).all()
            for fp in fps:
                fpp = ProductParams.query.filter(ProductParams.PPid == fp.PPid,
                                                 ProductParams.isdelete == false()).first()
                if not fpp:
                    continue
                self._fill_ppv(fpp)
                itemlist.append(fpp)

            pv.fill('item', itemlist)
        pp.fill('ppvlist', pvlist)

    @admin_required
    def list_uc(self):
        admin = get_current_admin()
        uclist = UnitCategory.query.filter(UnitCategory.isdelete == false()).order_by(
            UnitCategory.UCsort.desc(), UnitCategory.createtime.desc()).all_with_page()
        for uc in uclist:
            self._fill_uc(uc)
        return Success('获取成功', data=uclist)

    @admin_required
    def get_uc(self):
        admin = get_current_admin()
        data = parameter_required(('ucid'), )
        uc = UnitCategory.query.filter(
            UnitCategory.UCid == data.get('ucid'), UnitCategory.isdelete == false()).first_('分类已删除')
        self._fill_uc(uc)
        return Success('获取成功', data=uc)

    def _fill_uc(self, uc):
        unlist = Unit.query.filter(Unit.isdelete == false(), Unit.UCid == uc.UCid).order_by(
            Unit.createtime.desc()).all()
        for un in unlist:
            if un.PRid:
                product = Product.query.filter(Product.isdelete == false(), Product.PRid == un.PRid).first()
                if not product:
                    continue
                un.fill('prname', product.PRname)
            if un.PCid:
                pc = ProductCategory.query.filter(
                    ProductCategory.isdelete == false(), ProductCategory.PCid == un.PCid).first()
                if not pc:
                    continue
                un.fill('pcname', pc.PCname)
            if un.PPVid:
                ppv = ProductParamsValue.query.filter(
                    ProductParamsValue.isdelete == false(), ProductParamsValue.PPVid == un.PPVid).first()
                if not ppv:
                    continue
                pp = ProductParams.query.filter(
                    ProductParams.isdelete == false(), ProductParams.PPid == ppv.PPid).first()
                if not pp:
                    continue

                un.fill('ppname', "{}-{}".format(pp.PPname, ppv.PPVvalue))
        uc.fill('unlist', unlist)

    @admin_required
    def set_uc(self):
        admin = get_current_admin()
        data = parameter_required()
        ucid, ucname, ucsort = data.get('ucid'), data.get('ucname'), data.get('ucsort')
        ucdict = {}
        if ucname:
            ucdict['UCname'] = ucname
        if ucsort:
            try:
                ucsort = int(ucsort)
            except:
                raise ParamsError('权重只能是整数')
            ucdict['UCsort'] = ucsort
        with db.auto_commit():
            if not ucid:
                if not ucname:
                    raise ParamsError('分类名缺失')
                ucdict['UCid'] = str(uuid.uuid1())
                ucinstance = UnitCategory.create(ucdict)
                msg = '添加成功'
            else:
                ucinstance = UnitCategory.query.filter(
                    UnitCategory.UCid == ucid, UnitCategory.isdelete == false()).first_('分类已删除')
                if data.get('delete'):
                    ucinstance.update({'isdelete': True})
                    msg = '删除成功'
                else:
                    ucinstance.update(ucdict)
                    msg = '更新成功'
            db.session.add(ucinstance)
        return Success(message=msg, data={'ucid': ucinstance.UCid})

    @admin_required
    def set_un(self):
        admin = get_current_admin()
        data = parameter_required()
        unid, ucid, unname, prid, ucrequired, ununit, ununitprice, untype, unlimit, unlimitmin, pcid, ppvid = data.get(
            'unid'), data.get('ucid'), data.get('unname'), data.get('prid'), data.get('ucrequired'), data.get(
            'ununit'), data.get('ununitprice'), data.get('untype'), data.get(
            'unlimit'), data.get('unlimitmin'), data.get('pcid'), data.get('ppvid')
        undict = {}
        if unname:
            undict['UNname'] = unname
        if ucid:
            uc = UnitCategory.query.filter(
                UnitCategory.UCid == ucid, UnitCategory.isdelete == false()).first_('分类已删除')
        undict['UCid'] = ucid
        if prid:
            product = Product.query.filter(Product.PRid == prid, Product.isdelete == false()).first_('商品已删除')
        undict['PRid'] = prid
        if pcid:
            pc = ProductCategory.query.filter(
                ProductCategory.PCid == pcid, ProductCategory.isdelete == false()).first_("商品分类已删除")
        undict['PCid'] = pcid
        if ununit:
            undict['UNunit'] = ununit
        if ppvid:
            ppv = ProductParamsValue.query.filter(
                ProductParamsValue.PPVid == ppvid, ProductParamsValue.isdelete == false()).first_('参数值已删除')
        undict['PPVid'] = ppvid
        if ununitprice:
            try:
                ununitprice = Decimal(ununitprice)
            except:
                raise ParamsError('单价只能是数字')
            undict['UNunitPrice'] = ununitprice
        if untype:
            try:
                untype = UnitType(int(untype)).value
            except:
                raise ParamsError('参数类型有误')
        undict['UNtype'] = untype or 0
        if unlimit:
            try:
                unlimit = Decimal(unlimit)
            except:
                raise ParamsError('最大值只能是数字')
        undict['UNlimit'] = unlimit or 0
        if unlimitmin:
            try:
                unlimitmin = Decimal(unlimitmin)
            except:
                raise ParamsError('最小值只能是数字')
            undict['UNlimitMin'] = unlimitmin or 0
        undict['UCrequired'] = bool(ucrequired)

        with db.auto_commit():
            if not unid:
                if not unname:
                    raise ParamsError('计算名缺失')
                if not ununitprice:
                    raise ParamsError('单价缺失')
                if not (pcid or prid):
                    raise ParamsError('商品或者商品分类必须指定')

                undict['UNid'] = str(uuid.uuid1())
                uninstance = Unit.create(undict)
                msg = '添加成功'
            else:
                uninstance = Unit.query.filter(
                    Unit.UNid == unid, Unit.isdelete == false()).first_('部件已删除')
                if data.get('delete'):
                    uninstance.update({'isdelete': True})
                    msg = '删除成功'
                else:
                    uninstance.update(undict, null='not ignore')
                    msg = '更新成功'
            db.session.add(uninstance)
        return Success(message=msg, data={'ucid': uninstance.UNid})

    @token_required
    def calculation(self):
        """通过参数计算价格"""
        if not is_user():
            raise AuthorityError

        user = get_current_user()
        if not user.USinWhiteList:
            raise AuthorityError

        data = parameter_required(('prid', 'params'))
        prid = data.get('prid')
        product = Product.query.filter(Product.PRid == prid, Product.isdelete == false()).first_('商品已删除')
        params = data.get('params')
        # 参数分析
        wide = 0
        high = 0
        area = 0
        pillarshigh = 0
        perimeter = 0
        minner = 0
        ppvidlist = []
        try:
            for param in params:
                if param.get('ppvid'):
                    ppvidlist.append(param.get('ppvid'))
                pptype = int(param.get('pptype'))
                if pptype == ProductParamsType.wide.value:
                    wide = Decimal(param.get('value'))
                elif pptype == ProductParamsType.high.value:
                    high = Decimal(param.get('value'))
                elif pptype == ProductParamsType.pillarshigh.value:
                    pillarshigh = Decimal(param.get('value'))
        except:
            raise ParamsError('参数异常')

        area = wide * high
        perimeter = 2 * (wide + high)
        minner = min(wide, high)

        # 获取价格系数
        ul = UserLevelSetting.query.filter(
            UserLevelSetting.ULSlevel == user.USlevel, UserLevelSetting.isdelete == false()).first()
        coefficient = Decimal(ul.ULScoefficient if ul else 1)
        # 先计算固定成本
        filter_proudct = [or_(and_(Unit.PRid == product.PRid, ), Unit.PRid == None),
                          Unit.PCid == product.PCid,
                          Unit.isdelete == false(), UnitCategory.isdelete == false()]
        # 成本
        cost = Decimal('0')
        cost_item_list = []
        # unlist = Unit.query.join(UnitCategory, UnitCategory.UCid == Unit.UCid).filter(*filter_proudct,
        #                                                                               Unit.UCrequired == True).all()
        # for un in unlist:
        #     cost += self._add_price(cost, cost_item_list, un, coefficient)
        # 计算除人工费的其他费用
        unlist = Unit.query.join(UnitCategory, UnitCategory.UCid == Unit.UCid).filter(
            *filter_proudct, Unit.UNtype != UnitType.cost.value,
                             Unit.UNtype != UnitType.mount.value, or_(Unit.PPVid == None, Unit.PPVid.in_(ppvidlist))
        ).order_by(UnitCategory.UCsort.desc(), Unit.UNtype.asc(), Unit.UNlimit.asc()).all()

        for un in unlist:
            if un.UCrequired == True:
                cost += self._add_price(cost, cost_item_list, un, coefficient)
                continue
            if un.UNtype == UnitType.wide.value:
                if self._check_limit(wide, un):
                    cost += self._add_price(cost, cost_item_list, un, coefficient, wide)
                continue
            elif un.UNtype == UnitType.high.value:
                if self._check_limit(high, un):
                    cost += self._add_price(cost, cost_item_list, un, coefficient, high)
                continue
            elif un.UNtype == UnitType.pillarshigh.value:
                if self._check_limit(pillarshigh, un):
                    cost += self._add_price(cost, cost_item_list, un, coefficient, pillarshigh)
                continue
            elif un.UNtype == UnitType.perimeter.value:
                if self._check_limit(perimeter, un):
                    cost += self._add_price(cost, cost_item_list, un, coefficient, perimeter)
                continue
            elif un.UNtype == UnitType.area.value:
                if self._check_limit(area, un):
                    cost += self._add_price(cost, cost_item_list, un, coefficient, area)
                continue
            elif un.UNtype == UnitType.alarea.value:
                if self._check_limit(area, un):
                    cost += self._add_price(cost, cost_item_list, un, coefficient, perimeter)
            elif un.UNtype == UnitType.minner.value:
                if self._check_limit(minner, un):
                    cost += self._add_price(cost, cost_item_list, un, coefficient, minner)
                continue
            else:
                cost += self._add_price(cost, cost_item_list, un, coefficient)
                continue
        # 计算电源费用 todo 限制产品
        if wide and high:
            cost += self._caculate_power(ppvidlist, wide, high, cost_item_list, coefficient)
        # 计算人工费等依赖成本的费用
        unlist = Unit.query.join(UnitCategory, UnitCategory.UCid == Unit.UCid).filter(
            *filter_proudct, Unit.UCrequired == False, Unit.UNtype == UnitType.cost.value,
            or_(Unit.PPVid == None, Unit.PPVid.in_(ppvidlist))
        ).order_by(Unit.UNtype.asc(), Unit.UNlimit.asc()).all()
        # mount = Decimal(0)
        ex_cost = Decimal(0)

        current_app.logger.info('get cost = {}'.format(cost))
        for un in unlist:
            ex_cost += self._add_ex_cost(cost, cost_item_list, un, coefficient)
        current_app.logger.info('get ex cost = {}'.format(ex_cost))
        mount = cost + ex_cost
        current_app.logger.info('get mount = {}'.format(mount))

        # 计算 依赖总额的费用
        unlist = Unit.query.join(UnitCategory, UnitCategory.UCid == Unit.UCid).filter(
            *filter_proudct, Unit.UCrequired == False, Unit.UNtype == UnitType.mount.value,
            or_(Unit.PPVid == None, Unit.PPVid.in_(ppvidlist))
        ).order_by(Unit.UNtype.asc(), Unit.UNlimit.asc()).all()

        final_mount = mount
        for un in unlist:
            final_mount += self._add_ex_cost(mount, cost_item_list, un, coefficient)

        current_app.logger.info('get final_mount = {}'.format(final_mount))

        cost_item_list.append(('合计', '', '', '', final_mount))
        # 建立表格 todo
        filepath, filename = self._create_table(cost_item_list)
        cost_dict_list = [{'ucname': item[0], 'unname': item[1],
                           'ununit': item[2], 'ununitprice': item[3], 'mount': item[4]} for item in cost_item_list]

        # 创建查询记录
        with db.auto_commit():
            uh = UserHistory.create({
                "UHid": str(uuid.uuid1()),
                "USid": user.USid,
                "UHparams": json.dumps(params, cls=JSONEncoder),
                "PRid": prid,
                "UHprice": final_mount,
                "UHcost": json.dumps(cost_dict_list, cls=JSONEncoder),
                "UHfile": filename,
                "UHabs": filepath,
            })
            db.session.add(uh)
        return Success('询价成功', data={"mount": mount, "uhid": uh.UHid})

    def _add_price(self, cost, cost_item_list, un, coefficient, param=1):
        unitprice = Decimal(un.UNunitPrice) * coefficient
        # cost_item_list.append("{}: {} 元 {}".format(un.UNname, unitprice, un.UNunit))
        cost_mount = (unitprice * param).quantize(Decimal("0.00"))
        uc = UnitCategory.query.filter(UnitCategory.UCid == un.UCid, UnitCategory.isdelete == false()).first()
        ucname = uc.UCname if uc else ""
        cost_item_list.append((ucname, un.UNname, un.UNunit, unitprice, cost_mount))
        # cost += cost_mount
        return cost_mount

    def _add_ex_cost(self, cost, cost_item_list, un, coefficient):
        unitprice = Decimal(un.UNunitPrice) * coefficient
        # cost_item_list.append("{}: {} 元 {}".format(un.UNname, unitprice, un.UNunit))
        cost_mount = (unitprice * cost).quantize(Decimal("0.00"))
        uc = UnitCategory.query.filter(UnitCategory.UCid == un.UCid, UnitCategory.isdelete == false()).first()
        ucname = uc.UCname if uc else ""
        cost_item_list.append((ucname, un.UNname, "", "", cost_mount))
        # cost += cost_mount
        return cost_mount

    @token_required
    def download(self):
        """导出"""
        data = parameter_required(('uhid',))
        uhid = data.get('uhid')
        uh = UserHistory.query.filter(UserHistory.UHid == uhid, UserHistory.isdelete == false()).first_('查询记录已删除')

        if is_user():
            uhcost = json.loads(uh.UHcost)
            return Success('获取成功', data=uhcost)

        filepath, filename = uh.UHabs, uh.UHfile,
        if not os.path.isfile(os.path.join(filepath, filename)):
            raise ParamsError('报表未能成功导出')
        return send_from_directory(filepath, filename, as_attachment=True, cache_timeout=-1)
        # return send_templates

    def _create_table(self, rows):
        headers = ['灯箱部件', '物料名称', '单位', '单价', '合计']
        data = tablib.Dataset(*rows, headers=headers, title='询价导出页面')
        now = datetime.now()
        aletive_dir = 'img/xls/{year}/{month}/{day}'.format(year=now.year, month=now.month, day=now.day)
        abs_dir = os.path.join(BASEDIR, 'img', 'xls', str(now.year), str(now.month), str(now.day))
        xls_name = self._generic_omno() + '.xls'
        aletive_file = '{dir}/{xls_name}'.format(dir=aletive_dir, xls_name=xls_name)
        abs_file = os.path.abspath(os.path.join(BASEDIR, aletive_file))
        if not os.path.isdir(abs_dir):
            os.makedirs(abs_dir)
        with open(abs_file, 'wb') as f:
            f.write(data.xls)
        return abs_dir, xls_name
        # return send_from_directory(abs_dir, xls_name, as_attachment=True, cache_timeout=-1)

    @staticmethod
    def _generic_omno():
        """生成订单号"""
        return str(time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))) + \
               str(time.time()).replace('.', '')[-7:] + str(random.randint(1000, 9999))

    def _check_limit(self, params, un):
        return ((un.UNlimit and params <= un.UNlimit) or not un.UNlimit) and (
                (un.UNlimitMin and params > un.UNlimitMin) or not un.UNlimitMin)

    def _caculate_power(self, ppvidlist, wide, high, cost_item_list, coefficient):
        # gunlun_list = [
        #     '0c3f8a78-d171-11ea-877a-fa163e8df331',
        #     '97db244e-d170-11ea-b88d-fa163e8df331',
        #     'b700c132-d169-11ea-b88d-fa163e8df331',
        #     'e7300f40-d171-11ea-877a-fa163e8df331'
        # ]
        # 固定边长
        loap_len = Decimal(0.12)
        first_num_gunlun = Decimal(1.2)
        first_num_no_gunlun = Decimal(1.2)
        second_num_gunlun = Decimal(2)
        second_num_no_gunlun = Decimal(5)
        view_wide = wide - loap_len
        view_high = high - loap_len
        # isback = False
        current_app.logger.info('is view_wide {}'.format(view_wide))
        current_app.logger.info('is view_high {}'.format(view_high))
        view_min = min(view_high, view_wide)

        import configparser
        conf = configparser.ConfigParser()
        conf_path = os.path.join(BASEDIR, 'inquiry', 'config', 'lightprice.cfg')
        current_app.logger.info('get file = {}'.format(os.path.isfile(conf_path)))
        conf.read(conf_path)
        current_app.logger.info('get cfg {}'.format(conf.sections()))

        gunlun_list = json.loads(conf.get('gunlun', 'gunlun'))
        back_list = json.loads(conf.get('back', 'back'))
        side_list = json.loads(conf.get('side', 'side'))
        isgunlun = bool(list(set(ppvidlist).intersection(set(gunlun_list))))
        isback = bool(list(set(ppvidlist).intersection(set(back_list))))
        isside = bool(list(set(ppvidlist).intersection(set(side_list))))
        current_app.logger.info('is gunlun {}'.format(isgunlun))

        if not isback and not isside:
            return Decimal('0')

        if isgunlun:
            if not isback:
                if view_wide <= first_num_gunlun:
                    # 单侧打光
                    num_light = (view_wide / Decimal(0.1) - Decimal(0.3))
                    test_light = "单侧高边侧光源："
                elif view_wide <= second_num_gunlun:
                    # 双侧打光
                    test_light = "双侧高边侧光源："
                    num_light = (view_wide / Decimal(0.1) - Decimal(0.3)) * Decimal(2)
                else:
                    # 背光源

                    num_light = (view_wide / Decimal(0.2) - Decimal(0.3)).quantize(Decimal("0")) * (
                            view_high / Decimal(0.2) - Decimal(0.3)).quantize(Decimal("0"))
                    test_light = self._caculat_num(view_high, view_wide, num_light)
            else:
                # 背光源

                num_light = (view_wide / Decimal(0.2) - Decimal(0.3)).quantize(Decimal("0")) * (
                        view_high / Decimal(0.2) - Decimal(0.3)).quantize(Decimal("0"))

                test_light = self._caculat_num(view_high, view_wide, num_light)
        else:
            if not isback:
                if view_min <= first_num_no_gunlun:
                    # 单侧打光
                    test_light = "单侧短边侧光源："
                    num_light = (view_min / Decimal(0.1) - Decimal(0.3))
                elif view_min <= second_num_no_gunlun:
                    # 双侧打光
                    test_light = "双侧短边侧光源:"
                    num_light = (view_min / Decimal(0.1) - Decimal(0.3)) * Decimal(2)
                else:
                    # 背光源

                    num_light = (view_wide / Decimal(0.2) - Decimal(0.3)).quantize(Decimal("0")) * (
                            view_high / Decimal(0.2) - Decimal(0.3)).quantize(Decimal("0"))
                    test_light = self._caculat_num(view_high, view_wide, num_light)

            else:
                # 背光源

                num_light = (view_wide / Decimal(0.2) - Decimal(0.3)).quantize(Decimal("0")) * (
                        view_high / Decimal(0.2) - Decimal(0.3)).quantize(Decimal("0"))
                test_light = self._caculat_num(view_high, view_wide, num_light)

        num_light = Decimal(num_light).quantize(Decimal("0"))
        current_app.logger.info('is num_light {}'.format(num_light))
        power = (num_light * Decimal(2.5)).quantize(Decimal("0.00"))
        unit_price_light = (Decimal(conf.get('unit', 'price')) * coefficient).quantize(Decimal("0.00"))
        price_light = (num_light * unit_price_light).quantize(Decimal("0.00"))
        num_power, price_power, rate_power, unit_price = self._get_power(conf, power, coefficient)

        cost_item_list.append(('光源', "{}{}颗".format(test_light, num_light), "元/颗", unit_price_light, price_light))
        cost_item_list.append(('光源', "{}W 电源 * {} 个".format(rate_power, num_power), "元/个",
                               unit_price.quantize(Decimal("0.00")), price_power.quantize(Decimal("0.00"))))
        unit_price_loubao = (Decimal(conf.get('loubao', 'price')) * coefficient).quantize(Decimal("0.00"))
        cost_item_list.append(('光源', '漏保', '元/个', unit_price_loubao, unit_price_loubao))
        unit_price_dianliao = (Decimal(conf.get('dianliao', 'price1') if high * wide <= Decimal(4) else conf.get(
            'dianliao', 'price2')) * coefficient).quantize(Decimal("0.00"))
        cost_item_list.append(('光源', '电料', '元/台', unit_price_dianliao, unit_price_dianliao))

        return price_power + unit_price_dianliao + unit_price_loubao + price_light

    def _get_power(self, conf, power, coefficient):
        sections = conf.sections()
        sections = sorted([item for item in sections if 'w' in item])
        for i in range(1, int(math.ceil(power / Decimal(75))) + 1):
            for section in sections:
                num_power = Decimal(i)
                rate_power = Decimal(conf.get(section, 'rate'))
                if Decimal(rate_power * i) >= power:
                    unit_price = Decimal(conf.get(section, 'price')) * coefficient
                    price_power = unit_price * i
                    return num_power, price_power, rate_power, unit_price

    def _caculat_num(self, high, wide, num_light):
        if high < Decimal(1) and wide > high:
            pai = (high / Decimal(0.2)).quantize(Decimal("0"))
            tiao = ((wide / Decimal(0.2)).quantize(Decimal("0")) / Decimal(25)).quantize(Decimal('0'))
            ke = (wide / Decimal(0.2)).quantize(Decimal("0"))
            # ke = high /
            return '背光源：{} * {} 条 * {}颗 = 总共 {}颗'.format(pai, tiao, ke, num_light)
        else:
            pai = (wide / Decimal(0.2)).quantize(Decimal("0"))
            tiao = math.ceil(float(
                (high / Decimal(0.2)).quantize(Decimal("0")) / Decimal(25)))
            ke = (high / Decimal(0.2)).quantize(Decimal("0"))
            current_app.logger.info('get pai {} , get tiao {} get ke {}'.format(pai, tiao, ke))
            # ke = high /
            return '背光源：{} * {} 条 * {}颗 = 总共 {}颗'.format(tiao, pai, ke, num_light)
