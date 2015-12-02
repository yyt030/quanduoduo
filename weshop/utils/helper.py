# -*- coding: UTF-8 -*-
import json
from random import Random
import re
import urllib2
from flask import request


def random_str(randomlength=30):
    """生成指定长度的随机字符串"""
    str = ''
    chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
    length = len(chars) - 1
    random = Random()
    for i in range(randomlength):
        str += chars[random.randint(0, length)]
    return str


def parse_int(string):
    """将string转换成int，若无法转换，返回None"""
    try:
        value = int(string)
    except Exception:
        value = None
    return value


def get_int_arg(key, default=None):
    """获取int类型的请求参数"""
    return parse_int(request.args.get(key, default))


def validate_user_info(text):
    """验证用户信息是否不含有敏感信息"""
    return _validate_no_phone(text) and _validate_no_qq(text)


def _validate_no_phone(text):
    """检查text中是否有电话号码"""
    text = text.replace(" ", "")
    pattern = re.compile(r'.*1\d{10}.*')  # 首先仍然检查有没有连续11位数字
    match = pattern.match(text)
    if match:
        # 使用Match获得分组信息
        print "Phone Number Found!"
        return False
    else:
        regstr = r'\d+'  # 没有连续11位数字的情况下，检查整个文本中出现的数字
        match_list = re.findall(regstr, text, re.M)
        result_list = ''
        for i in match_list:
            result_list += i
        if len(result_list) >= 10:  # 如果文本中出现的数字总数超过了9个，则认为可能存在电话号码
            print "Suspected Phone Number Detected!"  # 检查到疑似的电话号码
            return False
        else:
            print "Phone Number Not Found"
            return True


def _validate_no_qq(text):
    """检查text中是否有QQ号码"""
    text = text.replace(" ", "")
    pattern = re.compile(r'.*[1-9]\d{4,11}.*')
    match = pattern.match(text)
    if match:
        print "QQ Number Found!"
        return False
    else:
        score = 0  # 使用加权进行判断

        # 首先判断整个文本中的数字是否出现了5个以上
        regstr = r'\d+'  # 没有连续5-12位数字的情况下，检查整个文本中出现的数字
        match_list = re.findall(regstr, text, re.M)  # re.M会输出所有匹配结果，默认只输出第一个匹配
        result_list = ''
        for i in match_list:
            result_list = result_list + i
        if len(result_list) >= 5:
            score = score + 1

        # 然后检查文本中是否出现了QQ、Qq、qq和qQ
        pattern = re.compile(r'.*(QQ|Qq|qQ|qq).*')
        match = pattern.match(text)
        if match:
            score = score + 1

        # 再检查文本中是否出现汉字“扣扣”、“口口”、“蔻蔻”、“koukou”等
        regstr = r'.*(' + u'扣'.encode('utf8') + '|' + u'口'.encode('utf8') + '|' + \
                 u'抠'.encode('utf8') + '|' + u'寇'.encode('utf8') + '|q|Q|kou){2}.*'
        pattern = re.compile(regstr)
        match = pattern.match(text)
        if match:  # 如果匹配，则认为有严重的嫌疑，加权+2
            print "text"
            score = score + 2

        # 如果加权大于等于2，则认为检测到了疑似QQ号
        if score >= 2:
            print "Suspected QQ Number Detected!"  # 检查到疑似的QQ号码
            return False
        else:
            print "QQ Number Not Found"
            return True

headers = {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'}

def get_url_data(url):
    req = urllib2.Request(url=url, headers=headers)
    return_data = urllib2.urlopen(req).read()
    return return_data


