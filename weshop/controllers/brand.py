# !/usr/bin/env python
# -*- coding: UTF-8 -*-
import json
import os
import string
import re, urllib2
import random
from PIL import Image
from coverage.html import STATIC_PATH
from flask import render_template, Blueprint, redirect, url_for, g, session, request, \
    make_response, current_app, send_from_directory
from weshop import csrf
from weshop.forms.shop import ShopSetting, BrandSetting, BrandAccountSetting
from weshop.utils import devices
from weshop.utils.devices import checkMobile
from ..models import db, User, Brand, Shop
from ..forms import SigninForm, RegisterForm
from ..utils.permissions import require_user, require_visitor
from ..utils.uploadsets import images, random_filename, process_question, avatars

bp = Blueprint('brand', __name__)


@bp.route('/', methods=['GET', 'POST'])
def index():
    """"""
    do = request.args.get("do")
    if do == 'businessdisplay':
        return render_template('shop/manage.html')
    return render_template('shop/select_brand.html')


@bp.route('/show', methods=['GET', 'POST'])
def show():
    """"""
    id = int(request.args.get("id", 0))
    brand = Brand.query.get(id)
    if brand:
        return render_template('brand/show.html', brand=brand)
    else:
        return render_template('brand/error.html')


@bp.route('/add', methods=['GET', 'POST'])
def brand_add():
    """添加品牌"""
    shop = {}
    form = BrandSetting()
    if form.is_submitted():
        print request.form
        exist = Brand.query.filter(Brand.name == form.brand.data).first()
        if exist:
            return render_template('account/error.html', error='您输入的品牌已存在！')
        else:
            brand = Brand(name=form.brand.data, industry_1=form.industry_1.data.decode('utf-8'),
                          industry_2=form.industry_2.data.decode('utf-8'), intro=form.intro.data, image=form.image.data,
                          thumb=form.thumb.data)
            db.session.add(brand)
            db.session.commit()
            session['brand'] = brand.id
            url = request.referrer
            return render_template('account/ok.html', tip='添加品牌成功，请添加一个门店！', url=url)
    return render_template('brand/setting.html', shop=shop, form=form)


@bp.route('/modify', methods=['GET', 'POST'])
def brand_modify():
    """修改品牌"""
    shop = {}
    url = request.values.get('current_url')
    print url
    brand_id = int(request.args.get("id", 0))
    act = request.args.get('act', '')
    if not brand_id:
        return render_template('account/error.html', error='页面不存在！')
    if act == 'audits':
        brand = Brand.query.filter(Brand.id == brand_id).first()
        brand.status = int(request.args.get('status', 1))
        if brand.status == 0:
            tip = '禁用成功'
        else:
            tip = '启用成功'
        db.session.add(brand)
        db.session.commit()
        return render_template('account/ok.html', tip=tip, url='manage?do=normal')
    form = BrandSetting()
    brand = Brand.query.get_or_404(brand_id)
    form.brand.data = brand.name
    form.industry_1.data = brand.industry_1
    form.industry_2.data = brand.industry_2
    form.intro.data = brand.intro
    form.image.data = brand.image
    form.thumb.data = brand.thumb
    if form.is_submitted():
        print request.form
        name = form.brand.data
        if name == "test":
            return render_template('account/error.html', error='您输入的品牌已存在！')
        else:
            return render_template('account/ok.html', tip='添加品牌成功，请添加一个门店！', url=url)
    return render_template('brand/setting.html', shop=shop, form=form)


@bp.route('/manage', methods=['GET', 'POST'])
def manage():
    """管理品牌"""
    curruser = g.user
    do = request.args.get("do", "normal")
    if do == 'normal':
        if curruser.role == 'admin':
            brands_query = Brand.query.filter(Brand.status == 1)
        else:
            brands_query = curruser.brandaccounts.filter(Brand.status == 1)
    else:
        if curruser.role == 'admin':
            brands_query = Brand.query.filter(Brand.status == 0)
        else:
            brands_query = curruser.brandaccounts.filter(Brand.status == 0)

    page = request.args.get('page', 1, type=int)
    pagination = brands_query.order_by(Brand.create_at.desc()).paginate(
        page, per_page=current_app.config['FLASKY_PER_PAGE'],
        error_out=False)
    brands = pagination.items

    return render_template('brand/manage.html', brands=brands, do=do, pagination=pagination)


@bp.route('/search', methods=['GET', 'POST'])
def brand_search():
    """搜索品牌"""
    message = "message"
    name = request.args.get("name", None)
    return json.dumps({"message": [], "redirect": "", "type": "tips"})


