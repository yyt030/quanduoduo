# !/usr/bin/env python
# -*- coding: UTF-8 -*-
from datetime import datetime, timedelta
import time
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
from weshop.utils.account import signin_user, signout_user
from ..models import db, User, Discount, Brand, MyFavoriteBrand, Shop, Profile, GetTicketRecord
from ..forms import SigninForm
from ..utils.permissions import require_user, require_visitor
from ..utils.uploadsets import images, random_filename, process_question, avatars
from weshop.utils.helper import get_url_data
from weshop.wechat import WeixinHelper
from weshop.wechat.backends.flask_interface import wechat_login

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
@require_user
def home():
    return render_template('account/home.html')


@bp.route('/user_data', methods=['GET', 'POST'])
@require_user
def user_data():
    return render_template('account/user_data.html')


@bp.route('/check_saler_info', methods=['GET', 'POST'])
@require_user
def check_saler_info():
    """确认收银员信息"""
    brand_id = int(request.args.get("bid", 0))
    openid = session.get("openid")
    do = request.args.get("do")
    print "openid,", openid
    if not openid:
        code = request.args.get("code")
        if not code:
            print "not code"
            return redirect(WeixinHelper.oauth3('/find'))
        else:
            data = json.loads(WeixinHelper.getAccessTokenByCode(code))
            access_token, openid, refresh_token = data["access_token"], data["openid"], data["refresh_token"]
            userinfo = json.loads(WeixinHelper.getSnsapiUserInfo(access_token, openid))
            print "user_info,", userinfo
            # print openid

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
    if do == 'check':
        # 绑定店员
        mobile = request.args.get("mobile")
        user = request.user
        user.mobile = mobile
        user.save()

        return json.dumps({"message": "提交成功", "type": "success"})
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
    openid = session.get("openid")
    print "openid,", openid
    if not openid:
        code = request.args.get("code")
        if not code:
            print "not code"
            return redirect(WeixinHelper.oauth3('/find'))
        else:
            data = json.loads(WeixinHelper.getAccessTokenByCode(code))
            access_token, openid, refresh_token = data["access_token"], data["openid"], data["refresh_token"]
            userinfo = json.loads(WeixinHelper.getSnsapiUserInfo(access_token, openid))
            print "user_info,", userinfo
            # print openid

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


@bp.route('/my_favorite_shop')
@bp.route('/favorite')
def favorite_brands():
    user = g.user
    type = request.args.get('type', 'new')
    act = request.args.get('act')
    brand_id = request.args.get('bid', type=int)
    if act == "add":
        exist = MyFavoriteBrand.query.filter(MyFavoriteBrand.user_id == user.id,
                                             MyFavoriteBrand.brand_id == brand_id).all()
        if not exist:
            favorite = MyFavoriteBrand()
            favorite.user_id = user.id
            favorite.brand_id = brand_id
            db.session.add(favorite)
            db.session.commit()
    if type == 'hot':
        # TODO
        records = MyFavoriteBrand.query.filter(MyFavoriteBrand.user_id == user.id).order_by(
            MyFavoriteBrand.create_at.desc())
    else:
        records = MyFavoriteBrand.query.filter(MyFavoriteBrand.user_id == user.id).order_by(
            MyFavoriteBrand.create_at.desc())

    brand = records.first().brand

    nav = 1
    return render_template('mobile/my_favorite_brand.html', type=type, nav=nav, brand=brand,
                           records=records)


@bp.route('/user_home')
@require_user
def user_home():
    """我的个人中心"""
    type = request.args.get("type")
    tickets = GetTicketRecord.query.all()
    nav = 4
    openid = session.get("openid")
    if not openid:
        code = request.args.get("code")
        if not code:
            print "not code"
            return redirect(WeixinHelper.oauth3(request.url))
        else:
            data = json.loads(WeixinHelper.getAccessTokenByCode(code))
            access_token, openid, refresh_token = data["access_token"], data["openid"], data["refresh_token"]
            userinfo = json.loads(WeixinHelper.getSnsapiUserInfo(access_token, openid))
            print "user_info,", userinfo
            # print openid

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
    return render_template('mobile/user_home.html', type=type, nav=nav, tickets=tickets)


