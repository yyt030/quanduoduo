#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from flask import g
from functools import wraps
from flask import abort, redirect, url_for, flash


def require_visitor(func):
    """Check if no user login"""

    @wraps(func)
    def decorator(*args, **kwargs):
        if g.user:
            return redirect(url_for('site.home'))
        return func(*args, **kwargs)

    return decorator


def require_user(func):
    """Check if user login"""

    @wraps(func)
    def decorator(*args, **kwargs):
        if not g.user:
            # flash('此操作需要登录账户')
            return redirect(url_for('site.login'))
        return func(*args, **kwargs)

    return decorator


def require_mobile_user(func):
    """Check if mobile user login"""

    @wraps(func)
    def decorator(*args, **kwargs):
        if not g.user:
            return redirect(url_for('wechat.signin'))
        return func(*args, **kwargs)

    return decorator





ADMIN_EMAIL = "admin"
ADMIN_PSW = "admin"


def require_admin(func):
    """Check if user is admin"""

    @wraps(func)
    def decorator(*args, **kwargs):
        if not g.user:
            # flash('此操作需要登录账户')
            return redirect(url_for('admin.login'))
        if g.user.name != 'admin' or g.user.email != 'admin@tuomeng.com':
            abort(403)
        return func(*args, **kwargs)

    return decorator