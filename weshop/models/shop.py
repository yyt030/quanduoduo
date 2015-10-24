#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from ._base import db


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

    brand_id = db.Column(db.Integer, unique=True)
    brand = db.relationship('Brand', backref=db.backref('shops', lazy='dynamic'))

    store = db.Column(db.String(50))
    title = db.Column(db.String(400))
    phone = db.Column(db.String(20))
    resideprovince = db.Column(db.String(20), default="")
    residecity = db.Column(db.String(20), default="")
    residedist = db.Column(db.String(20), default="")
    address = db.Column(db.String(100))
    lng = db.Column(db.String(20))
    lat = db.Column(db.String(20))

    def __repr__(self):
        return '<Shop %s>' % self.id


class Brand(db.Model):
    """品牌"""
    id = db.Column(db.Integer, primary_key=True, default=1000000)
    name = db.Column(db.String(50), unique=True)
    industry_1 = db.Column(db.String(50))
    industry_2 = db.Column(db.String(50))
    intro = db.Column(db.Text)
    image = db.Column(db.String(200))
    thumb = db.Column(db.String(200))

    def __repr__(self):
        return '<Brand %s>' % self.name
