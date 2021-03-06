# !/usr/bin/env python
# -*- coding: UTF-8 -*-
from datetime import datetime, timedelta
import logging
import time
import json
from urllib import urlencode

import os
import re
from flask import render_template, Blueprint, redirect, url_for, g, session, request, \
    make_response, current_app, send_from_directory
from sqlalchemy import func
from wechat_sdk import WechatBasic
from weshop import csrf
from weshop.utils.account import signin_user, signout_user
from ..models import db, User, Discount, Brand, MyFavoriteBrand, Shop, Profile, GetTicketRecord, Saler, WechatMessage, \
    Site
from ..forms import SigninForm, SalerInfoForm, SiteInfo, NewPwdForm
from ..utils.permissions import require_user, require_visitor, require_admin
from ..utils.uploadsets import images, process_question
from weshop.utils.helper import get_url_data
from weshop.wechat import WeixinHelper
from geopy.distance import great_circle

bp = Blueprint('site', __name__)


@bp.route('/', methods=['GET'])
def index():
    return render_template('site/index.html')


@bp.route('/login', methods=['GET', 'POST'])
@require_visitor
def login():
    form = SigninForm()
    error=""
    name = form.username.data
    if request.method=='POST':
        if form.validate_on_submit():
            user = User.query.filter(User.name == name).first()
            if user:
                signin_user(user)
                return redirect(url_for('site.home'))
        else:
            error="用户名或密码不正确"
    return render_template('account/login.html', form=form,error=error)


@bp.route('/signin', methods=['GET', 'POST'])
@require_visitor
def signin():
    return render_template('account/user_data.html')


@bp.route('/signout', methods=['GET', 'POST'])
def signout():
    signout_user()
    return redirect(url_for('site.login'))


@bp.route('/home', methods=['GET', 'POST'])
@require_user
def home():
    return render_template('account/home.html')


@bp.route("/setting/site", methods=('GET', 'POST'))
@require_admin
def site_info():
    form = SiteInfo()
    info = Site.query.first()
    if request.method == 'POST':
        if not info:
            info = Site(url=form.url.data, phone=form.phone.data,  email=form.phone.data,
                        address=form.address.data)
            db.session.add(info)
        else:
            info.url = form.url.data
            info.phone = form.phone.data
            info.email = form.email.data
            info.address = form.address.data
            info.icp = form.icp.data
        db.session.commit()
    else:
        if info:
            form.url.data = info.url
            form.phone.data = info.phone
            form.email.data = info.email
            form.address.data = info.address
            form.icp.data = info.icp
    return render_template("site/site_info.html", form=form, admin_nav=1, info=info)


@bp.route("/setting/resetpwd", methods=('GET', 'POST'))
@require_admin
def reset_pwd():
    form =NewPwdForm()
    if form.validate_on_submit():
        # 将新密码写入数据库
        g.user.password = form.newpwd.data
        g.user.hash_password()
        g.user.gene_token()
        db.session.add(g.user)
        db.session.commit()
        signout_user()
        return redirect(url_for('site.login'))
    return render_template("site/reset_pwd.html", form=form, admin_nav=1)

