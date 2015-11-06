#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import datetime
from ._base import db


class Brand(db.Model):
    """品牌"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    industry_1 = db.Column(db.String(50))
    industry_2 = db.Column(db.String(50))
    intro = db.Column(db.Text)
    image = db.Column(db.String(200))
    thumb = db.Column(db.String(200))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User')
    create_at = db.Column(db.DateTime, default=datetime.datetime.now)

    def __repr__(self):
        return '<Brand %s>' % self.name

    def shop_count(self):
        return Shop.query.filter(Shop.brand_id == self.id).count()


class Discount(db.Model):
    """优惠券"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), default='')
    intro = db.Column(db.String(500), default='')
    image = db.Column(db.String(50), default='')
    supply = db.Column(db.String(5), default='00')
    number = db.Column(db.Integer, default=20)
    usable = db.Column(db.Integer, default=7)
    perple = db.Column(db.Integer, default=1000)
    limits = db.Column(db.Integer, default=0)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User')

    shop_id = db.Column(db.Integer, db.ForeignKey('shop.id'))
    shop = db.relationship('Shop', backref=db.backref('discounts', lazy='dynamic'))

    count = db.Column(db.Integer, default=0)
    back = db.Column(db.Integer, default=0)
    create_at = db.Column(db.DateTime, default=datetime.datetime.now)
    latest_update = db.Column(db.DateTime, default=datetime.datetime.now)

    def __repr__(self):
        return '<Discount %s>' % self.id


# shop与discount之间的多对多关系表
shop_discount = db.Table('shop_discount',
                         db.Column('discount_id', db.Integer, db.ForeignKey('discount.id')),
                         db.Column('shop_id', db.Integer, db.ForeignKey('shop.id')))


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
