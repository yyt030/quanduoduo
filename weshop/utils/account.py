#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from flask import session
from weshop.models import User
import codecs


def signin_user(user):
    """Signin user"""
    session.permanent = 1
    session['role'] = user.role
    session['user_id'] = user.id


def signout_user():
    """Signout user"""
    session.pop('user_id', None)


def get_current_user():
    """获取当前user"""
    if not 'user_id' in session:
        return None
    user = User.query.filter(User.id == session['user_id']).first()
    if not user:
        signout_user()
        return None
    return user


class Singleton(object):
    _instances = {}

    def __new__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__new__(cls, *args, **kwargs)
        return cls._instances[cls]


class CheckName(Singleton):
    v = None

    def __init__(self, app, filename=None):
        filename = app.config.get('PROJECT_PATH') + '/dict.txt'
        if not self.__class__.v:
            my_file = codecs.open(filename, "r", "utf-8")
            line = my_file.readline()
            v = []
            while line:
                v[len(v):] = line.strip().split(' ')
                line = my_file.readline()
            self.__class__.v = v
            # print __name__ + '->init'

    @staticmethod
    def check(name):
        """
        check if name is a legal chinese name
        the encoding of name must be utf-8
        """
        v = CheckName.v
        # print 'name:' + name + ' ' + str(type(name)) + ' len:' + str(len(name))
        if len(name) < 2 or len(name) > 4:
            return False
        ret = False
        nt = name[:1]
        if nt in v:
            ret = True
        if len(name) > 2:
            nt = name[:2]
            if nt in v:
                ret = True
        for t in name:
            o = ord(t)
            if o < 0x4e00 or o >= 0x9fa6:
                ret = False
                break
        return ret