@bp.route('/my_tickets')
def tickets():
    """券包"""
    type = request.args.get("type", "not_use")
    user_id = g.user.id
    now = datetime.date(datetime.now())
    nav = 2
    if type == 'not_use':
        records = GetTicketRecord.query.filter(GetTicketRecord.user_id == user_id,
                                               GetTicketRecord.status == 'normal')
    elif type == 'expire':
        from sqlalchemy import or_
        records = GetTicketRecord.query.filter(GetTicketRecord.user_id == user_id,
                                               GetTicketRecord.status == type)
    else:
        records = GetTicketRecord.query.filter(GetTicketRecord.user_id == user_id)

    expire_date = ''
    if records.all():
        expire_date = datetime.date(records.first().discount.create_at) + timedelta(
            days=records.first().discount.usable)

    return render_template('mobile/my_tickets.html', type=type, nav=2, records=records, expire_date=expire_date)


@bp.route('/my_tickets_detail')
def tickets_detail():
    """券　详情页面"""
    nav = 2
    user_id = g.user.id
    tickets_id = request.args.get('tid', 0, type=int)

    ticket = GetTicketRecord.query.get(tickets_id)

    now = datetime.date(datetime.now())
    expire_date = datetime.date(ticket.create_at) + timedelta(days=ticket.discount.usable)
    isexpire = (now - expire_date).days

    print '-' * 10, isexpire
    shops = ticket.discount.shops
    return render_template('mobile/my_tickets_detail.html', nav=2, discount=ticket.discount,
                           shops=shops, expire_date=expire_date, isexpire=isexpire)


@bp.route('/gonglue')
def gonglue():
    """使用攻略"""
    return render_template('mobile/gonglue.html')


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
        session['access_token'] = access_token
        session['access_token_expires_at'] = token_dict.get('access_token_expires_at')
    response = ""
    wechat = WechatBasic(token=token)
    # 对签名进行校验
    if wechat.check_signature(signature=signature, timestamp=timestamp, nonce=nonce):

        # 获取请求类型
        if request.method == 'POST':
            # 读取用户发送消息
            body_text = request.data
            print body_text
            wechat.parse_data(body_text)
            # 获得解析结果
            message = wechat.get_message()
            print "message_type:", message.type
            # print request.data
            if message.type == 'text':
                if message.content == 'test':
                    response = wechat.response_text(u'^_^')
                else:
                    response = wechat.response_text(u'您好！')

            elif message.type == 'image':
                response = wechat.response_text(u'图片')
            elif message.type == 'scan':
                if message.key and message.ticket:
                    # TODO 扫码回收优惠券,这里还要判断扫码的用户是否为该品牌店授权的店员
                    # TODO 考虑到还有绑定店员的扫码事件,key分为两种：11[brandid],12[discount_id]
                    print message.key[0:2]
                    print message.key[2:]
                    if message.key[0:2] == '11':
                        brand_id = int(message.key[2:])
                        brand = Brand.query.get(brand_id)
                        if not brand:
                            response = wechat.response_text("要绑定的店铺不存在")
                        brand_text = "<a href='{0}/{1}?bid={2}'>{3}</a>".format(current_app.config.get("SITE_DOMAIN"),
                                                                                "check_saler_info",
                                                                                brand.id, brand.name)
                        print brand_text

                        text = "您正在申请绑定门店%s,点击输入手机号验证身份" % brand_text
                        response = wechat.response_text(text)
                    elif message.key[0:2] == '12':
                        record_id = int(message.key[2:])
                        callback_ticket(record_id)
                        response = ""
            elif message.type == 'subscribe':
                print message
                if message.key and message.ticket:
                    # TODO 扫码回收优惠券,这里还要判断扫码的用户是否为该品牌店授权的店员
                    # TODO 考虑到还有绑定店员的扫码事件,key分为两种：bind_[brandid],ticket_[code]
                    value = message.key.replace("qrscene_", "")
                    if value.split("_")[0] == 'ticket':
                        record_id = int(message.key.split("_")[1])
                        callback_ticket(record_id)
                        response = ""
                    elif value.split("_")[0] == 'bind':
                        brand_id = int(message.key.split("_")[1])
                        brand = Brand.query.get(brand_id)
                        brand_text = "<a href='{0}/{1}'>{2}</a>".format(current_app.config.get("SITE_DOMAIN"), "find",
                                                                        brand.name)
                        text = "您正在申请绑定门店%s,点击输入手机号验证身份" % brand_text
                        response = wechat.response_text(text)

                openid = session.get("openid")
                # 扫描二维码回收优惠券
                if not openid:
                    code = request.args.get("code")
                    if not code:
                        print "not code"
                        return redirect(WeixinHelper.oauth3(request.url))
                    else:
                        data = json.loads(WeixinHelper.getAccessTokenByCode(code))
                        access_token, openid, refresh_token = data["access_token"], data["openid"], data[
                            "refresh_token"]
                        userinfo = json.loads(WeixinHelper.getSnsapiUserInfo(access_token, openid))
                        print "user_info,", userinfo

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

                    response = wechat.response_text(u'欢迎关注汝州百事优惠圈')
            elif message.type == 'location':
                # 这里有location事件 TODO
                print "*" * 20

                return ""
            else:
                return ""

            return response

        else:

            return echostr
    else:

        return "error"


