# !/usr/bin/env python
# -*- coding: UTF-8 -*-
from flask import g
from flask_wtf import Form
from wtforms import TextAreaField, SelectField, PasswordField, RadioField, TextField, HiddenField, \
    IntegerField, FileField
from wtforms.validators import DataRequired, Regexp, EqualTo, InputRequired
from ..utils.helper import validate_user_info


class QuestionForm(Form):
    """提问form"""
    content = TextAreaField('内容', validators=[DataRequired('内容不能为空')])
    upload_img = HiddenField()
    receiver_id = HiddenField()
    exercise_id = HiddenField()
    course_id = HiddenField()

    # def validate_content(self, field):
    #     if not validate_user_info(field.data):
    #         raise ValueError('内容不应包含敏感信息')


class AnswerForm(Form):
    """回答form"""
    content = TextAreaField('回答', validators=[DataRequired('回答不能为空')])
    upload_img = HiddenField()
    # def validate_content(self, field):
    #     if not validate_user_info(field.data):
    #         raise ValueError('内容不应包含敏感信息')


class AskForm(Form):
     """快速提问 """
     content = HiddenField()
     upload_img = HiddenField()
     course_id = HiddenField()