@bp.route('/user_data', methods=['GET', 'POST'])
@require_user
def user_data():
    """过期，领券，回收"""
    init_data = [0, 0, 0, 0, 0, 0, 0]

    user = g.user
    if g.user.role == 'admin':
        brands = Brand.query
    else:
        brands = Brand.query.filter(Brand.brandaccounts.any(User.id == g.user.id))
    brand_arr = []
    for i in range(0, brands.count()):
        brand_arr.append(brands[i].id)
    expire_data, get_ticket_data, callback_data = count_last_week_data(brand_arr)
    # 优惠券
    discount_count = 0  # 发放总数
    discount_back = 0  # 回收总数
    user_count_list = []  # 领券用户数
    usedit_count_list = []  # 使用用户数
    active_users_count = 0  # 月活动用户总数
    curr_discount_count = 0  # 当前券总数
    closed_discount_count = 0  #

    start_month_day = (datetime.now() - timedelta(days=datetime.now().day - 1)).date()

    from sqlalchemy import func
    discount_count = db.session.query(func.sum(Discount.count)).filter(Discount.brand_id.in_(brand_arr)).scalar()
    discount_back = db.session.query(func.sum(Discount.back)).filter(Discount.brand_id.in_(brand_arr)).scalar()

    user_count = db.session.query(func.count(func.distinct(GetTicketRecord.user_id))).filter(
        GetTicketRecord.discount.has(Discount.brand_id.in_(brand_arr))).scalar()
    usedit_count = db.session.query(func.count(func.distinct(GetTicketRecord.user_id))).filter(
        GetTicketRecord.discount.has(Discount.brand_id.in_(brand_arr))).filter(
        GetTicketRecord.status == 'usedit').scalar()

    active_users_count = db.session.query(func.count(func.distinct(GetTicketRecord.user_id))).filter(
        GetTicketRecord.discount.has(Discount.brand_id.in_(brand_arr))).filter(
        GetTicketRecord.create_at >= start_month_day
    ).scalar()

    curr_discounts = Discount.query.filter(Discount.brand_id.in_(brand_arr))

    for curr_discount in curr_discounts:
        curr_discount_count += 1
        if curr_discount.is_expire is False:
            closed_discount_count += 1

    # 回收比例
    if discount_count == 0:
        back_vate = 0
    else:
        back_vate = '%.0f' % ((discount_back / discount_count) * 100)

    # 转化比例
    if user_count == 0:
        convert_vate = 0
    else:
        convert_vate = '%.0f' % ((usedit_count / user_count) * 100)

    return render_template('account/user_data.html', expire_data=expire_data, get_ticket_data=get_ticket_data,
                           callback_data=callback_data, discount_count=discount_count,
                           discount_back=discount_back, active_users_count=active_users_count,
                           curr_discount_count=curr_discount_count, closed_discount_count=closed_discount_count,
                           user_count=user_count, usedit_count=usedit_count,
                           back_vate=back_vate, convert_vate=convert_vate)


@bp.route('/check_saler_info', methods=['GET', 'POST'])
def check_saler_info():
    """确认收银员信息"""
    brand_id = int(request.args.get("bid", 0))
    openid = session.get("openid")
    do = request.args.get("do")
    form = SalerInfoForm()
    if not openid:
        code = request.args.get("code")
        if not code:
            print "not code"
            # print "/check_saler_info"
            return redirect(WeixinHelper.oauth3(request.url))
        else:
            wechat_login_fun(code)
    if do == 'check':
        # 绑定店员
        mobile = request.args.get("mobile")
        exist_saler = Saler.query.filter(Saler.user_id == g.user.id, Saler.brand_id == brand_id).first()
        if not exist_saler:
            g.user.mobile = mobile
            saler = Saler(user_id=g.user.id, brand_id=brand_id)
            db.session.add(saler)
            db.session.commit()
            wechat = WechatBasic(appid=appid, appsecret=appsecret)
            wechat.send_text_message(openid, "您已成功绑定门店")
            return json.dumps({"message": "提交成功", "type": "success"})
        else:
            return json.dumps({"message": "您已绑定门店,不用再次绑定", "type": "error"})
    return render_template('mobile/check_saler_info.html', brand_id=brand_id, form=form)


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
    access_token = session.get('access_token')
    user_agent = request.headers.get('User-Agent')
    print user_agent
    # 如果操作是在微信网页端进行，要获取openid
    if 'MicroMessenger' in user_agent:
        if not openid:
            code = request.args.get("code")
            if not code:
                print "not code"
                return redirect(WeixinHelper.oauth2(request.url))
            else:
                wechat_login_fun(code)

    industry1 = request.args.get("industry1", None)
    industry2 = request.args.get('industry2', None)
    district1 = request.args.get('district1', None)
    sortrank1 = request.args.get('sortrank1', None)
    page = request.args.get('page', 0, type=int)
    query = request.args.get("query", "")

    if query:
        discounts = Discount.query.join(Brand).filter(Brand.name.like('%{0}%'.format(query)))
        return render_template('mobile/search_result.html', discounts=discounts)

    # 拼装查询条件
    discounts = Discount.query.filter(Discount.is_re == 1)
    if industry1 != u'全部分类':
        if industry1:  # 品牌大类1
            discounts = discounts.filter(Discount.brand.has(Brand.industry_1 == industry1))
        if industry2:  # 品牌大类2
            discounts = discounts.filter(Discount.brand.has(Brand.industry_2 == industry2))
    curr_user_point = (session.get('longitude', ''), session.get('latitude', ''))
    # shop_list = []
    discount_list = []

    if district1 and session.get('longitude', ''):  # 地区
        if district1 == u'200米内':
            for discount in discounts.all():
                for shop in discount.shops.all():
                    if shop.get_distinct(curr_user_point) <= 0.2:
                        # shop_list.append(shop)
                        discount.append(shop.get_distinct(curr_user_point))
                        discount_list.append(discount)
        elif district1 == u'1千米内':
            for discount in discounts.all():
                for shop in discount.shops.all():
                    if shop.get_distinct(curr_user_point) <= 1:
                        # shop_list.append(shop)
                        discount_list.append(discount)
        elif district1 == u'5千米内':
            for discount in discounts.all():
                for shop in discount.shops.all():
                    if shop.get_distinct(curr_user_point) <= 5:
                        # shop_list.append(shop)
                        discount_list.append(discount)
        else:  # 全城范围
            pass
    else:
        discount_list = discounts.all()

    if sortrank1:  # 排序方式
        if sortrank1 == u'领取量':
            discount_list.sort(key=lambda x: x.count, reverse=True)
        elif sortrank1 == u'使用量':
            discount_list.sort(key=lambda x: x.back, reverse=True)
        else:  # 默认排序
            discount_list.sort(key=lambda x: x.create_at, reverse=True)

    discounts = discount_list

    EVENY_PAGE_NUM = current_app.config['FLASKY_PER_PAGE']
    if page:  # 加载页数
        discounts = discounts[page * EVENY_PAGE_NUM:
        (page + 1) * EVENY_PAGE_NUM]

    if industry1 or district1 or sortrank1:
        return render_template('mobile/search_result.html', discounts=discounts, industry1=industry1)

    return render_template('mobile/home.html', discounts=discounts, industry1=industry1)