def get_user_info(token, openid):
    url = 'https://api.weixin.qq.com/cgi-bin/user/info?access_token=%s&openid=%s&lang=zh_CN' % (token, openid)
    user_json_str = get_url_data(url)
    user_json = json.loads(user_json_str)

    return user_json


# @cache.memoize(timeout=7200)
def get_access_token(update=False):
    if session.get('access_token', None) and update is False:
        return session.get('access_token')
    else:
        url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=%s&secret=%s' \
              % (current_app.config.get('WECHAT_APPID'), current_app.config.get('WECHAT_APPSECRET'))
        access_token = get_url_data(url)
        dict_access_token = json.loads(access_token)
        str_access_token = dict_access_token['access_token']
        session['access_token'] = str_access_token

    return str_access_token


def get_wechat_info(request, openid):
    if not openid:
        code = request.args.get("code")
        if not code:
            return redirect(WeixinHelper.oauth3(request.url))
        else:
            data = json.loads(WeixinHelper.getAccessTokenByCode(code))
            access_token, openid, refresh_token = data["access_token"], data["openid"], data["refresh_token"]
            userinfo = json.loads(WeixinHelper.getSnsapiUserInfo(access_token, openid))
            print "user_info,", userinfo
            # print openid

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


def add_wechat_user_to_db(from_user):
    """
    添加微信用户到数据库，在数据库创建一个对应的user关联在一起
    """
    users = User.query.filter(User.profile.any(Profile.openid == str(from_user))).first()
    if not users:
        print u'creating a new user ...'
        print 'waiting...'
        user_json = get_user_info(get_access_token(), from_user)
        if 'errcode' in user_json:
            user_json = get_user_info(get_access_token(True), from_user)
        email = str(from_user) + '@qq.com'
        user = User(name=user_json['nickname'], email=email, password=from_user)
        user_profile = Profile()
        user_profile.openid = from_user
        user_profile.city = user_json['city']
        user_profile.country = user_json['country']
        user_profile.headimgurl = user_json['headimgurl']
        user_profile.language = user_json['language']
        user_profile.nickname = user_json['nickname']
        user_profile.province = user_json['province']
        user_profile.subscribe_time = datetime.fromtimestamp(user_json['subscribe_time'])
        user.profile.append(user_profile)
        db.session.add(user)
        db.session.commit()


def callback_ticket(record_id):
    """回收优惠券"""
    ticket_record = GetTicketRecord.query.get(record_id)
    ticket_record.status = 'usedit'
    db.session.add(ticket_record)
    db.session.commit()
    # 发送模板通知信息到微信
    # 调用公众号消息模板bK9Trpq_AmdHxnaT1kQ8d0lTJt-z3QBUNzacsnQbfXg 优惠券使用通知
    """{{first.DATA}}
        优惠券：{{keyword1.DATA}}
        兑换码：{{keyword2.DATA}}
        消费日：{{keyword3.DATA}}
        {{remark.DATA}}
    """
    json_data = {
        "first": {
            "value": "您已成功使用一张优惠券！",
            "color": "#173177"
        },
        "keyword1": {
            "value": ticket_record.discount.title,
            "color": "#173177"
        },
        "keyword2": {
            "value": ticket_record.code,
            "color": "#173177"
        },
        "keyword3": {
            "value": time.strftime("%Y-%m-%d", time.localtime()),
            "color": "#173177"
        },
        "remark": {
            "value": "感谢您的使用，请继续关注我们新的优惠活动！",
        }
    }
    wechat = WechatBasic(appid=appid, appsecret=appsecret)
    # 发送通知给指定优惠券所有人,message.source 为扫码用户
    wechat.send_template_message(str(ticket_record.user.password),
                                 'bK9Trpq_AmdHxnaT1kQ8d0lTJt-z3QBUNzacsnQbfXg', json_data)
