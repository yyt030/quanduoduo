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
from weshop.controllers.site import add_wechat_user_to_db
from weshop.forms.shop import ShopSetting, BrandSetting, DiscountSetting
from weshop.utils import devices
from weshop.utils.account import signin_user
from weshop.utils.devices import checkMobile
from ..models import db, User, Brand, Shop, Discount, shop_discount, Profile
from ..forms import SigninForm
from ..utils.permissions import require_user, require_visitor
from ..utils.uploadsets import images, random_filename, process_question, avatars
from weshop.wechat import WeixinHelper
from weshop.wechat.backends.flask_interface import wechat_login

bp = Blueprint('discount', __name__)

appid = 'wxb4b617b7a40c8eff'
appsecret = '5d684675679354b7c8544651fa909921'


# @wechat_login
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
    # discount.count 每天0：00清零 TODO 脚本任务
    left_count = discount.number - discount.count
    discount_shop_count = discount.shops.count()
    # print discount_shop_count
    user_agent = request.headers.get('User-Agent')
    # print user_agent
    if do == 'post':
        if 'MicroMessenger' not in user_agent:
            return json.dumps({"message": "请在微信里操作", "redirect": "permit", "type": "tips"})

        openid = session.get('openid')
        if not openid:
            code = request.args.get("code")
            if not code:
                return redirect(WeixinHelper.oauth3(request.url))
            else:
                data = json.loads(WeixinHelper.getAccessTokenByCode(code))
                access_token, openid, refresh_token = data["access_token"], data["openid"], data["refresh_token"]
                userinfo = json.loads(WeixinHelper.getSnsapiUserInfo(access_token, openid))
                print userinfo
                print openid
                print g.user

                if not g.user:
                    # 检查用户是否存在
                    add_wechat_user_to_db(openid)
                    user = User.query.filter(User.profile.any(Profile.openid == openid)).first()
                    if user is not None:
                        signin_user(user)
                        session['openid'] = openid
                        print u'与微信用户关联的user（%s） 已开始登陆网站...' % user.name

                else:
                    msg = u'当前已登录的用户：{user}'.format(user=g.user.name)
                    print msg
        wechat = WechatBasic(appid=appid, appsecret=appsecret)
        if session.get("openid"):
            # wechat.send_text_message(session['openid'], "test")
            # 调用公众号消息模板A0XK30w_sZPti5_gn33PJ5msng7yb71zAEcRa0E44oM发送领券通知
            """{first.DATA}}
            优惠券：{{keyword1.DATA}}
            来源：{{keyword2.DATA}}
            过期时间：{{keyword3.DATA}}
            使用说明：{{keyword4.DATA}}
            {{remark.DATA}}
            """
            json_data = {
                "first": {
                    "value": "恭喜你领券成功！",
                    "color": "#173177"
                },
                "keyword1": {
                    "value": discount.title,
                    "color": "#173177"
                },
                "keyword2": {
                    "value": "网页获取",
                    "color": "#173177"
                },
                "keyword3": {
                    "value": "2015年12月10日",
                    "color": "#173177"
                },
                "remark": {
                    "value": "凭优惠券详情二维码领取",
                    "color": "#173177"
                }
            }
            wechat.send_template_message(openid, 'A0XK30w_sZPti5_gn33PJ5msng7yb71zAEcRa0E44oM', json_data)
            # still 表示本周还能领多少张 TODO 静态数据需要替换
            # 领取后需要写入到get_discount_record 表
            # 下次是否能领取则通过这张表的数据来判断

            return json.dumps(
                {"message": {"still": 10, "allow": 0, "aid": discount.id, "ctime": "156151515"}, "redirect": "",
                 "type": "success"})

    # other discount in the discount
    other_discounts = Discount.query.filter(Discount.id != discount_id,
                                            Discount.brand_id == discount.brand_id)
    shops = discount.shops.all()
    return render_template('discount/detail.html', discount=discount, left_day=left_day,
                           discount_shop_count=discount_shop_count,
                           discount_id=discount_id, left_count=left_count,
                           other_discounts=other_discounts,
                           shops=shops)


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
                    # record = db.session.query(shop_discount).filter(shop_discount.discount_id == discount.id,
                    #                              shop_discount.shop_id == shop_id)
                    record = shop.discounts
                    if record:
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
