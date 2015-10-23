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
from weshop.utils import devices
from weshop.utils.devices import checkMobile
from ..models import db, User
from ..forms import SigninForm
from ..utils.permissions import require_user, require_visitor
from ..utils.uploadsets import images, random_filename, process_question, avatars

bp = Blueprint('site', __name__)


@bp.route('/', methods=['GET'])
def index():
    if checkMobile(request):
        print "mobile"
    goods = {}
    return render_template('site/index.html', goods=goods)


@bp.route('/login', methods=['GET', 'POST'])
@require_visitor
def login():
    return render_template('account/login.html')

@bp.route('/home', methods=['GET', 'POST'])
@require_visitor
def home():
    return render_template('account/home.html')

@bp.route('/favicon.ico', methods=['GET'])
def favicon():
    return ""


@bp.route('/switch_city/<int:city_id>')
def switch_city(city_id):
    """切换城市"""
    city = City.query.get_or_404(city_id)
    session['city'] = city.name
    session['city_id'] = city.id
    session['province_id'] = city.province_id
    return redirect(request.referrer or url_for('site.index'))


@bp.route('/get_resource')
def crossdomain_xml():
    """生成用于Flash跨域脚本的xml文件"""
    sitemap_xml = render_template('site/crossdomain.xml')
    response = make_response(sitemap_xml)
    response.headers["Content-Type"] = "application/xml"
    return response


@bp.route('/test')
def test():
    return str(zip(session.keys(), session.values()))


@bp.route('/photos/<string:folder>/<string:filename>', methods=['GET'])
def get_photo_resourse(folder, filename):
    PHOTO_URL = os.path.join(current_app.config.get('UPLOADS_DEFAULT_DEST'), 'images/%s') % folder
    return send_from_directory(PHOTO_URL, filename, mimetype='image/png')


@bp.route('/upload_image', methods=['POST'])
@require_user
def upload_image():
    try:
        # filename = images.save(request.files['file'],name='%s.' % random_filename())
        filename = process_question(request.files['file'], images, "")
    except Exception, e:
        return json.dumps({'status': 'no', 'error': e.__repr__()})
    else:
        return json.dumps({'status': 'yes', 'url': images.url(filename)})
