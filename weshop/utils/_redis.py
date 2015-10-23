# coding: utf-8
import time
from flask import current_app
from datetime import datetime
from redis import Redis


def set_user_active_time(user_id):
    """将此用户标记为online"""
    r = _connect_redis()
    if r:
        user_key = 'user-active:%d' % user_id
        p = r.pipeline()
        p.set(user_key, int(time.time()))
        p.execute()


def get_user_active_time(user_id):
    """获取用户最后登录时间，若不存在则返回None"""
    r = _connect_redis()
    if r:
        user_key = 'user-active:%d' % user_id
        active_time = r.get(user_key)
        if active_time:
            return datetime.fromtimestamp(int(active_time))
        else:
            return None
    else:
        return None

class LoginState(object):
    @staticmethod
    def signin(token, user_id):
        r = _connect_redis()
        if r:
            user_key = 'user-token:%s' % token 
            p = r.pipeline()
            p.set(user_key, user_id)
            p.execute()
    
    @staticmethod
    def signout(token):
        r = _connect_redis()
        if r:
            user_key = 'user-token:%s' % token 
            p = r.pipeline()
            p.delete(user_key)
            p.execute()
    
    @staticmethod
    def check_login(token):
        r = _connect_redis()
        if r:
            user_key = 'user-token:%s' % token
            user_id = r.get(user_key)
            if user_id:
                return user_id
            else:
                return -1
        else:
            return -1


def _connect_redis():
    """建立Redis连接"""
    config = current_app.config
    if config.get('REDIS'):
        return Redis(host=config.get('REDIS_HOST'), port=config.get('REDIS_PORT'),
                     db=config.get('REDIS_DB'))
    else:
        return None