@bp.route('/shop', methods=['GET', 'POST'])
def shop_list():
    """门店管理"""
    bid = int(request.args.get("bid", 0))
    brand = Brand.query.get(bid)
    shops_query = Shop.query.filter(Shop.brand_id == bid)
    page = request.args.get('page', 1, type=int)
    pagination = shops_query.order_by(Shop.id.desc()).paginate(
        page, per_page=current_app.config['FLASKY_PER_PAGE'],
        error_out=False)
    shops = pagination.items

    return render_template('brand/shop_list.html', shops=shops, brand=brand,
                           bid=bid, pagination=pagination)


@bp.route('/account', methods=['GET', 'POST'])
def account():
    """商户账户管理"""
    bid = int(request.args.get("bid", 0))
    uid = int(request.args.get('uid', 0))
    act = request.args.get('act')
    do = request.args.get("do", "normal")
    brand = Brand.query.get(bid)
    shops = Shop.query.filter(Shop.brand_id == bid).all()
    user = User.query.get(uid)

    form = RegisterForm()

    brand_brandaccounts = ''
    if brand:
        brand_brandaccounts = brand.brandaccounts

    if act == 'delete':
        if user:
            if user.brandaccounts.filter(Brand.id == bid).first():
                user.brandaccounts.remove(brand)
            for shop in shops:
                if user.shopaccounts.filter(Shop.id == shop.id).first():
                    user.shopaccounts.remove(shop)
            user.role = 'common'
            db.session.add(user)
            db.session.commit()
            url = request.referrer
            return render_template('account/ok.html', tip="删除成功！", url=url)
    elif act == 'modify':
        values = request.form
        if values:
            url = request.values.get('current_url')

            user_exist = User.query.filter(User.name == form.name.data).first()
            user_exist.name = form.name.data
            user_exist.email = form.email.data
            user_exist.mobile = form.mobile.data
            user_exist.password = form.password.data
            user_exist.role = 'shopowner'

            user_exist.hash_password()
            user_exist.gene_token()
            db.session.add(user_exist)

            bexist = brand.brandaccounts.filter(User.name == form.name.data).first()
            if not bexist:
                brand.brandaccounts.append(user_exist)

            # 添加授权账户分店
            shopvalues = []
            for value in values:
                if value.startswith('shop'):
                    shopvalues.append(int(values.get(value)))
            if shopvalues:
                for shop in shops:
                    sexist = shop.shopaccounts.filter(User.name == form.name.data).first()
                    if shop.id in shopvalues and not sexist:
                        print '-' * 10, shopvalues, shop.id,
                        shop.shopaccounts.append(user_exist)
            else:
                for shop in shops:
                    sexist = shop.shopaccounts.filter(User.name == form.name.data).first()
                    if sexist:
                        shop.shopaccounts.remove(user_exist)
            db.session.commit()

            return render_template('account/ok.html', tip='修改商户帐号成功！', url=url)

        return render_template('brand/account_detail.html', brand=brand, bid=bid, useraccount=user, form=form,
                               shops=shops,
                               brand_brandaccounts=brand_brandaccounts)

    elif act == 'add':
        values = request.form
        if values:
            url = request.values.get('current_url')
            exist = User.query.filter(User.name == form.name.data).first()
            if exist:
                return render_template('account/error.html', error='您输入的商户帐号已存在！')
            else:
                if len(form.mobile.data) or not (form.mobile.data).isdigit():
                    return render_template('account/error.html', error='您输入的用户名不正确！')
                user_new = User(name=form.name.data, email=form.email.data, mobile=form.mobile.data,
                                password=form.password.data)
                user_new.hash_password()
                user_new.gene_token()
                db.session.add(user_new)
                brand.brandaccounts.append(user_new)

                # 添加授权账户分店
                shopvalues = []
                for value in values:
                    if value.startswith('shop'):
                        shopvalues.append(int(values.get(value)))

                if shopvalues:
                    for shop in shops:
                        if shop.id in shopvalues:
                            shop.shopaccounts.append(user_new)
                db.session.commit()

                return render_template('account/ok.html', tip='添加商户帐号成功！', url=url)

        return render_template('brand/account_detail.html', brand=brand, bid=bid, useraccount=user, form=form,
                               shops=shops,
                               brand_brandaccounts=brand_brandaccounts)
    elif act == 'showall':
        user_session = User.query.get(session['user_id'])
        if user_session.role == 'admin':
            users = User.query.filter(User.role != 'admin').all()
        else:
            # 仅仅获取当前品牌下的账户
            users = brand.brandaccounts.all()
        return render_template('brand/account_list.html', brand=brand, bid=bid,
                               brand_brandaccounts=users)

    return render_template('brand/account_list.html', brand=brand, bid=bid,
                           brand_brandaccounts=brand_brandaccounts, do=do)


@bp.route('/account/delete', methods=['GET'])
def account_delete():
    user_id = int(request.args.get("user_id", 0))
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    url = request.referrer
    return render_template('account/ok.html', tip="删除成功！", url=url)
