#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from flask import g
from flask_wtf import Form
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import TextAreaField, SelectField, PasswordField, RadioField, TextField, HiddenField, \
    IntegerField, FloatField
from wtforms.validators import DataRequired, Regexp, EqualTo, InputRequired


class ShopSetting(Form):
    brand = TextField('品牌名', description='')
    store = TextField('门店', description='如：黄河路店')
    title = TextField('公告栏', description='')
    phone = TextField('手机号', description='')
    address = TextField('详细地址', description='')
    lng = TextField('', description='')
    lat = TextField('', description='')


class BrandSetting(Form):
    """品牌设置"""
    name = TextField('品牌名', description='')
    industry_1 = SelectField('', coerce=str, choices={})
    industry_2 = SelectField('', coerce=str, choices={})
    intro = TextAreaField("简介", description='可留空不填')
    image = TextField('背景', description='', default='back.jpg')
    thumb = TextField('logo', description='', default='icon.jpg')
