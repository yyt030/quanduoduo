#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from flask import g
from flask_wtf import Form
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import TextAreaField, SelectField, PasswordField, RadioField, TextField, HiddenField, \
    IntegerField
from wtforms.validators import DataRequired, Regexp, EqualTo, InputRequired




class MessageForm(Form):
    content = HiddenField('私信内容', validators=[DataRequired('内容不能为空')])


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


class RealNameAuthForm(Form):
    """实名认证"""
    id_image = FileField('身份证')
    student_image = FileField('学生证')
    teacher_image = FileField('教师证')


class FamousTeacherAuthForm(Form):
    """名师认证"""
    rank_id = SelectField('职称', coerce=int, validators=[InputRequired('职称不能为空')])
    teach_idea = TextAreaField('教学理念', validators=[DataRequired('教学理念不能为空')])
    teach_special = TextAreaField('教学特长', validators=[DataRequired('教学特长不能为空')])
    teach_experience = TextAreaField('教学经历', validators=[DataRequired('教学经历不能为空')])
    teach_achievement = TextAreaField('教学成果', validators=[DataRequired('教学成果不能为空')])
    other_material = TextAreaField('其他资料')


class TeacherAuthenForm(Form):
    """老师认证(新)"""
    real_name = TextField('真实姓名')
    degree = SelectField('专业', choices=[(0, '请选择学历'), (1, '大专'), (2, '本科'), (3, '硕士'), (4, '博士')])
    university = TextField('所在或毕业大学')
    major = TextField('专业')
    province = SelectField('籍贯')
    study_start_year = SelectField('开始时间', coerce=int, choices=[(i, i) for i in range(2015, 1980, -1)])
    study_end_year = SelectField('结束时间', coerce=int, choices=[(i, i) for i in range(2015, 1980, -1)])
    student_image = FileField("上传学生证或者毕业证")
    major_desc = TextAreaField('高考志愿咨询简介')
