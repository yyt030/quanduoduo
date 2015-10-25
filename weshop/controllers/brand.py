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
from ..models import db, User
from ..forms import SigninForm
from ..utils.permissions import require_user, require_visitor
from ..utils.uploadsets import images, random_filename, process_question, avatars

bp = Blueprint('brand', __name__)


@bp.route('', methods=['GET', 'POST'])
def index():
    """"""
    do = request.args.get("do")
    if do == 'businessdisplay':
        return render_template('shop/manage.html')
    return render_template('shop/select.html')


@bp.route('/add', methods=['GET', 'POST'])
def brand_add():
    """添加品牌"""
    shop = {}
    form = BrandSetting()
    if form.is_submitted():
        print request.form
        name = form.brand.data
        if name == "test":
            return render_template('account/error.html', error='您输入的品牌已存在！')
        else:
            return render_template('account/ok.html', error='您输入的品牌已存在！')
    return render_template('brand/setting.html', shop=shop, form=form)


@bp.route('/modify', methods=['GET', 'POST'])
def brand_modify():
    """修改品牌"""
    shop = {}
    id = int(request.args.get("id", 0))
    if not id:
        return render_template('account/error.html', error='页面不存在！')
    form = BrandSetting()
    if form.is_submitted():
        print request.form
        name = form.brand.data
        if name == "test":
            return render_template('account/error.html', error='您输入的品牌已存在！')
        else:
            return render_template('account/ok.html', tip='添加品牌成功，请添加一个门店！')
    return render_template('brand/setting.html', shop=shop, form=form)


@bp.route('/manage', methods=['GET', 'POST'])
def manage():
    """门店管理"""
    do = request.args.get("do", "normal")
    if do:
        query = {}

    return render_template('brand/manage.html', do=do)


@bp.route('/search', methods=['GET', 'POST'])
def brand_search():
    """搜索品牌"""
    message = "message"
    name = request.args.get("name", None)

    return json.dumps({"message": [], "redirect": "", "type": "tips"})
