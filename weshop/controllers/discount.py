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
from weshop.forms.shop import ShopSetting, BrandSetting, DiscountSetting
from weshop.utils import devices
from weshop.utils.devices import checkMobile
from ..models import db, User, Brand, Shop, Discount
from ..forms import SigninForm
from ..utils.permissions import require_user, require_visitor
from ..utils.uploadsets import images, random_filename, process_question, avatars

bp = Blueprint('discount', __name__)


@bp.route('/manage', methods=['GET', 'POST'])
def manage():
    """"""
    bid = int(request.args.get("bid", 0))
    brand = Brand.query.get(bid)
    discounts=Discount.query.all()
    return render_template('discount/manage.html', bid=bid, brand=brand,discounts=discounts)


@bp.route('/setting', methods=['GET', 'POST'])
def setting():
    """优惠券设置"""
    act = request.args.get("act")
    bid = int(request.args.get("bid", 0))
    form = DiscountSetting()
    shops = Shop.query.filter(Shop.brand_id == bid)
    if act == 'publish':
        print request.form
    if form.is_submitted():
        discount = Discount(title=form.title.data, intro=form.intro.data, image=form.image.data,
                            supply=form.supply.data, number=int(form.number.data), usable=form.usable.data,
                            perple=form.perple.data, limits=form.limit.data, user_id=g.user.id, shop_id=1,
                            )
        db.session.add(discount)
        db.session.commit()
    return render_template('discount/setting.html', form=form, shops=shops)
