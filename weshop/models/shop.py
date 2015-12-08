#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import datetime
import random
from ._base import db
import time

# 品牌 和 账户的 many to many 关系
brand_account = db.Table('brand_account',
                         db.Column('brand_id', db.Integer, db.ForeignKey('brand.id')),
                         db.Column('user_id', db.Integer, db.ForeignKey('user.id')))


class Brand(db.Model):
    """品牌"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    industry_1 = db.Column(db.String(50))
    industry_2 = db.Column(db.String(50))
    intro = db.Column(db.Text)
    image = db.Column(db.String(200))
    thumb = db.Column(db.String(200))
    status = db.Column(db.SMALLINT, default=1)

    # create_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    # create_user = db.relationship('User')

    brandaccounts = db.relationship('User', secondary=brand_account,
                                    backref=db.backref('brandaccounts', lazy='dynamic'), lazy='dynamic')

    create_at = db.Column(db.DateTime, default=datetime.datetime.now)

    def __repr__(self):
        return '<Brand %s>' % self.name

    def shop_count(self):
        return Shop.query.filter(Shop.brand_id == self.id).count()


# shop与discount之间的多对多关系表
shop_discount = db.Table('shop_discount',
                         db.Column('discount_id', db.Integer, db.ForeignKey('discount.id')),
                         db.Column('shop_id', db.Integer, db.ForeignKey('shop.id')))


class Discount(db.Model):
    """优惠券
    title 标题
    type 优惠形式
    intro 描述
    image 封面图
    supply 每天开抢时间
    number 每天提供份数
    usable 有效期 默认7天
    perple 每人可领个数
    limits 发放时间
    count 认领次数
    back 回收份数
    create_at 创建时间
    lateset_update 最后更新
    code 优惠券编码  8位唯一
    """
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), default='')
    type = db.Column(db.String(50), default='')
    intro = db.Column(db.String(500), default='')
    image = db.Column(db.String(50), default='')
    supply = db.Column(db.String(5), default='00')
    number = db.Column(db.Integer, default=20)
    usable = db.Column(db.Integer, default=7)
    perple = db.Column(db.Integer, default=1000)
    limits = db.Column(db.Integer, default=0)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User')

    brand_id = db.Column(db.Integer, db.ForeignKey('brand.id'))
    brand = db.relationship('Brand', backref=db.backref('discounts_brands', lazy='dynamic'))

    shops = db.relationship('Shop', secondary=shop_discount,
                            backref=db.backref('shop_discounts', lazy='dynamic'), lazy='dynamic')

    count = db.Column(db.Integer, default=0)
    back = db.Column(db.Integer, default=0)
    create_at = db.Column(db.DateTime, default=datetime.datetime.now)
    latest_update = db.Column(db.DateTime, default=datetime.datetime.now)
    code = db.Column(db.Integer, default=random.randint(10000000, 20000000))

    def is_end(self):
        end_date_time = self.create_at + datetime.timedelta(days=self.limits)
        now_time = datetime.datetime.now()
        if now_time >= end_date_time:
            return True
        else:
            return False

    @property
    def check_status(self):
        "如果发布此优惠券的时间已经过了每天的开抢时间，即表示未开始"
        status = {
            "reviewstatus": "未开始", "momentstatus": "未到时",
            "nobodystatus": "已领完", "closedstatus": "已结束",
            "normalstatus": "可领取"
        }

        end_date_time = self.create_at + datetime.timedelta(days=self.limits)
        now_time = datetime.datetime.now()

        if now_time >= end_date_time:
            if self.number != 0:
                return {"status": "closedstatus", "word": "已结束"}
            else:
                return {"status": "nobodystatus", "word": "已领完"}
        else:

            times_str = str(datetime.datetime.now().date()) + " " + str(self.supply) + ":00:00"
            now_hour = datetime.datetime.now().hour
            if now_hour < int(self.supply):
                return {"status": "reviewstatus", "word": "未开始"}
            else:
                return {"status": "normalstatus", "word": "可领取"}

    @property
    def check_state(self):
        state = {"reviewstate": "已上架", "closedstate": "已删除",
                 "lockedstate": "锁定中", "normalstate": "可领取"}

        return {"state": "normalstate", "word": "可领取"}

    def is_expired(self):
        """过期时间"""

    def __repr__(self):
        return '<Discount %s>' % self.id


class MyFavoriteDiscount(db.Model):
    """收藏的优惠券"""
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User')

    discount_id = db.Column(db.Integer, db.ForeignKey('discount.id'))
    discount = db.relationship('Discount', backref=db.backref('favorite_discounts', lazy='dynamic'))

    create_at = db.Column(db.DateTime, default=datetime.datetime.now)

    def __repr__(self):
        return '<MyFavoriteDiscount %s>' % self.id


class MyFavoriteBrand(db.Model):
    """收藏的商家"""
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User')

    brand_id = db.Column(db.Integer, db.ForeignKey('brand.id'))
    brand = db.relationship('Brand', backref=db.backref('favorite_brands', lazy='dynamic'))

    create_at = db.Column(db.DateTime, default=datetime.datetime.now)

    def __repr__(self):
        return '<MyFavoriteShop %s>' % self.id


# shop 店铺 和 账户的 many to many 关系
shop_account = db.Table('shop_account',
                        db.Column('shop_id', db.Integer, db.ForeignKey('shop.id')),
                        db.Column('user_id', db.Integer, db.ForeignKey('user.id')))


class Shop(db.Model):
    """店铺
    brand:品牌
    store:分店
    title:公告
    resideprovince,residecity,residedist:省市区
    address：地址
    lng：横坐标
    lat: 纵坐标
    """
    id = db.Column(db.Integer, primary_key=True)

    brand_id = db.Column(db.Integer, db.ForeignKey('brand.id'))
    brand = db.relationship('Brand', backref=db.backref('shops', lazy='dynamic'))

    shopaccounts = db.relationship('User', secondary=shop_account,
                                   backref=db.backref('shopaccounts', lazy='dynamic'), lazy='dynamic')

    store = db.Column(db.String(50))
    title = db.Column(db.String(400))
    phone = db.Column(db.String(20))
    province = db.Column(db.String(20), default="")
    city = db.Column(db.String(20), default="")
    dist = db.Column(db.String(20), default="")
    address = db.Column(db.String(100))
    lng = db.Column(db.String(20))
    lat = db.Column(db.String(20))

    def __repr__(self):
        return '<Shop %s>' % self.id


class ShopPhoto(db.Model):
    """商户相册"""
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Enum('0', '1', '2', '3', '4'), default='0')
    brand_id = db.Column(db.Integer, db.ForeignKey('brand.id'))
    brand = db.relationship('Brand', backref=db.backref('brand_photos', lazy='dynamic'))
    image = db.Column(db.String(50))
    intro = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User')

    def __repr__(self):
        return '<Shop %s>' % self.id
