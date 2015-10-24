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

bp = Blueprint('shop', __name__)


@bp.route('/publish', methods=['GET','POST'])
def publish():
    shop = {}
    form = ShopSetting()
    brandForm=BrandSetting()
    if form.validate_on_submit():
        print request.form
    return render_template('shop/shop_setting.html', shop=shop, form=form,brandForm=brandForm)


@bp.route('/brand/add', methods=['GET','POST'])
def brand_add():
    shop = {}
    form = ShopSetting()
    if form.validate_on_submit():
        print request.form
    return render_template('shop/brand_setting.html', shop=shop, form=form)

@bp.route('/resource/<string:folder1>/<string:folder2>/<string:filename>', methods=['GET'])
def get_resourse(folder1, folder2, filename):
    BASE_URL = os.path.join(current_app.config.get('PROJECT_PATH'), 'resource/%s/%s') % (folder1, folder2)

    ext = os.path.splitext(filename)[1][1:]
    if ext == 'jpg':
        mimetype = 'image/jpg'
    elif ext == 'css':
        mimetype = 'text/css'
    elif ext == 'png':
        mimetype = 'image/png'
    elif ext == 'js':
        mimetype = 'application/x-javascript'
    else:
        mimetype = "image/jpg"
    return send_from_directory(BASE_URL, filename, mimetype=mimetype)


@bp.route('/<int:sid>', methods=['GET'])
def detail(sid):
    shop = {}
    return render_template('shop/detail.html', shop=shop)
