#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from flask import g
from flask_wtf import Form
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import TextAreaField, SelectField, PasswordField, RadioField, TextField, HiddenField, \
    IntegerField
from wtforms.validators import DataRequired, Regexp, EqualTo, InputRequired


class SiteInfo(Form):
    url = TextField('网站网址', default='')
    title = TextField('首页TITLE标题', default='')
    phone = TextField('电话', default='')
    email = TextField('邮箱', default='')
    address = TextField('公司地址', default='')
    icp = TextField('备案号', default='')
    desc = TextAreaField('简介', default='')


class CompanyInfo(Form):
    name = TextField('公司名称', default='')
    tel = TextField('电话', default='')
    email = TextField('邮箱', default='')
    alipay_nickname = TextField('支付宝昵称', default='')
    alipay_name = TextField('支付宝名称', default='')
    alipay_account = TextField('支付宝账号', default='')
    desc = TextField('公司描述', default='')
    address = TextField('公司地址', default='')



