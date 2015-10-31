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

bp = Blueprint('shop', __name__)


@bp.route('/select', methods=['GET', 'POST'])
def select():
    """选择门店"""
    # TODO user_id
    brands = Brand.query.all()
    return render_template('shop/select_brand.html', brands=brands)


@bp.route('/publish', methods=['GET', 'POST'])
def publish():
    """发布门店"""

    form = ShopSetting()
    brandForm = BrandSetting()
    if not session.get("brand"):
        bid = int(request.args.get("bid", 0))
    else:
        bid = session['brand']
    brandinfo = Brand.query.get(bid)
    brandForm = BrandSetting(brand=brandinfo.name, intro=brandinfo.intro, image=brandinfo.image,
                             thumb=brandinfo.thumb)
    brandForm.industry_1.data = brandinfo.industry_1
    brandForm.industry_2.data = brandinfo.industry_2
    if form.validate_on_submit():
        print request.form
        exist = Shop.query.filter(Shop.store == form.store.data).first()
        if exist:
            return render_template('shop/error.html', error='此店铺已存在！')
        else:
            shop = Shop(store=form.brand.data, brand_id=bid, title=form.title.data, phone=form.phone.data,
                         address=form.address.data, lng=form.lng.data, lat=form.lat.data)
            db.session.add(shop)
            db.session.commit()
            del session['brand']
            return render_template('shop/ok.html', error='商户信息更新成功！',bid=bid)
    return render_template('shop/setting.html', form=form, brandForm=brandForm, brandinfo=brandinfo)


@bp.route('/resource/<string:folder1>/<string:folder2>/<string:filename>', methods=['GET'])
def get_resourse(folder1, folder2, filename):
    BASE_URL = os.path.join(current_app.config.get('PROJECT_PATH'), 'resource/%s/%s') % (folder1, folder2)

    ext = os.path.splitext(filename)[1][1:]
    mimetypes = {"jpg": 'image/jpg', "css": 'text/css', "png": "image/png", "js": 'application/x-javascript',
                 "xml": 'application/xHTML+XML'}
    return send_from_directory(BASE_URL, filename, mimetype=mimetypes.get(ext))


@bp.route('/<int:sid>', methods=['GET'])
def detail(sid):
    shop = {}
    return render_template('shop/show.html', shop=shop)
