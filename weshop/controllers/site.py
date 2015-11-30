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
from wechat_sdk import WechatBasic
from weshop import csrf
from weshop.utils import devices
from weshop.utils.account import signin_user, signout_user
from weshop.utils.devices import checkMobile
from ..models import db, User, Discount, Brand
from ..forms import SigninForm
from ..utils.permissions import require_user, require_visitor
from ..utils.uploadsets import images, random_filename, process_question, avatars
from weshop.wechat import WeixinHelper

bp = Blueprint('site', __name__)


@bp.route('/', methods=['GET'])
def index():
    return render_template('site/index.html')


@bp.route('/login', methods=['GET', 'POST'])
@require_visitor
def login():
    form = SigninForm()
    name = form.username.data
    if form.validate_on_submit():
        user = User.query.filter(User.name == name).first()
        if user:
            signin_user(user)
            return redirect(url_for('site.home'))
    return render_template('account/login.html', form=form)

@bp.route('/signin', methods=['GET', 'POST'])
@require_visitor
def signin():
    return render_template('account/user_data.html')

@bp.route('/signout', methods=['GET', 'POST'])
@require_visitor
def signout():
    signout_user()
    return redirect(url_for('site.index'))


@bp.route('/home', methods=['GET', 'POST'])
def home():
    return render_template('account/home.html')


@bp.route('/user_data', methods=['GET', 'POST'])
@require_user
def user_data():
    return render_template('account/user_data.html')


@bp.route('/resource/<string:folder1>/<string:filename>', defaults={"folder2": "", "folder3": ""}, methods=['GET'])
@bp.route('/resource/<string:folder1>/<string:folder2>/<string:filename>', defaults={"folder3": ""}, methods=['GET'])
@bp.route('/resource/<string:folder1>/<string:folder2>/<string:folder3>/<string:filename>', methods=['GET'])
def get_resourse(folder1, folder2, folder3, filename):
    if folder3 == "":
        BASE_URL = os.path.join(current_app.config.get('PROJECT_PATH'), 'resource/%s/%s') % (folder1, folder2)
        # print BASE_URL
        # print filename
    else:
        BASE_URL = os.path.join(current_app.config.get('PROJECT_PATH'), 'resource/%s/%s/%s') % (
            folder1, folder2, folder3)
    ext = os.path.splitext(filename)[1][1:]
    mimetypes = {"jpg": 'image/jpg', "css": 'text/css', "png": "image/png", "js": 'application/x-javascript',
                 "xml": 'application/xHTML+XML'}
    return send_from_directory(BASE_URL, filename, mimetype=mimetypes.get(ext))


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


@bp.route('/find')
def find():
    industry1 = request.args.get("industry1", None)
    search = request.args.get("search", "")
    if industry1 or search:
        discounts = Discount.query.filter(Discount.brand.has(Brand.industry_1 == industry1))
        return render_template('mobile/search_result.html', discounts=discounts, search=search, industry1=industry1)
    else:
        discounts = Discount.query.limit(10)
    return render_template('mobile/home.html', discounts=discounts, industry1=industry1)


@bp.route('/searchapi')
def search_api():
    industry1 = request.args.get("industry1", None)
    search = request.args.get("search", "")
    if industry1 != "全部分类":
        discounts = Discount.query.filter(Discount.brand.has(Brand.industry_1 == industry1))
    else:
        discounts = Discount.query.limit(20)
    brands = {}
    items = []
    for d in discounts:
        items.append({
            "did": d.id,
            "bid": d.brand_id,
            "title": d.title,
            "class": d.type,
            "total": d.number,
            "count": d.count,
            "supply": d.supply,
            "number": d.number
        })
        brands[d.brand_id] = {"bid": d.brand_id, "type": "local", "brand": d.brand.name,
                              "thumb": "images/" + d.brand.image,
                              "image": "back.jpg", "intro": d.brand.intro, "industry1": d.brand.industry_1,
                              "industry2": d.brand.industry_2, "rank": "0",
                              "business": "0", "discount": "0", "count": "1",
                              "state": "review", "ctime": "1448168448", "gtime": "0"}
    return json.dumps({"message": [items, brands], "redirect": "", "type": "ajax"})


@bp.route('/about')
def about():
    return render_template('mobile/about.html')


@bp.route('/agent')
def agent():
    return render_template('mobile/agent.html')


@bp.route('/fabu')
def fabu():
    return render_template('mobile/fabu.html')


@bp.route('/center')
def center():
    """菜单栏-发现"""
    return render_template('mobile/center.html')


@bp.route('/favorite')
def favorite_tickets():
    """我收藏的券包"""
    type = request.args.get("type")
    discounts = Discount.query.all()
    return render_template('mobile/my_favorite_tickets.html', type=type, discounts=discounts)


@bp.route('/my_tickets')
def tickets():
    """券包"""
    type = request.args.get("type")
    discounts = Discount.query.all()
    return render_template('mobile/my_tickets.html', type=type, discounts=discounts)


@csrf.exempt
@bp.route('/upload_image', methods=['GET', 'POST'])
def upload_image():
    if request.method == 'GET':
        return json.dumps({"error": 1, "message": "请选择要上传的图片！"})
    try:
        # filename = images.save(request.files['file'],name='%s.' % random_filename())
        filename = process_question(request.files['imgFile'], images, "")
    except Exception, e:
        return json.dumps({'status': 'no', 'error': e.__repr__()})
    else:
        data = {"error": 0, "message": "",
                "url": images.url(filename),
                "filename": filename}
        # print images.url(filename)
        return json.dumps(data)


token = 'q8745ac18171be1af01f6ac4a9085wd2'
EncodingAESKey = 'K1a1X0uIqopl6VH5MFK7AMC9skrL1UuEo1zSctgKeGU'
appid = 'wxb4b617b7a40c8eff'
appsecret = '5d684675679354b7c8544651fa909921'


@csrf.exempt
@bp.route('/interface', methods=['GET', 'POST'])
def interface():
    """初始化接入"""
    signature = str(request.args.get("signature"))
    timestamp = str(request.args.get('timestamp'))
    nonce = str(request.args.get('nonce'))
    echostr = request.args.get('echostr')

    if 'access_token' not in session:
        # 实例化 wechat
        access_token = None
        access_token_expires_at = None
        wechat = WechatBasic(appid=appid, appsecret=appsecret)
        token_dict = wechat.get_access_token()
        access_token = token_dict.get('access_token')
        print access_token
        session['access_token'] = access_token
        session['access_token_expires_at'] = token_dict.get('access_token_expires_at')

    wechat = WechatBasic(token=token)
    # 对签名进行校验
    if wechat.check_signature(signature=signature, timestamp=timestamp, nonce=nonce):

        # 获取请求类型
        if request.method == 'POST':
            # 读取用户发送消息
            body_text = request.data
            wechat.parse_data(body_text)
            # 获得解析结果
            message = wechat.get_message()
            # print request.data
            if message.type == 'text':
                if message.content == 'test':
                    response = wechat.response_text(u'^_^')
                else:
                    response = wechat.response_text(u'您好！')
            elif message.type == 'image':
                response = wechat.response_text(u'图片')
            else:
                response = wechat.response_text(u'欢迎关注汝州百事优惠圈')
            return response

        else:

            return echostr
    else:

        return "error"