@bp.route('/searchapi')
def search_api():
    industry1 = request.args.get('industry1', None)
    industry2 = request.args.get('industry2', None)
    district1 = request.args.get('district1', None)
    sortrank1 = request.args.get('sortrank1', None)

    page = request.args.get('page', 0, type=int)
    query = request.args.get("query", "")

    # 拼装查询条件
    discounts = Discount.query
    if industry1 != u'全部分类':
        if industry1:  # 品牌大类1
            discounts = discounts.filter(Discount.brand.has(Brand.industry_1 == industry1))
        if industry2:  # 品牌大类2
            discounts = discounts.filter(Discount.brand.has(Brand.industry_2 == industry2))
    curr_user_point = (session.get('longitude', ''), session.get('latitude', ''))
    # shop_list = []
    discount_list = []

    if district1 and session.get('longitude', ''):  # 地区
        if district1 == u'200米内':
            for discount in discounts.all():
                for shop in discount.shops.all():
                    if shop.get_distinct(curr_user_point) <= 0.2:
                        # shop_list.append(shop)
                        discount.append(shop.get_distinct(curr_user_point))
                        discount_list.append(discount)
        elif district1 == u'1千米内':
            for discount in discounts.all():
                for shop in discount.shops.all():
                    if shop.get_distinct(curr_user_point) <= 1:
                        # shop_list.append(shop)
                        discount_list.append(discount)
        elif district1 == u'5千米内':
            for discount in discounts.all():
                for shop in discount.shops.all():
                    if shop.get_distinct(curr_user_point) <= 5:
                        # shop_list.append(shop)
                        discount_list.append(discount)
        else:  # 全城范围
            pass
    else:
        discount_list = discounts.all()

    if sortrank1:  # 排序方式
        if sortrank1 == u'领取量':
            discount_list.sort(key=lambda x: x.count, reverse=True)
        elif sortrank1 == u'使用量':
            discount_list.sort(key=lambda x: x.back, reverse=True)
        else:  # 默认排序
            discount_list.sort(key=lambda x: x.create_at, reverse=True)

    discounts = discount_list

    EVENY_PAGE_NUM = current_app.config['FLASKY_PER_PAGE']
    if page:  # 加载页数
        discounts = discounts[page * EVENY_PAGE_NUM:
        (page + 1) * EVENY_PAGE_NUM]

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
    print request.url_root
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
    openid = session.get("openid")
    if not openid:
        code = request.args.get("code")
        if not code:
            print "not code"
            return redirect(WeixinHelper.oauth3(request.url))
        else:
            wechat_login_fun(code)
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

    if records.first():
        brand = records.first().brand
    else:
        brand = {}
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
            wechat_login_fun(code)
    return render_template('mobile/user_home.html', type=type, nav=nav, tickets=tickets)


