import uuid
from decimal import Decimal

from flask import request
from sqlalchemy import false, or_

from inquiry.config.enums import UnitType, ProductParamsType
from inquiry.extensions.error_response import ParamsError, AuthorityError
from inquiry.extensions.interface.user_interface import admin_required, get_current_admin, is_admin, get_current_user, \
    is_user, token_required
from inquiry.extensions.params_validates import parameter_required
from inquiry.extensions.register_ext import db
from inquiry.extensions.success_response import Success
from inquiry.models import Product, ProductCategory, ProductParams, ProductParamsValue, FrontParams, UnitCategory, Unit, \
    UserLevelSetting


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
        if pcurl:
            pc_dict['PCurl'] = pcurl
        if pcurl:
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
                    pc.update(pc_dict)
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
            'pptype'), data.get('ppremarks'), data.get('ppunit'), data.get('ppsort'), data.get('ppvlist')
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
        if ppunit:
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
                    pp.update(pp_dict)
                    msg = '编辑成功'

            db.session.add(pp)
            if ppvlist:
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
                    if ppv.get('frontid') and ppv.get('frontid') != pp.PPid:

                        front = ProductParams.query.filter(
                            ProductParams.PPid == ppv.get('frontid')).first_("后续参数已删除")
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
                        front.PRid = ""
                        instance_list.append(front)
                    ppvidlist.append(ppv_instance.PPVid)
                    instance_list.append(ppv_instance)
                db.session.add_all(instance_list)
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
                fpp = ProductParams.query.filter(ProductParams.PPid == fp.PPid, ProductParams.isdelete == false()).first()
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
        data = parameter_required(('ucid'),)
        uc = UnitCategory.query.filter(
            UnitCategory.UCid ==data.get('ucid'), UnitCategory.isdelete == false()).frist_('分类已删除')
        self._fill_uc(uc)
        return Success('获取成功', data=uc)


    def _fill_uc(self, uc):
        unlist = Unit.query.filter(Unit.isdelete == false(), Unit.UCid == uc.UCid).all()
        for un in unlist:
            if un.PRid:
                product = Product.query.filter(Product.isdelete == false(), Product.PRid == un.PRid).first()
                if not product:
                    continue
                un.fill('prname', product.PRname)
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
        unid, ucid, unname, prid, ucrequired, ununit, ununitprice, untype, unlimit, pcid = data.get('unid'), data.get(
            'ucid'), data.get('unname'), data.get('prid'), data.get('ucrequired'), data.get('ununit'), data.get(
            'ununitprice'), data.get('unlimit'), data.get('untype'), data.get('pcid')
        undict = {}
        if unname:
            undict['UNname'] = unname
        if ucid:
            uc = UnitCategory.query.filter(
                UnitCategory.UCid == ucid, UnitCategory.isdelete == false()).first_('分类已删除')
            undict['UCid'] = uc.UCid
        if prid:
            product = Product.query.filter(Product.PRid== prid, Product.isdelete == false()).first_('商品已删除')
            undict['PRid'] = product.PRid
        if pcid:
            pc = ProductCategory.query.filter(
                ProductCategory.PCid == pcid, ProductCategory.isdelete == false()).first_("商品分类已删除")
            ununit['PCid'] = pc.PCid
        if ununit:
            undict['UNunit'] = ununit
        if ununitprice:
            try:
                ununitprice = Decimal(ununitprice)
            except:
                raise ParamsError('单价只能是数字')
            undict['UNunitPrice'] = ununitprice
        if untype:
            # todo  enum
            try:
                untype = UnitType(int(untype)).value
            except:
                raise ParamsError('参数类型有误')
            undict['UNtype'] = untype
        if unlimit:
            try:
                unlimit = Decimal(unlimit)
            except:
                raise ParamsError('最大值只能是数字')
            undict['UNlimit'] = unlimit
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
                    uninstance.update(undict)
                    msg = '更新成功'
            db.session.add(uninstance)
        return Success(message=msg, data={'ucid': uninstance.UNid})

    @token_required
    def calculation(self):
        """通过参数计算价格"""
        if not is_user():
            raise AuthorityError

        user = get_current_admin()
        if not user.USinWhiteList:
            raise AuthorityError

        data = parameter_required(('prid', 'params'))
        prid = data.get('prid')
        product = Product.query.filter(Product.PRid == prid, Product.isdelete == false()).first_('商品已删除')
        params = data.get('params')
        # 获取价格系数
        ul = UserLevelSetting.query.filter(
            UserLevelSetting.ULSlevel == user.USlevel, UserLevelSetting.isdelete == false()).first()
        coefficient = Decimal(ul.ULScoefficient if ul else 1)
        # 先计算固定成本
        filter_proudct = [or_(Unit.PRid == product.PRid, Unit.PCid == product.PCid), Unit.isdelete == false()]
        # 总价
        mount = Decimal('0')
        mount_item_list = []
        unlist = Unit.query.filter(*filter_proudct, Unit.UCrequired == True).all()
        for un in unlist:
            unitprice = Decimal(un.UNunitPrice) * coefficient
            mount_item_list.append("{}: {} 元 {}".format(un.UNname, unitprice, un.UNunit))
            mount += unitprice

    @token_required
    def download(self):
        """导出"""
        pass

    @admin_required
    def useristory(self):
        """用户查询记录"""
        pass