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
from weshop.forms.shop import ShopSetting, BrandSetting
from weshop.utils import devices
from weshop.utils.devices import checkMobile
from ..models import db, User, Brand, Shop
from ..forms import SigninForm
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
    url = request.values.get('current_url')
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
    do = request.args.get("do", "normal")
    if do == 'normal':
        brands = Brand.query.filter(Brand.status == 1).all()
    else:
        brands = Brand.query.filter(Brand.status == 0).all()
    return render_template('brand/manage.html', brands=brands, do=do)


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
    shops = Shop.query.filter(Shop.brand_id == bid)
    return render_template('brand/shop_list.html', shops=shops, brand=brand, bid=bid)


@bp.route('/account_list', methods=['GET', 'POST'])
def account_list():
    """商户账户管理"""
    bid = int(request.args.get("bid", 0))
    brand = Brand.query.get(bid)
    for i in brand.brandaccounts:
        print '-' * 10, i.name, i.id, bid
    shops = Shop.query.filter(Shop.brand_id == bid)
    brandaccounts = brand.brandaccounts
    return render_template('brand/account_list.html', shops=shops, brand=brand, bid=bid, brandaccounts=brandaccounts)
