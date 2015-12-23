# !/usr/bin/env python
# -*- coding: UTF-8 -*-
from datetime import datetime, timedelta, time
from io import BytesIO
import json
import logging
import os
import string
import re, urllib2
import random
from PIL import Image
from coverage.html import STATIC_PATH
from flask import render_template, Blueprint, redirect, url_for, g, session, request, \
    make_response, current_app, send_from_directory, send_file
from sqlalchemy import or_
from wechat_sdk import WechatBasic
from weshop import csrf
from weshop.forms.shop import ShopSetting, BrandSetting
from weshop.utils import devices
from weshop.utils.devices import checkMobile
from ..models import db, User, Brand, Shop, Discount, GetTicketRecord, ShopPhoto, Saler
from ..forms import SigninForm, UploadForm
from ..utils.permissions import require_user, require_visitor, require_admin
from ..utils.uploadsets import images, random_filename, process_question, avatars
import datetime

bp = Blueprint('shop', __name__)


@bp.route('/select', methods=['GET', 'POST'])
@require_user
def select():
    """选择品牌"""
    # TODO user_id
    user = g.user
    # TODO 权限
    if user.role == 'admin':
        brands = Brand.query.filter(Brand.status == 1)
    else:
        # 仅仅获取当前帐号下品牌
        brands = user.brandaccounts.filter(Brand.status == 1)

    act = request.args.get("act")
    if act == 'discount':
        handle = "发布优惠"
    elif act == 'ticket_record':
        handle = "领券记录"
    elif act == 'account':
        handle = "商家账户"
    elif act == 'checkout':
        handle = '绑收银台'
    elif act == 'manage':
        handle = '管理门店'
    elif act == 'upload':
        handle = '编辑相册'
    else:
        handle = "管理门店"
    return render_template('shop/select_brand.html', handle=handle, act=act, brands=brands)


@bp.route('/qrcode', methods=['GET', 'POST'])
def qrcode():
    """管理二维码"""
    # TODO user_id
    id = request.args.get("id", type=int)
    shop = Shop.query.get(id)
    return render_template('shop/qrcode.html', shop=shop)


@bp.route('/upload', methods=['GET', 'POST'])
def upload():
    """上传相册"""
    # TODO user_id
    form = UploadForm()
    bid = int(request.args.get("bid", 0))
    brand = Brand.query.get_or_404(bid)
    shop_photos = ShopPhoto.query.filter(ShopPhoto.brand_id == bid)
    datas = dict(request.form)
    if request.method == 'POST':
        # print datas
        url = request.referrer
        new_images = datas.get('image-new[]')
        old_images = datas.get('image-old[]')
        titles = datas.get('title-new[]')
        types = datas.get('class-new[]')
        print old_images
        if new_images:
            item_count = len(new_images)
            for i in range(0, item_count):
                photo = ShopPhoto(image=new_images[i], type=types[i], intro=titles[i], brand_id=bid, user_id=g.user.id)
                db.session.add(photo)
                db.session.commit()
        if old_images:
            id_items = datas.get('id[]')
            for i in range(0, len(old_images)):
                if old_images[i] == 'true':
                    delete_id = int(id_items[i])
                    photo = ShopPhoto.query.get(delete_id)
                    db.session.delete(photo)
                    db.session.commit()
        return render_template('account/ok.html', tip="相册更新成功！", url=url)

    return render_template('shop/upload.html', form=form, shop_photos=shop_photos)


@bp.route('/photo_detail/<int:photo_id>', methods=['GET', 'POST'])
@require_user
def photo_detail(photo_id):
    """相册详情"""
    photo = ShopPhoto.query.get(photo_id)
    return render_template('shop/photo_detail.html', photo=photo)


@bp.route('/photo_list', methods=['GET', 'POST'])
def photo_list():
    """相册列表"""
    bid = request.args.get("bid", type=int)
    shop_id = request.args.get("shop_id", type=int)
    photos = ShopPhoto.query.filter(ShopPhoto.brand_id == bid)
    shop = Shop.query.get(shop_id)
    return render_template('shop/photo_list.html', shop=shop, photos=photos)


