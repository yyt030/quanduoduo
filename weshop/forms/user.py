#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from flask import g
from flask_wtf import Form
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import TextAreaField, SelectField, PasswordField, RadioField, TextField, HiddenField, \
    IntegerField
from wtforms.validators import DataRequired, Regexp, EqualTo, InputRequired


class PayForm(Form):
    month = SelectField('充值时长', validators=[DataRequired('充值时长不能为空')],
                        choices=[(i, "%d个月" % i) for i in range(1, 13)], coerce=int)


class ChangePwdForm(Form):
    """Form for change password"""
    old_password = PasswordField('原密码', validators=[DataRequired('原密码不能为空')])
    new_password = PasswordField('新密码', validators=[DataRequired('新密码不能为空')])
    re_new_password = PasswordField('重复新密码', validators=[
        DataRequired('请再次输入新密码'),
        EqualTo('new_password', message='两次密码输入不一致')
    ])

    # 验证用户名是否重复
    def validate_old_password(self, field):
        if not g.user.check_password(field.data):
            raise ValueError('密码错误')


class SearchUserForm(Form):
    name = TextField('姓名', validators=[DataRequired()])


class UploadForm(Form):
    photo_types = (("0", "消费环境"), ("1", "菜品介绍"), ("2", "服务项目"), ("3", "套餐说明"), ("4", "营销广告"))
    types = SelectField("类型", choices=photo_types)
