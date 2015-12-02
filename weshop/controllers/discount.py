# !/usr/bin/env python
# -*- coding: UTF-8 -*-
import json
import os
import string
import re, urllib2
import random
from PIL import Image
from coverage.html import STATIC_PATH
import datetime
from flask import render_template, Blueprint, redirect, url_for, g, session, request, \
    make_response, current_app, send_from_directory
from wechat_sdk import WechatBasic
from weshop import csrf
from weshop.forms.shop import ShopSetting, BrandSetting, DiscountSetting
from weshop.utils import devices
from weshop.utils.devices import checkMobile
from ..models import db, User, Brand, Shop, Discount, shop_discount
from ..forms import SigninForm
from ..utils.permissions import require_user, require_visitor
from ..utils.uploadsets import images, random_filename, process_question, avatars
from weshop.wechat.backends.flask_interface import wechat_login

bp = Blueprint('discount', __name__)

appid = 'wxb4b617b7a40c8eff'
appsecret = '5d684675679354b7c8544651fa909921'


@wechat_login
@bp.route('/', methods=['GET'])
@bp.route('/detail', methods=['GET'])
def detail():
    discount_id = int(request.args.get("id", 0))
    if not discount_id:
        discount_id = int(request.args.get("did", 0))
    do = request.args.get("do")
    discount = Discount.query.get_or_404(discount_id)
    now = datetime.datetime.now()
    end_time = discount.create_at + datetime.timedelta(days=discount.limits)
    delta = end_time - now
    left_day = delta.days
    discount_shop_count = discount.shops.count()
    # print discount_shop_count
    user_agent = request.headers.get('User-Agent')
    if do == 'post':
        if 'MQQBrowser' not in user_agent:
            return json.dumps({"message": "请在微信里操作", "redirect": "permit", "type": "tips"})
    wechat = WechatBasic(appid=appid, appsecret=appsecret)
    wechat.send_text_message(session['openid'], "test")
    print "start send message to wechat"

    return render_template('discount/detail.html', discount=discount, left_day=left_day,
                           discount_shop_count=discount_shop_count,
                           discount_id=discount_id)


@bp.route('/manage', methods=['GET', 'POST'])
def manage():
    """"""
    bid = int(request.args.get("bid", 0))
    brand = Brand.query.get(bid)
    discounts = Discount.query.filter(Discount.brand_id == bid)
    return render_template('discount/manage.html', bid=bid, brand=brand, discounts=discounts)


@bp.route('/setting', methods=['GET', 'POST'])
def setting():
    """优惠券设置"""
    act = request.args.get("act")
    bid = int(request.args.get("bid", 0))
    id = int(request.args.get("id", 0))
    form = DiscountSetting()
    values = request.form
    stores = []
    shops = Shop.query.filter(Shop.brand_id == bid)
    if request.method == 'GET':
        if act == 'modify':
            discount = Discount.query.get_or_404(id)

            shops = discount.shops
            form.title.data = discount.title
            form.type.data = discount.type
            form.intro.data = discount.intro
            form.image.data = discount.image
            form.supply.data = discount.supply
            form.limits.data = discount.limits
            for s in shops:
                stores.append(s.id)
    else:
        if form.is_submitted():
            title = form.title.data
            print title
            number = form.number.data
            discount_type = str(values.get("class"))
            print discount_type
            if title == '':
                error = '您还没输入优惠内容呢！'
                return render_template('shop/error.html', error=error)
            else:
                title_check = {"特价": "优惠券", "满减": "抵扣券", "折扣": "打折卡", "抵现": "代金券", "免单": "体验券"}
                correct_tag = title_check.get(discount_type)
                if str(correct_tag) not in title:
                    error = '此券只能叫%s不能叫%s' % (correct_tag, title[-3:])
                    return render_template('shop/error.html', error=error)
            if number == '':
                error = '请设置发行数量！'
                return render_template('shop/error.html', error=error)
            if act == 'publish':
                print request.form
                discount = Discount(title=title, type=discount_type.decode('utf-8'), intro=form.intro.data,
                                    image=form.image.data,
                                    supply=form.supply.data, number=number, usable=form.usable.data,
                                    perple=form.perple.data, limits=form.limits.data, user_id=g.user.id, brand_id=bid)
            else:
                discount = Discount.query.get_or_404(id)
                bid = discount.brand_id
                discount.title = form.title.data
                discount.type = values.get("class")
                discount.intro = form.intro.data
                discount.image = form.image.data
                discount.supply = form.supply.data
                discount.number = int(form.number.data)
                discount.usable = int(form.usable.data)
                discount.limits = int(values.get("limits"))
                discount.latest_update = datetime.datetime.now()
                perple = form.perple.data
                if perple == 'n':
                    discount.perple = 10000
                else:
                    discount.perple = int(form.perple.data)

            db.session.add(discount)
            db.session.commit()
            for k, v in values.items():
                if 'shop' in k:
                    shop_id = int(v)
                    shop = Shop.query.get(shop_id)
                    record = shop_discount.query(shop_discount.discount_id == discount.id,
                                                 shop_discount.shop_id == shop_id)
                    if not record:
                        discount.shops.append(shop)
                        db.session.add(g.user)
                        db.session.commit()
            return redirect(url_for('discount.manage', bid=bid))

    return render_template('discount/setting.html', form=form, shops=shops, stores=stores)


@bp.route('/delete', methods=['GET'])
def delete():
    discount_id = int(request.args.get("id", 0))
    discount = Discount.query.get_or_404(discount_id)
    db.session.delete(discount)
    db.session.commit()
    url = request.referrer
    print request.referrer
    return render_template('account/ok.html', tip="删除成功！", url=url)


@bp.route('/detail', methods=['GET'])
def detail():
    discount_id = int(request.args.get("id", 0))
    discount = Discount.query.get_or_404(discount_id)
    now = datetime.datetime.now()
    end_time = discount.create_at + datetime.timedelta(days=discount.limits)
    delta = end_time - now
    left_day = delta.days
    discount_shop_count = discount.shops.count()

    # other discount in the discount
    other_discounts = Discount.query.filter(Discount.id != discount_id,
                                            Discount.brand_id == discount.brand_id)
    shops = discount.shops.all()
    return render_template('discount/detail.html', discount=discount, left_day=left_day,
                           discount_shop_count=discount_shop_count,
                           discount_id=discount_id,
                           other_discounts=other_discounts,
                           shops=shops)
