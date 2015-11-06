#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from flask_wtf import Form
from sqlalchemy import or_
from wtforms import TextField, PasswordField, BooleanField, HiddenField, RadioField, SelectField, \
    TextAreaField, IntegerField
from wtforms.validators import DataRequired, EqualTo, Email, AnyOf, Length, Regexp, InputRequired
from ..models import User
from ..utils.account import CheckName


class SigninForm(Form):
    """登陆表单"""
    username = TextField('登录名:', validators=[DataRequired(u'邮箱不能为空')], description=u'用户名、QQ、邮件地址或手机号')
    password = PasswordField('密码:', validators=[DataRequired(u'密码不能为空')], description=u'密码')

    # 验证密码
    def validate_password(self, field):
        name = self.username.data.replace(' ', '')
        user = User.query.filter(or_(User.name == name, User.email == name, User.mobile==name)).first()

        if not user:
            raise ValueError(u'账户或密码错误')

        # if not user.is_active:
        #     raise ValueError(u'该账户尚未激活，请前往您的邮箱点击验证链接激活此账户')

        if user.check_password(field.data):
            self.user = user
        else:
            raise ValueError(u'账户或密码错误')


class RegisterForm(Form):
    """注册表单"""
    returnFlag = False
    name = TextField('登录名:', validators=[DataRequired('用户名不能为空')])
    qq = TextField('qq:', validators=[DataRequired('用户名不能为空')])
    mobile = TextField('手机号:', validators=[DataRequired('手机号不能为空')])
    email = TextField('邮箱地址:', description="用于验证账户及找回密码", validators=[DataRequired('邮箱不能为空'), Email('无效的邮箱')])
    address = TextField('发货地址:', description="发货详细地址或所在省市", validators=[DataRequired('邮箱不能为空'), Email('无效的邮箱')])
    password = PasswordField('密码:', validators=[DataRequired('密码不能为空')])
    repassword = PasswordField('确认密码:', validators=[DataRequired('请再次输入密码'),
                                                    EqualTo('password', message='两次密码输入不一致')])

    # 验证用户名是否重复
    def validate_name(self, field):
        if field.data == '':
            raise ValueError('用户名不能为空')

    # 验证密码是否重复
    def validate_email(self, field):
        field.data = field.data.lower()
        field.data = field.data.replace(' ', '')
        if User.query.filter(User.email == field.data).count() > 0:
            raise ValueError('邮箱已存在')


class SignupTeacherBasicForm(Form):
    """老师基本信息表单"""
    sex = RadioField('性别', choices=[('男', '男'), ('女', '女')], validators=[
        InputRequired('性别不能为空')
    ])
    province_id = IntegerField()
    city_id = IntegerField()
    region_id = IntegerField('所在地区',
                             validators=[
                                 DataRequired('所在地区不能为空')
                             ])
    type_id = SelectField('身份', coerce=int, validators=[
        DataRequired('身份不能为空')
    ])
    university = TextField('学校', validators=[
        DataRequired('学校不能为空')
    ])
    university_id = HiddenField()
    desc = TextAreaField('个人简介', validators=[
        DataRequired('个人简介不能为空'),
        Regexp(r'^([^(Q{4}|q{4})|])*$', 0, '请不要留下敏感的数字信息')
    ])


class SignupTeacherExtraForm(Form):
    """老师额外信息表单"""
    charge_id = SelectField('课时费用', coerce=int)
    teach_method_id = RadioField('授课方式',
                                 coerce=int,
                                 validators=[
                                     InputRequired('授课方式不能为空')
                                 ])


class SignupParentOrStudentBasicForm(Form):
    """家长/学生基本信息表单"""
    sex = RadioField('性别', choices=[('男', '男'), ('女', '女')], validators=[
        InputRequired('性别不能为空')
    ])
    province_id = IntegerField()
    city_id = IntegerField()
    region_id = IntegerField('所在地区', validators=[
        DataRequired('所在地区不能为空')
    ])
    desc = TextAreaField('学员简介', validators=[
        Regexp(r'^([^(Q{4}|q{4})|])*$', 0, '请不要留下敏感的数字信息')
    ])


class SignupParentOrStudentExtraForm(Form):
    """家长/学生额外信息表单"""
    charge_id = SelectField('课时报酬', coerce=int)
    require_for_teacher = TextAreaField('对老师的期望')


class SignupOpenidForm(Form):
    """注册表单"""
    email = TextField('验证邮箱', validators=[DataRequired('邮箱不能为空'), Email('无效的邮箱')])
    password = PasswordField('密码', validators=[DataRequired('密码不能为空')])

    def validate_password(self, field):
        email = self.email.data.replace(' ', '')
        user = User.query.filter(User.email == email).first()

        if not user:
            raise ValueError('邮箱不存在')

        if not user.is_active:
            raise ValueError('该账户尚未激活，请前往您的邮箱点击验证链接激活此账户')

        if user.check_password(field.data):
            self.user = user
        else:
            raise ValueError('账户或密码错误')


class RetrieveForm(Form):
    """找回密码"""
    email = TextField('注册邮箱', validators=[DataRequired('邮箱不能为空')])
    token = TextField('验证码')
    returnFlag = False

    # 验证邮箱是否存在
    def validate_email(self, field):
        field.data = field.data.lower()
        if User.query.filter(User.email == field.data).count() == 0:
            raise ValueError('账号不存在')


class NewPwdForm(Form):
    """新密码"""
    newpwd = PasswordField('新密码', validators=[
        DataRequired('密码不能为空'), Length(6, -1, "输入密码的最小长度为6位")
    ])
    pwdagain = PasswordField('重复新密码', validators=[
        DataRequired('请再次输入密码'),
        EqualTo('newpwd', message='两次密码输入不一致')
    ])
