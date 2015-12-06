#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from flask import g
from flask_wtf import Form
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import TextAreaField, SelectField, PasswordField, RadioField, TextField, HiddenField, \
    IntegerField, FloatField
from wtforms.validators import DataRequired, Regexp, EqualTo, InputRequired


class ShopSetting(Form):
    brand = TextField('品牌名', description='', default='')
    store = TextField('门店', description='如：黄河路店', default='')
    title = TextField('公告栏', description='', default='')
    phone = TextField('手机号', description='')
    address = TextField('详细地址', description='')
    lng = TextField('', description='')
    lat = TextField('', description='')


class BrandSetting(Form):
    """品牌设置"""
    brand = TextField('品牌名', description='')
    industry_1 = SelectField('行业', coerce=str, choices={})
    industry_2 = SelectField('子类目', coerce=str, choices={})
    intro = TextAreaField("简介", description='可留空不填')
    image = TextField('背景', description='', default='back.jpg')
    thumb = TextField('logo', description='', default='icon.jpg')


class BrandAccountSetting(Form):
    username = TextField('商家账户', description='', default='')
    password = HiddenField("密码")
    repassword = HiddenField("确认密码")


class DiscountSetting(Form):
    """折扣设置"""
    title = TextField('券面名称', description='', default='')
    type = TextField('优惠形式', description='', default='')
    intro = TextAreaField("温馨提示", default='')
    image = TextField("封面图", default='')
    supply = TextField("每天开抢时间", default='00')
    number = TextField("每天数量限制", default=20)
    usable = TextField("领券后有效期，含当天", default=7)
    perple = TextField("每人可领次数", default=5)
    limits = TextField("剩余发放天数", default=1)
    store = RadioField("", default=0)
