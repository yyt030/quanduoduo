#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import datetime
import re
from flask import g
from ..models import User


def timesince(value):
    """Friendly time gap"""
    now = datetime.datetime.now()
    delta = now - value
    if delta.days > 365:
        return '%d年前' % (delta.days / 365)
    if delta.days > 30:
        return '%d个月前' % (delta.days / 30)
    if delta.days > 0:
        return '%d天前' % delta.days
    if delta.seconds > 3600:
        return '%d小时前' % (delta.seconds / 3600)
    if delta.seconds > 60:
        return '%d分钟前' % (delta.seconds / 60)
    return '刚刚'

def get_date(value):
    t = str(value).replace("-","/")
    return t[5:10]

def get_page_name(template_reference):
    """获取当前模板名，并转换成page-site-index的格式"""
    template_name = template_reference._TemplateReference__context.name
    return "page-%s" % template_name.replace('/', '-').split('.')[0]


def striptags(value):
    """过滤html标签"""
    str1 = value.replace('</div>','')
    str2 = str1.replace('<div>',',')
    str3 =str2.replace(',<br>','')
    return  str3

def get_num(value):
    """获取查询的结果个数"""
    nums=value.count()
    return  nums