@bp.route('/setting', methods=['GET', 'POST'])
@require_user
def setting():
    """
    门店发布、编辑
    管理连锁店
    """
    act = request.args.get("act")
    bid = int(request.args.get("bid", 0))
    if act == "publish":
        form = ShopSetting()
        if not session.get("brand"):
            bid = int(request.args.get("bid", 0))
            session['brand'] = bid
        else:
            bid = session['brand']
        brandinfo = Brand.query.get(bid)
        brandForm = BrandSetting(brand=brandinfo.name, intro=brandinfo.intro, image=brandinfo.image,
                                 thumb=brandinfo.thumb, industry_1=brandinfo.industry_1,
                                 industry_2=brandinfo.industry_2)

        if form.validate_on_submit():
            exist = Shop.query.filter(Shop.store == form.store.data).first()
            if exist:
                return render_template('shop/error.html', error='此店铺已存在！')
            else:
                shop = Shop(store=form.store.data, brand_id=bid, title=form.title.data, phone=form.phone.data,
                            address=form.address.data, lng=form.lng.data, lat=form.lat.data)
                db.session.add(shop)
                db.session.commit()
                del session['brand']
                return render_template('shop/ok.html', tip='商户创建成功！', bid=bid)
        return render_template('shop/setting.html', form=form, brandForm=brandForm, act=act, brandinfo=brandinfo)
    elif act == 'modify':
        id = int(request.args.get("id", 0))
        shop = Shop.query.get(id)
        form = ShopSetting(store=shop.store, title=shop.title, phone=shop.phone, address=shop.address,
                           lat=shop.lat, lng=shop.lng)
        brandinfo = Brand.query.get(shop.brand_id)
        brandForm = BrandSetting(brand=brandinfo.name, intro=brandinfo.intro, image=brandinfo.image,
                                 thumb=brandinfo.thumb, industry_1=brandinfo.industry_1,
                                 industry_2=brandinfo.industry_2)

        if form.validate_on_submit():
            shop.store = form.store.data
            shop.phone = form.phone.data
            shop.address = form.address.data
            shop.lng = form.lng.data
            shop.lat = form.lat.data
            db.session.add(shop)
            db.session.commit()
            return render_template('shop/ok.html', tip='商户信息更新成功！', bid=shop.brand_id)
        return render_template('shop/setting.html', form=form, brandForm=brandForm, act=act, shop_id=id,
                               brandinfo=shop.brand)
    elif act == 'discount':
        return redirect(url_for('discount.manage', bid=bid))
    elif act == 'ticket_record':
        return redirect(url_for('discount.getlist', bid=bid))
    elif act == 'account':
        return redirect(url_for('brand.account', bid=bid))
    elif act == 'bind_saler':
        return redirect(url_for('shop.bind_saler', bid=bid))
    elif act == 'upload':
        return redirect(url_for('shop.upload', bid=bid))
    else:
        return redirect(url_for('brand.shop_list', bid=bid))


@bp.route('/resource/<string:folder1>/<string:folder2>/<string:filename>', methods=['GET'])
def get_resourse(folder1, folder2, filename):
    BASE_URL = os.path.join(current_app.config.get('PROJECT_PATH'), 'resource/%s/%s') % (folder1, folder2)

    ext = os.path.splitext(filename)[1][1:]
    mimetypes = {"jpg": 'image/jpg', "css": 'text/css', "png": "image/png", "js": 'application/x-javascript',
                 "xml": 'application/xHTML+XML'}
    return send_from_directory(BASE_URL, filename, mimetype=mimetypes.get(ext))


@bp.route('/<int:shop_id>', methods=['GET'])
def detail(shop_id):
    shop = Shop.query.get_or_404(shop_id)
    discounts = shop.shop_discounts.count()
    shop_photos = ShopPhoto.query.filter(ShopPhoto.brand_id == shop.brand_id)
    return render_template('shop/show.html', shop=shop, shop_photos=shop_photos, discounts=discounts)


