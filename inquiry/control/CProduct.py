import uuid
from decimal import Decimal

from sqlalchemy import false

from inquiry.extensions.error_response import ParamsError, AuthorityError
from inquiry.extensions.interface.user_interface import admin_required, get_current_admin, is_admin, get_current_user, \
    is_user
from inquiry.extensions.params_validates import parameter_required
from inquiry.extensions.register_ext import db
from inquiry.extensions.success_response import Success
from inquiry.models import Product, ProductCategory, ProductParams, ProductParamsValue, FrontParams


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
                product = Product.create({product_dict})

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

    def list(self):
        data = parameter_required()
        filter_args = [Product.isdelete == false(), ProductCategory.isdelete == false()]
        if is_admin:
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

    def get(self):
        if is_admin:
            _ = get_current_admin()
        elif is_user():
            user = get_current_user()
            if not user.USinWhiteList:

                raise AuthorityError('用户无权限，请联系管理员')
        else:
            raise AuthorityError

        data = parameter_required('prid')
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
                pc = Product.create({pc_dict})

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
        if pprequired:
            pp_dict['PCicon'] = pprequired
        if ppsort:
            try:
                ppsort = int(ppsort)
            except:
                raise ParamsError('权重只能是整数')
            pp_dict['PPsort'] = ppsort
        with db.auto_commit():
            if not ppid:
                if not prid:
                    raise ParamsError('需绑定产品')
                if not ppname:
                    raise ParamsError('缺少参数名')
                pp_dict['PPid'] = str(uuid.uuid1())
                pp = ProductParams.create({pp_dict})

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
                ProductParamsValue.query.filter(ProductParams.PPid == pp.PPid).delete_()
                instance_list = []
                for ppv in ppvlist:
                    ppvvalue = ppv.get('ppvvalue')
                    ppvprice = ppv.get('ppvprice', 0)
                    try:
                        ppvprice = Decimal(str(ppvprice))
                    except:
                        raise ParamsError('单价只能是数字')
                    ppv_instance = ProductParamsValue.create({
                        "PPVid": str(uuid.uuid1()), 'PPid': pp.PPid, "PPVvalue": ppvvalue, "PPVprice": ppvprice})
                    if ppv.get('frontid'):
                        front = ProductParams.query.filter(
                            ProductParams.PPid == ppv.get('frontid')).first_("后续参数已删除")

                        fp_instance = FrontParams.create({
                            "FPid": str(uuid.uuid1()),
                            "PPid": front.PPid,
                            "PPVid": ppv_instance.PPVid,

                        })
                        instance_list.append(fp_instance)
                    instance_list.append(ppv_instance)
                db.session.add_all(instance_list)

        return Success(message=msg, data={'ppid': pp.PPid})


    def list_pp(self):
        data = parameter_required('prid')
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


    def _fill_ppv(self, pp):
        pvlist = ProductParamsValue.query.filter(
            ProductParamsValue.PPid == pp.PPid, ProductParamsValue.isdelete == false()).order_by(
            ProductParamsValue.createtime.desc()).all()
        for pv in pvlist:

            fp = FrontParams.query.filter(FrontParams.PPVid == pv.PPVid, FrontParams.isdelete ==false()).all()
            fpp = ProductParams.query.filter(ProductParams.PPid == fp.PPid, ProductParams.isdelete == false()).first()
            if not fpp:
                continue

