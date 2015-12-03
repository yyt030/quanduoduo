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
            flash('此操作需要登录账户')
            return redirect(url_for('site.signin'))
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

def require_teacher(func):
    """Check if user is teacher"""

    @wraps(func)
    def decorator(*args, **kwargs):
        if not g.user:
            flash('此操作需要登录账户')
            return redirect(url_for('account.signin'))
        if g.user.role != 'teacher':
            abort(403)
        return func(*args, **kwargs)

    return decorator


def require_parent_or_student(func):
    """Check if user is parent or student"""

    @wraps(func)
    def decorator(*args, **kwargs):
        if not g.user:
            flash('此操作需要登录账户')
            return redirect(url_for('account.signin'))
        if g.user.role not in ['parent', 'student']:
            abort(403)
        return func(*args, **kwargs)

    return decorator


ADMIN_EMAIL = "admin@tuomeng.com"
ADMIN_PSW = "tuomeng2014"


def require_admin(func):
    """Check if user is admin"""

    @wraps(func)
    def decorator(*args, **kwargs):
        if not g.user:
            flash('此操作需要登录账户')
            return redirect(url_for('admin.login'))
        if g.user.name != 'admin' or g.user.email != 'admin@tuomeng.com':
            abort(403)
        return func(*args, **kwargs)

    return decorator