@bp.route('/delete', methods=['GET'])
@require_admin
def delete():
    shop_id = int(request.args.get("id", 0))
    shop = Shop.query.get_or_404(shop_id)
    db.session.delete(shop)
    db.session.commit()
    # url = request.args.get("source")
    url = request.referrer
    print request.url
    return render_template('account/ok.html', tip="删除成功！", url=url)


@bp.route('/list', methods=['GET'])
def list():
    bid = int(request.args.get("bid", 0))
    shops = Shop.query.filter(Shop.id == bid)
    return render_template('shop/list.html', shops=shops)


@bp.route('/checkout', methods=['GET'])
def checkout():
    verify = False
    is_expire = False
    usedit = False
    discount_id = request.args.get("discount_id", 0, type=int)
    record_id = request.args.get("record_id", 0, type=int)  # 领取id
    do = request.args.get("do")
    discount = Discount.query.get_or_404(discount_id)
    shops = discount.shops
    record = GetTicketRecord.query.get_or_404(record_id)
    if record.status == 'usedit':
        usedit = True
    if discount:
        expire_date = discount.create_at + timedelta(days=discount.usable)
        print discount.create_at, discount.usable
        expire_date = expire_date.date()
        if datetime.datetime.now().date() > expire_date:
            is_expire = True

    # 获取二维码ticket
    if do == 'get_qrcode':
        if record.status == 'verify':
            verify = True
        if not record.ticket:
            # 获取永久二维码 scene_id前缀12表示是优惠券类型的二维码
            wechat = WechatBasic(appid=current_app.config.get('WECHAT_APPID'),
                                 appsecret=current_app.config.get('WECHAT_APPSECRET'))
            data = {"action_name": "QR_LIMIT_SCENE",
                    "action_info": {"scene": {"scene_id": int(str("12") + str(record.id))}}}
            get_ticket_data = wechat.create_qrcode(data)
            ticket = get_ticket_data.get("ticket")
            session['ticket'] = ticket
            # 写入数据库
            record.ticket = ticket
            db.session.add(record)
            db.session.commit()
        else:
            ticket = record.ticket
        return json.dumps({"message": {"verify": verify, "ticket": ticket, "expire": 0}})
    elif do == 'download_qrcode':
        return ""
    return render_template('shop/checkout.html', shops=shops, expire_date=expire_date, is_expire=is_expire,
                           record_id=record_id, record=record, usedit=usedit,
                           discount=discount)


@bp.route('/bind_saler', methods=['GET', 'POST'])
def bind_saler():
    """绑定收银台"""
    bid = int(request.args.get("bid", 0))
    do = request.args.get("do", 0)
    brand = Brand.query.get(bid)
    salers = brand.brand_salers.count()
    users = brand.brandaccounts
    shop_id = 0
    # 获取二维码
    wechat = WechatBasic(appid=current_app.config.get('WECHAT_APPID'),
                         appsecret=current_app.config.get('WECHAT_APPSECRET'))
    temp_data = {"expire_seconds": 604800, "action_name": "QR_SCENE",
                 "action_info": {"scene": {"scene_id": int(str("11") + str(brand.id))}}}
    # data = {"action_name": "QR_LIMIT_SCENE", "action_info": {"scene": {"scene_id": int(str("11") + str(brand.id))}}}
    get_ticket_data = wechat.create_qrcode(temp_data)
    ticket = get_ticket_data.get("ticket")
    if do == 'download_qrcode':
        logging.info("download_qrcode")
        response=wechat.show_qrcode(ticket)
        response = make_response(response.content)
        response.headers['Content-Type'] = 'image/jpg'
        attachment_name="attachment; filename=汝州百事优惠圈绑定收银台专用二维码.jpg"
        response.headers['Content-Disposition'] = attachment_name
        return response


    return render_template('shop/bind_saler.html', brand=brand, ticket=ticket, users=users)


    # 您已成功绑定洛阳科技职业学院游泳馆的微信收银台 TODO


@bp.route('/delete_saler', methods=['GET'])
def delete_saler():
    """删除店员"""
    user_id = int(request.args.get("id", 0))
    if id:
        saler = Saler.query.filter(Saler.user_id == user_id).first()
        db.session.delete(saler)
        db.session.commit()
    return redirect('/shop/bind_saler')