@bp.route('/my_tickets')
def tickets():
    """券包"""
    openid = session.get("openid")
    if not openid:
        code = request.args.get("code")
        if not code:
            print "not code"
            return redirect(WeixinHelper.oauth3(request.url))
        else:
            wechat_login_fun(code)
    type = request.args.get("type", "not_use")
    user = g.user
    nav = 2
    if user:
        user_id = user.id
    else:
        user_id = ''

    records = GetTicketRecord.query.filter(GetTicketRecord.user_id == user_id)
    if type == 'not_use':
        from sqlalchemy import or_
        records = records.filter(or_(GetTicketRecord.status == 'normal', GetTicketRecord.status == 'verify'))
        new_records = []
        for record in records:
            if record.is_expire:
                new_records.append(record)

    elif type == 'expire':
        new_records = []
        for record in records:
            if not record.is_expire:
                new_records.append(record)

    return render_template('mobile/my_tickets.html', type=type, nav=2, records=new_records)


@bp.route('/my_tickets_detail')
def tickets_detail():
    """券　详情页面"""
    openid = session.get("openid")
    user_agent = request.headers.get('User-Agent')
    print user_agent
    # 如果操作是在微信网页端进行，要获取openid
    if 'MicroMessenger' in user_agent:
        if not openid:
            code = request.args.get("code")
            if not code:
                print "not code"
                return redirect(WeixinHelper.oauth2(request.url))
            else:
                wechat_login_fun(code)

    tickets_id = request.args.get('tid', 0, type=int)
    print "ticket_id", tickets_id
    ticket = GetTicketRecord.query.get(tickets_id)
    now = datetime.date(datetime.now())
    if ticket:
        expire_date = datetime.date(ticket.create_at) + timedelta(days=ticket.discount.usable)
        isexpire = (now - expire_date).days
        print '-' * 10, isexpire
    else:
        expire_date = ""
        isexpire = True
    shops = ticket.discount.shops
    return render_template('mobile/my_tickets_detail.html', nav=2, ticket=ticket, discount=ticket.discount,
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
        if access_token:
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
            print "target_user,", message.target
            print "from_user,", message.source
            print "message_type:", message.type
            openid = message.source
            # print request.data
            # 用户发送文本消息
            if message.type == 'text':
                if message.content == 'test':
                    response = wechat.response_text(u'^_^')
                else:
                    response = wechat.response_text(u'您好！')
                if not g.user:
                    # 检查用户是否存在
                    user = User.query.filter(User.profile.any(Profile.openid == openid)).first()
                    if user is not None:
                        signin_user(user)
                        print u'新用户（%s）关注微信...' % user.name
                    else:
                        user = add_wechat_user_to_db(openid)
                    session['openid'] = openid
                else:
                    user = g.user
                message = WechatMessage(user_id=user.id, content=message.content)
                db.session.add(message)
                db.session.commit()
            # 用户发送图片消息
            elif message.type == 'image':
                response = wechat.response_text(u'图片')
            elif message.type == 'scan':
                if message.key and message.ticket:
                    # TODO 扫码回收优惠券,这里还要判断扫码的用户是否为该品牌店授权的店员
                    # TODO 考虑到还有绑定店员的扫码事件,key分为两种：11[brandid],12[discount_id]
                    logging.info(message.key[0:2])
                    logging.info(message.key[2])
                    if message.key[0:2] == '11':
                        brand_id = int(message.key[2:])
                        brand = Brand.query.get(brand_id)
                        if not brand:
                            response = wechat.response_text("要绑定的店铺不存在")
                        data = {"bid": brand_id}
                        url_text = current_app.config.get("SITE_DOMAIN") + "/check_saler_info" + "?" + urlencode(data)
                        brand_text = "<a href='{0}'>{1}</a>".format(url_text, brand.name)
                        print brand_text

                        text = "您正在申请绑定门店%s,点击输入手机号验证身份" % brand_text
                        response = wechat.response_text(text)
                    elif message.key[0:2] == '12':
                        record_id = int(message.key[2:])
                        ticket_record = GetTicketRecord.query.get(record_id)
                        logging.info("tid" + str(ticket_record.id))
                        # 判断扫码用户是否为该店铺的店员
                        discount_id = ticket_record.discount_id
                        discount = Discount.query.get(discount_id)
                        scan_user = User.query.filter(User.profile.any(Profile.openid == openid)).first()
                        salers = Saler.query.filter(Saler.user_id == scan_user.id)
                        if salers.count() > 0:
                            saler = salers.filter(Saler.brand_id == discount.brand_id).first()
                            if not saler:
                                brand = Brand.query.get(discount.brand_id)
                                tip = "您不是该店铺{0}的店员".format(brand.name)
                                response = wechat.response_text(tip)
                            else:
                                callback_ticket(record_id)
                                saler.count += 1
                                db.session.add(saler)
                                db.session.commit()
                                response = ""
                        else:
                            tip = "您还没有绑定该店铺"
                            response = wechat.response_text(tip)
            # 用户在关注微信时就将用户数据写入数据库
            elif message.type == 'subscribe':
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
                        data = {"bid": brand_id}
                        url_text = current_app.config.get("SITE_DOMAIN") + "/check_saler_info" + "?" + urlencode(data)
                        brand_text = "<a href='{0}'>{1}</a>".format(url_text, brand.name)
                        text = "您正在申请绑定门店%s,点击输入手机号验证身份" % brand_text
                        response = wechat.response_text(text)

                openid = message.source
                if not g.user:
                    # 检查用户是否存在
                    user = User.query.filter(User.profile.any(Profile.openid == openid)).first()
                    if user is None:
                        add_wechat_user_to_db(openid)
                        print u'新用户（%s）关注微信' % user.name

                response = wechat.response_text(u'欢迎关注汝州百事优惠圈')
            elif message.type == 'location':
                # 这里有location事件 TODO
                latitude, longitude, precision = message.latitude, message.longitude, message.precision
                print '-' * 10, latitude, longitude, precision, request.remote_addr
                session['latitude'] = latitude
                session['longitude'] = longitude
                session['precision'] = precision
                g.latitude = latitude
                g.longitude = longitude
                g.precision = precision

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
            wechat_login_fun(code)


def add_wechat_user_to_db(from_user):
    """
    添加微信用户到数据库，在数据库创建一个对应的user关联在一起
    """

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


@bp.route('/get_distinct', methods=['GET', 'POST'])
def get_distinct():
    default_point = (112.873668, 34.156861)
    if not g.longitude or not g.latitude:
        curr_user_point = default_point
    else:
        curr_user_point = (g.longitude, g.latitude)
    for shop in Shop.query.all():
        print shop.id, shop.store, great_circle(curr_user_point, (shop.lng, shop.lat)).kilometers

    return make_response('this is test')


def wechat_login_fun(code):
    data = json.loads(WeixinHelper.getAccessTokenByCode(code))
    access_token, openid, refresh_token = data.get("access_token"), data.get("openid"), data.get("refresh_token")
    userinfo = json.loads(WeixinHelper.getSnsapiUserInfo(access_token, openid))
    print "user_info,", userinfo
    # print openid

    if not g.user:
        # 检查用户是否存在
        user = User.query.filter(User.profile.any(Profile.openid == openid)).first()
        if user is not None:
            signin_user(user)
            session['openid'] = openid
            session['access_token'] = openid

            print u'与微信用户关联的user（%s） 已开始登陆网站...' % user.name
        else:
            add_wechat_user_to_db(openid)


def count_last_week_data(brand_arr):
    """统计上周七天内的数据
    [0, 0, 0, 0, 0, 0, 0]
    周一-周日：0-6
    过期日期：优惠券创建时间+发放时间+1天
    1.首先获取当天日期
    2.然后获取上周一日期
    3.for循环得出上周7天日期
    """
    import datetime

    expire_data = [0, 0, 0, 0, 0, 0, 0]
    get_ticket_data = [0, 0, 0, 0, 0, 0, 0]
    callback_data = [0, 0, 0, 0, 0, 0, 0]
    today = datetime.date.today()
    last_monday = today - timedelta(days=today.weekday() + 7)
    for i in range(0, 6):
        index_day = last_monday + timedelta(days=i)
        expire_data[i] += int(GetTicketRecord.query.filter(
            GetTicketRecord.get_expire_date == index_day + timedelta(days=1)).count())
        get_ticket_data[i] += int(
            GetTicketRecord.query.filter(func.date(GetTicketRecord.create_at) == index_day).filter(
                GetTicketRecord.discount.has(Discount.brand_id.in_(brand_arr))).count())
        callback_data[i] += int(GetTicketRecord.query.filter(func.date(GetTicketRecord.create_at) == index_day,
                                                             GetTicketRecord.status == 'usedit').filter(
            GetTicketRecord.discount.has(Discount.brand_id.in_(brand_arr))).count())
    return expire_data, get_ticket_data, callback_data
