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
from ..models import db, User, Brand, Shop, Discount
from ..forms import SigninForm
from ..utils.permissions import require_user, require_visitor
from ..utils.uploadsets import images, random_filename, process_question, avatars

bp = Blueprint('shop', __name__)


@bp.route('/select', methods=['GET', 'POST'])
def select():
    """选择门店"""
    # TODO user_id
    brands = Brand.query.all()

    act = request.args.get("act")
    if act == 'discount':
        handle = "管理优惠"
    elif act == 'ticket_record':
        handle = "领券记录"
    elif act == 'account':
        handle = "商家账户"
    elif act == 'checkout':
        handle = '绑收银台'
    elif act == 'manage':
        handle = '管理门店'
    else:
        handle = "管理门店"
    return render_template('shop/select_brand.html', handle=handle, act=act, brands=brands)


@bp.route('/qrcode', methods=['GET', 'POST'])
def qrcode():
    """管理二维码"""
    # TODO user_id
    return render_template('shop/qrcode.html')


@bp.route('/upload', methods=['GET', 'POST'])
def upload():
    """管理二维码"""
    # TODO user_id
    return render_template('shop/upload.html')


@bp.route('/setting', methods=['GET', 'POST'])
def setting():
    """门店发布、编辑"""
    act = request.args.get("act")
    bid = int(request.args.get("bid", 0))
    if act == "publish":
        form = ShopSetting()
        if not session.get("brand"):
            bid = int(request.args.get("bid", 0))
            session['brand'] = bid
        else:
            bid = session['brand']
        brandinfo = Brand.query.get(bid)
        brandForm = BrandSetting(brand=brandinfo.name, intro=brandinfo.intro, image=brandinfo.image,
                                 thumb=brandinfo.thumb, industry_1=brandinfo.industry_1,
                                 industry_2=brandinfo.industry_2)

        if form.validate_on_submit():
            exist = Shop.query.filter(Shop.store == form.store.data).first()
            if exist:
                return render_template('shop/error.html', error='此店铺已存在！')
            else:
                shop = Shop(store=form.store.data, brand_id=bid, title=form.title.data, phone=form.phone.data,
                            address=form.address.data, lng=form.lng.data, lat=form.lat.data)
                db.session.add(shop)
                db.session.commit()
                del session['brand']
                return render_template('shop/ok.html', tip='商户创建成功！', bid=bid)
        return render_template('shop/setting.html', form=form, brandForm=brandForm, act=act, brandinfo=brandinfo)
    elif act == 'modify':
        id = int(request.args.get("id", 0))
        shop = Shop.query.get(id)
        form = ShopSetting(store=shop.store, title=shop.title, phone=shop.phone, address=shop.address,
                           lat=shop.lat, lng=shop.lng)
        brandinfo = Brand.query.get(shop.brand_id)
        brandForm = BrandSetting(brand=brandinfo.name, intro=brandinfo.intro, image=brandinfo.image,
                                 thumb=brandinfo.thumb, industry_1=brandinfo.industry_1,
                                 industry_2=brandinfo.industry_2)

        if form.validate_on_submit():
            shop.store = form.store.data
            shop.phone = form.phone.data
            shop.address = form.address.data
            shop.lng = form.lng.data
            shop.lat = form.lat.data
            db.session.add(shop)
            db.session.commit()
            return render_template('shop/ok.html', tip='商户信息更新成功！', bid=shop.brand_id)
        return render_template('shop/setting.html', form=form, brandForm=brandForm, act=act, shop_id=id,
                               brandinfo=shop.brand)
    elif act == 'discount':
        return redirect(url_for('discount.manage', bid=bid))
    elif act == 'ticket_record':
        return redirect(url_for('ticket_record.manage'))
    else:
        return redirect(url_for('brand.shop_list', bid=bid))


@bp.route('/resource/<string:folder1>/<string:folder2>/<string:filename>', methods=['GET'])
def get_resourse(folder1, folder2, filename):
    BASE_URL = os.path.join(current_app.config.get('PROJECT_PATH'), 'resource/%s/%s') % (folder1, folder2)

    ext = os.path.splitext(filename)[1][1:]
    mimetypes = {"jpg": 'image/jpg', "css": 'text/css', "png": "image/png", "js": 'application/x-javascript',
                 "xml": 'application/xHTML+XML'}
    return send_from_directory(BASE_URL, filename, mimetype=mimetypes.get(ext))


@bp.route('/<int:shop_id>', methods=['GET'])
def detail(shop_id):
    shop = Shop.query.get_or_404(shop_id)
    return render_template('shop/show.html', shop=shop)


@bp.route('/delete', methods=['GET'])
def delete():
    shop_id = int(request.args.get("id", 0))
    shop = Shop.query.get_or_404(shop_id)
    db.session.delete(shop)
    db.session.commit()
    # url = request.args.get("source")
    url = request.referrer
    print request.url
    return render_template('account/ok.html', tip="删除成功！", url=url)


@bp.route('/list', methods=['GET'])
def list():
    bid = int(request.args.get("bid", 0))
    shops = Shop.query.filter(Shop.id == bid)
    return render_template('shop/list.html', shops=shops)


@bp.route('/checkout', methods=['GET'])
def checkout():
    id = int(request.args.get("id", 0))
    d = Discount.query.get(id)
    bid=10000
    return render_template('shop/checkout.html', d=d,bid=bid)
